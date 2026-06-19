# 📋 BACKUP PROGETTO PAYPAL-EXCEL
**Data:** 2025-01-22  
**Stato:** Setup tecnico completato, pronto per integrazione PayPal API

## 🎯 OBIETTIVO PROGETTO
Automatizzare la sincronizzazione delle transazioni PayPal con un file Excel locale per gestione fiscale.

## STATO ATTUALE COMPLETATO

### **Setup Tecnico**
- ✅ Applicazione convertita da Google Sheets a Excel locale
- ✅ Ambiente virtuale Python configurato
- ✅ Dipendenze installate e testate
- ✅ File Excel funzionante con dati di esempio
- ✅ Risolto problema percorsi lunghi Windows con `subst`

### **File Principali Creati/Modificati**
- `excel_client.py` - Client Excel (sostituisce Google Sheets)
- `main.py` - Applicazione principale (modificata per Excel)
- `config.py` - Configurazione aggiornata
- `test_excel.py` - Script di test per Excel
- `requirements_minimal.txt` - Dipendenze essenziali
- `.env` - Configurazione ambiente

## SETUP TECNICO COMPLETATO

### **Ambiente Virtuale**
```cmd
# Problema risolto con subst (percorsi lunghi Windows)
subst P: "J:\googleDrive_sync\Portfolio and ongoing studies\Progetti (idee)\Get transaction Data with Paypal"
cd P:\
python -m venv venv
venv\Scripts\activate.bat
```

### **Dipendenze Installate**
```cmd
pip install requests==2.31.0
pip install python-dotenv==1.0.0
pip install schedule==1.2.0
pip install openpyxl==3.1.2
```

### **Test Completati**
```cmd
python test_excel.py create   #  File Excel creato
python test_excel.py sample   #  Dati esempio aggiunti
python test_excel.py all      #  Test completo OK
```

## 📁 STRUTTURA PROGETTO

```
Get transaction Data with Paypal/
├── main.py                    # App principale
├── excel_client.py           # Client Excel (NUOVO)
├── paypal_client.py          # Client PayPal API
├── config.py                 # Configurazione
├── test_excel.py             # Test Excel (NUOVO)
├── utils.py                  # Utilità
├── .env                      # Configurazione ambiente
├── requirements_minimal.txt  # Dipendenze minime
├── paypal_transactions.xlsx  # File Excel generato
├── venv/                     # Ambiente virtuale
└── PROJECT_BACKUP.md         # Questo file
```

## ⏳ PROSSIMI PASSI DA COMPLETARE

### **1. Configurazione PayPal API**
- [ ] Creare app su PayPal Developer (https://developer.paypal.com/)
- [ ] Ottenere Client ID e Client Secret
- [ ] Scegliere ambiente: Sandbox (test) o Live (produzione)
- [ ] Aggiornare file `.env` con credenziali

### **2. Test Integrazione PayPal**
```cmd
python main.py status    # Test connessione
python main.py sync 7    # Sync ultimi 7 giorni
```

### **3. Configurazione Automatica**
```cmd
python main.py schedule  # Sync automatica
```

## 🔑 CONFIGURAZIONE PAYPAL

### **File .env da aggiornare:**
```env
# PayPal API Configuration
PAYPAL_CLIENT_ID=TUO_CLIENT_ID_QUI
PAYPAL_CLIENT_SECRET=TUO_CLIENT_SECRET_QUI
PAYPAL_MODE=sandbox  # o 'live' per produzione

# Excel Configuration
EXCEL_FILE_PATH=paypal_transactions.xlsx
EXCEL_SHEET_NAME=PayPal_Transactions

# Application Settings
CHECK_INTERVAL_HOURS=24
LOG_LEVEL=INFO
```

### **Ambiente Sandbox vs Live:**

**SANDBOX (Consigliato per test):**
- ✅ Sicuro - nessun accesso a transazioni reali
- ✅ Dati di test fittizi
- ✅ Perfetto per verificare funzionamento
- ❌ Non mostra transazioni reali

**LIVE (Produzione):**
- ✅ Accesso transazioni PayPal reali
- ✅ Dati fiscali veri
- ⚠️ Richiede account PayPal Business
- ⚠️ Accede ai dati reali (solo lettura)

## 🛠️ COMANDI UTILI

### **Riattivare Ambiente**
```cmd
subst P: "J:\googleDrive_sync\Portfolio and ongoing studies\Progetti (idee)\Get transaction Data with Paypal"
cd P:\
venv\Scripts\activate.bat
```

### **Test Applicazione**
```cmd
python test_excel.py all      # Test completo Excel
python main.py status         # Status applicazione
python main.py sync 7         # Sync ultimi 7 giorni
python main.py schedule       # Avvia sync automatica
```

### **Analisi Dati**
```cmd
python utils.py analyze       # Analisi transazioni Excel
```

## 🐛 PROBLEMI RISOLTI

### **Problema: Percorsi lunghi Windows**
**Soluzione:** Comando `subst` per creare drive virtuale
```cmd
subst P: "percorso_lungo"
```

### **Problema: Pip corrotto in venv**
**Soluzione:** Ricreare venv con percorso corto tramite subst

### **Problema: Dipendenze pandas**
**Soluzione:** Rimosso pandas, usato solo openpyxl per Excel

## 📊 DATI FISCALI ESTRATTI

L'applicazione estrae questi dati fiscalmente rilevanti:
- Transaction ID (17 caratteri alfanumerici)
- Importi (lordo, netto, commissioni)
- Date e timestamp
- Informazioni pagatore
- Status transazioni
- Valute e paesi
- Codici evento transazione

## 🔄 COME RIPRENDERE IL PROGETTO

1. **Riattivare ambiente:**
   ```cmd
   subst P: "J:\googleDrive_sync\Portfolio and ongoing studies\Progetti (idee)\Get transaction Data with Paypal"
   cd P:\
   venv\Scripts\activate.bat
   ```

2. **Configurare PayPal API** (prossimo passo)

3. **Testare integrazione completa**

## 📞 SUPPORTO

Se hai problemi, i file di log sono in:
- `paypal_transactions.log` - Log applicazione
- Console output per errori immediati

---
**PROGETTO PRONTO PER INTEGRAZIONE PAYPAL API** 🚀
