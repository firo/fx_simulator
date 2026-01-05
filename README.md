# Sistema di Raccomandazione per Conversione USD → EUR

Questo sistema fornisce raccomandazioni pragmatiche per la conversione di USD in EUR, basandosi su un'analisi multi-fattore di indicatori tecnici. L'obiettivo non è predire il futuro del mercato Forex (notoriamente difficile), ma valutare se il momento attuale è statisticamente favorevole per una conversione rispetto al comportamento storico.

## ✨ Funzionalità Principali

Il sistema integra diversi indicatori tecnici per generare un **punteggio complessivo (0-100)** e una raccomandazione chiara:

-   **Analisi del Trend (Medie Mobili)**: Valuta la posizione del prezzo corrente rispetto alle SMA 20, 50 e 200 giorni per identificare la direzione del trend di breve, medio e lungo termine.
-   **Analisi del Momentum (RSI)**: Utilizza l'Indicatore di Forza Relativa (RSI) per determinare se il Dollaro è ipervenduto (buono per chi vende USD) o ipercomprato (sfavorevole).
-   **Analisi della Volatilità (Bande di Bollinger)**: Posiziona il prezzo corrente all'interno delle Bande di Bollinger, indicando se si trova vicino ai minimi (potenziale acquisto di EUR a buon prezzo) o ai massimi (potenziale vendita di EUR a prezzo alto).
-   **Contesto Storico (Percentile)**: Calcola la posizione del tasso odierno rispetto a tutti i tassi degli ultimi 12 mesi, fornendo un contesto di convenienza storica.
-   **Scoring Multi-Indicatore**: Combina i segnali di tutti gli indicatori in un unico score (0-100), dove un punteggio più alto indica un momento più favorevole per convertire USD in EUR.
-   **Raccomandazione Testuale Dettagliata**: Genera una raccomandazione chiara ("OTTIMO MOMENTO", "BUON MOMENTO", ecc.) con un messaggio esplicativo e dettagli specifici basati sui contributi di ciascun indicatore.
-   **Gestione Errori Robusta**: Include eccezioni personalizzate (`MarketDataError`) e logging per una maggiore stabilità e trasparenza in caso di problemi (connessione, dati).
-   **Cache Dati Intelligente**: Scarica e mantiene in cache i dati di mercato per un'ora, riducendo i tempi di attesa per analisi consecutive.

## 🛠️ Installazione e Utilizzo

Per eseguire il sistema di raccomandazione, sono necessari Python 3 e Git.

1.  **Clona il Repository**
    ```bash
    git clone <URL_DEL_TUO_REPOSITORY>
    cd fx_simulator
    ```

2.  **Crea un Ambiente Virtuale** (Consigliato)
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Su Windows: venv\Scripts\activate
    ```

3.  **Installa le Dipendenze**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Esegui lo Script**
    ```bash
    python fx_simulator.py
    ```
    Lo script ti chiederà l'importo in USD e il tasso di cambio Fineco (USD -> EUR).

## 📊 Interpretare il Report di Raccomandazione

Dopo l'esecuzione, il sistema stamperà un report dettagliato con la raccomandazione:

```
======================================================================
RACCOMANDAZIONE CONVERSIONE USD → EUR
======================================================================

🟢 OTTIMO MOMENTO (Score: 70/100)
Tutti gli indicatori tecnici sono favorevoli. È un momento statisticamente vantaggioso per convertire.

💰 CONVERSIONE:
   10,000.00 USD → 9,550.00 EUR
   Tasso Fineco: 1 USD = 0.9550 EUR

📊 MERCATO:
   Tasso corrente: 1.05000 EUR/USD
   Spread Fineco: -0.48%
   Range 12 mesi: 1.04000 - 1.15000
   Posizione nel range: 9.1%

📈 ANALISI TECNICA:
   ✓ Trend favorevole (prezzo sotto medie mobili)
   ✓ RSI indica ipervenduto (USD forte)
   ✓ Prezzo vicino a banda di Bollinger inferiore
   ✓ Nel 15.0° percentile degli ultimi 12 mesi

🔍 INDICATORI DETTAGLIATI:
   • Trend (medie mobili): 40/40 punti
   • RSI: 25.0 → 30/30 punti
   • Bollinger: posizione 0.10 → 20/20 punti
   • Percentile 12M: 15.0% → 10/10 punti

⏰ Analisi aggiornata al: 2026-01-05 12:00:00
======================================================================
```

-   **Azione e Score**: Indica la raccomandazione complessiva (es. "OTTIMO MOMENTO") e il punteggio da 0 (peggiore) a 100 (migliore).
-   **Spread Fineco**: La differenza percentuale tra il tasso Fineco e il tasso di mercato corrente.
-   **Range 12 mesi**: Il range dei tassi (EUR/USD) osservati nell'ultimo anno.
-   **Posizione nel range**: Dove si colloca il tasso corrente all'interno di questo range (0% = minimo, 100% = massimo).
-   **Analisi Tecnica Dettagliata**: Mostra un elenco puntato dei segnali specifici che contribuiscono alla raccomandazione finale.
-   **Indicatori Dettagliati**: Fornisce i valori numerici e i punteggi individuali per ciascun indicatore (Trend, RSI, Bollinger, Percentile).

---

*Disclaimer: Questo software è a scopo puramente analitico e didattico. Non costituisce consulenza finanziaria e non deve essere utilizzato come unica base per decisioni di investimento. I mercati finanziari sono volatili e comportano rischi.*