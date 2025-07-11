Got it\! My apologies for the confusion. You need a `README.md` specifically tailored for a **Streamlit application** that will be hosted on GitHub and deployed to a cloud platform. This means emphasizing deployment, environment setup, and Streamlit-specific details.

Here's a `README.md` for your **Streamlit SOX Audit Automation App**:

-----

# SOX Audit Automation App (Streamlit)

This repository hosts a web-based application built with Streamlit, designed to assist with SOX (Sarbanes-Oxley) audit procedures. It automates the analysis of RCM (Risk and Control Matrix) and Trial Balance data, helping auditors efficiently identify "in-scope" areas, map controls, and flag items for manual review based on user-defined criteria.

This application is ideal for teams who need to collaborate on SOX audit data analysis in a user-friendly, browser-accessible environment without local software installations.

## Features

  * **User-Friendly Interface**: An intuitive web interface built with Streamlit, accessible via any web browser.
  * **File Upload (Excel)**: Securely upload your RCM and Trial Balance data directly from Excel files (`.xlsx`).
  * **Sheet Selection**: Dynamically select the correct sheet within your uploaded Excel files.
  * **Data Preview**: View the first few rows of your uploaded data to ensure correct parsing and file integrity.
  * **Dynamic Account Type Selection**: The application automatically extracts unique "Account Types" from your Trial Balance, allowing you to select specific types for focused analysis.
  * **Configurable In-Scope Threshold**: Adjust a percentage threshold to define "in-scope" brands based on their cumulative contribution to total account value.
  * **Automated Analysis & Flagging**:
      * Identifies "In Scope" and "Out of Scope" brands based on financial values and the set threshold.
      * Maps brands from the Trial Balance to controls in the RCM based on "Brand Name".
      * Automatically flags items requiring manual auditor review, including:
          * "In Scope" brands that are not mapped in the RCM.
          * "In Scope" brands marked as "Non-Key" in the RCM.
          * "Out of Scope" brands surprisingly marked as "Key" in the RCM.
  * **Comprehensive Reporting (Downloadable)**:
      * Generates a detailed Excel report (`.xlsx`) available for download, featuring:
          * A consolidated summary of all analyzed "Account Types", including scope, RCM mapping status, key status, and auditor flags (with clear color-coding).
          * A consolidated list of all RCM controls that matched any analyzed "Account Type".
          * Individual sheets for each analyzed "Account Type", presenting both brand-level summaries and matched RCM controls.
  * **Visual Charts (Downloadable PDF)**: Creates a downloadable PDF document with insightful charts for each analyzed "Account Type", including:
      * Pie Chart: Distribution of "In Scope" vs. "Out of Scope" brands.
      * Bar Chart: Account Value by Brand.
      * Line Chart: Cumulative Percentage of Account Value by Brand, clearly showing the "in-scope" threshold.


## Getting Started

### Prerequisites

To run this application locally or deploy it, you'll need:

  * **Python 3.8+**
  * **`pip`** (Python package installer)
  * **Git** (for cloning the repository)

### Installation (Local Development)

1.  **Clone the repository**:

    ```bash
    git clone https://github.com/YourUsername/your-sox-app-repo.git
    cd your-sox-app-repo
    ```

2.  **Create a virtual environment** (recommended):

    ```bash
    python -m venv venv
    ```

      * **On Windows**:
        ```bash
        .\venv\Scripts\activate
        ```
      * **On macOS/Linux**:
        ```bash
        source venv/bin/activate
        ```

3.  **Install dependencies**:
    Create a `requirements.txt` file in the root of your repository with the following content:

    ```
    streamlit
    pandas
    matplotlib
    openpyxl
    xlsxwriter
    ```

    Then install them:

    ```bash
    pip install -r requirements.txt
    ```

### How to Run Locally

1.  **Ensure prerequisites are met** and dependencies are installed (steps above).
2.  **Run the Streamlit app**:
    ```bash
    streamlit run app.py  # Assuming your main Streamlit script is named app.py
    ```
    This command will open the application in your default web browser (usually at `http://localhost:8501`).

## File Structure Expectations for Input Data

For the analysis to be accurate, your input Excel files must adhere to specific column requirements:

### RCM Excel File (`.xlsx`)

  * **Required Columns**:
      * `Control Description`
      * `Control ID`
      * `Brand Name`
      * `Key? (Y/N)` (This column is critical for determining 'Key Status'. Expected values are case-insensitive and can include 'Y', 'N', 'Yes', 'No', 'Key', 'Non-Key'.)

