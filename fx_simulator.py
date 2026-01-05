# -*- coding: utf-8 -*-
"""
Punto di ingresso principale per il Simulatore Avanzato di Cambio.

Questo script funge da interfaccia utente a riga di comando (CLI).
Le sue responsabilità sono:
1. Verificare la presenza delle dipendenze necessarie.
2. Raccogliere l'input dell'utente (importo da convertire).
3. Invocare la libreria `fx_lib` per eseguire l'analisi complessa.
4. Formattare e presentare i risultati all'utente in modo chiaro.
"""

import sys
from fx_lib import run_full_analysis, print_analysis_report, MarketDataError

# =================================================================
# SEZIONE 0: CONTROLLO DELLE DIPENDENZE
# =================================================================
# Prima di eseguire qualsiasi logica, si assicura che le librerie
# fondamentali siano installate nell'ambiente Python.
try:
    import scipy
    import pandas # Aggiunto per un controllo più esplicito, dato l'uso estensivo
    import yfinance # Aggiunto per un controllo più esplicito
except ImportError as ie:
    # Se una dipendenza non viene trovata, stampa un messaggio di errore chiaro
    # su stderr e termina l'esecuzione con un codice di errore.
    print(f"\n[!] ATTENZIONE: Mancano delle dipendenze necessarie ({ie.name}).", file=sys.stderr)
    print("    Per favore, esegui questo comando nel tuo terminale:", file=sys.stderr)
    print("    pip install -r requirements.txt\n", file=sys.stderr)
    sys.exit(1)


# =================================================================
# SEZIONE 1: INPUT INTERATTIVO DELL'UTENTE
# =================================================================
# Qui vengono definiti e raccolti i parametri per l'analisi.
print("\n--- SIMULATORE AVANZATO CAMBIO EUR/USD (FINECO) ---")
try:
    # Richiede all'utente l'importo e lo converte in un numero.
    # Gestisce input con la virgola e abbreviazioni (es. 100 per 100,000).
    user_input = input("Inserisci l'importo in USD (es. 100 per 100k$): ")
    val_raw = float(user_input.replace(',', '.'))
    USD_AMOUNT = val_raw * 1000 if val_raw < 1000 else val_raw
except ValueError:
    # Se l'input non è valido, usa un valore di default per continuare.
    USD_AMOUNT = 125000.00
    print(f"Input non valido o mancante. Uso il valore di default: {USD_AMOUNT:,.2f} USD")

# Parametri fissi dell'analisi: tasso applicato e simbolo del cambio.
# In una versione futura, potrebbero diventare anche questi input utente.
FINECO_RATE_USD_EUR = 0.8462 
SYMBOL = "EURUSD=X"

# =================================================================
# SEZIONE 2: ESECUZIONE DELL'ANALISI TRAMITE LIBRERIA E REPORT
# =================================================================
# Questa è la chiamata al "cervello" del programma.
# Lo script delega tutta la complessità (download dati, calcoli)
# alla funzione `run_full_analysis` nella libreria `fx_lib`.
try:
    results = run_full_analysis(USD_AMOUNT, FINECO_RATE_USD_EUR, symbol=SYMBOL)
    print_analysis_report(results) # Usa la nuova funzione di stampa

except (ValueError, MarketDataError) as e:
    # Gestione degli errori specifici sollevati da validate_inputs o da MarketDataError
    print(f"\n❌ ERRORE nell'analisi: {e}", file=sys.stderr)
    print("Verifica i tuoi input o la connessione a internet.", file=sys.stderr)
except Exception as e:
    # Gestione generica per altri errori imprevisti
    print(f"\n❌ ERRORE imprevisto: {e}", file=sys.stderr)
    print("Si è verificato un problema inatteso. Contatta il supporto.", file=sys.stderr)



