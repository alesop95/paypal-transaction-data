import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # PayPal Configuration
    PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
    PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')
    PAYPAL_MODE = os.getenv('PAYPAL_MODE', 'sandbox')  # 'sandbox' or 'live'
    
    # PayPal API URLs
    PAYPAL_BASE_URL = {
        'sandbox': 'https://api-m.sandbox.paypal.com',
        'live': 'https://api-m.paypal.com'
    }
    
    # Excel Configuration (Local File)
    EXCEL_FILE_PATH = os.getenv('EXCEL_FILE_PATH', 'paypal_transactions.xlsx')
    EXCEL_SHEET_NAME = os.getenv('EXCEL_SHEET_NAME', 'PayPal_Transactions')
    
    # Google Sheets Configuration (Optional - for future use)
    GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
    GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
    GOOGLE_SHEET_NAME = os.getenv('GOOGLE_SHEET_NAME', 'PayPal_Transactions')
    
    # Application Settings
    CHECK_INTERVAL_HOURS = int(os.getenv('CHECK_INTERVAL_HOURS', 24))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Google Sheets API Scopes (Optional)
    GOOGLE_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        required_vars = [
            'PAYPAL_CLIENT_ID',
            'PAYPAL_CLIENT_SECRET'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
