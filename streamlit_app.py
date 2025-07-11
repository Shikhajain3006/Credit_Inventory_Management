# 📊 SOX Audit Automation Web App
# Updated: July 2025 – Optimized for memory, formatting, dynamic threshold, and logging

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.backends.backend_pdf import PdfPages
import io
import tempfile
import xlsxwriter
import os # Import os for file operations
from datetime import datetime # Import datetime for timestamps

st.set_page_config(layout="wide")
st.title("📊 SOX Audit Automation Web App")

# Mappings for process groups based on account types
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

# Color rules for Excel output based on analysis flags
color_rules = {
    ("In Scope", "Yes"): '#C6EFCE', # Light Green - In Scope & Mapped (Good)
    ("In Scope", "No"): '#FF9999', # Red - In Scope & Not Mapped (⚠️ Review)
    ("Out of Scope", "Yes"): '#FFEB9C', # Light Yellow - Out of Scope & Mapped (💡 Info: Check if it should be In Scope)
    ("Out of Scope", "No"): '#D9D9D9', # Light Grey - Out of Scope & Not Mapped (Expected)
    "⚠️ Review: In Scope & Non-Key": '#F4B084', # Orange - In Scope but Non-Key (⚠️ Review)
    "⚠️ Review: Out of Scope & Key": '#D9D2E9', # Purple - Out of Scope but Key (⚠️ Review)
    "⚠️ Review: In Scope & not Mapped in RCM": '#FF6347' # Tomato Red for unmapped In-Scope
}

def clean_number(value):
    """Cleans and converts a string value to a float, handling commas and percentage signs."""
    if isinstance(value, str):
        value = value.replace(',', '').replace('%', '').strip()
    try:
        return float(value)
    except (ValueError, TypeError): # Catch specific errors for robustness
        return 0.0

def map_control_id_to_process(control_id):
    """Maps a Control ID to a specific process group based on its numeric prefix."""
    try:
        # Handle cases where control_id might be NaN or not a string
        id_str = str(control_id)
        if not id_str or id_str.lower() == 'nan':
            return "Unknown"

        # Split by '-' and take the last part to handle multiple hyphens
        id_fragment = id_str.split("-")[-1].strip()
        
        # Extract only digits and period, ensuring no empty string if non-numeric
        numeric_str = ''.join([ch for ch in id_fragment if ch.isdigit() or ch == '.'])
        
        if not numeric_str: # If no numeric part found after cleaning
            return "Unknown"

        # Convert to float, taking first few digits for robust mapping if ID is long
        numeric_part = float(numeric_str[:6]) # Increased to 6 for more flexibility

        # Mapping logic based on numeric ranges
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
    except (IndexError, ValueError, TypeError):
        return "Unknown" # Catch any parsing errors

def drop_blank_rows(df):
    """Removes rows that are entirely empty (all NaN) or contain only whitespace strings."""
    if df.empty:
        return df
    # Drop rows where all elements are NaN
    df_cleaned = df.dropna(how='all')
    # Drop rows where all elements are empty strings or contain only whitespace
    # Use .apply(str) to ensure all elements are strings before stripping
    if not df_cleaned.empty:
        df_cleaned = df_cleaned.loc[~(df_cleaned.apply(lambda x: x.astype(str).str.strip() == "").all(axis=1))]
    return df_cleaned

@st.cache_data
def load_sheet_names(file_buffer, file_type):
    """Loads sheet names from an Excel or CSV file."""
    if file_type == 'xlsx':
        return pd.ExcelFile(file_buffer).sheet_names
    elif file_type == 'csv':
        return ['Sheet1'] # CSVs inherently have one "sheet"
    return []

@st.cache_data
def parse_sheet(file_buffer, sheet_name, file_type):
    """Parses a specific sheet from an Excel or CSV file."""
    if file_type == 'xlsx':
        return pd.read_excel(file_buffer, sheet_name=sheet_name)
    elif file_type == 'csv':
        # Reset buffer to start for reading CSV
        file_buffer.seek(0) 
        return pd.read_csv(file_buffer)
    return pd.DataFrame()

st.markdown("---")

