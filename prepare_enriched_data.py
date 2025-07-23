import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path("data")
df = pd.read_csv(DATA_DIR / "combined_firewall.csv", parse_dates=["timestamp"])
df["timestamp"] = df["timestamp"].dt.tz_localize(None)

rng = np.random.default_rng(42)

# --- 1. Add simulated application
apps = [
    "web-browsing", "dns", "ms-outlook", "ms-office365-base",
    "youtube", "facebook", "twitter", "windows-update"
]
df["application"] = rng.choice(apps, size=len(df), p=[0.3, 0.1, 0.15, 0.1, 0.1, 0.1, 0.05, 0.1])

# --- 2. Add simulated URL categories
categories = [
    "Computer & Internet", "Social Media", "News", "Business",
    "Search Engines", "Content Delivery", "Gov", "Education", "Any"
]
df["url_category"] = rng.choice(categories, size=len(df), p=[0.25,0.15,0.1,0.1,0.1,0.1,0.05,0.05,0.1])

# --- 3. Assign user_id based on src_ip
unique_ips = df["src_ip"].dropna().unique()
user_map = {ip: f"User {i+1}" for i, ip in enumerate(unique_ips)}
df["user_id"] = df["src_ip"].map(user_map)

# --- 4. Compute total traffic (bytes)
df["total_traffic_bytes"] = df["bytes_sent"].fillna(0) + df["bytes_received"].fillna(0)

# Save enriched version
df.to_csv(DATA_DIR / "enriched_firewall.csv", index=False)
print("Saved enriched firewall data.")
