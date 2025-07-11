# SOX Audit Automation GUI

This desktop application provides a streamlined solution for assisting with SOX (Sarbanes-Oxley) audit procedures by automating the analysis of RCM (Risk and Control Matrix) and Trial Balance data. It helps auditors identify "in-scope" areas, map controls, and flag items for manual review based on predefined criteria and a user-adjustable materiality threshold.

## Features

* **File Upload**: Easily upload RCM and Trial Balance data from Excel files (`.xlsx`).
* **Sheet Selection**: Select specific sheets within your Excel files for analysis.
* **Data Preview**: View the first 5 rows of your uploaded RCM and Trial Balance data to ensure correct file loading.
* **Dynamic Account Type Selection**: Automatically populates a list of unique "Account Types" from your Trial Balance, allowing you to select specific types for analysis.
* **In-Scope Threshold Adjustment**: Adjust the percentage threshold to define "in-scope" brands based on cumulative account value.
* **Automated Analysis**:
    * Determines "In Scope" and "Out of Scope" brands based on account values and the set threshold.
    * Maps brands from the Trial Balance to the RCM based on "Brand Name".
    * Flags items for manual auditor review based on conditions such as:
        * "In Scope" but not mapped in RCM.
        * "In Scope" but marked as "Non-Key" in RCM.
        * "Out of Scope" but marked as "Key" in RCM.
* **Comprehensive Reporting**:
    * Generates a detailed Excel report (`.xlsx`) with:
        * A consolidated summary of all "Account Types" analyzed, including scope, mapping, key status, and auditor flags.
        * A consolidated view of all RCM controls that matched any analyzed "Account Type".
        * Individual sheets for each analyzed "Account Type", showing both brand-level summaries and matched RCM controls with specific formatting for easy review.
* **Visual Charts (PDF)**: Creates a PDF document containing charts for each analyzed "Account Type", including:
    * Pie chart of Scope Distribution (In Scope vs. Out of Scope).
    * Bar chart of Account Value by Brand.
    * Line chart showing Cumulative Percentage of Account Value by Brand, with the in-scope threshold clearly marked.
* **Intuitive User Interface**: Built with Tkinter for a straightforward desktop application experience.

## Getting Started

### Prerequisites

To run this application, you need:

* **Python 3.x**: Download and install from [python.org](https://www.python.org/).
* **Required Python Libraries**:
    * `pandas`
    * `matplotlib`
    * `openpyxl`
    * `xlsxwriter`
    * `tkinter` (usually included with Python installation)

You can install the necessary libraries using pip. Open your terminal or command prompt and run the following command:

```bash
pip install pandas matplotlib openpyxl xlsxwriter