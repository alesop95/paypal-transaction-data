# PayPal to Google Sheets Transaction Sync

Questa applicazione automatizza il processo di sincronizzazione delle transazioni PayPal con Google Sheets, estraendo tutti i dati fiscalmente rilevanti per la contabilità.

## Caratteristiche

- **Estrazione automatica dati fiscali**: recupera transaction ID (17 caratteri alfanumerici), importi, commissioni, date, e informazioni del pagatore
- **Integrazione Google Sheets**: salva automaticamente i dati in un foglio Google formattato
- **Prevenzione duplicati**: evita di inserire transazioni già presenti
- **Sync programmata**: esecuzione automatica a intervalli configurabili
- **Logging completo**: tracciamento dettagliato di tutte le operazioni
- **Supporto sandbox/live**: configurabile per ambiente di test o produzione
- **Conformità fiscale**: dati estratti secondo le best practice per la contabilità

## Dati Estratti

L'applicazione estrae i seguenti dati fiscalmente rilevanti da ogni transazione PayPal:

### Identificatori Principali
- **Transaction ID**: ID transazione principale (17 caratteri alfanumerici) per scopi fiscali
- **PayPal Reference ID**: ID di riferimento PayPal
- **Order ID**: ID ordine associato

### Informazioni Finanziarie
- **Gross Amount**: Importo lordo della transazione
- **Currency Code**: Codice valuta (EUR, USD, etc.)
- **Fee Amount**: Commissioni PayPal
- **Net Amount**: Importo netto ricevuto

### Dettagli Transazione
- **Transaction Date**: Data e ora della transazione
- **Transaction Status**: Stato della transazione (Completed, Pending, etc.)
- **Transaction Event Code**: Codice evento PayPal
- **Subject**: Oggetto/descrizione della transazione

### Informazioni Pagatore
- **Payer Name**: Nome del pagatore
- **Payer Email**: Email del pagatore
- **Payer Country**: Paese del pagatore
- **Account ID**: ID account PayPal del pagatore

### Dati Aggiuntivi
- **Invoice ID**: ID fattura (se presente)
- **Custom Field**: Campi personalizzati
- **Protection Eligibility**: Eligibilità protezione acquirente

## Prerequisiti

1. **Account PayPal Business** con accesso alle API
2. **Google Account** con accesso a Google Sheets
3. **Python 3.8+**

## Setup

### 1. Installazione Dipendenze

```bash
pip install -r requirements.txt
```

### 2. Configurazione PayPal API

