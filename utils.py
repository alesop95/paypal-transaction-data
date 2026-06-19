#!/usr/bin/env python3
"""
Utilità per l'applicazione PayPal to Google Sheets
Script con funzioni di supporto per gestione e monitoraggio
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import argparse

def analyze_transactions():
    """Analizza le transazioni nel Google Sheet"""
    try:
        from google_sheets_client import GoogleSheetsClient
        
        client = GoogleSheetsClient()
        
        # Ottieni i dati dal sheet
        range_name = f"{client.sheet_name}!A:U"
        result = client.service.spreadsheets().values().get(
            spreadsheetId=client.sheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        if len(values) <= 1:
            print("Nessuna transazione trovata nel sheet")
            return
        
        # Converti in DataFrame per analisi
        headers = values[0]
        data = values[1:]
        
        # Assicurati che tutte le righe abbiano lo stesso numero di colonne
        max_cols = len(headers)
        for i, row in enumerate(data):
            while len(row) < max_cols:
                row.append('')
        
        df = pd.DataFrame(data, columns=headers)
        
        print("=" * 60)
        print("ANALISI TRANSAZIONI PAYPAL")
        print("=" * 60)
        
        # Statistiche generali
        print("Statistiche Generali:")
        print(f"   Totale transazioni: {len(df)}")
        
        # Analisi per valuta
        if 'Currency' in df.columns:
            currency_counts = df['Currency'].value_counts()
            print("Transazioni per Valuta:")
            for currency, count in currency_counts.items():
                if currency:  # Skip empty values
                    print(f"   {currency}: {count}")
        
        # Analisi per status
        if 'Status' in df.columns:
            status_counts = df['Status'].value_counts()
            print("Transazioni per Status:")
            for status, count in status_counts.items():
                if status:  # Skip empty values
                    print(f"   {status}: {count}")
        
        # Analisi importi (se numerici)
        if 'Gross Amount' in df.columns:
            try:
                # Converti gli importi in numerico (rimuovi caratteri non numerici)
                amounts = pd.to_numeric(df['Gross Amount'].str.replace('[^0-9.-]', '', regex=True), errors='coerce')
                amounts = amounts.dropna()
                
                if not amounts.empty:
                    print("Analisi Importi:")
                    print(f"   Importo totale: {amounts.sum():.2f}")
                    print(f"   Importo medio: {amounts.mean():.2f}")
                    print(f"   Importo minimo: {amounts.min():.2f}")
                    print(f"   Importo massimo: {amounts.max():.2f}")
            except Exception as e:
                print(f"   Errore nell'analisi importi: {e}")
        
        # Analisi temporale
        if 'Transaction Date' in df.columns:
            try:
                # Conta transazioni per giorno
                dates = pd.to_datetime(df['Transaction Date'], errors='coerce')
                dates = dates.dropna()
                
                if not dates.empty:
                    date_counts = dates.dt.date.value_counts().sort_index()
                    print("Transazioni Recenti:")
                    for date, count in date_counts.tail(5).items():
                        print(f"   {date}: {count}")
            except Exception as e:
                print(f"   Errore nell'analisi temporale: {e}")
        
        # Analisi paesi
        if 'Payer Country' in df.columns:
            country_counts = df['Payer Country'].value_counts()
            print("Transazioni per Paese:")
            for country, count in country_counts.head(10).items():
                if country:  # Skip empty values
                    print(f"   {country}: {count}")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"Errore nell'analisi: {e}")

def export_to_excel():
    """Esporta i dati del Google Sheet in un file Excel"""
    try:
        from google_sheets_client import GoogleSheetsClient
        
        client = GoogleSheetsClient()
        
        # Ottieni i dati dal sheet
        range_name = f"{client.sheet_name}!A:U"
        result = client.service.spreadsheets().values().get(
            spreadsheetId=client.sheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        if len(values) <= 1:
            print("Nessuna transazione da esportare")
            return
        
        # Converti in DataFrame
        headers = values[0]
        data = values[1:]
        
        # Assicurati che tutte le righe abbiano lo stesso numero di colonne
        max_cols = len(headers)
        for i, row in enumerate(data):
            while len(row) < max_cols:
                row.append('')
        
        df = pd.DataFrame(data, columns=headers)
        
        # Nome file con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"paypal_transactions_{timestamp}.xlsx"
        
        # Esporta in Excel
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='PayPal_Transactions', index=False)
            
            # Aggiungi un foglio con statistiche
            stats_data = []
            
            # Statistiche generali
            stats_data.append(['Totale Transazioni', len(df)])
            stats_data.append(['Data Export', datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            stats_data.append(['', ''])
            
            # Statistiche per valuta
            if 'Currency' in df.columns:
                currency_counts = df['Currency'].value_counts()
                stats_data.append(['Transazioni per Valuta', ''])
                for currency, count in currency_counts.items():
                    if currency:
                        stats_data.append([currency, count])
                stats_data.append(['', ''])
            
            # Statistiche per status
            if 'Status' in df.columns:
                status_counts = df['Status'].value_counts()
                stats_data.append(['Transazioni per Status', ''])
                for status, count in status_counts.items():
                    if status:
                        stats_data.append([status, count])
            
            stats_df = pd.DataFrame(stats_data, columns=['Metrica', 'Valore'])
            stats_df.to_excel(writer, sheet_name='Statistiche', index=False)
        
        print(f"OK: Dati esportati in: {filename}")
        
    except Exception as e:
        print(f"Errore nell'export: {e}")

def cleanup_logs():
    """Pulisce i file di log vecchi"""
    log_files = ['paypal_transactions.log', 'sync.log']
    
    for log_file in log_files:
        if os.path.exists(log_file):
            # Ottieni la dimensione del file
            size = os.path.getsize(log_file)
            size_mb = size / (1024 * 1024)
            
            if size_mb > 10:  # Se il file è > 10MB
                # Crea backup e tronca
                backup_name = f"{log_file}.backup"
                os.rename(log_file, backup_name)
                print(f"OK: Log {log_file} archiviato come {backup_name}")
            else:
                print(f"INFO: Log {log_file}: {size_mb:.2f}MB - OK")

def validate_transaction_ids():
    """Valida che tutti i transaction ID siano nel formato corretto (17 caratteri alfanumerici)"""
    try:
        from google_sheets_client import GoogleSheetsClient
        
        client = GoogleSheetsClient()
        
        # Ottieni solo la colonna Transaction ID
        range_name = f"{client.sheet_name}!A:A"
        result = client.service.spreadsheets().values().get(
            spreadsheetId=client.sheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        if len(values) <= 1:
            print("Nessuna transazione da validare")
            return
        
        print("Validazione Transaction ID:")
        print("-" * 40)
        
        invalid_ids = []
        valid_count = 0
        
        for i, row in enumerate(values[1:], start=2):  # Skip header
            if row and row[0]:
                transaction_id = row[0].strip()
                
                # Verifica formato: 17 caratteri alfanumerici maiuscoli
                if len(transaction_id) == 17 and transaction_id.isalnum() and transaction_id.isupper():
                    valid_count += 1
                else:
                    invalid_ids.append((i, transaction_id))
        
        print(f"OK: Transaction ID validi: {valid_count}")
        
        if invalid_ids:
            print(f"ERRORE: Transaction ID non validi: {len(invalid_ids)}")
            print("\nDettagli ID non validi:")
            for row_num, tid in invalid_ids[:10]:  # Mostra solo i primi 10
                print(f"   Riga {row_num}: '{tid}' (lunghezza: {len(tid)})")
            
            if len(invalid_ids) > 10:
                print(f"   ... e altri {len(invalid_ids) - 10}")
        else:
            print("OK: Tutti i Transaction ID sono nel formato corretto")
        
    except Exception as e:
        print(f"Errore nella validazione: {e}")

def check_duplicates():
    """Controlla la presenza di transaction ID duplicati"""
    try:
        from google_sheets_client import GoogleSheetsClient
        
        client = GoogleSheetsClient()
        
        # Ottieni solo la colonna Transaction ID
        range_name = f"{client.sheet_name}!A:A"
        result = client.service.spreadsheets().values().get(
            spreadsheetId=client.sheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        if len(values) <= 1:
            print("Nessuna transazione da controllare")
            return
        
        print("Controllo Duplicati:")
        print("-" * 30)
        
        transaction_ids = []
        for row in values[1:]:  # Skip header
            if row and row[0]:
                transaction_ids.append(row[0].strip())
        
        # Trova duplicati
        seen = set()
        duplicates = set()
        
        for tid in transaction_ids:
            if tid in seen:
                duplicates.add(tid)
            else:
                seen.add(tid)
        
        if duplicates:
            print(f"ERRORE: Trovati {len(duplicates)} Transaction ID duplicati:")
            for dup in sorted(duplicates):
                count = transaction_ids.count(dup)
                print(f"   {dup} (presente {count} volte)")
        else:
            print("OK: Nessun duplicato trovato")
        
        print(f"\nTotale transazioni uniche: {len(seen)}")
        print(f"Totale righe: {len(transaction_ids)}")
        
    except Exception as e:
        print(f"Errore nel controllo duplicati: {e}")

def backup_sheet():
    """Crea un backup del Google Sheet"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"paypal_backup_{timestamp}.json"
        
        from google_sheets_client import GoogleSheetsClient
        
        client = GoogleSheetsClient()
        
        # Ottieni tutti i dati
        range_name = f"{client.sheet_name}!A:U"
        result = client.service.spreadsheets().values().get(
            spreadsheetId=client.sheet_id,
            range=range_name
        ).execute()
        
        # Salva in JSON
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'sheet_id': client.sheet_id,
            'sheet_name': client.sheet_name,
            'data': result.get('values', [])
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        print(f"OK: Backup creato: {filename}")
        
    except Exception as e:
        print(f"Errore nel backup: {e}")

def main():
    parser = argparse.ArgumentParser(description='Utilità PayPal to Google Sheets')
    parser.add_argument('command', choices=[
        'analyze', 'export', 'cleanup', 'validate', 'duplicates', 'backup'
    ], help='Comando da eseguire')
    
    args = parser.parse_args()
    
    if args.command == 'analyze':
        analyze_transactions()
    elif args.command == 'export':
        export_to_excel()
    elif args.command == 'cleanup':
        cleanup_logs()
    elif args.command == 'validate':
        validate_transaction_ids()
    elif args.command == 'duplicates':
        check_duplicates()
    elif args.command == 'backup':
        backup_sheet()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Utilità PayPal to Google Sheets")
        print("\nComandi disponibili:")
        print("  python utils.py analyze     - Analizza transazioni")
        print("  python utils.py export      - Esporta in Excel")
        print("  python utils.py cleanup     - Pulisce log")
        print("  python utils.py validate    - Valida Transaction ID")
        print("  python utils.py duplicates  - Controlla duplicati")
        print("  python utils.py backup      - Backup del sheet")
    else:
        main()
