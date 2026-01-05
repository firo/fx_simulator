# Simulatore di Cambio FX Avanzato

Questo è un simulatore a riga di comando (CLI) per analizzare la convenienza di un'operazione di cambio valuta, con un focus sul cambio da USD a EUR.

Lo strumento va oltre un semplice calcolo di conversione, fornendo indicatori statistici avanzati e un'analisi contestualizzata per aiutare l'utente a prendere decisioni informate. Utilizza dati storici da Yahoo Finance per valutare se il tasso di cambio odierno è favorevole rispetto all'andamento dell'ultimo anno.

## ✨ Funzionalità Principali

- **Analisi Multi-fattore**: Il commento dinamico non si basa solo sul prezzo, ma combina tre fattori chiave:
    1.  **Posizionamento Storico**: Un percentile statistico calcola la convenienza del tasso odierno rispetto a tutti i giorni dell'ultimo anno.
    2.  **Rischio di Mercato**: La volatilità a 30 giorni (giornaliera e annualizzata) misura il livello di incertezza e rischio.
    3.  **Trend di Breve Termine**: Il confronto con la media mobile a 50 giorni (SMA50) indica la direzione attuale del mercato.
- **Metriche Dettagliate**: Calcola e mostra metriche utili come lo spread percentuale pagato all'intermediario, la volatilità annualizzata, e il potenziale guadagno/perdita rispetto ai momenti migliori e peggiori dell'anno.
- **Gestione Errori Robusta**: Implementa eccezioni personalizzate (`MarketDataError`) e blocchi `try-except` per gestire elegantemente problemi di connessione, dati mancanti o input non validi.
- **Cache Dati Intelligente**: Utilizza un pattern Singleton con cache temporizzata. I dati di mercato vengono conservati per un'ora, evitando download ripetuti e velocizzando le analisi successive.
- **Validazione Automatica**: Controlla la validità degli input utente e la qualità dei dati scaricati (es. numero minimo di righe, freschezza dei dati).
- **Architettura Modulare**: La logica di business è isolata in una libreria riutilizzabile (`fx_lib.py`), separata dall'interfaccia utente (`fx_simulator.py`).

## 🛠️ Installazione e Utilizzo

Per eseguire il simulatore, sono necessari Python 3 e Git.

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
    Lo script ti chiederà di inserire l'importo in USD che desideri convertire.

## 📊 Interpretare l'Output

Dopo l'esecuzione, lo script stamperà un report dettagliato:

```
======================================================================
ANALISI CAMBIO USD -> EUR
======================================================================

💰 CONVERSIONE:
   112,000.00 USD → 94,774.40 EUR
   Tasso Fineco: 1.18371 EUR/USD
   Spread vs mercato: 1.31%

📊 MERCATO:
   Tasso attuale: 1.16840 EUR/USD
   Percentile 12M: 0.4%
   Volatilità: 0.0025 (3.97% annualizzata)
   SMA 50 giorni: 1.16370

📈 CONFRONTO STORICO (ultimi 12 mesi):
   Miglior tasso: 1.07000 il 2025-01-13
   Peggior tasso: 1.18130 il 2025-12-15
   Potenziale guadagno vs miglior momento: -13,776.43 EUR (-12.7%)

💡 SCENARIO: ECCELLENTE. Il Dollaro è ai massimi storici rispetto agli ultimi 12 mesi, un'opportunità potenzialmente d'oro. Il mercato è relativamente stabile. Il trend favorisce l'Euro (sopra media del 0.4%).

📅 Ultimo aggiornamento dati: 2026-01-05 (0 giorni fa)
======================================================================
```

- **Spread vs mercato**: Il costo implicito della tua operazione di cambio. Un valore basso è migliore.
- **Percentile 12M**: **L'indicatore più importante.** Un valore basso (es. < 15%) significa che il tasso di oggi è tra i più favorevoli di tutto l'anno.
- **Volatilità annualizzata**: Misura il "nervosismo" del mercato. Valori alti (es. > 10%) indicano maggiore incertezza.
- **SMA 50 giorni**: La media dei prezzi degli ultimi 50 giorni. Se il tasso attuale è sopra questa media, il trend di breve termine favorisce l'Euro; se è sotto, favorisce il Dollaro.
- **💡 SCENARIO**: Il riassunto intelligente che combina tutti i fattori in un'analisi di facile comprensione.

---

*Disclaimer: Questo software è sviluppato a scopo didattico e analitico. Non deve essere considerato come consulenza finanziaria.*