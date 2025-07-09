# streamlit_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import io
import zipfile
import tempfile

# Reuse your account mapping and scope color logic
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

def run_sox_analysis(rcm_df, trial_df, account_types):
    output_excel = io.BytesIO()
    pdf_buffer = io.BytesIO()
    pdf_pages = PdfPages(pdf_buffer)

    with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
        workbook = writer.book
        center_fmt = workbook.add_format({'align': 'center', 'valign': 'vcenter'})

        all_brand_summaries = []
        all_matched_controls = []

        for account_type_input in account_types:
            search_phrase = account_type_input.lower()
            matched_controls = rcm_df[rcm_df['Control Description'].astype(str).str.lower().str.contains(search_phrase, na=False)].copy()
            matched_controls['Mapped Process Group'] = matched_controls['Control ID'].apply(map_control_id_to_process)

            expected_group = account_type_to_process_group.get(search_phrase, None)
            if expected_group:
                matched_controls = matched_controls[matched_controls['Mapped Process Group'].str.lower() == expected_group.lower()]

            if 'Key? (Y/N)' not in matched_controls.columns:
                continue

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
            brand_values['Account Type'] = account_type_input
            brand_values = brand_values[['Account Type'] + [col for col in brand_values.columns if col != 'Account Type' and col != 'Key Status']]
            all_brand_summaries.append(brand_values)

            matched_controls['Scope'] = matched_controls['Brand Name'].map(brand_values.set_index('Brand Name')['Scope']).fillna("Out of Scope")
            matched_controls['Account Type'] = account_type_input
            matched_controls = matched_controls[['Account Type'] + [col for col in matched_controls.columns if col != 'Account Type']]
            all_matched_controls.append(matched_controls)

            # Charts
            fig = plt.figure(figsize=(10, 4))
            axs = fig.subplots(1, 2)
            plot_data = brand_values[brand_values['Scope'].isin(['In Scope', 'Out of Scope'])].copy()
            color_map = plot_data['Scope'].map({'In Scope': 'green', 'Out of Scope': 'red'})
            axs[0].bar(plot_data['Brand Name'], plot_data['% of Total'] * 100, color=color_map)
            axs[0].set_title(f"{account_type_input.title()} - Contribution by Brand")
            axs[0].set_ylabel("% of Total")
            axs[0].tick_params(axis='x', rotation=45)
            axs[0].grid(True)

            plot_data.groupby("Scope")['Account Value'].sum().plot.pie(
                autopct='%1.1f%%', colors=['green', 'red'], startangle=90, ax=axs[1])
            axs[1].set_title(f"{account_type_input.title()} - Scope Split")
            axs[1].set_ylabel("")

            fig.tight_layout()
            pdf_pages.savefig(fig)
            plt.close(fig)

        if all_brand_summaries:
            df_summary = pd.concat(all_brand_summaries, ignore_index=True)
            df_summary.to_excel(writer, sheet_name="ALL_AccountType_Summary", index=False)

        if all_matched_controls:
            df_rcm = pd.concat(all_matched_controls, ignore_index=True)
            df_rcm.to_excel(writer, sheet_name="ALL_RCM_Combined", index=False)

        pdf_pages.close()

    return output_excel.getvalue(), pdf_buffer.getvalue()

# Streamlit Web UI
st.title("SOX Automation - Web App")
rcm_file = st.file_uploader("Upload RCM Excel File", type=["xlsx"])
trial_file = st.file_uploader("Upload Trial Balance Excel File", type=["xlsx"])

if rcm_file and trial_file:
    rcm_sheets = pd.ExcelFile(rcm_file).sheet_names
    trial_sheets = pd.ExcelFile(trial_file).sheet_names
    selected_rcm_sheet = st.selectbox("Select RCM Sheet", rcm_sheets)
    selected_trial_sheet = st.selectbox("Select Trial Sheet", trial_sheets)

    rcm_df = pd.read_excel(rcm_file, sheet_name=selected_rcm_sheet)
    trial_df = pd.read_excel(trial_file, sheet_name=selected_trial_sheet)
    account_types = trial_df['Account Type'].dropna().unique().tolist()
    selected_accounts = st.multiselect("Select Account Types", account_types)

    if st.button("Run Analysis") and selected_accounts:
        with st.spinner("Processing..."):
            excel_bytes, pdf_bytes = run_sox_analysis(rcm_df, trial_df, selected_accounts)
            st.success("Analysis complete!")

            st.download_button("Download Excel Output", data=excel_bytes, file_name="ScopedRCM_TB_Automation_Output.xlsx")
            st.download_button("Download PDF Charts", data=pdf_bytes, file_name="ScopedRCM_TB_Automation_Output_Charts.pdf")
