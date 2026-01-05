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
from datetime import datetime, timedelta
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketDataError(Exception):
    """Eccezione personalizzata per errori nel recupero dati di mercato."""
    pass


class _MarketData:
    """
    Classe interna che implementa il pattern Singleton (Borg/Monostate).
    Tutte le istanze condivideranno lo stesso stato, inclusa la cache dei dati.
    """
    _instance = None
    _data_cache = {}
    _cache_timestamp = {}  # Timestamp per validare la freschezza dei dati

    def __new__(cls):
        """Costruttore che assicura la creazione di una sola istanza."""
        if cls._instance is None:
            cls._instance = super(_MarketData, cls).__new__(cls)
        return cls._instance

    def get_data(self, symbol, period="18mo", interval="1d", force_refresh=False):
        """
        Recupera i dati di mercato per un dato simbolo. 
        
        Args:
            symbol: Simbolo del tasso di cambio (es. "EURUSD=X")
            period: Periodo storico da recuperare
            interval: Intervallo temporale
            force_refresh: Forza il refresh dei dati anche se in cache
            
        Returns:
            DataFrame con i dati di mercato
            
        Raises:
            MarketDataError: Se il download fallisce o i dati sono insufficienti
        """
        cache_key = f"{symbol}-{period}-{interval}"
        
        # Verifica se i dati sono in cache e ancora freschi (max 1 ora)
        if not force_refresh and cache_key in self._data_cache:
            cache_age = datetime.now() - self._cache_timestamp.get(cache_key, datetime.min)
            if cache_age < timedelta(hours=1):
                logger.info(f"Utilizzo dati in cache per {symbol}")
                return self._data_cache[cache_key]
        
        # Download dei dati
        try:
            logger.info(f"Download dati per {symbol}...")
            data = yf.download(symbol, period=period, interval=interval, progress=False)
            
            # Validazione dati
            if data is None or data.empty:
                raise MarketDataError(f"Nessun dato ricevuto per {symbol}")
            
            data = data.dropna()
            
            if len(data) < 50:  # Minimo per calcolare SMA50
                raise MarketDataError(f"Dati insufficienti per {symbol}: solo {len(data)} righe")
            
            # Salva in cache
            self._data_cache[cache_key] = data
            self._cache_timestamp[cache_key] = datetime.now()
            
            logger.info(f"Download completato: {len(data)} righe per {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Errore nel download dati per {symbol}: {str(e)}")
            raise MarketDataError(f"Impossibile scaricare dati per {symbol}: {str(e)}")


# Istanza globale e unica del Singleton
market_data_provider = _MarketData()


def get_scalar(value):
    """
    Funzione di utilità per estrarre un singolo valore float da tipi di dato
    comuni in analisi dati (Pandas Series, Numpy arrays). 
    
    Returns:
        float: Valore scalare estratto
        
    Raises:
        ValueError: Se il valore non può essere convertito
    """
    try:
        if pd.isna(value):
            raise ValueError("Valore NaN non valido")
            
        if hasattr(value, 'item'):
            return float(value.item())
            
        if isinstance(value, (pd.Series, np.ndarray)):
            if isinstance(value, pd.Series) and value.empty:
                raise ValueError("Serie vuota")
            return float(value.iloc[0] if isinstance(value, pd.Series) else value[0])
            
        return float(value)
        
    except (ValueError, TypeError) as e:
        logger.error(f"Errore nella conversione a scalar: {str(e)}")
        raise ValueError(f"Impossibile convertire valore a scalar: {str(e)}")

def _genera_commento(percentile, volatility, mkt_today, sma50, volatility_threshold=0.0075):
    """
    Genera un'analisi dinamica e intelligente basata su percentile, volatilità e trend (SMA50). 
    
    Args:
        percentile: Percentile del tasso attuale rispetto agli ultimi 12 mesi
        volatility: Volatilità a 30 giorni
        mkt_today: Tasso di cambio corrente
        sma50: Media mobile a 50 giorni
        volatility_threshold: Soglia per considerare il mercato volatile
        
    Returns:
        str: Commento descrittivo dello scenario
    """
    # 1. Definizione dello scenario di base basato sul percentile
    # NOTA: Per EUR/USD, percentile basso = USD forte = buono per conversione USD->EUR
    if percentile <= 15:
        scenario = "ECCELLENTE"
        descrizione_base = "Il Dollaro è ai massimi storici rispetto agli ultimi 12 mesi, un'opportunità potenzialmente d'oro."
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
    if volatility > volatility_threshold * 2:
        ctx_volatilita = "Il mercato è molto volatile e rischioso in questo momento."
    elif volatility > volatility_threshold:
        ctx_volatilita = "Il mercato mostra una certa volatilità."
    else:
        ctx_volatilita = "Il mercato è relativamente stabile."

    # 3. Aggiunta del contesto di trend (confronto con SMA50)
    # Per EUR/USD, un prezzo sotto la media indica trend al rialzo dell'USD
    diff_pct = ((mkt_today - sma50) / sma50) * 100
    
    if abs(diff_pct) < 0.5:
        ctx_trend = "Il tasso è allineato con la media di medio termine."
    elif mkt_today < sma50:
        ctx_trend = f"Il trend favorisce il Dollaro (sotto media del {abs(diff_pct):.1f}%)."
    else:
        ctx_trend = f"Il trend favorisce l'Euro (sopra media del {diff_pct:.1f}%)."

    # 4. Composizione del commento finale
    return f"SCENARIO: {scenario}. {descrizione_base} {ctx_volatilita} {ctx_trend}"

