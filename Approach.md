# Firewall Threat & Anomaly Detection – Project Overview

## 1. Why we’re doing this
Firewall is giving millions of log lines every single day. Who has time to read all that?  
So, our idea is to let data science do the difficult work:

* Checking all the logs properly to find the pattern and problem points.  
* Finding any danger or anything strange automatically, almost then and there.  
* Showing everything on one simple screen, so our analysts can just see the main thing.
---

## 2. The data we use
* **Source:** [Internet Firewall Data Set (Kaggle)](https://www.kaggle.com/datasets/tunguz/internet-firewall-data-set)  
* **Data saved in the path** `data/combined_firewall.csv` (plus raw/intermediate files)  
* **Data Synthesis codebases:** `data_synthesis.py` adds things like `total_traffic_bytes` and `hour_of_day`.

| Column | Meaning |
|--------|---------|
| `timestamp` | UTC time of the log entry |
| `src_ip`, `dst_ip` | source / destination address |
| `bytes_sent`, `bytes_received` | traffic volume |
| `application`, `url_category` | higher‑level context |
| `action` | what the firewall did (allow / deny / drop) |

---

## 3. What we found in the data
Full details are in the file (**`01_data_eda.ipynb`**), but the simple summary is:

* Only some few IPs are using all the bandwidth. The traffic is not balanced. 
* More than 80% of the blocked data is coming from less than 5% of the IPs. We can just block them straight away.
* Traffic is mostly high during office time, from 8 AM to 6 PM. If usage is high after that, something is suspicious.
* Websites marked as “**Unknown**” or “**Suspicious**” are getting blocked 6 times more than any normal website.

---

## 4. Features we feed the model
First pass, we keep it simple:

1. `bytes_sent`  
2. `bytes_received`  
3. `total_traffic_bytes` (sent + received)  
4. `hour_of_day` (from the timestamp)

Scaling done with `StandardScaler` and saved to `scaler.joblib`.

---

## 5. How the model works
Our logs are not having any labels like "**good**" or "**bad**". That's why we have to use unsupervised learning.

* Algorithm we used: Isolation Forest (from pyod library)
* How much threat we are expecting (contamination): We are assuming that about 2% of the traffic is bad.
* Notebook file: **`02_model.ipynb`**

### A Quick Check on Performance
For a simple evaluation, we are thinking like this: if the action is **`deny`** or **`drop`**, it is probably a bad thing. Everything else is probably fine.

| Metric | Score |
|--------|-------|
| Precision | **0.15** |
| Recall | **1.00** |
| F1 | **0.26** |

The recall is high (**1.00**), which means we are catching almost all the bad things. For now, it is also flagging some good things as bad, but that is okay. Later, we will add more features to make the precision better.

The trained model saveds in **`model.joblib`**.

---

## 6. The dashboard
Code File: **`dashboard.py`** (Streamlit)

What and all you can do with it:

* You can filter the data by time (all time, last 1 hour, 12 hours, 24 hours).
* You can see pie charts for applications, websites, source and destination IPs.
* See a bar chart to know the total traffic over time.  
* Check tables to find the top users and top website categories.
* You can also compare which traffic is allowed and which is blocked.

To run it, just use this command:
```bash
streamlit run dashboard.py
```
<!-- DASHBOARD_IMAGE_PLACEHOLDER -->
<img src="dashboard_screenshot.png" alt="Dashboard preview" width="100%">

---
## 7. Reproducing the Results
### 7.1 Environment setup
```bash
python -m venv env
source env/bin/activate      # Windows: env\Scripts\activate
pip install -r requirements.txt
```

### 7.2 Data preparation
Raw Kaggle CSVs → combine/enrich → `combined_firewall.csv`:
```bash
python prepare_enriched_data.py
```
### 7.3 Model training (optional)
```bash
jupyter notebook 02_model.ipynb
```
### 7.4 Run the dashboard
```bash
streamlit run dashboard.py
```

---
## 8. Repository Structure (key files)
```
│  Approach.md            ← (this file)
│  requirements.txt       ← dependencies
│  dashboard.py           ← Streamlit app
│  prepare_enriched_data.py
│  data_synthesis.py
│  model.joblib, scaler.joblib
│  01_data_eda.ipynb
│  02_model.ipynb
└─ data/
   └─ combined_firewall.csv
```
---
© 2025 – Firewall Threat Detection Project 