st.info("""
    **How to Use:**
    1.  **Upload RCM File:** This file should contain your Risk & Control Matrix with columns like 'Control Description', 'Control ID', 'Brand Name', and 'Key? (Y/N)'.
    2.  **Upload Trial Balance File:** This file should have 'Account Type' as its first column, and subsequent columns representing Brand Names with their respective financial values.
    3.  **Select Sheets:** Choose the correct sheets from your uploaded Excel files.
    4.  **Set Threshold:** Adjust the slider to define what percentage of cumulative account value should be considered 'In Scope'.
    5.  **Select Account Types:** Choose the specific account types you wish to analyze.
    6.  **Run Automation:** Click the button to generate the report and charts.
    7.  **Download Reports:** Download your Excel report and PDF charts.
""")

# File uploaders - supporting xlsx and csv
uploaded_rcm = st.file_uploader("Upload RCM File (.xlsx or .csv)", type=["xlsx", "csv"], key="rcm_uploader")
uploaded_tb = st.file_uploader("Upload Trial Balance File (.xlsx or .csv)", type=["xlsx", "csv"], key="tb_uploader")

# State to store download data and filenames
if 'excel_data' not in st.session_state:
    st.session_state.excel_data = None
    st.session_state.excel_filename = None
    st.session_state.pdf_data = None
    st.session_state.pdf_filename = None
    st.session_state.log_msgs = [] # For storing logs across runs if needed

