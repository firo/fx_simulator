# -*- coding: utf-8 -*-
"""
Libreria per l'analisi avanzata del tasso di cambio (es. EUR/USD).

Questa libreria fornisce funzionalità per scaricare dati di mercato, calcolare
indicatori statistici come percentile e volatilità, e restituire un'analisi
completa per supportare decisioni di conversione di valuta.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import percentileofscore

# Design Pattern: Singleton per la gestione dei dati di mercato.
# L'obiettivo è creare un'unica istanza che gestisca il download e la cache dei dati.
# Questo previene download multipli degli stessi dati (costosi in termini di tempo e rete)
# e assicura che diverse parti del programma accedano agli stessi dati (coerenza).
class _MarketData:
    """
    Classe interna che implementa il pattern Singleton (Borg/Monostate).
    Tutte le istanze condivideranno lo stesso stato, inclusa la cache dei dati.
    """
    _instance = None
    _data_cache = {}  # Cache condivisa da tutte le istanze

    def __new__(cls):
        """Costruttore che assicura la creazione di una sola istanza."""
        if cls._instance is None:
            # Se l'istanza non esiste, la crea...
            cls._instance = super(_MarketData, cls).__new__(cls)
        # ...altrimenti, restituisce l'istanza esistente.
        return cls._instance

    def get_data(self, symbol, period="18mo", interval="1d"):
        """
        Recupera i dati di mercato per un dato simbolo.
        Se i dati sono in cache, li restituisce. Altrimenti, li scarica e li mette in cache.
        """
        cache_key = f"{symbol}-{period}-{interval}"
        if cache_key not in self._data_cache:
            print(f"Dati per {symbol} non in cache. Download in corso...")
            data = yf.download(symbol, period=period, interval=interval, progress=False)
            self._data_cache[cache_key] = data.dropna()
        return self._data_cache[cache_key]

# Istanza globale e unica del Singleton. Questo è l'oggetto che verrà usato
# dal resto del programma per accedere ai dati.
market_data_provider = _MarketData()


def get_scalar(value):
    """
    Funzione di utilità per estrarre un singolo valore float da tipi di dato
    comuni in analisi dati (Pandas Series, Numpy arrays).
    """
    if hasattr(value, 'item'):
        return float(value.item())
    if isinstance(value, (pd.Series, np.ndarray)):
        # Estrae il primo elemento se è una serie/array, gestendo il caso di serie vuota.
        return float(value.iloc[0]) if not value.empty else np.nan
    return float(value)

def _genera_commento(percentile, volatility, volatility_threshold=0.0075):
    """
    Genera un commento qualitativo basato sulla posizione percentile del tasso di cambio
    e sul livello di volatilità del mercato.
    """
    base_comment = ""
    # Per EUR/USD, un tasso più basso è favorevole per chi converte USD in EUR.
    # Quindi, un percentile basso (tasso vicino ai minimi) è un segnale positivo.
    if percentile <= 15:
        base_comment = "ECCELLENTE: Il Dollaro è ai massimi storici. Momento d'oro per convertire."
    elif percentile <= 40:
        base_comment = "BUONO: Il Dollaro è forte. La conversione è vantaggiosa."
    elif percentile <= 70:
        base_comment = "NEUTRO: Il cambio è in una fase intermedia. Considera una conversione parziale."
    else:
        base_comment = "SFAVOREVOLE: L'Euro è molto forte. Se possibile, attendi un ritracciamento."

    volatility_comment = ""
    # Se la volatilità supera una soglia, aggiunge un avvertimento.
    if volatility > volatility_threshold:
        volatility_comment = " Attenzione: la volatilità del mercato è alta."

    return base_comment + volatility_comment

def run_full_analysis(usd_amount, fineco_rate_usd_eur, symbol="EURUSD=X"):
    """
    Funzione principale che orchestra l'intera analisi del cambio.

    Args:
        usd_amount (float): L'importo in USD da convertire.
        fineco_rate_usd_eur (float): Il tasso di cambio applicato (da USD a EUR).
        symbol (str): Il ticker del cambio da analizzare (default: "EURUSD=X").

    Returns:
        dict: Un dizionario contenente tutti i risultati dell'analisi.
    """
    # 1. Recupero dati tramite il Singleton: efficiente e centralizzato.
    data = market_data_provider.get_data(symbol)
    
    mkt_today = get_scalar(data['Close'].iloc[-1])

    # 2. Calcoli di base: conversione e definizione del periodo di analisi (ultimi 12 mesi).
    eur_actual = usd_amount * fineco_rate_usd_eur
    one_year_ago = data.index[-1] - pd.DateOffset(years=1)
    last_12m = data.loc[data.index >= one_year_ago].copy()

    # 3. Calcolo del Percentile Statistico (Proposta 2):
    #    Misura la posizione del tasso odierno rispetto a tutti i tassi dell'ultimo anno.
    #    'kind=rank' gestisce i pareggi. Un valore basso (es. 10) significa che
    #    il tasso di oggi è più basso (migliore) del 90% dei tassi dell'ultimo anno.
    stat_percentile = percentileofscore(last_12m['Close'], mkt_today, kind='rank')
    if isinstance(stat_percentile, np.ndarray):
        stat_percentile = stat_percentile[0]

    # 4. Calcolo della Volatilità Storica (Proposta 3):
    #    Misura la deviazione standard dei rendimenti giornalieri su una finestra mobile (30gg).
    #    Un valore alto indica che il prezzo sta subendo forti oscillazioni (maggior rischio/opportunità).
    daily_returns = data['Close'].pct_change()
    volatility = get_scalar(daily_returns.rolling(window=30).std().iloc[-1])

    # 5. Generazione del commento dinamico basato sui nuovi indicatori.
    commento_dinamico = _genera_commento(stat_percentile, volatility)

    # 6. Calcoli storici per fornire un contesto di confronto.
    best_mkt_rate = get_scalar(last_12m['Low'].min())
    fineco_equivalent_rate = 1 / fineco_rate_usd_eur
    spread_points = fineco_equivalent_rate - mkt_today
    best_eur_historical = usd_amount / (best_mkt_rate + spread_points)
    best_day = last_12m['Low'].idxmin()
    if isinstance(best_day, pd.Series):
        best_day = best_day.iloc[0]

    # 7. Restituzione di un dizionario strutturato con tutti i dati calcolati.
    #    Questo disaccoppia la logica di calcolo dalla logica di presentazione.
    return {
        "eur_actual": eur_actual,                 # Importo in EUR ottenuto con il tasso applicato.
        "mkt_today": mkt_today,                   # Tasso di mercato odierno.
        "stat_percentile": stat_percentile,       # Percentile statistico (0-100, basso è meglio).
        "volatility": volatility,                 # Volatilità a 30 giorni.
        "commento_dinamico": commento_dinamico,   # Analisi qualitativa testuale.
        "best_eur_historical": best_eur_historical, # Miglior importo ottenibile nell'anno.
        "eur_difference_from_max": best_eur_historical - eur_actual, # Delta dal massimo potenziale.
        "best_day": best_day,                     # Giorno in cui si è verificato il tasso migliore.
    }