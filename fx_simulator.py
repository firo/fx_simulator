import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# =================================================================
# 1. INPUT INTERATTIVO
# =================================================================
print("\n--- SIMULATORE CAMBIO EUR/USD (FINECO) ---")
try:
    user_input = input("Inserisci l'importo in USD (es. 125 per 125k$): ")
    val_raw = float(user_input.replace(',', '.'))
    USD_AMOUNT = val_raw * 1000 if val_raw < 1000 else val_raw
except ValueError:
    USD_AMOUNT = 125000.00

SYMBOL = "EURUSD=X"
# Tasso Fineco (USD -> EUR) - Inserisci quello che vedi sul portale
FINECO_RATE_USD_EUR = 0.8462 

# =================================================================
# 2. DOWNLOAD E PULIZIA DATI
# =================================================================
data = yf.download(SYMBOL, period="18mo", interval="1d", progress=False)
data = data.dropna()

def get_scalar(value):
    if hasattr(value, 'item'): return float(value.item())
    if isinstance(value, (pd.Series, np.ndarray)): return float(value.iloc[0])
    return float(value)

latest_close = get_scalar(data['Close'].iloc[-1])
mkt_today = latest_close # Usiamo la chiusura più recente per il benchmark

# =================================================================
# 3. CALCOLO SPREAD E RECOR STORICO
# =================================================================
fineco_equivalent_rate = 1 / FINECO_RATE_USD_EUR
eur_actual = USD_AMOUNT * FINECO_RATE_USD_EUR

one_year_ago = data.index[-1] - pd.DateOffset(years=1)
last_12m = data.loc[data.index >= one_year_ago].copy()

best_mkt_rate = get_scalar(last_12m['Low'].min())
worst_mkt_rate = get_scalar(last_12m['High'].max())
best_day_raw = last_12m['Low'].idxmin()

# Correzione del warning: uso di .iloc[0]
if isinstance(best_day_raw, (pd.Index, pd.Series)):
    best_day = best_day_raw.iloc[0]
else:
    best_day = best_day_raw

# Calcolo differenza rispetto al miglior scenario possibile
spread_points = fineco_equivalent_rate - mkt_today
best_eur_historical = USD_AMOUNT / (best_mkt_rate + spread_points)

# =================================================================
# 4. LOGICA DI COMMENTO DINAMICO
# =================================================================
# Calcoliamo dove si trova il prezzo attuale in una scala da 0 (minimo) a 100 (massimo)
# Per chi vende USD, più il tasso è BASSO, più è vantaggioso.
percentile = ((mkt_today - best_mkt_rate) / (worst_mkt_rate - best_mkt_rate)) * 100

def genera_commento(p):
    if p <= 15:
        return "ECCELLENTE: Il Dollaro è vicino ai massimi dell'anno. È un momento d'oro per convertire."
    elif p <= 40:
        return "BUONO: Il Dollaro è forte rispetto alla media. La conversione è vantaggiosa."
    elif p <= 70:
        return "NEUTRO: Il cambio è a metà strada. Valuta una conversione parziale (DCA)."
    else:
        return "SFAVOREVOLE: L'Euro è molto forte. Se possibile, attendi un ritracciamento."

commento_dinamico = genera_commento(percentile)

# =================================================================
# 5. OUTPUT
# =================================================================
print("\n" + "="*60)
print(f"REPORT CAMBIO DINAMICO - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
print("="*60)
print(f"Capitale: {USD_AMOUNT:,.2f} USD  |  Ottenuti: {eur_actual:,.2f} €")
print(f"Tasso Fineco (USD/EUR): {FINECO_RATE_USD_EUR:.4f} (Mercato: {mkt_today:.4f})")
print(f"Posizionamento cambio:  {percentile:.1f}% (0%=Migliore, 100%=Peggiore)")
print("-" * 60)
print(f"ANALISI: {commento_dinamico}")
print("-" * 60)

print(f"Record 12 mesi ({best_day.strftime('%d/%m/%Y')}): {best_eur_historical:,.2f} €")
print(f"Differenza dal massimo potenziale: -{best_eur_historical - eur_actual:,.2f} €")
print("="*60 + "\n")