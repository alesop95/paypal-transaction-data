import logging
import schedule
import time
import sys
from datetime import datetime, timedelta
from typing import List, Dict

from config import Config
from paypal_client import PayPalClient
from excel_client import ExcelClient

class PayPalToSheetsApp:
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Validate configuration
        try:
            Config.validate_config()
        except ValueError as e:
            self.logger.error(f"Configuration error: {e}")
            sys.exit(1)
        
        # Initialize clients
        self.paypal_client = PayPalClient()
        self.excel_client = ExcelClient()
        
        self.logger.info("PayPal to Excel app initialized")
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('paypal_transactions.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def sync_transactions(self, days_back: int = 7) -> Dict:
        """
        Sync PayPal transactions to Excel file
        
        Args:
            days_back: Number of days back to check for transactions
            
        Returns:
            Dictionary with sync results
        """
        self.logger.info(f"Starting transaction sync for last {days_back} days")
        
        try:
            # Ensure the Excel file is set up correctly
            self.excel_client.create_or_update_sheet()
            
            # Get recent transactions from PayPal
            self.logger.info("Fetching transactions from PayPal...")
            transactions = self.paypal_client.get_recent_transactions(days_back)
            
            if not transactions:
                self.logger.info("No transactions found in PayPal")
                return {
                    'status': 'success',
                    'transactions_found': 0,
                    'transactions_added': 0,
                    'message': 'No transactions found'
                }
            
            self.logger.info(f"Found {len(transactions)} transactions in PayPal")
            
            # Add transactions to Excel file
            self.logger.info("Adding transactions to Excel file...")
            added_count = self.excel_client.append_transactions(transactions)
            
            # Get Excel file summary
            summary = self.excel_client.get_sheet_summary()
            
            result = {
                'status': 'success',
                'transactions_found': len(transactions),
                'transactions_added': added_count,
                'total_in_sheet': summary.get('total_transactions', 0),
                'currencies': summary.get('currencies', []),
                'status_counts': summary.get('status_counts', {}),
                'last_sync': datetime.now().isoformat(),
                'message': f'Successfully synced {added_count} new transactions'
            }
            
            self.logger.info(f"Sync completed: {result['message']}")
            return result
            
        except Exception as e:
            error_msg = f"Error during sync: {str(e)}"
            self.logger.error(error_msg)
            return {
                'status': 'error',
                'message': error_msg,
                'transactions_found': 0,
                'transactions_added': 0
            }
    
    def sync_specific_date_range(self, start_date: str, end_date: str = None) -> Dict:
        """
        Sync transactions for a specific date range
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format (optional)
            
        Returns:
            Dictionary with sync results
        """
        try:
            # Convert dates to PayPal API format
            start_datetime = f"{start_date}T00:00:00"
            if end_date:
                end_datetime = f"{end_date}T23:59:59"
            else:
                end_datetime = datetime.now().strftime('%Y-%m-%dT23:59:59')
            
            self.logger.info(f"Syncing transactions from {start_datetime} to {end_datetime}")
            
            # Ensure the sheet is set up correctly
            self.sheets_client.create_or_update_sheet()
            
            # Get transactions from PayPal
            raw_transactions = self.paypal_client.get_transactions(start_datetime, end_datetime)
            
            # Extract fiscal data
            transactions = []
            for raw_transaction in raw_transactions:
                fiscal_data = self.paypal_client.extract_fiscal_data(raw_transaction)
                if fiscal_data and fiscal_data.get('transaction_id'):
                    transactions.append(fiscal_data)
            
            if not transactions:
                return {
                    'status': 'success',
                    'transactions_found': 0,
                    'transactions_added': 0,
                    'message': 'No transactions found for the specified date range'
                }
            
            # Add to sheets
            added_count = self.sheets_client.append_transactions(transactions)
            
            result = {
                'status': 'success',
                'transactions_found': len(transactions),
                'transactions_added': added_count,
                'date_range': f"{start_date} to {end_date or 'today'}",
                'message': f'Successfully synced {added_count} new transactions for date range'
            }
            
            self.logger.info(f"Date range sync completed: {result['message']}")
            return result
            
        except Exception as e:
            error_msg = f"Error during date range sync: {str(e)}"
            self.logger.error(error_msg)
            return {
                'status': 'error',
                'message': error_msg
            }
    
    def get_status(self) -> Dict:
        """Get current status of the application and data"""
        try:
            # Get sheet summary
            sheet_summary = self.sheets_client.get_sheet_summary()
            
            # Test PayPal connection
            try:
                self.paypal_client._get_access_token()
                paypal_status = "Connected"
            except Exception as e:
                paypal_status = f"Error: {str(e)}"
            
            return {
                'paypal_connection': paypal_status,
                'google_sheets_connection': "Connected",
                'sheet_summary': sheet_summary,
                'config': {
                    'paypal_mode': Config.PAYPAL_MODE,
                    'sheet_id': Config.GOOGLE_SHEET_ID,
                    'sheet_name': Config.GOOGLE_SHEET_NAME,
                    'check_interval_hours': Config.CHECK_INTERVAL_HOURS
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def run_scheduled_sync(self):
        """Run the scheduled sync job"""
        self.logger.info("Running scheduled sync...")
        result = self.sync_transactions()
        
        if result['status'] == 'success':
            self.logger.info(f"Scheduled sync successful: {result['message']}")
        else:
            self.logger.error(f"Scheduled sync failed: {result['message']}")
    
    def start_scheduler(self):
        """Start the scheduled sync process"""
        self.logger.info(f"Starting scheduler with {Config.CHECK_INTERVAL_HOURS} hour intervals")
        
        # Schedule the sync job
        schedule.every(Config.CHECK_INTERVAL_HOURS).hours.do(self.run_scheduled_sync)
        
        # Run an initial sync
        self.logger.info("Running initial sync...")
        self.run_scheduled_sync()
        
        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def manual_sync(self, days_back: int = None):
        """Run a manual sync"""
        if days_back is None:
            days_back = 7
        
        print(f"Starting manual sync for last {days_back} days...")
        result = self.sync_transactions(days_back)
        
        print(f"Sync Result:")
        print(f"  Status: {result['status']}")
        print(f"  Transactions found: {result.get('transactions_found', 0)}")
        print(f"  Transactions added: {result.get('transactions_added', 0)}")
        print(f"  Message: {result.get('message', '')}")
        
        if result['status'] == 'success' and 'total_in_sheet' in result:
            print(f"  Total transactions in sheet: {result['total_in_sheet']}")
            if result.get('currencies'):
                print(f"  Currencies: {', '.join(result['currencies'])}")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python main.py sync [days_back]     - Manual sync (default: 7 days)")
        print("  python main.py sync-range YYYY-MM-DD [YYYY-MM-DD] - Sync specific date range")
        print("  python main.py status               - Show current status")
        print("  python main.py schedule             - Start scheduled sync")
        return
    
    app = PayPalToSheetsApp()
    command = sys.argv[1].lower()
    
    if command == 'sync':
        days_back = 7
        if len(sys.argv) > 2:
            try:
                days_back = int(sys.argv[2])
            except ValueError:
                print("Invalid days_back value. Using default: 7")
        
        app.manual_sync(days_back)
    
    elif command == 'sync-range':
        if len(sys.argv) < 3:
            print("Please provide start date: python main.py sync-range YYYY-MM-DD [YYYY-MM-DD]")
            return
        
        start_date = sys.argv[2]
        end_date = sys.argv[3] if len(sys.argv) > 3 else None
        
        result = app.sync_specific_date_range(start_date, end_date)
        print(f"Sync Result: {result}")
    
    elif command == 'status':
        status = app.get_status()
        print("Application Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
    
    elif command == 'schedule':
        print("Starting scheduled sync process...")
        print("Press Ctrl+C to stop")
        try:
            app.start_scheduler()
        except KeyboardInterrupt:
            print("\nScheduled sync stopped")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
