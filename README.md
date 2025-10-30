# Credit Memo SOX Automation 💳

**AI-Powered Credit Approval Validation for SOX Compliance**

## 📋 Overview

This tool automates the validation of credit memos against approval policies for SOX (Sarbanes-Oxley) compliance. It uses Azure OpenAI GPT-4 to intelligently analyze credit transactions, verify approvals, and flag compliance issues.

### Key Features

- ✅ **AI-Powered Analysis** - GPT-4 analyzes credit memos against company policies
- ✅ **Automated SOX Status** - Determines compliance status (Pass/Fail/Pending)
- ✅ **Approval Verification** - Validates approval levels based on credit amount
- ✅ **Exception Reporting** - Flags non-compliant transactions
- ✅ **Interactive Chat** - Ask questions about credit memo compliance
- ✅ **Export Reports** - Generate Excel reports with analysis results

## 🏗️ Architecture

```
Use Case 2 - Credit Approval Automation/
├── App/
│   ├── app.py               # Main Streamlit application
│   ├── requirements.txt     # Python dependencies
│   ├── .gitignore          # Git ignore patterns
│   └── .streamlit/         # Streamlit configuration
│       └── secrets.toml    # Secrets (not in git)
├── Final files/
│   ├── Credit memo.xlsx    # Sample credit memo data
│   └── Write_Up.pdf        # Documentation
├── credit_venv/            # Python virtual environment
├── .env                    # Environment variables (not in git)
└── .gitignore             # Git ignore patterns
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Azure OpenAI account with GPT-4 deployment
- Credit memo data in Excel format

### Step 1: Setup Virtual Environment

```bash
# Navigate to the App directory
cd "Use Case 2 - Credit Approval Automation/App"

# Create virtual environment (if not exists)
python -m venv ../credit_venv

# Activate virtual environment
# Windows:
..\credit_venv\Scripts\activate
# Linux/Mac:
source ../credit_venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

Create a `.env` file in the parent directory:

```env
# Use Case 2 - Credit Approval Automation/.env

AZURE_OPENAI_API_KEY=your-azure-openai-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-4.1
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

Or for Streamlit Cloud, configure secrets in `.streamlit/secrets.toml`:

```toml
# App/.streamlit/secrets.toml (for Streamlit Cloud)

AZURE_OPENAI_API_KEY = "your-key"
AZURE_OPENAI_ENDPOINT = "https://your-resource.openai.azure.com"
```

### Step 3: Run the Application

```bash
# Make sure you're in the App directory
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 📊 How It Works

### Credit Memo Validation Process

1. **Upload Credit Memo File**
   - Excel file with credit transactions
   - Required columns: Customer ID, Credit Amount, Approver, etc.

2. **AI Analysis**
   - GPT-4 analyzes each transaction
   - Compares against approval policy thresholds
   - Validates approver authority levels

3. **SOX Status Determination**
   - ✅ **Pass** - Properly approved within authority limits
   - ❌ **Fail** - Missing approval or insufficient authority
   - ⏳ **Pending** - Requires additional review

4. **Results & Reporting**
   - View detailed analysis in the app
   - Export results to Excel
   - Interactive chat for questions

### Approval Policy Logic

The system validates credit memos against these typical thresholds:

| Credit Amount | Required Approver Level |
|---------------|------------------------|
| $0 - $10,000 | Manager |
| $10,001 - $50,000 | Director |
| $50,001 - $100,000 | VP |
| $100,000+ | C-Level (CFO/CEO) |

**Note:** Thresholds can be customized based on your company policy.

## 🎯 Features in Detail

### 1. File Upload & Validation
- Automatic column detection
- Data quality checks
- Missing field identification

### 2. AI-Powered Analysis
```python
# Example analysis
Credit Amount: $75,000
Approver: John Doe (Director)
Status: ❌ FAIL - Requires VP approval for amounts over $50,000
```

### 3. Interactive Chat Interface
Ask questions like:
- "Show me all failed credit memos"
- "How many credits need VP approval?"
- "List credits approved by John Doe"

### 4. Export & Reporting
- Excel export with color-coded status
- Summary statistics (Pass/Fail counts)
- Compliance percentage

## 🔧 Configuration

### Environment Variables

