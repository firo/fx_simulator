# -*- coding: utf-8 -*-
"""
Sistema di Raccomandazione per Conversione USD->EUR
Approccio pragmatico basato su indicatori tecnici multipli
SENZA modelli predittivi complessi (che non funzionano bene sul Forex)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import percentileofscore
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(name)s: %(message)s')
logger = logging.getLogger(__name__)


class FXRecommendationSystem:
    """
    Sistema di raccomandazione basato su indicatori tecnici multipli.
    Non cerca di predire il futuro, ma valuta se il momento attuale
    è statisticamente favorevole rispetto al passato.
    """
    
    def __init__(self, symbol="EURUSD=X"):
        self.symbol = symbol
        self.data = None
        self.indicators = {}
        
    def fetch_data(self, period="2y"):
        """Scarica dati storici."""
        try:
            self.data = yf.download(self.symbol, period=period, interval="1d", progress=False)
            self.data = self.data.dropna()
            logger.info(f"Scaricati {len(self.data)} giorni di dati per {self.symbol}")
            return True
        except Exception as e:
            logger.error(f"Errore download: {e}")
            return False
    
    def calculate_technical_indicators(self):
        """Calcola indicatori tecnici standard."""
        if self.data is None or self.data.empty:
            raise ValueError("Dati non disponibili")
        
        # Fix: assicurati che close sia una Series 1D
        close = self.data['Close']
        if isinstance(close, pd.DataFrame):
            close = close.squeeze()  # Converte DataFrame a Series
        
        # 1. TREND - Medie Mobili
        self.indicators['sma_20'] = close.rolling(window=20).mean()
        self.indicators['sma_50'] = close.rolling(window=50).mean()
        self.indicators['sma_200'] = close.rolling(window=200).mean()
        
        # 2. MOMENTUM - RSI (Relative Strength Index)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        
        # Evita divisione per zero
        rs = gain / loss.replace(0, np.nan)
        self.indicators['rsi'] = 100 - (100 / (1 + rs))
        
        # 3. VOLATILITÀ - Bollinger Bands
        self.indicators['bb_middle'] = close.rolling(window=20).mean()
        bb_std = close.rolling(window=20).std()
        self.indicators['bb_upper'] = self.indicators['bb_middle'] + (2 * bb_std)
        self.indicators['bb_lower'] = self.indicators['bb_middle'] - (2 * bb_std)
        
        # 4. VOLATILITÀ - ATR (Average True Range)
        high = self.data['High']
        low = self.data['Low']
        
        # Fix: assicurati che siano Series 1D
        if isinstance(high, pd.DataFrame):
            high = high.squeeze()
        if isinstance(low, pd.DataFrame):
            low = low.squeeze()
            
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        self.indicators['atr'] = tr.rolling(window=14).mean()
        
        # 5. VOLUME WEIGHTED
        volume = self.data['Volume']
        if isinstance(volume, pd.DataFrame):
            volume = volume.squeeze()
            
        self.indicators['vwap'] = (close * volume).cumsum() / volume.cumsum()
        
        return self.indicators
    
    def get_current_signal(self):
        """
        Genera segnali basati su indicatori tecnici.
        Ritorna uno score da 0 (pessimo) a 100 (ottimo) per conversione USD->EUR.
        """
        if self.data is None or not self.indicators:
            raise ValueError("Calcola prima gli indicatori")
        
        current_price = self.data['Close'].iloc[-1]
        if isinstance(current_price, pd.Series):
            current_price = current_price.iloc[0]
        current_price = float(current_price)
        
        signals = {}
        
        # SEGNALE 1: Posizione rispetto alle medie mobili (40 punti max)
        # Per EUR/USD, prezzo BASSO = USD forte = buono per USD->EUR
        sma20 = float(self.indicators['sma_20'].iloc[-1])
        sma50 = float(self.indicators['sma_50'].iloc[-1])
        sma200 = float(self.indicators['sma_200'].iloc[-1])
        
        trend_score = 0
        if current_price < sma20:
            trend_score += 10  # Sotto SMA20 = molto buono
        if current_price < sma50:
            trend_score += 15  # Sotto SMA50 = buono
        if current_price < sma200:
            trend_score += 15  # Sotto SMA200 = trend lungo favorevole
        
        signals['trend_score'] = trend_score
        signals['trend_detail'] = {
            'current': current_price,
            'sma20': sma20,
            'sma50': sma50,
            'sma200': sma200,
        }
        
        # SEGNALE 2: RSI - Ipervenduto favorisce USD (30 punti max)
        rsi = float(self.indicators['rsi'].iloc[-1])
        if rsi < 30:
            rsi_score = 30  # Molto ipervenduto = ottimo
        elif rsi < 40:
            rsi_score = 20  # Ipervenduto = buono
        elif rsi < 50:
            rsi_score = 10  # Leggermente debole = ok
        elif rsi > 70:
            rsi_score = 0   # Ipercomprato = pessimo
        else:
            rsi_score = 5   # Neutro
        
        signals['rsi_score'] = rsi_score
        signals['rsi_value'] = rsi
        
        # SEGNALE 3: Bollinger Bands (20 punti max)
        bb_upper = float(self.indicators['bb_upper'].iloc[-1])
        bb_lower = float(self.indicators['bb_lower'].iloc[-1])
        bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
        
        if bb_position < 0.2:
            bb_score = 20  # Vicino a banda inferiore = ottimo
        elif bb_position < 0.4:
            bb_score = 10  # Sotto media = buono
        elif bb_position > 0.8:
            bb_score = 0   # Vicino a banda superiore = pessimo
        else:
            bb_score = 5   # Neutro
        
        signals['bb_score'] = bb_score
        signals['bb_position'] = bb_position
        
        # SEGNALE 4: Percentile storico 12 mesi (10 punti)
        last_12m_data = self.data['Close'].iloc[-252:]
        if isinstance(last_12m_data, pd.DataFrame):
            last_12m_data = last_12m_data.squeeze()
        
        # Rimuovi NaN prima del calcolo percentile
        last_12m_clean = last_12m_data.dropna()
        percentile = percentileofscore(last_12m_clean, current_price, kind='rank')
        
        if percentile <= 20:
            perc_score = 10
        elif percentile <= 40:
            perc_score = 7
        elif percentile <= 60:
            perc_score = 3
        else:
            perc_score = 0
        
        signals['percentile_score'] = perc_score
        signals['percentile_value'] = float(percentile)
        
        # SCORE TOTALE
        total_score = (
            signals['trend_score'] + 
            signals['rsi_score'] + 
            signals['bb_score'] + 
            signals['percentile_score']
        )
        
        return total_score, signals
    
    def get_recommendation(self, usd_amount, fineco_rate_usd_eur):
        """
        Genera una raccomandazione completa.
        """
        if self.data is None:
            self.fetch_data()
        
        if not self.indicators:
            self.calculate_technical_indicators()
        
        score, signals = self.get_current_signal()
        
        # Conversione attuale
        eur_amount = usd_amount * fineco_rate_usd_eur
        current_market_rate = self.data['Close'].iloc[-1]
        if isinstance(current_market_rate, pd.Series):
            current_market_rate = current_market_rate.iloc[0]
        current_market_rate = float(current_market_rate)
        
        # Calcolo spread Fineco
        fineco_market_rate = 1 / fineco_rate_usd_eur
        spread_pct = ((fineco_market_rate - current_market_rate) / current_market_rate) * 100
        
        # Range storico 12 mesi
        last_12m_data = self.data['Close'].iloc[-252:]
        if isinstance(last_12m_data, pd.DataFrame):
            last_12m_data = last_12m_data.squeeze()
        
        best_rate = float(last_12m_data.min())
        worst_rate = float(last_12m_data.max())
        
        # Posizione attuale nel range
        range_position = (current_market_rate - best_rate) / (worst_rate - best_rate)
        
        # Genera raccomandazione testuale
        if score >= 70:
            action = "🟢 OTTIMO MOMENTO"
            message = "Tutti gli indicatori tecnici sono favorevoli. È un momento statisticamente vantaggioso per convertire."
        elif score >= 50:
            action = "🟡 BUON MOMENTO"
            message = "La maggior parte degli indicatori è favorevole. Momento sopra la media per convertire."
        elif score >= 30:
            action = "🟠 MOMENTO NEUTRO"
            message = "Gli indicatori sono misti. Potresti aspettare un momento migliore, ma non è critico."
        else:
            action = "🔴 MOMENTO SFAVOREVOLE"
            message = "Gli indicatori suggeriscono di aspettare. Il dollaro è relativamente debole."
        
        # Aggiungi dettagli specifici
        details = []
        if signals['trend_score'] >= 30:
            details.append("✓ Trend favorevole (prezzo sotto medie mobili)")
        elif signals['trend_score'] < 10:
            details.append("✗ Trend sfavorevole (prezzo sopra medie mobili)")
        
        if signals['rsi_value'] < 40:
            details.append("✓ RSI indica ipervenduto (USD forte)")
        elif signals['rsi_value'] > 60:
            details.append("✗ RSI indica ipercomprato (USD debole)")
        
        if signals['bb_position'] < 0.3:
            details.append("✓ Prezzo vicino a banda di Bollinger inferiore")
        elif signals['bb_position'] > 0.7:
            details.append("✗ Prezzo vicino a banda di Bollinger superiore")
        
        if signals['percentile_value'] < 30:
            details.append(f"✓ Nel {signals['percentile_value']:.1f}° percentile degli ultimi 12 mesi")
        elif signals['percentile_value'] > 70:
            details.append(f"✗ Nel {signals['percentile_value']:.1f}° percentile degli ultimi 12 mesi")
        
        return {
            'score': score,
            'action': action,
            'message': message,
            'details': details,
            'conversion': {
                'usd_amount': usd_amount,
                'eur_amount': round(eur_amount, 2),
                'fineco_rate': fineco_rate_usd_eur,
            },
            'market': {
                'current_rate': round(current_market_rate, 5),
                'spread_pct': round(spread_pct, 2),
                'best_12m': round(best_rate, 5),
                'worst_12m': round(worst_rate, 5),
                'range_position_pct': round(range_position * 100, 1),
            },
            'signals': signals,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }


def print_recommendation_report(rec):
    """Stampa un report leggibile."""
    print("\n" + "="*70)
    print("RACCOMANDAZIONE CONVERSIONE USD → EUR")
    print("="*70)
    
    print(f"\n{rec['action']} (Score: {rec['score']}/100)")
    print(f"{rec['message']}")
    
    print(f"\n💰 CONVERSIONE:")
    print(f"   {rec['conversion']['usd_amount']:,.2f} USD → {rec['conversion']['eur_amount']:,.2f} EUR")
    print(f"   Tasso Fineco: 1 USD = {rec['conversion']['fineco_rate']:.4f} EUR")
    
    print(f"\n📊 MERCATO:")
    print(f"   Tasso corrente: {rec['market']['current_rate']:.5f} EUR/USD")
    print(f"   Spread Fineco: {rec['market']['spread_pct']:.2f}%")
    print(f"   Range 12 mesi: {rec['market']['best_12m']:.5f} - {rec['market']['worst_12m']:.5f}")
    print(f"   Posizione nel range: {rec['market']['range_position_pct']:.1f}%")
    
    print(f"\n📈 ANALISI TECNICA:")
    for detail in rec['details']:
        print(f"   {detail}")
    
    print(f"\n🔍 INDICATORI DETTAGLIATI:")
    print(f"   • Trend (medie mobili): {rec['signals']['trend_score']}/40 punti")
    print(f"   • RSI: {rec['signals']['rsi_value']:.1f} → {rec['signals']['rsi_score']}/30 punti")
    print(f"   • Bollinger: posizione {rec['signals']['bb_position']:.2f} → {rec['signals']['bb_score']}/20 punti")
    print(f"   • Percentile 12M: {rec['signals']['percentile_value']:.1f}% → {rec['signals']['percentile_score']}/10 punti")
    
    print(f"\n⏰ Analisi aggiornata al: {rec['timestamp']}")
    print("="*70 + "\n")


# ESEMPIO DI UTILIZZO
if __name__ == "__main__":
    # Inizializza il sistema
    fx_system = FXRecommendationSystem()
    
    # Parametri
    USD_AMOUNT = 10000
    FINECO_RATE = 0.955  # Esempio: 1 USD = 0.955 EUR
    
    try:
        # Genera raccomandazione
        recommendation = fx_system.get_recommendation(USD_AMOUNT, FINECO_RATE)
        
        # Stampa report
        print_recommendation_report(recommendation)
        
    except Exception as e:
        logger.error(f"Errore: {e}")
        print(f"❌ Errore: {e}")