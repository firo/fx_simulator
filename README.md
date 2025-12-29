# FX Simulator - USD to EUR (Fineco Logic)

Simulatore avanzato per analizzare la convenienza del cambio valuta da USD a EUR. Il sistema confronta i tassi in tempo reale di Yahoo Finance con lo spread reale applicato dal servizio Multicurrency di Fineco.
Questo è un esempio del risultato sulla base di 10k

```
--- SIMULATORE CAMBIO EUR/USD (FINECO) ---
Inserisci l'importo in USD (es. 100 per 100k$): 10

============================================================
REPORT CAMBIO DINAMICO - 29/12/2025 09:21
============================================================
Capitale: 10,000.00 USD  |  Ottenuti: 8,462.00 €
Tasso Fineco (USD/EUR): 0.8462 (Mercato: 1.1780)
Posizionamento cambio:  94.5% (0%=Migliore, 100%=Peggiore)
------------------------------------------------------------
ANALISI: SFAVOREVOLE: L'Euro è molto forte. Se possibile, attendi un ritracciamento.
------------------------------------------------------------
Record 12 mesi (13/01/2025): 9,783.39 €
Differenza dal massimo potenziale: -1,321.39 €
============================================================
```
## 🚀 Funzionalità
- **Cambio Immediato**: Calcolo netto basato sul tasso USD/EUR inserito manualmente (formato Fineco).
- **Analisi Spread**: Calcolo della commissione implicita (pips) applicata dalla banca rispetto al tasso interbancario.
- **Record Storico**: Individuazione automatica del miglior tasso degli ultimi 12 mesi con calcolo del guadagno mancato.
- **Posizionamento Dinamico**: Calcolo del percentile di convenienza (0-100%) per capire se il Dollaro è forte o debole rispetto alla media storica annuale.
- **Commento**: Suggerimento operativo generato dinamicamente in base alla posizione del prezzo nel range di volatilità.

## 🛠 Setup e Installazione

1. Crea l'ambiente virtuale:
   `python -m venv venv`
   `source venv/bin/activate` (Su Windows: `venv\Scripts\activate`)

2. Installa le dipendenze:
   `pip install yfinance pandas numpy`

3. Esegui lo script:
   `python fx_simulator.py`

## 🧠 Logica di Calcolo

### 1. Il Tasso Fineco (Inverso)
Poiché Fineco esprime il cambio USD->EUR come un moltiplicatore (es. 0.8462), lo script lo inverte per confrontarlo con il tasso standard di mercato EUR/USD:
TassoEquivalent = 1 / TassoFineco

### 2. Analisi del Percentile (Convenienza)
Il "Posizionamento Cambio" indica dove si trova il prezzo attuale in una scala tra il minimo (0%) e il massimo (100%) dell'ultimo anno:
- **Percentile < 20%**: Il Dollaro è vicino ai suoi massimi (Momento ottimo per cambiare).
- **Percentile > 70%**: L'Euro è vicino ai suoi massimi (Momento sfavorevole).

### 3. Spread Bancario
Viene calcolato il delta tra il mercato "Mid-Market" e il tasso applicato per quantificare il costo del servizio (solitamente ~33 pips per Fineco).

## 📊 Struttura Progetto
- fx_simulator.py: Script principale Python.
- requirements.txt: Elenco dipendenze (yfinance, pandas, numpy).
- README.md: Documentazione tecnica e finanziaria.

---

## 🤖 AI Context Prompt (Copia questo per nuove richieste)
Se desideri evolvere questo script chiedendo aiuto a un'IA generativa, incolla il seguente testo come introduzione:

> "Sto lavorando a un simulatore di cambio FX in Python che analizza la conversione USD/EUR. Lo script scarica dati da Yahoo Finance e simula le condizioni di Fineco Multicurrency (usando tassi inversi e spread di circa 33 pips). La logica principale si basa sul calcolo del percentile di convenienza rispetto al range di volatilità annuale. Ho già un setup funzionante con Pandas e YFinance. Ti fornirò il codice e vorrei che tu mi aiutassi a: [INSERISCI QUI LA TUA RICHIESTA]"

---
*Disclaimer: Questo software è a scopo puramente analitico e non costituisce consulenza finanziaria o sollecitazione al risparmio.*
