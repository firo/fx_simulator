# Simulatore di Cambio FX Avanzato

Questo è un simulatore a riga di comando (CLI) per analizzare la convenienza di un'operazione di cambio valuta, con un focus sul cambio da USD a EUR.

Lo strumento va oltre un semplice calcolo di conversione, fornendo indicatori statistici avanzati per aiutare l'utente a comprendere il contesto di mercato attuale. Utilizza dati storici da Yahoo Finance per valutare se il tasso di cambio odierno è favorevole rispetto all'andamento dell'ultimo anno.

## ✨ Funzionalità Principali

- **Analisi Statistica del Tasso**: Calcola la posizione del tasso di cambio attuale usando un **percentile statistico** rispetto alla distribuzione dei tassi dell'ultimo anno, offrendo una valutazione molto più accurata di una semplice scala lineare.
- **Indicatore di Volatilità**: Misura la volatilità del mercato a 30 giorni per fornire un'indicazione del rischio e dell'instabilità attuali.
- **Commento Dinamico**: Fornisce un'analisi testuale di facile comprensione che combina i dati di percentile e volatilità per dare un consiglio pratico.
- **Architettura Modulare**: La logica di business è isolata in una libreria riutilizzabile (`fx_lib.py`), separata dall'interfaccia utente (`fx_simulator.py`).
- **Efficienza**: Implementa un design pattern **Singleton** per la gestione dei dati, assicurando che i dati di mercato vengano scaricati una sola volta per sessione, anche in caso di analisi multiple.

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
    Il progetto richiede alcune librerie Python. Installale tramite il file `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Esegui lo Script**
    Una volta installate le dipendenze, avvia il simulatore:
    ```bash
    python fx_simulator.py
    ```
    Lo script ti chiederà di inserire l'importo in USD che desideri convertire.

## 📊 Interpretare l'Output

Dopo l'esecuzione, lo script stamperà un report simile a questo:

```
REPORT ANALISI AVANZATA - 05/01/2026 10:30
============================================================
Capitale: 125,000.00 USD  |  Ottenuti con Fineco: 105,775.00 €
Tasso Mercato: 1.0810
------------------------------------------------------------
Posizionamento Statistico: 15.2° percentile (0=Migliore, 100=Peggiore)
Volatilità a 30gg: 0.0045 (Indice di Rischio/Opportunità)
------------------------------------------------------------
ANALISI: BUONO: Il Dollaro è forte. La conversione è vantaggiosa.
------------------------------------------------------------
Record Storico (per confronto):
  - Miglior cambio 12 mesi (28/09/2025): 110,500.00 €
  - Differenza dal massimo potenziale: -4,725.00 €
============================================================
```

- **Posizionamento Statistico**: **Questo è l'indicatore più importante.** Un valore basso (es. < 20) significa che il tasso di cambio attuale è più favorevole (più basso, nel caso di EUR/USD per chi vende USD) della maggior parte dei giorni dell'ultimo anno. **Più basso è, meglio è.**
- **Volatilità a 30gg**: Un valore alto (es. > 0.0075) indica che il mercato è "nervoso" e il prezzo sta oscillando molto. Questo può rappresentare sia un'opportunità che un rischio.
- **ANALISI**: Il commento riassume gli indicatori in un consiglio pratico.

---

*Disclaimer: Questo software è sviluppato a scopo didattico e analitico. Non deve essere considerato come consulenza finanziaria.*