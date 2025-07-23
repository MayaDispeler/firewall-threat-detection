import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# -------- create a synthetic log --------
def create_synthetic_logs(n=1000, seed=42):
    rng = np.random.default_rng(seed)

    timestamps = pd.date_range(start="2025-07-01", periods=n, freq="H")
    src_ip = [f"10.0.{rng.integers(0, 255)}.{rng.integers(1, 255)}" for _ in range(n)]
    dst_ip = [f"172.16.{rng.integers(0, 255)}.{rng.integers(1, 255)}" for _ in range(n)]
    bytes_sent = rng.integers(100, 100000, n)
    bytes_received = rng.integers(100, 100000, n)
    action = rng.choice(["allow", "deny", "drop"], p=[0.85, 0.10, 0.05], size=n)
    application = rng.choice([
        "web-browsing", "ssl", "dns", "ftp", "ssh", "smtp", "snmp", "unknown"
    ], size=n)
    url_category = rng.choice([
        "business", "social-media", "news", "malware", "adult", "unknown"
    ], size=n)
    user_id = [f"user{rng.integers(1, 1000)}" for _ in range(n)]
    total_traffic_byte = bytes_sent + bytes_received

    df_syn = pd.DataFrame({
        "timestamp": timestamps,
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "bytes_sent": bytes_sent,
        "bytes_received": bytes_received,
        "action": action,
        "application": application,
        "url_category": url_category,
        "user_id": user_id,
        "total_traffic_byte": total_traffic_byte
    })

    return df_syn

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
df_syn = create_synthetic_logs()
df_syn.to_csv(DATA_DIR / "synthetic_log.csv", index=False)