### Trial Balance Excel File (`.xlsx`)

  * **Required Columns**:
      * `Account Type` (This *must* be the **first** column in the sheet.)
      * Followed by one or more columns representing **brand names with corresponding financial values**. These columns are dynamically identified as the data points for brand-specific analysis.

## Usage Guide (Step-by-Step)

1.  **Launch the App**: If running locally, execute `streamlit run app.py`. If deployed, open the application URL in your web browser.
2.  **Upload RCM File**:
      * In the sidebar (or main area), locate the "Upload RCM Excel File" section.
      * Click the "Browse files" button and select your RCM Excel spreadsheet (`.xlsx`).
3.  **Select RCM Sheet**:
      * Once the RCM file is uploaded, a dropdown will appear. Select the correct sheet containing your RCM data.
      * A preview of the first few rows of your RCM data will be displayed.
4.  **Upload Trial Balance File**:
      * Locate the "Upload Trial Balance Excel File" section.
      * Click "Browse files" and select your Trial Balance Excel spreadsheet (`.xlsx`).
5.  **Select Trial Balance Sheet**:
      * After uploading the Trial Balance file, select the appropriate sheet from the dropdown.
      * A preview of the first few rows of your Trial Balance data will be shown.
      * **Important**: The application will validate column presence. If `Account Type` is missing or no brand value columns are detected, an error message will guide you.
6.  **Adjust In-Scope Threshold**:
      * Use the slider labeled "Threshold for In Scope (%)" to set your desired materiality percentage. This determines which brands are classified as "In Scope" based on their cumulative value.
7.  **Select Account Types for Analysis**:
      * A multiselect box populated with unique 'Account Type' values from your Trial Balance will appear.
      * Select one or more account types you wish to analyze.
8.  **Run Analysis**:
      * Click the "Run Analysis" button.
      * A progress indicator will appear. Processing time may vary depending on file size.
9.  **Download Results**:
      * Upon completion, "Download Excel Report" and "Download PDF Charts" buttons will appear.
      * Click these buttons to save the generated analysis reports and charts to your local machine.

## Output Files

The application generates two main downloadable files:

  * **Excel Report (`.xlsx`)**: This comprehensive report includes:
      * `ALL_AccountType_Summary`: A sheet with conditional formatting highlighting all analyzed brands, their scope, RCM mapping, key status, and manual auditor flags.
      * `ALL_RCM_Combined`: A consolidated view of all RCM controls that were matched during the analysis.
      * Individual sheets for each `Account Type` analyzed (e.g., `Accounts_Payable_summary`, `Accounts_Payable_RCM`), providing detailed, specific breakdowns.
  * **PDF Charts (`.pdf`)**: This document provides visual insights for each analyzed account type, helping to quickly understand the data:
      * **Scope Distribution**: A pie chart showing the proportion of "In Scope" versus "Out of Scope" brands.
      * **Account Value by Brand**: A bar chart visualizing the financial value associated with each brand.
      * **Cumulative Percentage**: A line chart illustrating the cumulative contribution of brands towards the total value, with the "in-scope" threshold marked.

## Deployment (Streamlit Cloud)

This application is designed to be easily deployable on platforms like Streamlit Cloud.

1.  **Push to GitHub**: Ensure your `app.py` (or your main Streamlit script) and `requirements.txt` are in the root directory of your GitHub repository.
2.  **Connect to Streamlit Cloud**:
      * Go to [Streamlit Cloud](https://share.streamlit.io/).
      * Sign in with your GitHub account.
      * Click "New app" and select your repository and the main Python file (`app.py`).
      * Click "Deploy\!"

Streamlit Cloud will automatically detect your `requirements.txt` and install the necessary libraries, then deploy your application.

## Troubleshooting

  * **"Error: File Upload Failed"**: Check that you are uploading valid `.xlsx` Excel files.
  * **"Validation Error: ... missing required columns"**: Review the "File Structure Expectations" above. Ensure your RCM and Trial Balance files contain all mandatory columns with correct spelling and capitalization. Remember `Account Type` must be the first column in your Trial Balance.
  * **"Error during analysis: \<specific Python error\>"**: If you encounter an error, check the application logs (if deployed) or your terminal output (if running locally). Common issues include data inconsistencies, unexpected non-numeric values where numbers are expected, or malformed Excel data.
  * **App not loading locally**: Ensure your virtual environment is activated and you are running `streamlit run app.py` from the directory containing `app.py`. Check for any error messages in your terminal.
  * **Deployment issues on Streamlit Cloud**: Check your app's logs on the Streamlit Cloud dashboard. Common causes are missing dependencies in `requirements.txt` or syntax errors in the Python code.

## Contributing

Contributions are welcome\! If you find a bug or have a feature request, please open an issue. If you'd like to contribute code, please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

-----