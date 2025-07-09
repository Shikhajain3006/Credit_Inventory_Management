import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import io
import tempfile
import xlsxwriter

st.set_page_config(layout="centered")
st.title("📊 SOX Audit Automation Web App")

account_type_to_process_group = {
    "accounts payable": "PTP",
    "inventory": "Inventory",
    "order to cash": "OTC",
    "payroll": "Payroll",
    "financial close": "Financial Close",
    "fixed assets": "Fixed Assets",
    "tax": "Tax",
    "treasury": "Treasury",
    "real estate": "RE",
    "business combinations": "Business Combinations"
}

color_rules = {
    ("In Scope", "Yes"): '#C6EFCE',
    ("In Scope", "No"): '#FF9999',
    ("Out of Scope", "Yes"): '#FFEB9C',
    ("Out of Scope", "No"): '#D9D9D9',
    "In Scope & Non-Key": '#F4B084',
    "Out of Scope & Key": '#D9D2E9'
}


def clean_number(value):
    if isinstance(value, str):
        value = value.replace(',', '').replace('%', '').strip()
    try:
        return float(value)
    except:
        return 0.0

def map_control_id_to_process(control_id):
    try:
        id_fragment = str(control_id).split("-")[1]
        numeric_str = ''.join([ch if ch.isdigit() or ch == '.' else '' for ch in id_fragment])
        numeric_part = float(numeric_str[:4])
        if 1.0 <= numeric_part < 2.0: return "PTP"
        elif 2.0 <= numeric_part < 3.0: return "Payroll"
        elif 3.0 <= numeric_part < 4.0: return "OTC"
        elif 4.0 <= numeric_part < 5.0: return "Inventory"
        elif 5.0 <= numeric_part < 6.0: return "Financial Close"
        elif 6.0 <= numeric_part < 7.0: return "Fixed Assets"
        elif 7.0 <= numeric_part < 8.0: return "Treasury"
        elif 8.0 <= numeric_part < 9.0: return "Tax"
        elif 9.0 <= numeric_part < 10.0: return "RE"
        elif 10.0 <= numeric_part < 11.0: return "Business Combinations"
        else: return "Other"
    except:
        return "Unknown"

st.markdown("---")

uploaded_rcm = st.file_uploader("Upload RCM Excel File", type=["xlsx"])
uploaded_tb = st.file_uploader("Upload Trial Balance Excel File", type=["xlsx"])

