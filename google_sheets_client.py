import os
import logging
from typing import List, Dict, Optional
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import Config

class GoogleSheetsClient:
    def __init__(self):
        self.credentials = None
        self.service = None
        self.sheet_id = Config.GOOGLE_SHEET_ID
        self.sheet_name = Config.GOOGLE_SHEET_NAME
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize the service
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        creds = None
        token_file = 'token.json'
        
        # Check if we have stored credentials
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, Config.GOOGLE_SCOPES)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    self.logger.error(f"Failed to refresh credentials: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(Config.GOOGLE_CREDENTIALS_FILE):
                    raise FileNotFoundError(
                        f"Google credentials file not found: {Config.GOOGLE_CREDENTIALS_FILE}\n"
                        "Please download your credentials.json from Google Cloud Console"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    Config.GOOGLE_CREDENTIALS_FILE, Config.GOOGLE_SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.credentials = creds
        self.service = build('sheets', 'v4', credentials=creds)
        self.logger.info("Successfully authenticated with Google Sheets API")
    
    def _get_sheet_headers(self) -> List[str]:
        """Define the headers for the PayPal transactions sheet"""
        return [
            'Transaction ID',
            'PayPal Reference ID', 
            'Order ID',
            'Transaction Date',
            'Updated Date',
            'Status',
            'Event Code',
            'Subject',
            'Gross Amount',
            'Currency',
            'Fee Amount',
            'Net Amount',
            'Payer Name',
            'Payer Email',
            'Payer Account ID',
            'Payer Country',
            'Invoice ID',
            'Custom Field',
            'Protection Eligibility',
            'Extracted At',
            'API Mode'
        ]
    
    def create_or_update_sheet(self):
        """Create the sheet if it doesn't exist or update headers"""
        try:
            # Try to get the sheet
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.sheet_id
            ).execute()
            
            # Check if our sheet exists
            sheet_exists = False
            for sheet in sheet_metadata.get('sheets', []):
                if sheet['properties']['title'] == self.sheet_name:
                    sheet_exists = True
                    break
            
            if not sheet_exists:
                # Create the sheet
                request_body = {
                    'requests': [{
                        'addSheet': {
                            'properties': {
                                'title': self.sheet_name,
                                'gridProperties': {
                                    'rowCount': 1000,
                                    'columnCount': 21
                                }
                            }
                        }
                    }]
                }
                
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.sheet_id,
                    body=request_body
                ).execute()
                
                self.logger.info(f"Created new sheet: {self.sheet_name}")
            
            # Set up headers
            headers = self._get_sheet_headers()
            range_name = f"{self.sheet_name}!A1:U1"
            
            body = {
                'values': [headers]
            }
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            # Format headers (make them bold)
            format_request = {
                'requests': [{
                    'repeatCell': {
                        'range': {
                            'sheetId': self._get_sheet_id(),
                            'startRowIndex': 0,
                            'endRowIndex': 1,
                            'startColumnIndex': 0,
                            'endColumnIndex': len(headers)
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'textFormat': {
                                    'bold': True
                                },
                                'backgroundColor': {
                                    'red': 0.9,
                                    'green': 0.9,
                                    'blue': 0.9
                                }
                            }
                        },
                        'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                    }
                }]
            }
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.sheet_id,
                body=format_request
            ).execute()
            
            self.logger.info("Sheet headers updated and formatted")
            
        except HttpError as e:
            self.logger.error(f"Error creating/updating sheet: {e}")
            raise
    
    def _get_sheet_id(self) -> int:
        """Get the sheet ID for formatting requests"""
        try:
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.sheet_id
            ).execute()
            
            for sheet in sheet_metadata.get('sheets', []):
                if sheet['properties']['title'] == self.sheet_name:
                    return sheet['properties']['sheetId']
            
            return 0  # Default to first sheet
            
        except Exception as e:
            self.logger.error(f"Error getting sheet ID: {e}")
            return 0
    
    def get_existing_transaction_ids(self) -> set:
        """Get all existing transaction IDs from the sheet to avoid duplicates"""
        try:
            range_name = f"{self.sheet_name}!A:A"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return set()
            
            # Skip header row and extract transaction IDs
            transaction_ids = set()
            for row in values[1:]:  # Skip header
                if row and row[0]:  # Check if transaction ID exists
                    transaction_ids.add(row[0])
            
            self.logger.info(f"Found {len(transaction_ids)} existing transactions in sheet")
            return transaction_ids
            
        except HttpError as e:
            self.logger.error(f"Error reading existing transactions: {e}")
            return set()
    
    def append_transactions(self, transactions: List[Dict]) -> int:
        """
        Append new transactions to the sheet
        
        Args:
            transactions: List of transaction dictionaries with fiscal data
            
        Returns:
            Number of transactions actually added
        """
        if not transactions:
            self.logger.info("No transactions to append")
            return 0
        
        # Get existing transaction IDs to avoid duplicates
        existing_ids = self.get_existing_transaction_ids()
        
        # Filter out existing transactions
        new_transactions = [
            t for t in transactions 
            if t.get('transaction_id') and t['transaction_id'] not in existing_ids
        ]
        
        if not new_transactions:
            self.logger.info("No new transactions to add (all already exist)")
            return 0
        
        # Convert transactions to rows
        rows = []
        for transaction in new_transactions:
            row = [
                transaction.get('transaction_id', ''),
                transaction.get('paypal_reference_id', ''),
                transaction.get('order_id', ''),
                transaction.get('transaction_date', ''),
                transaction.get('transaction_updated_date', ''),
                transaction.get('transaction_status', ''),
                transaction.get('transaction_event_code', ''),
                transaction.get('transaction_subject', ''),
                transaction.get('gross_amount', ''),
                transaction.get('currency_code', ''),
                transaction.get('fee_amount', ''),
                transaction.get('net_amount', ''),
                transaction.get('payer_name', ''),
                transaction.get('payer_email', ''),
                transaction.get('payer_account_id', ''),
                transaction.get('payer_country_code', ''),
                transaction.get('invoice_id', ''),
                transaction.get('custom_field', ''),
                transaction.get('protection_eligibility', ''),
                transaction.get('extracted_at', ''),
                transaction.get('api_mode', '')
            ]
            rows.append(row)
        
        try:
            # Append the data
            range_name = f"{self.sheet_name}!A:U"
            body = {
                'values': rows
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            added_count = len(rows)
            self.logger.info(f"Successfully added {added_count} new transactions to sheet")
            
            return added_count
            
        except HttpError as e:
            self.logger.error(f"Error appending transactions to sheet: {e}")
            raise
    
    def update_transaction_status(self, transaction_id: str, new_status: str) -> bool:
        """Update the status of a specific transaction"""
        try:
            # Find the row with this transaction ID
            range_name = f"{self.sheet_name}!A:F"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            for i, row in enumerate(values[1:], start=2):  # Skip header, start from row 2
                if row and row[0] == transaction_id:
                    # Update the status (column F)
                    update_range = f"{self.sheet_name}!F{i}"
                    body = {
                        'values': [[new_status]]
                    }
                    
                    self.service.spreadsheets().values().update(
                        spreadsheetId=self.sheet_id,
                        range=update_range,
                        valueInputOption='RAW',
                        body=body
                    ).execute()
                    
                    self.logger.info(f"Updated status for transaction {transaction_id} to {new_status}")
                    return True
            
            self.logger.warning(f"Transaction {transaction_id} not found in sheet")
            return False
            
        except HttpError as e:
            self.logger.error(f"Error updating transaction status: {e}")
            return False
    
    def get_sheet_summary(self) -> Dict:
        """Get summary information about the sheet"""
        try:
            range_name = f"{self.sheet_name}!A:U"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if len(values) <= 1:  # Only headers or empty
                return {
                    'total_transactions': 0,
                    'last_update': None,
                    'currencies': [],
                    'status_counts': {}
                }
            
            # Analyze the data
            transactions = values[1:]  # Skip headers
            total_count = len(transactions)
            
            # Get currencies and statuses
            currencies = set()
            statuses = {}
            
            for row in transactions:
                if len(row) > 9 and row[9]:  # Currency column
                    currencies.add(row[9])
                if len(row) > 5 and row[5]:  # Status column
                    status = row[5]
                    statuses[status] = statuses.get(status, 0) + 1
            
            # Get last update time
            last_update = None
            if transactions and len(transactions[-1]) > 19 and transactions[-1][19]:
                last_update = transactions[-1][19]
            
            return {
                'total_transactions': total_count,
                'last_update': last_update,
                'currencies': list(currencies),
                'status_counts': statuses
            }
            
        except HttpError as e:
            self.logger.error(f"Error getting sheet summary: {e}")
            return {}
