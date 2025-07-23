# Firewall Threat & Anomaly Detection – Approach Documentation

## 1. Problem Statement
Modern firewalls generate millions of log lines every day.  Manually sifting through them is impractical.  The goal of this project is to leverage data-science techniques to:

* perform **exploratory data analysis (EDA)** on the raw logs to uncover patterns & pain-points,
* build an **AI-driven threat / anomaly detection model** that flags suspicious traffic in (near) real-time, and
* serve the insights through a **simple dashboard** that security analysts can use to monitor incidents across multiple time-frames.

---
## 2. Data
* **Source:** [Internet Firewall Data Set (Kaggle)](https://www.kaggle.com/datasets/tunguz/internet-firewall-data-set)
* **Location in repo:** `data/combined_firewall.csv` (plus intermediate/raw files)
* **Synthetic enrichment:** `data_synthesis.py` adds columns such as `total_traffic_bytes`, `hour_of_day`, etc. to better train the model.

Key columns
| Column | Meaning |
|--------|---------|
| `timestamp` | UTC-time of log entry |
| `src_ip`, `dst_ip` | source / destination address |
| `bytes_sent`, `bytes_received` | traffic volume |
| `application`, `url_category` | higher-level context |
| `action` | firewall decision (allow / deny / drop) |

---
## 3. Exploratory Data Analysis (EDA)
EDA was performed in **`01_data_eda.ipynb`**.  Highlights:

* Traffic is highly **right-skewed**; a handful of IPs dominate bandwidth.
* >80 % of dropped/denied packets originate from <5 % of source IPs ⇒ candidate block-list.
* Traffic spikes follow an 8 AM–6 PM work-day pattern; off-hour spikes deserve inspection.
* Certain URL categories ("Unknown", "Suspicious") coincide with `action = deny/drop` more than 6× the global rate.

Plots (see notebook): distribution histograms, hourly heat-map, bar charts of top applications & categories.

---
## 4. Feature Engineering
Minimal numeric feature set for the first iteration:

1. `bytes_sent`
2. `bytes_received`
3. `total_traffic_bytes` = sent + received
4. `hour_of_day` = `timestamp.hour`

These are scaled using `StandardScaler` (saved as `scaler.joblib`).

---
## 5. Modelling Approach
Logs are **unlabelled** – we do not have ground-truth attack annotations.  Therefore an **unsupervised anomaly-detection algorithm** is appropriate.

* **Algorithm:** Isolation Forest via [`pyod`](https://pyod.readthedocs.io/)
* **Contamination:** 2 % (assumption: only a small fraction of traffic is malicious)
* **Implementation:** see **`02_model.ipynb`**

### Evaluation
We use a **proxy label**: treat `action ∈ {deny, drop}` as *likely bad* (class = 1) and the rest as *benign* (class = 0).  Using this heuristic:

| Metric | Score |
|--------|-------|
| Precision | **0.15** |
| Recall    | **1.00** |
| F1-score  | **0.26** |

*High recall* is desirable – we prefer catching everything at the expense of false positives.  Future work focuses on improving precision via additional features (e.g. protocol, port, rolling statistics).

The fitted model is persisted to `model.joblib` for reuse by the dashboard / APIs.

---
## 6. Dashboard
File: **`dashboard.py`** – powered by **Streamlit**.

Features
* Time-frame filter: *All*, *last 1 h*, *12 h*, *24 h*
* Pie charts of traffic by application, URL category, source & destination IPs
* Bar-chart time-series of total traffic
* Tables of top users, categories
* Action distribution (allow vs deny/drop)

Launch with:
```bash
streamlit run dashboard.py
```

---
## 7. Reproducing the Results
### 7.1 Environment setup
```bash
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
pip install -r requirements.txt
```
*Add `fpdf` if you plan to export PDFs from the dashboard.*

### 7.2 Data preparation
Raw Kaggle CSVs → combine/enrich → `combined_firewall.csv`:
```bash
python prepare_enriched_data.py  # or run the notebook cells
```
### 7.3 Model training (optional)
```bash
jupyter notebook 02_model.ipynb  # run all cells to retrain & save artefacts
```
### 7.4 Run the dashboard
```bash
streamlit run dashboard.py
```

---
## 8. Repository Structure (key files)
```
│  Approach.md            ← **(this file)**
│  requirements.txt       ← dependency list
│  dashboard.py           ← Streamlit app
│  prepare_enriched_data.py
│  data_synthesis.py
│  model.joblib, scaler.joblib
│  01_data_eda.ipynb
│  02_model.ipynb
└─ data/
   └─ combined_firewall.csv (processed dataset)
```

---
## 9. Future Improvements
* Incorporate categorical features via one-hot encoding or embeddings.
* Deploy model as a REST service (FastAPI) for real-time ingestion.
* Add alerting (Slack/email) when anomaly score exceeds threshold.
* Evaluate alternative algorithms (e.g. AutoEncoder, One-Class SVM) & ensemble their outputs.

---
© 2025 – Firewall Threat Detection Project 