if uploaded_rcm and uploaded_tb:
    xls_rcm = pd.ExcelFile(uploaded_rcm)
    xls_tb = pd.ExcelFile(uploaded_tb)

    rcm_sheet = st.selectbox("Select RCM Sheet", xls_rcm.sheet_names)
    tb_sheet = st.selectbox("Select Trial Balance Sheet", xls_tb.sheet_names)

    trial_df = xls_tb.parse(tb_sheet)
    account_types = sorted(trial_df['Account Type'].dropna().str.strip().unique())
    selected_account_types = st.multiselect("Select Account Types", options=account_types)

    if st.button("Run SOX Automation"):
        with st.spinner("Running analysis..."):
            rcm_df = xls_rcm.parse(rcm_sheet)

            output = io.BytesIO()
            chart_pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix="_Charts.pdf").name
            pdf_pages = PdfPages(chart_pdf_path)

            all_brand_summaries = []
            all_matched_controls = []

            temp_summaries = []  # hold temp for summary sheets
            temp_rcms = []  # hold temp for RCM sheets

            for account_type_input in selected_account_types:
                search_phrase = account_type_input.lower()
                matched_controls = rcm_df[rcm_df['Control Description'].astype(str).str.lower().str.contains(search_phrase, na=False)].copy()
                matched_controls['Mapped Process Group'] = matched_controls['Control ID'].apply(map_control_id_to_process)
                expected_group = account_type_to_process_group.get(search_phrase, None)
                if expected_group:
                    matched_controls = matched_controls[matched_controls['Mapped Process Group'].str.lower() == expected_group.lower()]

                if 'Key? (Y/N)' not in matched_controls.columns:
                    st.error("Missing 'Key? (Y/N)' column in the RCM file.")
                    st.stop()

                account_row = trial_df[trial_df['Account Type'].str.strip().str.lower() == search_phrase]
                if matched_controls.empty or account_row.empty:
                    continue

                values_row = account_row.iloc[0, 1:]
                brand_values = values_row.fillna(0).apply(clean_number).reset_index()
                brand_values.columns = ['Brand Name', 'Account Value']
                total_value = brand_values['Account Value'].sum()
                brand_values['% of Total'] = brand_values['Account Value'] / total_value
                brand_values = brand_values.sort_values(by='Account Value', ascending=False).reset_index(drop=True)
                brand_values['Cumulative %'] = brand_values['% of Total'].cumsum()

                scope_flags, threshold_reached = [], False
                for cum in brand_values['Cumulative %']:
                    if not threshold_reached:
                        scope_flags.append("In Scope")
                        if cum >= 0.8:
                            threshold_reached = True
                    else:
                        scope_flags.append("Out of Scope")
                brand_values['Scope'] = scope_flags

                matched_brands = matched_controls['Brand Name'].dropna().tolist()
                brand_values['Mapped in RCM'] = brand_values['Brand Name'].apply(lambda x: "Yes" if x in matched_brands else "No")

                key_status_map = matched_controls.set_index('Brand Name')['Key? (Y/N)'].to_dict()
                brand_values['Key Status'] = brand_values['Brand Name'].apply(lambda x: key_status_map.get(x) if x in matched_brands else "")

                def derive_key_flag(row):
                    if row['Brand Name'] not in matched_brands:
                        return ""
                    key_status = str(row['Key Status']).strip().lower()
                    if row['Scope'] == "In Scope" and key_status == "non-key":
                        return "In Scope & Non-Key"
                    elif row['Scope'] == "Out of Scope" and key_status == "key":
                        return "Out of Scope & Key"
                    return ""

                brand_values['Key Flag'] = brand_values.apply(derive_key_flag, axis=1)
                brand_values['Review Flag'] = brand_values.apply(
                    lambda row: "⚠️ Review" if row['Scope'] == "In Scope" and row['Mapped in RCM'] == "No" else "", axis=1)
                brand_values['Account Type'] = account_type_input
                brand_values = brand_values[['Account Type'] + [col for col in brand_values.columns if col not in ['Account Type', 'Key Status']]]

                matched_controls['Scope'] = matched_controls['Brand Name'].map(
                    brand_values.set_index('Brand Name')['Scope']).fillna("Out of Scope")
                matched_controls['Account Type'] = account_type_input
                matched_controls = matched_controls[['Account Type'] + [col for col in matched_controls.columns if col != 'Account Type']]

                # Drop empty rows again right before export
                brand_values = brand_values[brand_values.notna().any(axis=1)]
                matched_controls = matched_controls[~matched_controls.apply(lambda row: all(str(cell).strip() == '' or pd.isna(cell) for cell in row), axis=1)]


                all_brand_summaries.append(brand_values)
                all_matched_controls.append(matched_controls)

                temp_summaries.append((account_type_input, brand_values))
                temp_rcms.append((account_type_input, matched_controls))

            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                workbook = writer.book
                center_fmt = workbook.add_format({'align': 'center', 'valign': 'vcenter'})

                # Write consolidated first
                if all_brand_summaries:
                    df_summary = pd.concat(all_brand_summaries, ignore_index=True)
                    df_summary.to_excel(writer, sheet_name="ALL_AccountType_Summary", index=False)
                    sheet = writer.sheets["ALL_AccountType_Summary"]
                    for col_num, col in enumerate(df_summary.columns):
                        sheet.write(0, col_num, col, center_fmt)
                        sheet.set_column(col_num, col_num, 20, center_fmt)
                    for row_num, row in df_summary.iterrows():
                        key_flag = row.get('Key Flag', '')
                        highlight_color = color_rules.get(key_flag, color_rules.get((row['Scope'], row['Mapped in RCM']), None))
                        for col_num, value in enumerate(row):
                            value = "" if pd.isna(value) else value
                            col_name = df_summary.columns[col_num]
                            fmt = workbook.add_format({'bg_color': highlight_color, 'align': 'center', 'valign': 'vcenter'}) if highlight_color else center_fmt
                            if col_name == 'Account Value':
                                fmt.set_num_format('#,##0')
                            elif col_name in ['% of Total', 'Cumulative %']:
                                fmt.set_num_format('0.00%')
                            sheet.write(row_num+1, col_num, value, fmt)

                if all_matched_controls:
                    df_rcm = pd.concat(all_matched_controls, ignore_index=True)
                    df_rcm = df_rcm[df_rcm.notna().any(axis=1)]
                    df_rcm.to_excel(writer, sheet_name="ALL_RCM_Combined", index=False)

                # Now write individual summaries and RCM sheets
                for (acc_type, brand_values), (_, matched_controls) in zip(temp_summaries, temp_rcms):
                    sheet = writer.book.add_worksheet(f"{acc_type[:31]}_summary")
                    for col_num, col in enumerate(brand_values.columns):
                        sheet.write(0, col_num, col, center_fmt)
                        sheet.set_column(col_num, col_num, 20, center_fmt)
                    for row_num, row in brand_values.iterrows():
                        key_flag = row.get('Key Flag', '')
                        highlight_color = color_rules.get(key_flag, color_rules.get((row['Scope'], row['Mapped in RCM']), None))
                        for col_num, value in enumerate(row):
                            value = "" if pd.isna(value) else value
                            col_name = brand_values.columns[col_num]
                            fmt = workbook.add_format({'bg_color': highlight_color, 'align': 'center', 'valign': 'vcenter'}) if highlight_color else center_fmt
                            if col_name == 'Account Value':
                                fmt.set_num_format('#,##0')
                            elif col_name in ['% of Total', 'Cumulative %']:
                                fmt.set_num_format('0.00%')
                            sheet.write(row_num+1, col_num, value, fmt)

                    rcm_sheet = writer.book.add_worksheet(f"{acc_type[:31]}_RCM")
                    for col_num, col in enumerate(matched_controls.columns):
                        rcm_sheet.write(0, col_num, col, center_fmt)
                        rcm_sheet.set_column(col_num, col_num, 20, center_fmt)
                    for row_num, row in matched_controls.iterrows():
                        for col_num, value in enumerate(row):
                            value = "" if pd.isna(value) else value
                            rcm_sheet.write(row_num+1, col_num, value, center_fmt)

                    # Chart export
                    fig = plt.figure(figsize=(10, 4))
                    axs = fig.subplots(1, 2)
                    plot_data = brand_values[brand_values['Scope'].isin(['In Scope', 'Out of Scope'])].copy()
                    color_map = plot_data['Scope'].map({'In Scope': 'green', 'Out of Scope': 'red'})
                    axs[0].bar(plot_data['Brand Name'], plot_data['% of Total'] * 100, color=color_map)
                    axs[0].set_title(f"{acc_type.title()} - Contribution by Brand")
                    axs[0].set_ylabel("% of Total")
                    axs[0].tick_params(axis='x', rotation=45)
                    axs[0].grid(True)
                    plot_data.groupby("Scope")['Account Value'].sum().plot.pie(
                        autopct='%1.1f%%', colors=['green', 'red'], startangle=90, ax=axs[1])
                    axs[1].set_title(f"{acc_type.title()} - Scope Split")
                    axs[1].set_ylabel("")
                    fig.tight_layout()
                    pdf_pages.savefig(fig)
                    plt.close(fig)

            pdf_pages.close()
            st.success("Analysis complete. Download files below:")
            st.download_button("📊 Download Excel Report", data=output.getvalue(), file_name="SOX_Audit_Report.xlsx")
            with open(chart_pdf_path, "rb") as f:
                st.download_button("📄 Download PDF Charts", data=f.read(), file_name="SOX_Charts.pdf")
