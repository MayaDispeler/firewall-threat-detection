import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import io
from fpdf import FPDF

st.set_page_config(page_title="Firewall Dashboard", layout="wide")

st.sidebar.image("https://img.icons8.com/color/96/000000/firewall.png", width=60)
st.sidebar.title("Firewall Dashboard")
st.sidebar.markdown(
    "Monitor, analyze, and detect anomalies in your network traffic. "
    "Use the filters below to explore the data interactively."
)
time_option = st.sidebar.selectbox("Select timeframe", ["All", "1h", "12h", "24h"])

DATA_PATH = Path("data/combined_firewall.csv")


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
    df["timestamp"] = df["timestamp"].dt.tz_localize(None)
    df["bytes_sent"] = df["bytes_sent"].fillna(0)
    df["bytes_received"] = df["bytes_received"].fillna(0)
    if "total_traffic_bytes" not in df.columns:
        df["total_traffic_bytes"] = df["bytes_sent"] + df["bytes_received"]
    return df


df = load_data()

if time_option == "All":
    df_time = df.copy()
else:
    hours = int(time_option.replace("h", ""))
    base_time = df["timestamp"].min()
    cutoff = base_time + pd.Timedelta(hours=hours)
    df_time = df[df["timestamp"] <= cutoff]

st.title("Firewall network traffic monitoring dashboard")
st.markdown(
    "This dashboard visualizes network traffic, applications, categories, IP activity, "
    "and more."
)
st.markdown("---")

st.header("Traffic Distribution")
donut_cols = st.columns(4)

with donut_cols[0]:
    st.subheader("Applications by traffic")
    app_data = (
        df_time.groupby("application")["total_traffic_bytes"].sum().nlargest(6)
    )
    if not app_data.empty:
        st.plotly_chart(
            px.pie(
                values=app_data.values,
                names=app_data.index,
                hole=0.5,
                color_discrete_sequence=px.colors.sequential.Blues,
            ),
            use_container_width=True,
        )

with donut_cols[1]:
    st.subheader("URL categories by traffic")
    cat_data = (
        df_time.groupby("url_category")["total_traffic_bytes"].sum().nlargest(6)
    )
    if not cat_data.empty:
        st.plotly_chart(
            px.pie(
                values=cat_data.values,
                names=cat_data.index,
                hole=0.5,
                color_discrete_sequence=px.colors.sequential.RdPu,
            ),
            use_container_width=True,
        )

with donut_cols[2]:
    st.subheader("Traffic source IP")
    src_data = (
        df_time.dropna(subset=["src_ip"])
        .groupby("src_ip")["total_traffic_bytes"]
        .sum()
        .nlargest(6)
    )
    if not src_data.empty:
        st.plotly_chart(
            px.pie(
                values=src_data.values,
                names=src_data.index,
                hole=0.5,
                color_discrete_sequence=px.colors.sequential.Blues_r,
            ),
            use_container_width=True,
        )

with donut_cols[3]:
    st.subheader("Traffic destination IP")
    dst_data = (
        df_time.dropna(subset=["dst_ip"])
        .groupby("dst_ip")["total_traffic_bytes"]
        .sum()
        .nlargest(6)
    )
    if not dst_data.empty:
        st.plotly_chart(
            px.pie(
                values=dst_data.values,
                names=dst_data.index,
                hole=0.5,
                color_discrete_sequence=px.colors.sequential.RdPu_r,
            ),
            use_container_width=True,
        )

st.markdown("---")

st.header("Network traffic")
total_traffic_gb = df_time["total_traffic_bytes"].sum() / (1024**3)
st.markdown(
    f"<h1 style='text-align:center; color:#FF6F61; font-size:4em;'>{total_traffic_gb:.2f} GB</h1>",
    unsafe_allow_html=True,
)
st.caption("Total network traffic")
st.markdown("---")

st.header("Detailed Data Tables")
table_cols = st.columns(2)

with table_cols[0]:
    st.subheader("URL categories by traffic")
    table1 = (
        df_time.groupby("url_category")
        .agg(
            Traffic=(
                "total_traffic_bytes",
                lambda x: f"{x.sum() / (1024**3):.2f} GB"
                if x.sum() > 1024**3
                else f"{x.sum() / (1024**2):.2f} MB",
            ),
            Sessions=("src_ip", "count"),
            Users=("user_id", pd.Series.nunique),
        )
        .reset_index()
        .sort_values(by="Traffic", ascending=False)
    )
    st.dataframe(table1, use_container_width=True, height=350)

with table_cols[1]:
    st.subheader("Source user & IP by traffic")
    df_sub = df_time.dropna(subset=["src_ip"])
    table2 = (
        df_sub.groupby(["user_id", "src_ip", "application"])
        .agg(
            Traffic=(
                "total_traffic_bytes",
                lambda x: f"{x.sum() / (1024**3):.2f} GB"
                if x.sum() > 1024**3
                else f"{x.sum() / (1024**2):.2f} MB",
            )
        )
        .reset_index()
        .sort_values(by="Traffic", ascending=False)
    )
    st.dataframe(table2, use_container_width=True, height=350)
st.markdown("---")

st.header("Network traffic by zone")
df_time["hour"] = df_time["timestamp"].dt.floor("1h")
time_data = df_time.groupby("hour")["total_traffic_bytes"].sum()
if not time_data.empty:
    bar_zone_fig = px.bar(
        x=time_data.index,
        y=time_data.values,
        labels={"x": "Time", "y": "Traffic (Bytes)"},
        color_discrete_sequence=["#0083B8"],
        title="Network traffic by zone",
    ).update_layout(width=1200, height=400)
    st.plotly_chart(bar_zone_fig, use_container_width=True)
