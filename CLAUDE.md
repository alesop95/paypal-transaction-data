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

Norme caricate su richiesta, una riga per situazione con le parole con cui si presenta, così che il caricamento non dipenda dal ricordare che la norma esista.

- `git worktree list` mostra più di un albero, se ne crea o se ne rimuove uno, si deve decidere da dove leggere la memoria versionata: skill `alberi-di-lavoro`.
- Un recupero web fallisce con 403 o con una pagina di verifica anti-bot, la fonte sta su Reddit o su Discord, serve la trascrizione di un video, si sta per annotare una fonte non letta: skill `fonti-non-recuperabili`.
- Si scrive o si valuta una prova automatica, si chiude un difetto, una verifica manuale smentisce una suite verde, si sta per dichiarare completo un intervento il cui scopo era un effetto misurabile: skill `prove-che-misurano`.
- Si inizializza o si allinea il progetto, oppure cambia il modo in cui si prova e si rilascia, e va deciso come separare test e produzione: skill `separazione-ambienti`.
