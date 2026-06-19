#!/usr/bin/env python3
"""
Script di test rapido per verificare il funzionamento con Excel
"""

import sys
import os
from pathlib import Path

def test_excel_creation():
    """Testa la creazione del file Excel"""
    try:
        from excel_client import ExcelClient
        
        print("Test creazione file Excel...")
        client = ExcelClient()
        
        print(f"File Excel: {client.excel_file}")
        print(f"Sheet Name: {client.sheet_name}")
        
        # Crea/aggiorna il file Excel con le intestazioni
        print("Configurazione intestazioni Excel...")
        client.create_or_update_sheet()
        
        # Ottieni il sommario
        summary = client.get_sheet_summary()
        print("OK: File Excel creato con successo!")
        print(f"Transazioni esistenti: {summary.get('total_transactions', 0)}")
        print(f"Percorso file: {summary.get('file_path', '')}")
        
        return True
        
    except Exception as e:
        print(f"ERRORE: {e}")
        return False

def add_sample_data():
    """Aggiunge dati di esempio per testare"""
    try:
        from excel_client import ExcelClient
        
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
            },
            {
                'transaction_id': 'TEST2345678901DEF',
                'paypal_reference_id': 'REF234567890',
                'order_id': 'ORDER-002',
                'transaction_date': '2024-01-16T14:20:00',
                'transaction_updated_date': '2024-01-16T14:20:00',
                'transaction_status': 'Completed',
                'transaction_event_code': 'T0006',
                'transaction_subject': 'Another Test Transaction',
                'gross_amount': '250.00',
                'currency_code': 'EUR',
                'fee_amount': '7.25',
                'net_amount': '242.75',
                'payer_name': 'Giulia Bianchi',
                'payer_email': 'giulia.bianchi@example.com',
                'payer_account_id': 'PAYER234567',
                'payer_country_code': 'IT',
                'invoice_id': 'INV-002',
                'custom_field': 'Another Test',
                'protection_eligibility': 'Eligible',
                'extracted_at': '2024-01-16T14:25:00',
                'api_mode': 'sandbox'
            }
        ]
        
        client = ExcelClient()
        added_count = client.append_transactions(sample_transactions)
        
        print(f"OK: Aggiunti {added_count} dati di esempio")
        
        # Mostra sommario aggiornato
        summary = client.get_sheet_summary()
        print(f"Totale transazioni nel file: {summary.get('total_transactions', 0)}")
        
        return True
        
    except Exception as e:
        print(f"ERRORE: {e}")
        return False

def test_app_status():
    """Testa lo status dell'applicazione"""
    try:
        # Importa solo se le dipendenze sono disponibili
        from main import PayPalToSheetsApp
        
        print("Test status applicazione...")
        app = PayPalToSheetsApp()
        status = app.get_status()
        
        print("Status applicazione:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"ERRORE nel test app: {e}")
        return False

def main():
    print("=" * 50)
    print("TEST EXCEL CLIENT")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Comandi disponibili:")
        print("  python test_excel.py create   - Crea file Excel")
        print("  python test_excel.py sample   - Aggiungi dati esempio")
        print("  python test_excel.py status   - Test status app")
        print("  python test_excel.py all      - Esegui tutti i test")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'create':
        if test_excel_creation():
            print("\nFile Excel configurato correttamente!")
            print("Prossimo passo: python test_excel.py sample")
        else:
            print("\nRisolvi i problemi prima di continuare")
    
    elif command == 'sample':
        if add_sample_data():
            print("\nDati di esempio aggiunti!")
            print("Puoi aprire il file Excel per vedere i dati")
            print("Prossimo passo: python test_excel.py status")
    
    elif command == 'status':
        test_app_status()
    
    elif command == 'all':
        print("Esecuzione test completi...\n")
        
        print("1. Test creazione Excel:")
        if not test_excel_creation():
            print("Test fallito, interruzione")
            return
        
        print("\n2. Test dati di esempio:")
        if not add_sample_data():
            print("Test fallito, interruzione")
            return
        
        print("\n3. Test status applicazione:")
        test_app_status()
        
        print("\n" + "=" * 50)
        print("TUTTI I TEST COMPLETATI!")
        print("=" * 50)
        print(f"\nIl file Excel è stato creato: paypal_transactions.xlsx")
        print("Puoi aprirlo con Excel per vedere i dati di esempio")
    
    else:
        print(f"Comando sconosciuto: {command}")

if __name__ == "__main__":
    main()
