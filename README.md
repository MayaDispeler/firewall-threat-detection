# Firewall Threat Detection Project

Hello! So, what is this project? Simply put, firewall logs are huge, no? Millions of lines. Who will read all that? So we are just using some data science to do the hard work for us.

---

### So, what and all have we done?

*   **First, we understood the data (EDA):** We properly went through the logs to see what is the actual story. We found out which IPs are eating all the data, when traffic is maximum, and which websites are the main culprits.
*   **Then, we built one small AI model:** We used a simple method called 'Isolation Forest'. Nothing fancy, boss. Just a smart way to find anything that looks a bit... off. The final model is sitting in `model.joblib`.
*   **And, a dashboard to see everything:** We made a simple screen with Streamlit to show all the findings. You can see live what is being blocked, what is allowed, and filter for different times also.
*   **Everything is inside:** All the code, notebooks, everything is in this folder only, so you can also run it.

For the full story, all the nitty-gritty details are there in the **[`Approach.md`](Approach.md)** file. Please to check it.

---

### How to run this thing?

Just follow these steps, it is very easy.

1.  **First, get the code and set up the environment:**
    ```bash
    git clone https://github.com/MayaDispeler/firewall-threat-detection.git
    cd firewall-threat-detection
    python -m venv env

    # For Windows people
    env\Scripts\activate

    # For Mac/Linux people
    source env/bin/activate
    ```

2.  **Next, you have to install the packages:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **That's all! Just run the dashboard:**
    ```bash
    streamlit run dashboard.py
    ```

Simple, no? If you want to create the data file again or train the model again, all commands for that are given in `Approach.md`.

---

### But is the model any good?

Good question. We did one small check. See, we don't have any data that is properly labelled as 'attack'. So we just made one assumption: if the firewall said `deny` or `drop`, it must be a bad thing.

| Metric | Score |
|--------|-------|
| Precision | 0.15 |
| Recall    | 1.00 |
| F1-score  | 0.26 |

Now, don't get worried by the low precision. The main thing to see is the **Recall is 1.00**. That means our model is catching *every single thing* the firewall thought was a problem. Yes, it is being a bit over-cautious and flagging some good things also, but better safe than sorry, no? We can always make it better later.

---

### How the files are kept

```
│  README.md                <-- This file only!
│  Approach.md              <-- The full story is here
│  requirements.txt         <-- All packages needed for install
│  dashboard.py             <-- The main application
│  ...and other required files
```

---
*License: MIT*