if uploaded_rcm and uploaded_tb:
    # Determine file types
    rcm_file_type = 'csv' if uploaded_rcm.name.endswith('.csv') else 'xlsx'
    tb_file_type = 'csv' if uploaded_tb.name.endswith('.csv') else 'xlsx'

    rcm_sheets = load_sheet_names(uploaded_rcm, rcm_file_type)
    tb_sheets = load_sheet_names(uploaded_tb, tb_file_type)

    selected_rcm_sheet = st.selectbox("Select RCM Sheet", rcm_sheets, key="rcm_sheet_select")
    selected_tb_sheet = st.selectbox("Select Trial Balance Sheet", tb_sheets, key="tb_sheet_select")

    threshold = st.slider("Set Threshold for In Scope (%)", min_value=50, max_value=100, value=80, step=5,
                          help="Brands are marked 'In Scope' until their cumulative account value reaches this percentage of the total for their Account Type.") / 100.0

    try:
        rcm_df = parse_sheet(uploaded_rcm, selected_rcm_sheet, rcm_file_type)
        trial_df = parse_sheet(uploaded_tb, selected_tb_sheet, tb_file_type)
    except Exception as e:
        st.error(f"Error reading selected sheet(s): {e}. Please ensure the correct sheet is selected and the file is not corrupted.")
        st.stop()

    # --- Initial Column Validations ---
    # Validate required columns in Trial Balance
    required_tb_columns = ['Account Type']
    if not all(col in trial_df.columns for col in required_tb_columns):
        st.error(f"Trial Balance file is missing the required column: **'Account Type'**. Please ensure this column exists.")
        st.stop()
    
    # Check if there are columns beyond 'Account Type' in Trial Balance to represent brands
    if len(trial_df.columns) <= 1:
        st.error(f"Trial Balance file must contain columns for brand values (e.g., 'Brand A', 'Brand B') in addition to the 'Account Type' column. These brand columns will be used to calculate financial values.")
        st.stop()


    # Validate required columns in RCM
    required_rcm_columns = ['Control Description', 'Control ID', 'Brand Name', 'Key? (Y/N)']
    missing_rcm_cols = [col for col in rcm_df.columns if col not in rcm_df.columns] # This line was a typo, fixed below
    missing_rcm_cols = [col for col in required_rcm_columns if col not in rcm_df.columns] # Corrected line
    if missing_rcm_cols:
        st.error(f"RCM file is missing one or more required columns: **{', '.join(missing_rcm_cols)}**. Please check your RCM file.")
        st.stop()
    
    # Drop rows with all NaNs or empty strings from RCM and Trial Balance upfront
    rcm_df = drop_blank_rows(rcm_df)
    trial_df = drop_blank_rows(trial_df)

    # --- Data Previews ---
    st.subheader("Data Previews")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**RCM Data Preview (Sheet: '{selected_rcm_sheet}')**")
        st.dataframe(rcm_df.head(), use_container_width=True)
    with col2:
        st.write(f"**Trial Balance Data Preview (Sheet: '{selected_tb_sheet}')**")
        st.dataframe(trial_df.head(), use_container_width=True)


    # Get unique account types after initial cleanup
    account_types = sorted(trial_df['Account Type'].dropna().astype(str).str.strip().unique())
    
    # "Select All" checkbox
    select_all_account_types = st.checkbox("Select All Account Types", key="select_all_checkbox")
    
    if select_all_account_types:
        selected_account_types = account_types
    else:
        selected_account_types = st.multiselect("Select Account Types for Analysis", options=account_types, key="account_types_select")

    log_msgs = []

    if st.button("Run SOX Automation", key="run_button"):
        if not selected_account_types:
            st.warning("Please select at least one Account Type to run the analysis.")
            st.stop()

        # Clear previous run's stored data
        st.session_state.excel_data = None
        st.session_state.excel_filename = None
        st.session_state.pdf_data = None
        st.session_state.pdf_filename = None
        st.session_state.log_msgs = [] # Clear logs for new run

        with st.spinner("Running analysis... This may take a few moments..."):
            excel_output = io.BytesIO()
            pdf_output = io.BytesIO() # Use BytesIO for PDF as well

            # Final export name
            excel_filename = "Final Automation Report.xlsx"
            pdf_filename = "SOX_Charts.pdf" # Static name as requested implicitly by changing Excel name

            pdf_pages = PdfPages(pdf_output) # Write directly to BytesIO

            all_brand_summaries = [] # For consolidated summary sheet
            all_matched_controls = [] # For consolidated RCM sheet
            
            # To hold (acc_type, summary_df, rcm_df) for individual sheets to ensure order
            individual_sheets_to_export_ordered = [] 

            processed_account_types_count = 0

            for account_type_input in selected_account_types:
                try:
                    search_phrase = account_type_input.lower()
                    
                    # Filter RCM: Control Description contains search phrase & Mapped Process Group matches
                    current_matched_controls = rcm_df[
                        rcm_df['Control Description'].astype(str).str.lower().str.contains(search_phrase, na=False)
                    ].copy()
                    
                    # Apply process mapping
                    current_matched_controls['Mapped Process Group'] = current_matched_controls['Control ID'].apply(map_control_id_to_process)
                    
                    expected_group = account_type_to_process_group.get(search_phrase, None)
                    if expected_group:
                        current_matched_controls = current_matched_controls[
                            current_matched_controls['Mapped Process Group'].str.lower() == expected_group.lower()
                        ]

                    # Filter Trial Balance for the current account type
                    current_account_row = trial_df[trial_df['Account Type'].astype(str).str.strip().str.lower() == search_phrase]
                    
                    if current_matched_controls.empty or current_account_row.empty:
                        log_msgs.append(f"⚠️ Skipping '{account_type_input}': No matching controls in RCM or no account data in Trial Balance for this type.")
                        continue
                    
                    processed_account_types_count += 1

                    # Extract brand values (all columns after 'Account Type' assumed to be brands)
                    # Use .iloc[0] to get the first row if multiple match, and .drop to remove 'Account Type' column
                    values_row = current_account_row.iloc[0].drop('Account Type', errors='ignore').fillna(0) 
                    current_brand_values = values_row.apply(clean_number).reset_index()
                    current_brand_values.columns = ['Brand Name', 'Account Value']
                    
                    # Filter out brands with zero account value after cleaning
                    current_brand_values = current_brand_values[current_brand_values['Account Value'] != 0].copy()

                    if current_brand_values.empty:
                        log_msgs.append(f"⚠️ Skipping '{account_type_input}': No non-zero brand values found in Trial Balance after cleaning.")
                        continue

                    total_value = current_brand_values['Account Value'].sum()
                    current_brand_values['% of Total'] = current_brand_values['Account Value'] / total_value if total_value != 0 else 0.0
                    
                    current_brand_values = current_brand_values.sort_values(by='Account Value', ascending=False).reset_index(drop=True)
                    current_brand_values['Cumulative %'] = current_brand_values['% of Total'].cumsum()

                    # Determine 'In Scope'/'Out of Scope' based on cumulative percentage
                    scope_flags, threshold_reached = [], False
                    for cum in current_brand_values['Cumulative %']:
                        if not threshold_reached:
                            scope_flags.append("In Scope")
                            if cum >= threshold:
                                threshold_reached = True
                        else:
                            scope_flags.append("Out of Scope")
                    current_brand_values['Scope'] = scope_flags

                    # Map 'Mapped in RCM' status
                    matched_rcm_brands = current_matched_controls['Brand Name'].dropna().unique().tolist()
                    current_brand_values['Mapped in RCM'] = current_brand_values['Brand Name'].apply(lambda x: "Yes" if x in matched_rcm_brands else "No")

                    # Map 'Key Status'
                    key_status_map = current_matched_controls.set_index('Brand Name')['Key? (Y/N)'].fillna('').astype(str).to_dict()
                    current_brand_values['Key Status'] = current_brand_values['Brand Name'].apply(lambda x: key_status_map.get(x, "") if x in matched_rcm_brands else "")

                    # --- Combine Key Flag and Review Flag into one column: "Flag - Manual Auditor Check" ---
                    def derive_auditor_check_flag(row):
                        flag_messages = []

                        # Logic for Review: In Scope & not Mapped in RCM (Highest priority for unmapped in-scope)
                        if row['Scope'] == "In Scope" and row['Mapped in RCM'] == "No":
                            flag_messages.append("⚠️ Review: In Scope & not Mapped in RCM")
                        else:
                            # Only apply Key/Non-Key checks if it IS mapped in RCM
                            key_status = str(row['Key Status']).strip().lower()
                            if row['Mapped in RCM'] == "Yes":
                                if row['Scope'] == "In Scope" and key_status in ["no", "non-key"]:
                                    flag_messages.append("⚠️ Review: In Scope & Non-Key")
                                elif row['Scope'] == "Out of Scope" and key_status in ["yes", "key"]:
                                    flag_messages.append("⚠️ Review: Out of Scope & Key")
                        
                        return ", ".join(flag_messages) if flag_messages else ""

                    current_brand_values['Flag - Manual Auditor Check'] = current_brand_values.apply(derive_auditor_check_flag, axis=1)
                    
                    current_brand_values['Account Type'] = account_type_input
                    
                    # Reorder and clean columns for summary
                    summary_cols_order = ['Account Type', 'Brand Name', 'Account Value', '% of Total', 'Cumulative %', 
                                          'Scope', 'Mapped in RCM', 'Key Status', 'Flag - Manual Auditor Check']
                    # Ensure all required columns exist before reordering
                    current_brand_values = current_brand_values[[col for col in summary_cols_order if col in current_brand_values.columns]]
                    current_brand_values = drop_blank_rows(current_brand_values).reset_index(drop=True)

                    # Add 'Scope' to RCM dataframe for context
                    if 'Brand Name' in current_matched_controls.columns:
                        temp_scope_map = current_brand_values.set_index('Brand Name')['Scope'].to_dict()
                        current_matched_controls['Scope'] = current_matched_controls['Brand Name'].map(temp_scope_map).fillna("Not Analyzed in TB Scope")
                    else:
                        current_matched_controls['Scope'] = "N/A - Brand Name column missing in RCM for scope mapping" 
                    
                    current_matched_controls['Account Type'] = account_type_input
                    # Reorder and clean columns for RCM
                    rcm_cols_order = ['Account Type'] + [col for col in current_matched_controls.columns if col != 'Account Type']
                    current_matched_controls = current_matched_controls[rcm_cols_order]
                    current_matched_controls = drop_blank_rows(current_matched_controls).reset_index(drop=True)

                    # Append to lists for consolidated sheets
                    all_brand_summaries.append(current_brand_values)
                    all_matched_controls.append(current_matched_controls)

                    # Append to list for ordered individual sheets
                    individual_sheets_to_export_ordered.append((account_type_input, current_brand_values, current_matched_controls))

                    log_msgs.append(f"✅ Processed: {account_type_input} → {len(current_brand_values)} brands, {len(current_matched_controls)} controls")

                except Exception as e:
                    log_msgs.append(f"❌ Error processing '{account_type_input}': {str(e)}")
            
            st.session_state.log_msgs = log_msgs # Store logs in session state

            # --- Write to Excel ---
            with pd.ExcelWriter(excel_output, engine="xlsxwriter") as writer:
                workbook = writer.book
                
                # Define common formats (with border)
                # Removed 'center_fmt' as it will be applied to all cells
                data_base_fmt = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
                header_fmt = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1, 'bold': True}) # Added bold for headers
                
                # Pre-create all color formats for efficiency, now based on data_base_fmt
                color_excel_formats = {}
                for key, color_code in color_rules.items():
                    # Create a new format for each color, inheriting from data_base_fmt
                    color_excel_formats[key] = workbook.add_format({'bg_color': color_code, 'align': 'center', 'valign': 'vcenter', 'border': 1})

                # --- Consolidated Summary Sheet (ALL_AccountType_Summary) ---
                if all_brand_summaries:
                    df_summary_consolidated = pd.concat(all_brand_summaries, ignore_index=True)

                    sheet_name = "ALL_AccountType_Summary"
                    df_summary_consolidated.to_excel(writer, sheet_name=sheet_name, index=False, header=False) 
                    sheet = writer.sheets[sheet_name]
                    
                    # Write headers with header format and set column width
                    for col_num, col_name in enumerate(df_summary_consolidated.columns):
                        sheet.write(0, col_num, col_name, header_fmt) # Use header_fmt
                        # Set column widths based on content or a sensible default
                        if col_name == 'Control Description':
                            sheet.set_column(col_num, col_num, 40)
                        elif col_name in ['Account Type', 'Brand Name', 'Scope', 'Mapped in RCM', 'Key Status']:
                            sheet.set_column(col_num, col_num, 20)
                        elif col_name in ['Account Value', '% of Total', 'Cumulative %']:
                            sheet.set_column(col_num, col_num, 15)
                        elif col_name == 'Flag - Manual Auditor Check':
                            sheet.set_column(col_num, col_num, 35) # Wider for the combined flag
                        else:
                            sheet.set_column(col_num, col_num, 15) 

                    # Write data with conditional formatting and specific number formats
                    for row_num, row in df_summary_consolidated.iterrows():
                        flag_value = row.get('Flag - Manual Auditor Check', '')
                        scope_mapped_tuple = (row.get('Scope'), row.get('Mapped in RCM'))
                        
                        # Determine highlight color key based on precedence
                        highlight_color_key = None
                        if flag_value and flag_value in color_rules: # Prioritize combined flag if it exists and has a rule
                            highlight_color_key = flag_value
                        elif scope_mapped_tuple in color_rules: # Then check Scope and Mapped in RCM
                            highlight_color_key = scope_mapped_tuple

                        # Get the base format (with color if applicable)
                        current_cell_fmt = color_excel_formats.get(highlight_color_key, data_base_fmt) 

                        for col_num, value in enumerate(row):
                            display_value = "" if pd.isna(value) else value
                            col_name = df_summary_consolidated.columns[col_num]
                            
                            # Create a new format for each cell to combine background color with number format
                            # This ensures number formats are applied correctly with the background color
                            final_cell_format = workbook.add_format({
                                'bg_color': current_cell_fmt.bg_color,
                                'align': 'center',
                                'valign': 'vcenter',
                                'border': 1
                            })

                            if col_name == 'Account Value':
                                final_cell_format.set_num_format('#,##0')
                            elif col_name in ['% of Total', 'Cumulative %']:
                                final_cell_format.set_num_format('0.00%')
                            
                            sheet.write(row_num + 1, col_num, display_value, final_cell_format)


                # --- Consolidated RCM Sheet (ALL_RCM_Combined) ---
                if all_matched_controls:
                    df_rcm_consolidated = pd.concat(all_matched_controls, ignore_index=True)

                    sheet_name = "ALL_RCM_Combined"
                    df_rcm_consolidated.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
                    sheet = writer.sheets[sheet_name]

                    # Write headers and set column width
                    for col_num, col_name in enumerate(df_rcm_consolidated.columns):
                        sheet.write(0, col_num, col_name, header_fmt) # Use header_fmt
                        if col_name in ['Control Description', 'Risk Description']:
                            sheet.set_column(col_num, col_num, 40)
                        elif col_name in ['Account Type', 'Control ID', 'Brand Name', 'Mapped Process Group', 'Scope']:
                            sheet.set_column(col_num, col_num, 25)
                        else:
                            sheet.set_column(col_num, col_num, 15) 

                    # Write data, applying data_base_fmt to all cells for centering and border
                    for row_num, row in df_rcm_consolidated.iterrows():
                        for col_num, value in enumerate(row):
                            sheet.write(row_num + 1, col_num, "" if pd.isna(value) else value, data_base_fmt)


                # --- Individual Sheets (Summary & RCM) for each processed account type ---
                for (acc_type, brand_values_df, matched_controls_df) in individual_sheets_to_export_ordered:
                    # Summary Sheet
                    sheet_name_summary = f"{acc_type[:25]}_summary" 
                    # Ensure sheet name is unique if truncated names clash
                    while sheet_name_summary in writer.book.sheetnames:
                        sheet_name_summary += "_" # Add suffix if name exists
                    sheet_summary = writer.book.add_worksheet(sheet_name_summary)
                    
                    # Write headers for individual summary
                    for col_num, col_name in enumerate(brand_values_df.columns):
                        sheet_summary.write(0, col_num, col_name, header_fmt) # Use header_fmt
                        if col_name == 'Control Description':
                            sheet_summary.set_column(col_num, col_num, 40)
                        elif col_name in ['Account Type', 'Brand Name', 'Scope', 'Mapped in RCM', 'Key Status']:
                            sheet_summary.set_column(col_num, col_num, 20)
                        elif col_name in ['Account Value', '% of Total', 'Cumulative %']:
                            sheet_summary.set_column(col_num, col_num, 15)
                        elif col_name == 'Flag - Manual Auditor Check':
                            sheet_summary.set_column(col_num, col_num, 35) # Wider for the combined flag
                        else:
                            sheet_summary.set_column(col_num, col_num, 15)

                    # Write data for individual summary with conditional formatting
                    for row_num, row in brand_values_df.iterrows():
                        flag_value = row.get('Flag - Manual Auditor Check', '')
                        scope_mapped_tuple = (row.get('Scope'), row.get('Mapped in RCM'))
                        
                        highlight_color_key = None
                        if flag_value and flag_value in color_rules:
                            highlight_color_key = flag_value
                        elif scope_mapped_tuple in color_rules:
                            highlight_color_key = scope_mapped_tuple

                        current_cell_fmt = color_excel_formats.get(highlight_color_key, data_base_fmt)

                        for col_num, value in enumerate(row):
                            display_value = "" if pd.isna(value) else value
                            col_name = brand_values_df.columns[col_num]
                            
                            final_cell_format = workbook.add_format({
                                'bg_color': current_cell_fmt.bg_color, 
                                'align': 'center', 
                                'valign': 'vcenter', 
                                'border': 1
                            })

                            if col_name == 'Account Value':
                                final_cell_format.set_num_format('#,##0')
                            elif col_name in ['% of Total', 'Cumulative %']:
                                final_cell_format.set_num_format('0.00%')
                            
                            sheet_summary.write(row_num + 1, col_num, display_value, final_cell_format)

                    # RCM Sheet
                    sheet_name_rcm = f"{acc_type[:25]}_RCM" 
                    # Ensure sheet name is unique if truncated names clash
                    while sheet_name_rcm in writer.book.sheetnames:
                        sheet_name_rcm += "_" # Add suffix if name exists
                    rcm_sheet = writer.book.add_worksheet(sheet_name_rcm)
                    
                    # Write headers for individual RCM
                    for col_num, col_name in enumerate(matched_controls_df.columns):
                        rcm_sheet.write(0, col_num, col_name, header_fmt) # Use header_fmt
                        if col_name in ['Control Description', 'Risk Description']:
                            rcm_sheet.set_column(col_num, col_num, 40)
                        elif col_name in ['Account Type', 'Control ID', 'Brand Name', 'Mapped Process Group', 'Scope']:
                            rcm_sheet.set_column(col_num, col_num, 25)
                        else:
                            rcm_sheet.set_column(col_num, col_num, 15)
                    
                    # Write data, applying data_base_fmt to all cells
                    for row_num, row in matched_controls_df.iterrows():
                        for col_num, value in enumerate(row):
                            rcm_sheet.write(row_num + 1, col_num, "" if pd.isna(value) else value, data_base_fmt)


                # --- Charts for each Account Type (PDF) ---
                # Use a consistent color map for charts. viridis is a good perceptually uniform option.
                in_scope_color = cm.viridis(0.2) # Example color from viridis colormap
                out_of_scope_color = cm.viridis(0.8) # Another example color from viridis colormap

                for (acc_type, brand_values_df, _) in individual_sheets_to_export_ordered: # Only need summary df for charts
                    fig = plt.figure(figsize=(12, 5)) 
                    axs = fig.subplots(1, 2)
                    
                    # Filter out brands with 0% contribution for plotting clarity
                    plot_data = brand_values_df[brand_values_df['% of Total'] > 0].copy()

                    if not plot_data.empty:
                        # Bar Chart: Contribution by Brand (only for in-scope/out-of-scope)
                        if 'Scope' in plot_data.columns:
                            # Map 'In Scope' to first color, 'Out of Scope' to second color
                            color_map_bar = plot_data['Scope'].map({'In Scope': in_scope_color, 'Out of Scope': out_of_scope_color}).fillna('gray') 
                            axs[0].bar(plot_data['Brand Name'], plot_data['% of Total'] * 100, color=color_map_bar)
                        else:
                            axs[0].bar(plot_data['Brand Name'], plot_data['% of Total'] * 100, color='skyblue') 
                            
                        axs[0].set_title(f"{acc_type.title()} - Contribution by Brand", fontsize=14)
                        axs[0].set_ylabel("% of Total", fontsize=10)
                        axs[0].tick_params(axis='x', rotation=60, labelsize=9) # Removed 'ha' argument
                        axs[0].grid(axis='y', linestyle='--', alpha=0.7) 
                        axs[0].set_facecolor('#f7f7f7') 

                        # Pie Chart: Scope Split
                        scope_counts = plot_data.groupby("Scope")['Account Value'].sum()
                        if not scope_counts.empty and scope_counts.sum() > 0: 
                            pie_colors_mapping = {'In Scope': in_scope_color, 'Out of Scope': out_of_scope_color}
                            # Ensure colors align with the actual scope categories present
                            actual_pie_colors = [pie_colors_mapping.get(s, 'gray') for s in scope_counts.index]

                            scope_counts.plot.pie(
                                autopct='%1.1f%%', 
                                colors=actual_pie_colors, 
                                startangle=90, 
                                ax=axs[1], 
                                textprops={'fontsize': 10}, 
                                pctdistance=0.85, 
                                labeldistance=1.1 
                            )
                            axs[1].set_title(f"{acc_type.title()} - Scope Split", fontsize=14)
                            axs[1].set_ylabel("") 
                        else:
                            axs[1].text(0.5, 0.5, "No data for Scope Split", horizontalalignment='center', verticalalignment='center', transform=axs[1].transAxes, fontsize=12)
                            axs[1].set_axis_off() 

                    else: # Handle cases where plot_data is empty
                        axs[0].text(0.5, 0.5, "No brand data to plot", horizontalalignment='center', verticalalignment='center', transform=axs[0].transAxes, fontsize=12)
                        axs[0].set_axis_off()
                        axs[1].text(0.5, 0.5, "No brand data to plot", horizontalalignment='center', verticalalignment='center', transform=axs[1].transAxes, fontsize=12)
                        axs[1].set_axis_off()
                        
                    fig.suptitle(f"SOX Audit Analysis for {acc_type.title()}", fontsize=16, y=1.02) 
                    fig.tight_layout(rect=[0, 0.03, 1, 0.98]) 
                    pdf_pages.savefig(fig)
                    plt.close(fig)

            pdf_pages.close()
            
            # Store generated files in session state for downloading
            st.session_state.excel_data = excel_output.getvalue()
            st.session_state.excel_filename = excel_filename
            st.session_state.pdf_data = pdf_output.getvalue()
            st.session_state.pdf_filename = pdf_filename

            st.success(f"Analysis complete for {processed_account_types_count} account types. Download files below:")
            
    # --- Download Buttons (always visible if data is available in session state) ---
    if st.session_state.excel_data:
        st.download_button(
            "📊 Download Excel Report", 
            data=st.session_state.excel_data, 
            file_name=st.session_state.excel_filename, 
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_excel_button"
        )
    
    if st.session_state.pdf_data:
        st.download_button(
            "📄 Download PDF Charts", 
            data=st.session_state.pdf_data, 
            file_name=st.session_state.pdf_filename, 
            mime="application/pdf",
            key="download_pdf_button"
        )
    
    # Optional: A button to clear generated files from session state
    if st.session_state.excel_data or st.session_state.pdf_data or st.session_state.log_msgs:
        if st.button("🔄 Reset Application", help="Clears all uploaded files, selections, generated data, and logs."):
            st.session_state.excel_data = None
            st.session_state.excel_filename = None
            st.session_state.pdf_data = None
            st.session_state.pdf_filename = None
            st.session_state.log_msgs = [] # Also clear logs
            st.cache_data.clear() # Clear all Streamlit data caches
            st.rerun() # Rerun to update the UI and hide download buttons

    with st.expander("🪵 Analysis Logs"):
        if st.session_state.log_msgs:
            for msg in st.session_state.log_msgs:
                st.markdown(msg)
        else:
            st.info("No logs yet. Run the analysis to see logs.")