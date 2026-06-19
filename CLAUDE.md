# paypal-transaction-data

> Istruzioni di progetto, versionate. Indice dei satelliti e procedura di ripresa. Le preferenze personali vivono in `CLAUDE.local.md` (ignorato).

## Cos'e questo progetto

Applicazione Python che interroga l'API PayPal e produce un report Excel delle transazioni (vedi `README.md` e gli script `.py`). La configurazione passa da un file `.env` con le credenziali PayPal API.

## Dati sensibili (mai versionati)

Il file `.env` con le credenziali PayPal, i file `.xlsx` con i dati delle transazioni, l'ambiente `venv/` e i binari `.exe` sono gitignored. Il riferimento versionato e `.env.example` con valori placeholder. Allo stato attuale il `.env` contiene solo placeholder, non credenziali reali.

## Sviluppo e identita

git locale, identita personale `alesop95`, alias SSH `github-personal`. Remoto ancora da collegare. Commit e push restano manuali.

## Standard

Allineato a `.claude/PROJECT-SYSTEM.md`: regole, engine skills, catalogo `PACKAGES.md`, schede `context/` scaffold da popolare.
