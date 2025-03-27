# Rifle_Spread_Pattern_Analysis

## Descrizione
Questo software permette di analizzare un'immagine di un bersaglio e rilevare i colpi sparati. Inoltre, calcola e disegna la circonferenza con diametro minimo che contiene una determinata percentuale di colpi più vicini tra loro, escludendo quelli più vicini al centro.

## Funzionalità
- Caricamento di immagini di bersagli.
- Rilevamento automatico dei colpi tramite elaborazione dell'immagine.
- Calcolo della circonferenza ottimale contenente la percentuale impostata di colpi.
- Visualizzazione dei risultati con evidenziazione dei colpi e della circonferenza.
- Esportazione dell'immagine elaborata.

## Requisiti
- Python 3.x
- Librerie richieste:
  - `opencv-python`
  - `numpy`
  - `Pillow`
  - `tkinter`
  - `math`
  - `threading`
  - `random`

Puoi installare le dipendenze con il comando:
```sh
pip install opencv-python numpy Pillow
```

Tkinter, math, threading and random sono integrate con ogni installazione di Python,
quindi se viene visualizzato l'errore di mancanza dipendenze
provare a reinstallare Python

## Istruzioni per l'Uso

1. **Avvia il programma**
   ```sh
   python main.py
   ```

2. **Caricare un'immagine**
   - Cliccare su "Seleziona Immagine" e scegliere un file immagine.

3. **Impostare i parametri**
   - `Threshold`: Valore di soglia per l'elaborazione dell'immagine.
   - `Area Minima`: Dimensione minima di un colpo da considerare.
   - `Percentuale`: Percentuale di colpi più vicini da includere nel calcolo della circonferenza.

4. **Analizzare l'immagine**
   - Cliccare su "Analizza Colpi" per avviare il processo.

5. **Visualizzare i risultati**
   - Il software mostrerà i colpi rilevati e la circonferenza calcolata.

6. **Esportare l'immagine**
   - Cliccare su "Export Immagine" per salvare l'immagine elaborata.

## Contatti
Per segnalare problemi o suggerire miglioramenti, aprire un'issue sul repository GitHub o contattare lo sviluppatore.

---
© 2024 - Analisi Colpi su Bersaglio
