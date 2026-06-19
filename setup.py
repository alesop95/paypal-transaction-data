#!/usr/bin/env python3
"""
Setup script per l'applicazione PayPal to Google Sheets
Questo script aiuta nella configurazione iniziale dell'applicazione
"""

import os
import sys
import json
from pathlib import Path

def print_header():
    print("=" * 60)
    print("  PayPal to Google Sheets - Setup Wizard")
    print("=" * 60)
    print()

def check_python_version():
    """Verifica la versione di Python"""
    if sys.version_info < (3, 8):
        print("ERRORE: Python 3.8 o superiore è richiesto")
        print(f"   Versione attuale: {sys.version}")
        sys.exit(1)
    else:
        print(f"OK: Python {sys.version.split()[0]} - OK")

def check_requirements():
    """Verifica se i requirements sono installati"""
    try:
        import requests
        import google.auth
        import google_auth_oauthlib
        import googleapiclient
        import dotenv
        import pandas
        import schedule
        print("OK: Dipendenze Python - OK")
        return True
    except ImportError as e:
        print(f"ERRORE: Dipendenze mancanti: {e}")
        print("   Esegui: pip install -r requirements.txt")
        return False

def create_env_file():
    """Crea il file .env se non esiste"""
    env_path = Path('.env')
    env_example_path = Path('.env.example')
    
    if env_path.exists():
        print("OK: File .env già esistente")
        return True
    
    if not env_example_path.exists():
        print("ERRORE: File .env.example non trovato")
        return False
    
    # Copia .env.example in .env
    with open(env_example_path, 'r') as f:
        content = f.read()
    
    with open(env_path, 'w') as f:
        f.write(content)
    
    print("OK: File .env creato da .env.example")
    print("   IMPORTANTE: Modifica il file .env con i tuoi dati!")
    return True

def validate_env_file():
    """Valida il contenuto del file .env"""
    env_path = Path('.env')
    if not env_path.exists():
        print("ERRORE: File .env non trovato")
        return False
    
    required_vars = [
        'PAYPAL_CLIENT_ID',
        'PAYPAL_CLIENT_SECRET',
        'GOOGLE_SHEET_ID'
    ]
    
    missing_vars = []
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    for var in required_vars:
        if f"{var}=your_" in content or f"{var}=" not in content:
            missing_vars.append(var)
    
    if missing_vars:
        print("ERRORE: Variabili .env non configurate:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    else:
        print("OK: File .env configurato")
    return True

def check_credentials_file():
    """Verifica se il file credentials.json esiste"""
    creds_path = Path('credentials.json')
    if creds_path.exists():
        print("OK: File credentials.json trovato")
        return True
    else:
        print("ERRORE: File credentials.json non trovato")
        print("   Scarica le credenziali da Google Cloud Console")
        return False

def test_paypal_connection():
    """Test connessione PayPal"""
    try:
        from config import Config
        from paypal_client import PayPalClient
        
        Config.validate_config()
        client = PayPalClient()
        token = client._get_access_token()
        
        if token:
            print("OK: Connessione PayPal - OK")
            return True
        else:
            print("ERRORE: Connessione PayPal - FALLITA")
            return False
            
    except Exception as e:
        print(f"ERRORE: Connessione PayPal - ERRORE: {e}")
        return False

def test_google_sheets_connection():
    """Test connessione Google Sheets"""
    try:
        from google_sheets_client import GoogleSheetsClient
        
        client = GoogleSheetsClient()
        summary = client.get_sheet_summary()
        
        print("OK: Connessione Google Sheets - OK")
        return True
        
    except Exception as e:
        print(f"ERRORE: Connessione Google Sheets - ERRORE: {e}")
        return False

def run_initial_sync():
    """Esegue un sync iniziale di test"""
    try:
        from main import PayPalToSheetsApp
        
        app = PayPalToSheetsApp()
        result = app.sync_transactions(days_back=1)  # Solo ultimo giorno per test
        
        if result['status'] == 'success':
            print(f"OK: Sync iniziale completato")
            print(f"   Transazioni trovate: {result['transactions_found']}")
            print(f"   Transazioni aggiunte: {result['transactions_added']}")
            return True
        else:
            print(f"ERRORE: Sync iniziale fallito: {result['message']}")
            return False
            
    except Exception as e:
        print(f"ERRORE: Sync iniziale - ERRORE: {e}")
        return False

def interactive_setup():
    """Setup interattivo guidato"""
    print("\nSetup Interattivo")
    print("-" * 30)
    
    # PayPal setup
    print("\n1. Configurazione PayPal:")
    client_id = input("   PayPal Client ID: ").strip()
    client_secret = input("   PayPal Client Secret: ").strip()
    mode = input("   Modalità (sandbox/live) [sandbox]: ").strip() or "sandbox"
    
    # Google Sheets setup
    print("\n2. Configurazione Google Sheets:")
    sheet_id = input("   Google Sheet ID: ").strip()
    sheet_name = input("   Nome foglio [PayPal_Transactions]: ").strip() or "PayPal_Transactions"
    
    # App settings
    print("\n3. Impostazioni Applicazione:")
    interval = input("   Intervallo sync (ore) [24]: ").strip() or "24"
    
    # Crea file .env
    env_content = f"""# PayPal API Configuration
PAYPAL_CLIENT_ID={client_id}
PAYPAL_CLIENT_SECRET={client_secret}
PAYPAL_MODE={mode}

# Google Sheets Configuration
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEET_ID={sheet_id}
GOOGLE_SHEET_NAME={sheet_name}

# Application Settings
CHECK_INTERVAL_HOURS={interval}
LOG_LEVEL=INFO
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\nOK: File .env creato con successo!")

def main():
    print_header()
    
    # Verifica sistema
    print("Verifica Sistema:")
    check_python_version()
    
    deps_ok = check_requirements()
    if not deps_ok:
        print("\nERRORE: Setup interrotto: installa le dipendenze prima di continuare")
        sys.exit(1)
    
    # Setup file di configurazione
    print("\nSetup Configurazione:")
    
    if not Path('.env').exists():
        print("File .env non trovato. Avvio setup interattivo...")
        interactive_setup()
    else:
        create_env_file()
    
    # Verifica configurazione
    print("\nVerifica Configurazione:")
    env_ok = validate_env_file()
    creds_ok = check_credentials_file()
    
    if not env_ok:
        print("\nATTENZIONE: Configura il file .env prima di continuare")
        return
    
    if not creds_ok:
        print("\nATTENZIONE: Scarica credentials.json da Google Cloud Console")
        return
    
    # Test connessioni
    print("\nTest Connessioni:")
    paypal_ok = test_paypal_connection()
    sheets_ok = test_google_sheets_connection()
    
    if paypal_ok and sheets_ok:
        print("\nTest Sync Iniziale:")
        sync_ok = run_initial_sync()
        
        if sync_ok:
            print("\n" + "=" * 60)
            print("\nSETUP COMPLETATO CON SUCCESSO!")
            print("=" * 60)
            print("\nComandi disponibili:")
            print("  python main.py sync          - Sync manuale")
            print("  python main.py status        - Stato applicazione")
            print("  python main.py schedule      - Avvia sync programmata")
            print("\nPer maggiori informazioni, consulta README.md")
        else:
            print("\nATTENZIONE: Setup completato ma sync iniziale fallito")
            print("   Controlla i log per maggiori dettagli")
    else:
        print("\nERRORE: Setup incompleto: risolvi i problemi di connessione")

if __name__ == "__main__":
    main()
