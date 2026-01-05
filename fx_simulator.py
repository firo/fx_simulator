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

from datetime import datetime
from fx_lib import run_full_analysis
import sys

# =================================================================
# SEZIONE 0: CONTROLLO DELLE DIPENDENZE
# =================================================================
# Prima di eseguire qualsiasi logica, si assicura che le librerie
# fondamentali siano installate nell'ambiente Python.
try:
    import scipy
except ImportError:
    # Se una dipendenza non viene trovata, stampa un messaggio di errore chiaro
    # su stderr e termina l'esecuzione con un codice di errore.
    print("\n[!] ATTENZIONE: Mancano delle dipendenze necessarie (es. scipy).", file=sys.stderr)
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
    print(f"Input non valido. Uso il valore di default: {USD_AMOUNT:,.2f} USD")

# Parametri fissi dell'analisi: tasso applicato e simbolo del cambio.
# In una versione futura, potrebbero diventare anche questi input utente.
FINECO_RATE_USD_EUR = 0.8462 
SYMBOL = "EURUSD=X"

# =================================================================
# SEZIONE 2: ESECUZIONE DELL'ANALISI TRAMITE LIBRERIA
# =================================================================
# Questa è la chiamata al "cervello" del programma.
# Lo script delega tutta la complessità (download dati, calcoli)
# alla funzione `run_full_analysis` nella libreria `fx_lib`.
try:
    # Il risultato è un dizionario, che disaccoppia i dati dalla loro presentazione.
    results = run_full_analysis(USD_AMOUNT, FINECO_RATE_USD_EUR, symbol=SYMBOL)

    # =================================================================
    # SEZIONE 3: OUTPUT E PRESENTAZIONE DEI RISULTATI
    # =================================================================
    # Questa sezione si occupa esclusivamente di mostrare i dati all'utente
    # in un formato leggibile e ben organizzato.
    print("\n" + "="*60)
    print(f"REPORT ANALISI AVANZATA - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("="*60)
    print(f"Capitale: {USD_AMOUNT:,.2f} USD  |  Ottenuti con Fineco: {results['eur_actual']:,.2f} €")
    print(f"Tasso Mercato: {results['mkt_today']:.4f}")
    print("-" * 60)
    
    # Spiegazione del percentile per aiutare l'interpretazione dei risultati.
    print(f"Posizionamento Statistico: {results['stat_percentile']:.1f}° percentile (0=Migliore, 100=Peggiore)")
    print(f"Volatilità a 30gg: {results['volatility']:.4f} (Indice di Rischio/Opportunità)")
    print("-" * 60)
    print(f"ANALISI: {results['commento_dinamico']}")
    print("-" * 60)
    print("Record Storico (per confronto):")
    print(f"  - Miglior cambio 12 mesi ({results['best_day'].strftime('%d/%m/%Y')}): {results['best_eur_historical']:,.2f} €")
    print(f"  - Differenza dal massimo potenziale: -{results['eur_difference_from_max']:,.2f} €")
    print("="*60 + "\n")

except Exception as e:
    # Gestione generica degli errori che potrebbero verificarsi durante l'analisi
    # (es. problemi di connessione, ticker non valido).
    print(f"\nERRORE: Impossibile completare l'analisi.", file=sys.stderr)
    print(f"Dettagli: {e}", file=sys.stderr)
    print(f"Verifica la tua connessione a internet o che il ticker '{SYMBOL}' sia corretto.\n", file=sys.stderr)