def validate_inputs(usd_amount, fineco_rate_usd_eur):
    """
    Valida gli input dell'utente. 
    
    Raises:
        ValueError: Se gli input non sono validi
    """
    if usd_amount <= 0:
        raise ValueError(f"L'importo USD deve essere positivo, ricevuto: {usd_amount}")
    
    if fineco_rate_usd_eur <= 0:
        raise ValueError(f"Il tasso Fineco deve essere positivo, ricevuto: {fineco_rate_usd_eur}")
    
    # Sanity check: EUR/USD tipicamente tra 0.8 e 1.5
    fineco_rate_eurusd = 1 / fineco_rate_usd_eur
    if fineco_rate_eurusd < 0.5 or fineco_rate_eurusd > 2.0:
        logger.warning(f"Tasso Fineco sospetto: EUR/USD = {fineco_rate_eurusd:.4f}")

def run_full_analysis(usd_amount, fineco_rate_usd_eur, symbol="EURUSD=X"):
    """
    Funzione principale che orchestra l'intera analisi del cambio. 
    
    Args:
        usd_amount: Importo in USD da convertire
        fineco_rate_usd_eur: Tasso di conversione USD->EUR offerto da Fineco
        symbol: Simbolo del tasso di cambio (default: "EURUSD=X")
        
    Returns:
        dict: Dizionario con tutti i risultati dell'analisi
        
    Raises:
        ValueError: Se gli input non sono validi
        MarketDataError: Se ci sono problemi con il recupero dei dati
    """
    # 0. Validazione input
    validate_inputs(usd_amount, fineco_rate_usd_eur)
    
    try:
        # 1. Recupero dati tramite il Singleton
        data = market_data_provider.get_data(symbol)
        
        # Verifica che ci siano dati recenti (ultimi 7 giorni)
        last_date = data.index[-1]
        days_old = (datetime.now() - last_date.to_pydatetime()).days
        if days_old > 7:
            logger.warning(f"Dati non recentissimi: ultimo aggiornamento {days_old} giorni fa")
        
        mkt_today = get_scalar(data['Close'].iloc[-1])
        
        # 2. Calcoli di base
        eur_actual = usd_amount * fineco_rate_usd_eur
        
        # Calcolo ultimi 12 mesi con controllo
        one_year_ago = data.index[-1] - pd.DateOffset(years=1)
        last_12m = data.loc[data.index >= one_year_ago].copy()
        
        if len(last_12m) < 200:  # ~200 giorni lavorativi in un anno
            logger.warning(f"Dati 12 mesi incompleti: solo {len(last_12m)} righe")
        
        # 3. Calcolo degli indicatori chiave
        # Percentile statistico (rank method per gestire valori duplicati)
        stat_percentile = percentileofscore(last_12m['Close'], mkt_today, kind='rank')
        stat_percentile = float(stat_percentile)
        
        # Volatilità storica (30 giorni)
        daily_returns = data['Close'].pct_change()
        volatility_series = daily_returns.rolling(window=30).std()
        
        if volatility_series.iloc[-1] is None or pd.isna(volatility_series.iloc[-1]):
            raise ValueError("Impossibile calcolare la volatilità")
        
        volatility = get_scalar(volatility_series.iloc[-1])
        
        # Media Mobile a 50 giorni
        sma50_series = data['Close'].rolling(window=50).mean()
        
        if pd.isna(sma50_series.iloc[-1]):
            raise ValueError("Impossibile calcolare SMA50")
        
        sma50 = get_scalar(sma50_series.iloc[-1])
        
        # 4. Generazione del commento intelligente
        commento_dinamico = _genera_commento(stat_percentile, volatility, mkt_today, sma50)
        
        # 5. Calcoli storici per confronto
        best_mkt_rate = get_scalar(last_12m['Low'].min())
        worst_mkt_rate = get_scalar(last_12m['High'].max())
        
        # Calcolo spread Fineco (differenza tra tasso Fineco e mercato)
        fineco_equivalent_rate = 1 / fineco_rate_usd_eur
        spread_points = fineco_equivalent_rate - mkt_today
        spread_percentage = (spread_points / mkt_today) * 100
        
        # Migliore conversione possibile negli ultimi 12 mesi
        best_eur_historical = usd_amount / (best_mkt_rate + spread_points)
        worst_eur_historical = usd_amount / (worst_mkt_rate + spread_points)
        
        # Giorno del miglior tasso
        best_day = last_12m['Low'].idxmin()
        if isinstance(best_day, pd.Series):
            best_day = best_day.iloc[0]
        
        worst_day = last_12m['High'].idxmax()
        if isinstance(worst_day, pd.Series):
            worst_day = worst_day.iloc[0]
        
        # 6. Restituzione dei risultati
        return {
            # Risultati conversione
            "eur_actual": round(eur_actual, 2),
            "usd_amount": usd_amount,
            
            # Tassi di mercato
            "mkt_today": round(mkt_today, 5),
            "fineco_rate_eurusd": round(fineco_equivalent_rate, 5),
            "spread_points": round(spread_points, 5),
            "spread_percentage": round(spread_percentage, 2),
            
            # Indicatori statistici
            "stat_percentile": round(stat_percentile, 1),
            "volatility": round(volatility, 5),
            "volatility_annualized": round(volatility * np.sqrt(252), 4),  # Volatilità annualizzata
            "sma50": round(sma50, 5),
            
            # Analisi
            "commento_dinamico": commento_dinamico,
            
            # Confronto storico
            "best_mkt_rate_12m": round(best_mkt_rate, 5),
            "worst_mkt_rate_12m": round(worst_mkt_rate, 5),
            "best_eur_historical": round(best_eur_historical, 2),
            "worst_eur_historical": round(worst_eur_historical, 2),
            "eur_difference_from_max": round(best_eur_historical - eur_actual, 2),
            "eur_difference_from_min": round(eur_actual - worst_eur_historical, 2),
            "potential_gain_pct": round(((best_eur_historical - eur_actual) / eur_actual) * 100, 2),
            
            # Date
            "best_day": best_day.strftime("%Y-%m-%d"),
            "worst_day": worst_day.strftime("%Y-%m-%d"),
            "last_update": last_date.strftime("%Y-%m-%d"),
            "data_age_days": days_old,
        }
        
    except MarketDataError:
        raise
    except Exception as e:
        logger.error(f"Errore nell'analisi: {str(e)}")
        raise MarketDataError(f"Errore nell'elaborazione dell'analisi: {str(e)}")


