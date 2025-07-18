-----

# SOX Audit Automation App (Streamlit)

This repository hosts a powerful and user-friendly web-based application built with Streamlit, specifically designed to automate key aspects of SOX (Sarbanes-Oxley) audit procedures. It intelligently analyzes your Risk and Control Matrix (RCM) and Trial Balance data to help you efficiently identify "in-scope" areas, map controls, and flag items requiring manual auditor review based on your specified criteria.

This application is perfect for audit teams seeking a collaborative, browser-accessible tool that streamlines SOX compliance efforts without the need for complex local software installations.

## Features

  * **User-Friendly Web Interface**: Intuitive design built with Streamlit, making it accessible and easy to use directly from your web browser.
  * **Secure File Upload**: Easily and securely upload your RCM and Trial Balance data from standard Excel files (`.xlsx`).
  * **Flexible Sheet Selection**: Dynamically select the relevant sheet within your uploaded Excel workbooks.
  * **Interactive Data Preview**: Get an immediate visual confirmation with previews of the first few rows of your uploaded data, ensuring correctness.
  * **Dynamic Account Type Selection**: The application automatically extracts and presents unique "Account Types" found in your Trial Balance, allowing for focused and customizable analysis.
  * **Configurable In-Scope Threshold**: Adjust a percentage-based slider to precisely define your materiality threshold, determining which brands are classified as "in-scope" based on their cumulative contribution to the total account value.
  * **Automated Analysis & Intelligent Flagging**:
      * Automatically identifies "In Scope" and "Out of Scope" brands based on financial values and your set threshold.
      * Intelligently maps brands from your Trial Balance data to the controls defined in your RCM.
      * Generates clear flags for items that require manual auditor attention, covering critical scenarios:
          * "In Scope" brands that are *not* found or mapped in your RCM.
          * "In Scope" brands that are unexpectedly marked as "Non-Key" controls in your RCM.
          * "Out of Scope" brands that are surprisingly marked as "Key" controls in your RCM.
  * **Comprehensive Downloadable Reporting**:
      * Produces a detailed Excel report (`.xlsx`) available for download, which includes:
          * `ALL_AccountType_Summary`: A consolidated sheet presenting a holistic view of all analyzed account types, with brands categorized by scope, RCM mapping status, key control status, and the generated auditor flags. This sheet is **color-coded** for quick visual identification of review areas.
          * `ALL_RCM_Combined`: A consolidated listing of all RCM controls that were successfully matched and analyzed across your selected account types.
          * **Individual Account Type Sheets**: For each specific "Account Type" you analyzed (e.g., `Accounts_Payable_summary`, `Accounts_Payable_RCM`), dedicated sheets provide a granular breakdown of brand summaries and associated RCM controls.
  * **Insightful Visual Charts (Downloadable PDF)**: Creates a high-quality PDF document packed with visual insights for each analyzed "Account Type", making data interpretation faster and easier:
      * **Scope Distribution Pie Chart**: Offers a clear visual breakdown of the proportion of "In Scope" versus "Out of Scope" brands.
      * **Account Value Bar Chart**: Illustrates the financial value contributed by each individual brand.
      * **Cumulative Percentage Line Chart**: Visually tracks the cumulative contribution of brands towards the total value, with your defined "in-scope" threshold prominently marked.

## Demo