1. Andare su [PayPal Developer](https://developer.paypal.com/)
2. Creare una nuova applicazione
3. Ottienere `Client ID` e `Client Secret`
4. Configurare i webhook se necessario

### 3. Configurazione Google Sheets API

1. Andare su [Google Cloud Console](https://console.cloud.google.com/)
2. Creare un nuovo progetto o selezionare uno esistente
3. Abilitare l'API Google Sheets
4. Creare credenziali (OAuth 2.0 Client ID)
5. Scaricare il file `credentials.json`

### 4. Preparazione Google Sheet

1. Creare un nuovo Google Sheet
2. Copiare l'ID del sheet dall'URL (la parte tra `/d/` e `/edit`)
3. Assicurarsi che l'account Google abbia accesso in scrittura

### 5. Configurazione Ambiente

1. Copiare `.env.example` in `.env`:
```bash
cp .env.example .env
```

2. Compilare il file `.env` con i propri dati:
```env
# PayPal API Configuration
PAYPAL_CLIENT_ID=your_paypal_client_id_here
PAYPAL_CLIENT_SECRET=your_paypal_client_secret_here
PAYPAL_MODE=sandbox  # o 'live' per produzione

# Google Sheets Configuration
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEET_ID=your_google_sheet_id_here
GOOGLE_SHEET_NAME=PayPal_Transactions

# Application Settings
CHECK_INTERVAL_HOURS=24
LOG_LEVEL=INFO
```

## Utilizzo

### Sync Manuale

Sincronizzare le transazioni degli ultimi 7 giorni:
```bash
python main.py sync
```

Sincronizza un numero specifico di giorni:
```bash
python main.py sync 30
```

### Sync per Intervallo di Date

Sincronizzare transazioni per un periodo specifico:
```bash
python main.py sync-range 2024-01-01 2024-01-31
```

### Controllo Status

Verificare lo stato dell'applicazione e delle connessioni:
```bash
python main.py status
```

### Sync Programmata

Avviare il processo di sincronizzazione automatica:
```bash
python main.py schedule
```

## Struttura Dati Google Sheets

Il foglio Google viene automaticamente formattato con le seguenti colonne:

| Colonna | Descrizione | Importanza Fiscale |
|---------|-------------|-------------------|
| Transaction ID | ID transazione principale | ⭐⭐⭐ Essenziale |
| PayPal Reference ID | Riferimento PayPal | ⭐⭐ Importante |
| Order ID | ID ordine | ⭐⭐ Importante |
| Transaction Date | Data transazione | ⭐⭐⭐ Essenziale |
| Status | Stato transazione | ⭐⭐⭐ Essenziale |
| Gross Amount | Importo lordo | ⭐⭐⭐ Essenziale |
| Currency | Valuta | ⭐⭐⭐ Essenziale |
| Fee Amount | Commissioni | ⭐⭐⭐ Essenziale |
| Net Amount | Importo netto | ⭐⭐⭐ Essenziale |
| Payer Name | Nome pagatore | ⭐⭐ Importante |
| Payer Email | Email pagatore | ⭐⭐ Importante |
| Payer Country | Paese pagatore | ⭐⭐ Importante |
| Invoice ID | ID fattura | ⭐⭐ Importante |

## Logging

L'applicazione genera log dettagliati in:
- **Console**: Output in tempo reale
- **File**: `paypal_transactions.log`

Livelli di log configurabili: DEBUG, INFO, WARNING, ERROR

## Sicurezza

- **Credenziali crittografate**: le credenziali Google vengono salvate in modo sicuro
- **Token refresh automatico**: gestione automatica dei token scaduti
- **Variabili ambiente**: credenziali sensibili non hardcodate
- **HTTPS**: tutte le comunicazioni API sono crittografate

## Conformità Fiscale

L'applicazione è progettata per rispettare i requisiti fiscali:

1. **Transaction ID univoci**: ogni transazione ha un ID univoco di 17 caratteri
2. **Tracciabilità completa**: tutti i dati necessari per la riconciliazione
3. **Timestamp precisi**: date e orari delle transazioni
4. **Importi dettagliati**: lordo, netto, e commissioni separati
5. **Informazioni pagatore**: dati del cliente per fatturazione

## Troubleshooting

### Errore di Autenticazione PayPal
```
Error: Failed to get PayPal access token
```
**Soluzione**: verificare `PAYPAL_CLIENT_ID` e `PAYPAL_CLIENT_SECRET` nel file `.env`

### Errore Google Sheets
```
Error: Google credentials file not found
```
**Soluzione**: assicurarsi che il file `credentials.json` sia presente e il path sia corretto

### Transazioni Duplicate
L'applicazione previene automaticamente i duplicati confrontando i Transaction ID esistenti.

### Rate Limiting
PayPal ha limiti di rate per le API. L'applicazione gestisce automaticamente questi limiti.

## Automazione Avanzata

### Cron Job (Linux/Mac)
Per eseguire automaticamente ogni giorno alle 9:00:
```bash
0 9 * * * cd /path/to/project && python main.py sync >> sync.log 2>&1
```

### Task Scheduler (Windows)
Configurare un'attività programmata per eseguire `python main.py sync`

### Docker (Opzionale)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py", "schedule"]
```

## Supporto

Per problemi o domande:
1. Controllare i log in `paypal_transactions.log`
2. Verificare la configurazione con `python main.py status`
3. Controllare la documentazione API PayPal e Google Sheets

## Note Importanti

- **Ambiente Sandbox**: usare sempre l'ambiente sandbox per i test
- **Backup**: fare backup regolari del Google Sheet
- **Monitoraggio**: controllare regolarmente i log per errori
- **Aggiornamenti**: mantenere aggiornate le dipendenze per la sicurezza

## Licenza

Questo progetto è per uso personale/aziendale. Rispetta i termini di servizio di PayPal e Google.
