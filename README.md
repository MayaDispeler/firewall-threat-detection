# Firewall Threat Detection

A lightweight, end-to-end pipeline for analysing firewall logs, detecting anomalies with machine-learning, and visualising insights via a Streamlit dashboard.

## Quick Start

1. **Clone & create environment**
   ```bash
   git clone https://github.com/MayaDispeler/firewall-threat-detection.git
   cd firewall-threat-detection
   python -m venv env
   # Windows
   env\Scripts\activate
   # macOS / Linux
   source env/bin/activate
   pip install -r requirements.txt
   ```
2. **Prepare data (optional)** – rebuild `data/combined_firewall.csv`
   ```bash
   python prepare_enriched_data.py
   ```
3. **Retrain model (optional)**
   ```bash
   jupyter notebook 02_model.ipynb  # run all cells
   ```
4. **Launch dashboard**
   ```bash
   streamlit run dashboard.py
   ```

## Deliverables
| ID | Artefact | Location |
|----|----------|----------|
| I | **Approach documentation** – methodology, EDA summary, modelling, dashboard, future work | [`Approach.md`](Approach.md) |
| II | **Code + Requirements** – scripts, notebooks, model weights, install/run instructions | root folder, `requirements.txt` |
| III | **Evaluation metrics** – proxy labels vs anomaly output | section 5 in `Approach.md` & notebook output |

### Key Metrics (proxy evaluation)
| Metric | Score |
|--------|-------|
| Precision | 0.15 |
| Recall    | 1.00 |
| F1-score  | 0.26 |

High recall ensures nearly all suspicious events are captured; future iterations will focus on raising precision through richer features and model ensembles.

## Repository Structure
```
│  README.md
│  Approach.md
│  requirements.txt
│  dashboard.py          ← Streamlit app
│  prepare_enriched_data.py
│  data_synthesis.py
│  model.joblib / scaler.joblib
│  01_data_eda.ipynb     ← Exploratory analysis
│  02_model.ipynb        ← Model training & evaluation
└─ data/
   └─ combined_firewall.csv
```

## License
MIT