```env
# Required
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_ENDPOINT=<your-endpoint>

# Optional (with defaults)
AZURE_OPENAI_DEPLOYMENT=gpt-4.1
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

### Approval Policy Customization

To modify approval thresholds, edit the policy logic in `app.py`:

```python
# Find the approval validation function
def validate_approval(credit_amount, approver_level):
    if credit_amount <= 10000:
        return "Manager" in approver_level
    elif credit_amount <= 50000:
        return "Director" in approver_level
    # Add your custom thresholds here
```

## 📁 Input File Format

### Required Excel Columns

| Column Name | Description | Example |
|------------|-------------|---------|
| `Customer ID` | Unique customer identifier | CUST-001 |
| `Customer Name` | Customer name | Acme Corp |
| `Credit Amount` | Credit memo amount ($) | 45000 |
| `Approver` | Person who approved | John Doe |
| `Approver Level` | Approver's authority level | Director |
| `Date` | Credit memo date | 2025-01-15 |
| `Reason` | Reason for credit | Damaged goods |

### Sample Data Structure

```excel
Customer ID | Customer Name | Credit Amount | Approver  | Approver Level | Date       | Reason
CUST-001   | Acme Corp     | 45000         | John Doe  | Director       | 2025-01-15 | Damaged goods
CUST-002   | Tech Inc      | 125000        | Jane Smith| VP             | 2025-01-20 | Contract dispute
```

## 📊 Output Reports

### Analysis Results

The app generates:

1. **Main Dashboard**
   - Total credit memos analyzed
   - Pass/Fail/Pending counts
   - Compliance percentage
   - Visual charts

2. **Detailed Results Table**
   - All transactions with SOX status
   - Color-coded (Green=Pass, Red=Fail, Yellow=Pending)
   - Filtering and sorting

3. **Excel Export**
   - All original data + AI analysis
   - SOX Status column
   - Approval validation notes
   - Summary sheet

## 🐛 Troubleshooting

### "Azure OpenAI credentials missing"
**Solution:** 
- Verify `.env` file exists and contains correct API keys
- For Streamlit Cloud, check `.streamlit/secrets.toml`

### "File upload failed"
**Solution:**
- Ensure Excel file has correct column names
- Check for empty rows or invalid data
- Verify file is not corrupted

### "AI analysis not working"
**Solution:**
- Verify Azure OpenAI deployment name is correct
- Check API key has GPT-4 access
- Review Azure OpenAI quota limits

### "SOX status shows 'Unknown'"
**Solution:**
- Check that credit amount and approver level columns are filled
- Verify data types (amounts should be numbers)
- Review approval policy thresholds

## 🔐 Security

- ✅ API keys stored in `.env` (never committed to Git)
- ✅ `.gitignore` configured for sensitive files
- ✅ Streamlit secrets for cloud deployment
- ✅ No data persisted after session ends

## 🆚 Use Case Comparison

This project includes three SOX automation use cases:

| Use Case | Focus | AI/Automation | Complexity |
|----------|-------|---------------|------------|
| **Use Case 1** (ai-app/cloud-app) | SOX Control Mapping | GPT-4 + Embeddings | High |
| **Use Case 2** (This Tool) | Credit Memo Approval | GPT-4 Analysis | Medium |
| **Use Case 3** | Inventory Reserve | Rule-Based | Low |

## 📚 Additional Resources

### Sample Files
- `Final files/Credit memo.xlsx` - Example credit memo data
- `Final files/Write_Up.pdf` - Detailed documentation

### Related Documentation
- [Main Project README](../../README.md)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Streamlit Documentation](https://docs.streamlit.io/)

## 🛠️ Development

### Running Tests

```bash
# Test with sample data
streamlit run app.py

# Upload the sample file from Final files/
# Review results and verify SOX status logic
```

### Customization

The tool can be customized for:
- Different approval policies
- Additional validation rules
- Custom reporting formats
- Integration with other systems

## 📞 Support

For issues or questions:
1. Check this README for common solutions
2. Review error messages in the app
3. Verify Azure OpenAI credentials and quota
4. Check the main project documentation

## 📄 License

Part of the SOX Automation project. See main repository for license details.

---

**Last Updated:** October 30, 2025  
**Version:** 2.0  
**Use Case:** Credit Memo SOX Compliance Validation
