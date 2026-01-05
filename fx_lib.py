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

def _genera_commento(percentile, volatility, mkt_today, sma50, volatility_threshold=0.0075):
    """
    Genera un'analisi dinamica e intelligente basata su percentile, volatilità e trend (SMA50).
    """
    # 1. Definizione dello scenario di base basato sul percentile
    if percentile <= 15:
        scenario = "ECCELLENTE"
        descrizione_base = "Il Dollaro è ai massimi storici, un'opportunità potenzialmente d'oro."
    elif percentile <= 40:
        scenario = "BUONO"
        descrizione_base = "Il Dollaro è forte rispetto alla media, la conversione è vantaggiosa."
    elif percentile <= 70:
        scenario = "NEUTRO"
        descrizione_base = "Il cambio è in una fase intermedia, senza una chiara convenienza."
    else:
        scenario = "SFAVOREVOLE"
        descrizione_base = "L'Euro è forte, rendendo la conversione tendenzialmente svantaggiosa."

    # 2. Aggiunta del contesto di volatilità
    ctx_volatilita = "Il mercato è stabile."
    if volatility > volatility_threshold:
        ctx_volatilita = "Il mercato è nervoso e imprevedibile."

    # 3. Aggiunta del contesto di trend (confronto con SMA50)
    # Per EUR/USD, un prezzo sotto la media è buono per chi compra EUR.
    trend_favorevole_usd = mkt_today < sma50
    if trend_favorevole_usd:
        ctx_trend = "Il trend di breve termine sembra favorire un ulteriore rafforzamento del Dollaro."
    else:
        ctx_trend = "Il trend di breve termine sta spingendo a favore dell'Euro."

    # 4. Composizione del commento finale
    commento_finale = f"SCENARIO: {scenario}. {descrizione_base} {ctx_volatilita} {ctx_trend}"
    return commento_finale

def run_full_analysis(usd_amount, fineco_rate_usd_eur, symbol="EURUSD=X"):
    """
    Funzione principale che orchestra l'intera analisi del cambio.
    """
    # 1. Recupero dati tramite il Singleton
    data = market_data_provider.get_data(symbol)
    
    mkt_today = get_scalar(data['Close'].iloc[-1])

    # 2. Calcoli di base
    eur_actual = usd_amount * fineco_rate_usd_eur
    one_year_ago = data.index[-1] - pd.DateOffset(years=1)
    last_12m = data.loc[data.index >= one_year_ago].copy()

    # 3. Calcolo degli indicatori chiave
    # Percentile statistico
    stat_percentile = percentileofscore(last_12m['Close'], mkt_today, kind='rank')
    if isinstance(stat_percentile, np.ndarray):
        stat_percentile = stat_percentile[0]

    # Volatilità storica
    daily_returns = data['Close'].pct_change()
    volatility = get_scalar(daily_returns.rolling(window=30).std().iloc[-1])

    # Media Mobile a 50 giorni (Indicatore di Trend)
    sma50 = get_scalar(data['Close'].rolling(window=50).mean().iloc[-1])

    # 4. Generazione del commento intelligente
    commento_dinamico = _genera_commento(stat_percentile, volatility, mkt_today, sma50)

    # 5. Calcoli storici per confronto
    best_mkt_rate = get_scalar(last_12m['Low'].min())
    fineco_equivalent_rate = 1 / fineco_rate_usd_eur
    spread_points = fineco_equivalent_rate - mkt_today
    best_eur_historical = usd_amount / (best_mkt_rate + spread_points)
    best_day = last_12m['Low'].idxmin()
    if isinstance(best_day, pd.Series):
        best_day = best_day.iloc[0]

    # 6. Restituzione dei risultati
    return {
        "eur_actual": eur_actual,
        "mkt_today": mkt_today,
        "stat_percentile": stat_percentile,
        "volatility": volatility,
        "sma50": sma50,
        "commento_dinamico": commento_dinamico,
        "best_eur_historical": best_eur_historical,
        "eur_difference_from_max": best_eur_historical - eur_actual,
        "best_day": best_day,
    }