st.markdown("---")

st.header("Additional Insights & Analytics")
COLOR_SEQ = px.colors.sequential.RdPu_r

# --- Redesigned compact layout ---
# Row 1 → three charts side-by-side
row1_col1, row1_col2, row1_col3 = st.columns(3)

with row1_col1:
    st.subheader("Action Distribution")
    action_counts = df_time["action"].value_counts().dropna()
    if not action_counts.empty:
        action_fig = px.pie(
            values=action_counts.values,
            names=action_counts.index,
            hole=0.4,
            color_discrete_sequence=COLOR_SEQ,
        ).update_layout(title="Actions", height=300, margin=dict(t=40, b=20))
        st.plotly_chart(action_fig, use_container_width=True)

with row1_col2:
    st.subheader("Top Users by Traffic")
    user_traffic = (
        df_time.groupby("user_id")["total_traffic_bytes"].sum().sort_values(ascending=False).head(10)
    )
    if not user_traffic.empty:
        user_fig = px.bar(
            x=user_traffic.index.astype(str),
            y=user_traffic.values,
            labels={"x": "User ID", "y": "Traffic (Bytes)"},
            color_discrete_sequence=COLOR_SEQ,
        ).update_layout(title="Top 10 Users", height=300, margin=dict(t=40, b=20))
        st.plotly_chart(user_fig, use_container_width=True)

with row1_col3:
    st.subheader("Top Apps by Sessions")
    app_sessions = df_time["application"].value_counts().head(10)
    if not app_sessions.empty:
        app_fig = px.bar(
            x=app_sessions.index,
            y=app_sessions.values,
            labels={"x": "Application", "y": "Sessions"},
            color_discrete_sequence=COLOR_SEQ,
        ).update_layout(title="Top 10 Applications", height=300, margin=dict(t=40, b=20))
        st.plotly_chart(app_fig, use_container_width=True)

# Row 2 → two time-series charts side-by-side
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("Traffic by Hour of Day")
    if df_time["timestamp"].notna().any():
        df_time["hour_of_day"] = df_time["timestamp"].dt.hour
        hourly_traffic = df_time.groupby("hour_of_day")["total_traffic_bytes"].sum()
        if not hourly_traffic.empty:
            hour_fig = px.line(
                x=hourly_traffic.index,
                y=hourly_traffic.values,
                labels={"x": "Hour", "y": "Traffic (Bytes)"},
                color_discrete_sequence=COLOR_SEQ,
            ).update_traces(mode="lines+markers").update_layout(height=300, margin=dict(t=40, b=20))
            st.plotly_chart(hour_fig, use_container_width=True)

with row2_col2:
    st.subheader("Bytes Sent vs. Received")
    if {"bytes_sent", "bytes_received"}.issubset(df_time.columns):
        bytes_time = df_time.copy()
        bytes_time["hour"] = bytes_time["timestamp"].dt.floor("1h")
        sent = bytes_time.groupby("hour")["bytes_sent"].sum()
        received = bytes_time.groupby("hour")["bytes_received"].sum()
        bytes_df = (
            pd.DataFrame({"Bytes Sent": sent, "Bytes Received": received})
            .reset_index()
            .melt(id_vars="hour", var_name="Type", value_name="Bytes")
        )
        if not bytes_df.empty and bytes_df["Bytes"].notna().any():
            bytes_fig = px.line(
                bytes_df,
                x="hour",
                y="Bytes",
                color="Type",
                color_discrete_sequence=COLOR_SEQ,
            ).update_traces(mode="lines+markers").update_layout(height=300, margin=dict(t=40, b=20))
            st.plotly_chart(bytes_fig, use_container_width=True)

# Metric row
metric_col1, metric_col2 = st.columns(2)
with metric_col1:
    st.metric("Unique Source IPs", df_time["src_ip"].nunique())
with metric_col2:
    st.metric("Unique Destination IPs", df_time["dst_ip"].nunique())

# Action summary inside an expander to save space
action_table = (
    df_time.groupby("action").agg(Count=("action", "count"), Total_Traffic=("total_traffic_bytes", "sum")).reset_index()
)
action_table["Total_Traffic"] = action_table["Total_Traffic"].apply(lambda x: f"{x/(1024**2):.2f} MB")

with st.expander("Action Summary Table", expanded=False):
    st.dataframe(action_table, use_container_width=True)

# Full-width heatmap
st.subheader("User Activity Heatmap (User vs Hour)")
if "user_id" in df_time.columns and df_time["user_id"].notna().any():
    temp = df_time.copy()
    temp["hour_of_day"] = temp["timestamp"].dt.hour
    top_users = temp.groupby("user_id")["total_traffic_bytes"].sum().sort_values(ascending=False).head(20).index
    temp = temp[temp["user_id"].isin(top_users)]
    pivot = pd.pivot_table(temp, index="user_id", columns="hour_of_day", values="total_traffic_bytes", aggfunc="sum", fill_value=0) / (1024**2)
    if not pivot.empty:
        heatmap_fig = go.Figure(data=go.Heatmap(z=pivot.values, x=[f"{h:02d}" for h in pivot.columns], y=pivot.index, colorscale="RdPu", colorbar=dict(title="Traffic (MB)")))
        heatmap_fig.update_layout(height=450, margin=dict(t=40, b=40))
        st.plotly_chart(heatmap_fig, use_container_width=True)

st.markdown(
    "<div style='text-align: center; color: gray;'><small>Dashboard by Srihari | Data Source: Firewall Logs | Powered by Streamlit & Plotly</small></div>",
    unsafe_allow_html=True,
)