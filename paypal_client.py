import requests
import base64
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import Config

class PayPalClient:
    def __init__(self):
        self.client_id = Config.PAYPAL_CLIENT_ID
        self.client_secret = Config.PAYPAL_CLIENT_SECRET
        self.base_url = Config.PAYPAL_BASE_URL[Config.PAYPAL_MODE]
        self.access_token = None
        self.token_expires_at = None
        
        self.logger = logging.getLogger(__name__)
    
    def _get_access_token(self) -> str:
        """Get or refresh PayPal access token"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
        
        # Encode credentials
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = 'grant_type=client_credentials'
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/oauth2/token",
                headers=headers,
                data=data
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)  # Refresh 1 min early
            
            self.logger.info("Successfully obtained PayPal access token")
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get PayPal access token: {e}")
            raise
    
    def _make_api_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make authenticated request to PayPal API"""
        token = self._get_access_token()
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"PayPal API request failed: {e}")
            if hasattr(e.response, 'text'):
                self.logger.error(f"Response: {e.response.text}")
            raise
    
    def get_transactions(self, start_date: str, end_date: str = None, page_size: int = 500) -> List[Dict]:
        """
        Get PayPal transactions for a date range
        
        Args:
            start_date: Start date in YYYY-MM-DDTHH:MM:SS format
            end_date: End date in YYYY-MM-DDTHH:MM:SS format (defaults to now)
            page_size: Number of transactions per page (max 500)
        
        Returns:
            List of transaction dictionaries
        """
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'fields': 'all',
            'page_size': min(page_size, 500)  # PayPal max is 500
        }
        
        all_transactions = []
        page = 1
        
        while True:
            params['page'] = page
            
            try:
                response = self._make_api_request('/v1/reporting/transactions', params)
                
                transactions = response.get('transaction_details', [])
                if not transactions:
                    break
                
                all_transactions.extend(transactions)
                
                # Check if there are more pages
                if len(transactions) < page_size:
                    break
                
                page += 1
                self.logger.info(f"Retrieved page {page-1} with {len(transactions)} transactions")
                
            except Exception as e:
                self.logger.error(f"Error retrieving transactions page {page}: {e}")
                break
        
        self.logger.info(f"Total transactions retrieved: {len(all_transactions)}")
        return all_transactions
    
    def get_transaction_details(self, transaction_id: str) -> Dict:
        """Get detailed information for a specific transaction"""
        try:
            return self._make_api_request(f'/v1/reporting/transactions/{transaction_id}')
        except Exception as e:
            self.logger.error(f"Error retrieving transaction {transaction_id}: {e}")
            return {}
    
    def extract_fiscal_data(self, transaction: Dict) -> Dict:
        """
        Extract fiscally relevant data from a PayPal transaction
        
        Based on the context provided, we focus on:
        - Transaction ID (17 alphanumeric capitals) - the actual capture/transaction ID
        - Order ID (for reference)
        - Amount and currency
        - Date and time
        - Payer information
        - Fee information
        - Status
        """
        try:
            transaction_info = transaction.get('transaction_info', {})
            payer_info = transaction.get('payer_info', {})
            cart_info = transaction.get('cart_info', {})
            
            # Extract the main transaction ID (17 alphanumeric capitals)
            transaction_id = transaction_info.get('transaction_id', '')
            
            fiscal_data = {
                # Core identifiers
                'transaction_id': transaction_id,  # This is the 17-char ID for fiscal purposes
                'paypal_reference_id': transaction_info.get('paypal_reference_id', ''),
                'order_id': cart_info.get('item_details', [{}])[0].get('item_code', '') if cart_info.get('item_details') else '',
                
                # Transaction details
                'transaction_date': transaction_info.get('transaction_initiation_date', ''),
                'transaction_updated_date': transaction_info.get('transaction_updated_date', ''),
                'transaction_status': transaction_info.get('transaction_status', ''),
                'transaction_event_code': transaction_info.get('transaction_event_code', ''),
                'transaction_subject': transaction_info.get('transaction_subject', ''),
                
                # Financial information
                'gross_amount': transaction_info.get('transaction_amount', {}).get('value', '0'),
                'currency_code': transaction_info.get('transaction_amount', {}).get('currency_code', ''),
                'fee_amount': transaction_info.get('fee_amount', {}).get('value', '0'),
                'net_amount': transaction_info.get('ending_balance', {}).get('value', '0'),
                
                # Payer information
                'payer_name': payer_info.get('payer_name', {}).get('alternate_full_name', ''),
                'payer_email': payer_info.get('email_address', ''),
                'payer_account_id': payer_info.get('account_id', ''),
                'payer_address_status': payer_info.get('address_status', ''),
                'payer_country_code': payer_info.get('country_code', ''),
                
                # Additional fiscal information
                'invoice_id': transaction_info.get('invoice_id', ''),
                'custom_field': transaction_info.get('custom_field', ''),
                'protection_eligibility': transaction_info.get('protection_eligibility', ''),
                
                # Timestamps for record keeping
                'extracted_at': datetime.now().isoformat(),
                'api_mode': Config.PAYPAL_MODE
            }
            
            return fiscal_data
            
        except Exception as e:
            self.logger.error(f"Error extracting fiscal data from transaction: {e}")
            return {}
    
    def get_recent_transactions(self, days_back: int = 7) -> List[Dict]:
        """Get transactions from the last N days with fiscal data extracted"""
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%dT00:00:00')
        end_date = datetime.now().strftime('%Y-%m-%dT23:59:59')
        
        self.logger.info(f"Retrieving transactions from {start_date} to {end_date}")
        
        raw_transactions = self.get_transactions(start_date, end_date)
        
        # Extract fiscal data from each transaction
        fiscal_transactions = []
        for transaction in raw_transactions:
            fiscal_data = self.extract_fiscal_data(transaction)
            if fiscal_data and fiscal_data.get('transaction_id'):  # Only include valid transactions
                fiscal_transactions.append(fiscal_data)
        
        return fiscal_transactions
