#!/usr/bin/env python3
"""
Script di test rapido per verificare la connessione al Google Sheet
"""

import sys
import os
from pathlib import Path

def test_sheet_connection():
    """Testa la connessione al Google Sheet"""
    try:
        # Verifica che il file .env esista
        if not Path('.env').exists():
            print("ERRORE: File .env non trovato")
            return False
        
        # Verifica che credentials.json esista
        if not Path('credentials.json').exists():
            print("ERRORE: File credentials.json non trovato")
            print("Devi scaricare le credenziali da Google Cloud Console:")
            print("1. Vai su https://console.cloud.google.com/")
            print("2. Crea un progetto o seleziona uno esistente")
            print("3. Abilita Google Sheets API")
            print("4. Crea credenziali OAuth 2.0")
            print("5. Scarica il file JSON e rinominalo 'credentials.json'")
            return False
        
        # Importa e testa il client
        from google_sheets_client import GoogleSheetsClient
        
        print("Test connessione al Google Sheet...")
        client = GoogleSheetsClient()
        
        print(f"Sheet ID: {client.sheet_id}")
        print(f"Sheet Name: {client.sheet_name}")
        
        # Crea/aggiorna il sheet con le intestazioni
        print("Configurazione intestazioni sheet...")
        client.create_or_update_sheet()
        
        # Ottieni il sommario
        summary = client.get_sheet_summary()
        print("OK: Connessione riuscita!")
        print(f"Transazioni esistenti: {summary.get('total_transactions', 0)}")
        
        return True
        
    except Exception as e:
        print(f"ERRORE: {e}")
        return False

def add_sample_data():
    """Aggiunge dati di esempio per testare"""
    try:
        from google_sheets_client import GoogleSheetsClient
        
        # Dati di esempio
        sample_transactions = [
            {
                'transaction_id': 'TEST1234567890ABC',
                'paypal_reference_id': 'REF123456789',
                'order_id': 'ORDER-001',
                'transaction_date': '2024-01-15T10:30:00',
                'transaction_updated_date': '2024-01-15T10:30:00',
                'transaction_status': 'Completed',
                'transaction_event_code': 'T0006',
                'transaction_subject': 'Test Transaction',
                'gross_amount': '100.00',
                'currency_code': 'EUR',
                'fee_amount': '3.50',
                'net_amount': '96.50',
                'payer_name': 'Mario Rossi',
                'payer_email': 'mario.rossi@example.com',
                'payer_account_id': 'PAYER123456',
                'payer_country_code': 'IT',
                'invoice_id': 'INV-001',
                'custom_field': 'Test Field',
                'protection_eligibility': 'Eligible',
                'extracted_at': '2024-01-15T10:35:00',
                'api_mode': 'sandbox'
            }
        ]
        
        client = GoogleSheetsClient()
        added_count = client.append_transactions(sample_transactions)
        
        print(f"OK: Aggiunti {added_count} dati di esempio")
        return True
        
    except Exception as e:
        print(f"ERRORE: {e}")
        return False

def main():
    print("=" * 50)
    print("TEST GOOGLE SHEET")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Comandi disponibili:")
        print("  python test_sheet.py test    - Testa connessione")
        print("  python test_sheet.py sample  - Aggiungi dati esempio")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'test':
        if test_sheet_connection():
            print("\nSheet configurato correttamente!")
            print("Prossimo passo: python test_sheet.py sample")
        else:
            print("\nRisolvi i problemi prima di continuare")
    
    elif command == 'sample':
        if add_sample_data():
            print("\nDati di esempio aggiunti!")
            print("Ora puoi testare: python main.py status")
    
    else:
        print(f"Comando sconosciuto: {command}")

if __name__ == "__main__":
    main()