*(If you have a live demo, link it here. Example: [Live Demo on Streamlit Cloud](https://www.google.com/search?q=https://your-streamlit-app-url.streamlit.app/))*

## Getting Started: From Zero to Deployment

This guide will walk you through setting up your environment, preparing your code, pushing it to GitHub, and finally deploying your Streamlit app to the cloud.

### Step 1: Install Python

If you don't already have Python installed on your computer, follow these instructions:

  * **Windows**:

    1.  Go to the official Python website: [python.org/downloads/windows/](https://www.python.org/downloads/windows/)
    2.  Download the latest Python 3.8+ installer (e.g., "Windows installer (64-bit)").
    3.  Run the installer. **IMPORTANT**: On the first screen, make sure to check the box that says **"Add Python to PATH"** before clicking "Install Now". This is crucial for running Python commands from your terminal.
    4.  Follow the prompts to complete the installation.
    5.  To verify, open Command Prompt (`cmd`) and type:
        ```bash
        python --version
        ```
        You should see "Python 3.x.x".

  * **macOS**:

    1.  Go to the official Python website: [python.org/downloads/macos/](https://www.python.org/downloads/macos/)
    2.  Download the latest Python 3.8+ installer (e.g., "macOS 64-bit universal2 installer").
    3.  Run the `.pkg` installer and follow the prompts.
    4.  To verify, open Terminal (Applications \> Utilities \> Terminal) and type:
        ```bash
        python3 --version
        ```
        You should see "Python 3.x.x".

  * **Linux**:
    Python 3 is usually pre-installed on most Linux distributions. To verify, open your terminal and type:

    ```bash
    python3 --version
    ```

    If it's not installed or you need a newer version, use your distribution's package manager (e.g., `sudo apt update && sudo apt install python3` for Debian/Ubuntu).

### Step 2: Set Up Git & GitHub Account

Git is a version control system, and GitHub is a platform for hosting Git repositories.

1.  **Create a GitHub Account**:

      * If you don't have one, sign up for a free account at [github.com/join](https://github.com/join).

2.  **Install Git**:

      * **Windows**: Download and install Git from [git-scm.com/download/win](https://git-scm.com/download/win). Follow the default installation options.
      * **macOS**: Git is often pre-installed. If not, you can install it via Homebrew (`brew install git`) or by installing Xcode Command Line Tools (`xcode-select --install`).
      * **Linux**: Use your distribution's package manager (e.g., `sudo apt install git` for Debian/Ubuntu).

3.  **Configure Git**: After installation, open your terminal/command prompt and set your user name and email (replace with your actual info):

    ```bash
    git config --global user.name "Your Name"
    git config --global user.email "your_email@example.com"
    ```

### Step 3: Prepare Your Project for GitHub

1.  **Create a New GitHub Repository**:

      * Go to [github.com/new](https://github.com/new) in your web browser.
      * Give your repository a meaningful name (e.g., `sox-audit-app`).
      * Choose "Public" or "Private" (Public is required for free Streamlit Cloud hosting).
      * **Do NOT** check "Add a README file", "Add .gitignore", or "Choose a license" here. We'll add them manually.
      * Click "Create repository".

2.  **Organize Your Project Files Locally**:

      * Create a new folder on your computer for your project (e.g., `my_sox_app`).
      * Place your main application code inside this folder. **Rename your Python script to `app.py`** (this is the default name Streamlit Cloud looks for).
      * **Create `requirements.txt`**: In the same folder as `app.py`, create a new text file named `requirements.txt`. Open it and add the following lines (these are the Python libraries your app needs):
        ```
        streamlit
        pandas
        matplotlib
        openpyxl
        xlsxwriter
        ```
      * **Create `README.md`**: Create another file named `README.md` in the same folder. You can copy the content of *this* `README.md` file into it.
      * **Example Folder Structure**:
        ```
        my_sox_app/
        ├── app.py          # Your main Streamlit application code
        ├── requirements.txt  # List of Python dependencies
        └── README.md       # This Readme file
        ```

3.  **Initialize Git in Your Local Project**:

      * Open your terminal/command prompt.
      * Navigate into your project folder:
        ```bash
        cd my_sox_app
        ```
      * Initialize a new Git repository:
        ```bash
        git init
        ```

4.  **Add Files to Git**:

      * Tell Git to track all files in your project:
        ```bash
        git add .
        ```
      * Commit your changes (this saves them to your local Git history):
        ```bash
        git commit -m "Initial commit: Add SOX app and requirements"
        ```

5.  **Connect Local Repository to GitHub**:

      * Go back to the GitHub page for the repository you created earlier.
      * On the repository page, you'll see a section "Quick setup" or "…or push an existing repository from the command line". Copy the two lines provided there. They will look something like this (replace with your actual repository URL):
        ```bash
        git remote add origin https://github.com/YourUsername/your-sox-app-repo.git
        git branch -M main
        ```
      * Paste these two lines into your terminal and press Enter after each.

6.  **Push Your Code to GitHub**:

      * Send your local code to the GitHub repository:

        ```bash
        git push -u origin main
        ```

      * You might be asked to enter your GitHub username and password/Personal Access Token.

      * **Success\!** Your code is now on GitHub. You can refresh your GitHub repository page to see your files.

### Step 4: Deploy Your App to Streamlit Cloud

Streamlit Cloud is a free and easy way to host your Streamlit applications online.

1.  **Go to Streamlit Cloud**:

      * Open your web browser and go to [share.streamlit.io](https://share.streamlit.io/).
      * Click on **"Sign up free"** or **"Log in"** and authenticate using your **GitHub account**.

2.  **Connect to Your GitHub Repository**:

      * Once logged in, click on the **"New app"** button (or the "+" icon if you already have apps).
      * In the "Deploy a Streamlit app" dialog:
          * **Repository**: Select your GitHub repository from the dropdown list (e.g., `YourUsername/your-sox-app-repo`).
          * **Branch**: Choose the branch where your code is (usually `main`).
          * **Main file path**: Enter the name of your main Streamlit script (e.g., `app.py`).
          * **App URL**: This will be automatically generated.
      * **(Optional)** Click "Advanced settings" to adjust Python version or add secrets, but for this app, default settings should be fine.

3.  **Deploy Your App\!**:

      * Click the **"Deploy\!"** button.
      * Streamlit Cloud will now clone your repository, install the dependencies from `requirements.txt`, and build your application. This process may take a few minutes.
      * Once deployed, your app will open in a new tab, and you'll get a unique public URL that you can share\!

## File Structure Expectations for Input Data (Important\!)

For the analysis to be accurate, your input Excel files uploaded within the Streamlit app must adhere to the following column requirements:

### RCM Excel File (`.xlsx`)

  * **Required Columns (Exact Names & Case)**:
      * `Control Description`
      * `Control ID`
      * `Brand Name`
      * `Key? (Y/N)` (This column is critical for determining 'Key Status'. Expected values are case-insensitive and can include 'Y', 'N', 'Yes', 'No', 'Key', 'Non-Key'.)

### Trial Balance Excel File (`.xlsx`)

  * **Required Columns (Exact Names & Case)**:
      * `Account Type` (This *must* be the **first** column in the sheet.)
      * `Brand Name` (This must also be present. It serves as a descriptive column.)
      * Followed by one or more **additional columns that contain the actual financial values for different brands**. These numeric columns will be dynamically identified as the data points for brand-specific analysis (e.g., columns `B`, `C`, `D`, etc., in your Excel that hold numbers).

## Usage Guide (Once App is Live)

1.  **Access the App**: Open your Streamlit app's URL in any web browser.
2.  **Upload RCM File**:
      * Click the "Browse files" button within the "Upload RCM Excel File" section.
      * Select your RCM Excel spreadsheet (`.xlsx`).
3.  **Select RCM Sheet**:
      * A dropdown will appear. Select the correct sheet containing your RCM data.
      * A preview of the first few rows of your RCM data will be displayed for verification.
4.  **Upload Trial Balance File**:
      * Click "Browse files" within the "Upload Trial Balance Excel File" section.
      * Select your Trial Balance Excel spreadsheet (`.xlsx`).
5.  **Select Trial Balance Sheet**:
      * Select the appropriate sheet from the dropdown for your Trial Balance data.
      * A preview of the first few rows of your Trial Balance data will be shown.
      * **Important**: The application will perform column validation here. If required columns are missing, an error message will guide you.
6.  **Adjust In-Scope Threshold**:
      * Use the slider labeled "Threshold for In Scope (%)" to set your desired materiality percentage.
7.  **Select Account Types for Analysis**:
      * A multi-select box will populate with unique 'Account Type' values from your loaded Trial Balance.
      * Select one or more account types you wish to analyze.
8.  **Run Analysis**:
      * Click the "Run Analysis" button.
      * A progress indicator will appear. Processing time varies with file size.
9.  **Download Results**:
      * Upon completion, "Download Excel Report" and "Download PDF Charts" buttons will appear.
      * Click these buttons to save the generated analysis reports and charts to your local machine.
10. **Clear Data (Optional)**: Click the "Clear Downloaded Files" button to reset the app's state if you wish to start a fresh analysis or clear any sensitive data from the session.

## Troubleshooting

  * **App not loading / "Connection Error"**:
      * If running locally: Ensure your terminal/command prompt is still running the `streamlit run app.py` command without errors. Check your network connection.
      * If deployed: Check your app's logs on the Streamlit Cloud dashboard (`share.streamlit.io -> Your App -> Manage app -> View logs`).
  * **"Error: File Upload Failed"**: Ensure you are uploading valid `.xlsx` Excel files. Streamlit might also have file size limits (200MB default).
  * **"Validation Error: ... missing required columns"**: This means one or more of the specific column names (`Account Type`, `Brand Name`, `Control Description`, `Control ID`, `Key? (Y/N)`) are not found in your uploaded files or are misspelled/incorrectly cased. Review the "File Structure Expectations" carefully.
  * **"Error during analysis: \<specific Python error\>"**: Check the application logs (visible in the terminal if running locally, or on Streamlit Cloud dashboard under "Manage app" -\> "View logs"). This usually points to issues with the data content (e.g., non-numeric values in numeric columns, unexpected data formats).
  * **App works locally but not on Streamlit Cloud**:
      * **`requirements.txt`**: Double-check that *all* libraries listed under "Installation (Local Development)" are present in your `requirements.txt` file and match the exact package names.
      * **File Paths**: Ensure your `app.py` doesn't rely on specific local file paths. Streamlit apps run in a cloud environment.
      * **Python Version**: Streamlit Cloud allows you to select a Python version. Ensure it's compatible with your local environment.

## Contributing

Contributions are highly welcome\! If you encounter any bugs, have suggestions for new features, or want to improve existing functionality:

1.  **Open an Issue**: Please describe the bug or feature request clearly in the "Issues" section of this GitHub repository.
2.  **Fork the Repository**: If you wish to contribute code, fork this repository to your own GitHub account.
3.  **Create a Pull Request**: Make your changes in your forked repository and submit a pull request back to the `main` branch of this repository. Provide a clear description of your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file in the repository for full details.

-----