def print_analysis_report(results):
    """
    Stampa un report formattato dei risultati dell'analisi. 
    
    Args:
        results: Dizionario dei risultati da run_full_analysis
    """
    print("\n" + "="*70)
    print("ANALISI CAMBIO USD -> EUR")
    print("="*70)
    
    print(f"\n💰 CONVERSIONE:")
    print(f"   {results['usd_amount']:,.2f} USD → {results['eur_actual']:,.2f} EUR")
    print(f"   Tasso Fineco: {results['fineco_rate_eurusd']:.5f} EUR/USD")
    print(f"   Spread vs mercato: {results['spread_percentage']:.2f}%")
    
    print(f"\n📊 MERCATO:")
    print(f"   Tasso attuale: {results['mkt_today']:.5f} EUR/USD")
    print(f"   Percentile 12M: {results['stat_percentile']:.1f}%")
    print(f"   Volatilità: {results['volatility']:.4f} ({results['volatility_annualized']:.2%} annualizzata)")
    print(f"   SMA 50 giorni: {results['sma50']:.5f}")
    
    print(f"\n📈 CONFRONTO STORICO (ultimi 12 mesi):")
    print(f"   Miglior tasso: {results['best_mkt_rate_12m']:.5f} il {results['best_day']}")
    print(f"   Peggior tasso: {results['worst_mkt_rate_12m']:.5f} il {results['worst_day']}")
    print(f"   Potenziale guadagno vs miglior momento: {results['eur_difference_from_max']:,.2f} EUR ({results['potential_gain_pct']:.1f}%)")
    
    print(f"\n💡 {results['commento_dinamico']}")
    
    print(f"\n📅 Ultimo aggiornamento dati: {results['last_update']} ({results['data_age_days']} giorni fa)")
    print("="*70 + "\n")


# Esempio di utilizzo
if __name__ == "__main__":
    try:
        # Parametri di esempio
        USD_AMOUNT = 10000
        FINECO_RATE = 0.955  # Esempio: 1 USD = 0.955 EUR
        
        results = run_full_analysis(USD_AMOUNT, FINECO_RATE)
        print_analysis_report(results)
        
    except (ValueError, MarketDataError) as e:
        print(f"❌ Errore: {str(e)}")
    except Exception as e:
        print(f"❌ Errore imprevisto: {str(e)}")
        logger.exception("Traceback completo:")
