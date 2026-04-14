import streamlit as st
import pandas as pd
import psycopg2
from psycopg2 import Error
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="🤖 Rover Telemetry Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🤖 Rover Telemetry Dashboard")
st.markdown("---")

# ============================================================================
# PASSKEY AUTHENTICATION
# ============================================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.warning("🔐 This dashboard is password protected")
    passkey = st.text_input("Enter Passkey:", type="password")
    
    if st.button("Login"):
        if passkey == st.secrets.get("passkey", "rover2026"):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Invalid passkey!")
    st.stop()

# ============================================================================
# DATABASE CONNECTION
# ============================================================================
@st.cache_resource
def get_db_connection():
    """Create connection to Pukki DBaaS"""
    try:
        conn = psycopg2.connect(
            host=st.secrets["db"]["host"],
            port=st.secrets["db"]["port"],
            database=st.secrets["db"]["dbname"],
            user=st.secrets["db"]["user"],
            password=st.secrets["db"]["password"],
            sslmode="require"
        )
        return conn
    except Error as e:
        st.error(f"❌ Database connection error: {e}")
        return None

@st.cache_data(ttl=300)  # Refresh every 5 minutes
def fetch_telemetry_data():
    """Fetch all telemetry data from database using parameterized query"""
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        query = "SELECT id, timestamp, latitude, longitude, speed, battery_level, temperature, sensor_reading FROM telemetry ORDER BY timestamp DESC"
        df = pd.read_sql(query, conn)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Error as e:
        st.error(f"❌ Query error: {e}")
        return None
    finally:
        if conn:
            conn.close()

# ============================================================================
# FETCH DATA
# ============================================================================
df = fetch_telemetry_data()

if df is None or df.empty:
    st.error("❌ No telemetry data found. Please run setup_db.py first to populate the database.")
    st.info("Steps to fix:")
    st.markdown("""
    1. Download `setup_db.py` from the repo
    2. Update database credentials (host, user, password)
    3. Run: `python setup_db.py`
    4. Refresh this page
    """)
    st.stop()

st.success(f"✓ Connected! Loaded {len(df)} telemetry records")

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================
st.sidebar.header("📊 Filters")

time_range = st.sidebar.slider(
    "Time Range (last N hours):",
    min_value=1,
    max_value=12,
    value=6
)

df_filtered = df[df['timestamp'] >= pd.Timestamp.now() - pd.Timedelta(hours=time_range)]

# ============================================================================
# MAIN DASHBOARD
# ============================================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📍 Total Records", len(df_filtered))

with col2:
    avg_speed = df_filtered['speed'].mean()
    st.metric("🚗 Avg Speed (m/s)", f"{avg_speed:.2f}")

with col3:
    avg_battery = df_filtered['battery_level'].mean()
    st.metric("🔋 Avg Battery (%)", f"{avg_battery:.1f}")

with col4:
    avg_temp = df_filtered['temperature'].mean()
    st.metric("🌡️ Avg Temperature (°C)", f"{avg_temp:.1f}")

st.markdown("---")

# ============================================================================
# CHARTS
# ============================================================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Battery Level Over Time")
    fig_battery = px.line(
        df_filtered.sort_values('timestamp'),
        x='timestamp',
        y='battery_level',
        title="Battery Discharge Rate",
        labels={'battery_level': 'Battery (%)', 'timestamp': 'Time'}
    )
    st.plotly_chart(fig_battery, use_container_width=True)

with col2:
    st.subheader("🌡️ Temperature Over Time")
    fig_temp = px.line(
        df_filtered.sort_values('timestamp'),
        x='timestamp',
        y='temperature',
        title="Temperature Readings",
        labels={'temperature': 'Temperature (°C)', 'timestamp': 'Time'}
    )
    st.plotly_chart(fig_temp, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🚗 Speed Over Time")
    fig_speed = px.bar(
        df_filtered.sort_values('timestamp'),
        x='timestamp',
        y='speed',
        title="Rover Speed",
        labels={'speed': 'Speed (m/s)', 'timestamp': 'Time'}
    )
    st.plotly_chart(fig_speed, use_container_width=True)

with col2:
    st.subheader("📡 Sensor Readings")
    fig_sensor = px.scatter(
        df_filtered,
        x='timestamp',
        y='sensor_reading',
        size='speed',
        hover_data=['latitude', 'longitude'],
        title="Sensor Data (size = speed)",
        labels={'sensor_reading': 'Sensor Reading', 'timestamp': 'Time'}
    )
    st.plotly_chart(fig_sensor, use_container_width=True)

st.markdown("---")

# ============================================================================
# GPS MAP
# ============================================================================
st.subheader("🗺️ GPS Trajectory")
if not df_filtered.empty:
    st.map(df_filtered[['latitude', 'longitude']], zoom=13)

st.markdown("---")

# ============================================================================
# DATA TABLE
# ============================================================================
st.subheader("📋 Raw Data")
st.dataframe(
    df_filtered.sort_values('timestamp', ascending=False),
    use_container_width=True,
    height=400
)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("💻 **Rover Telemetry Dashboard** | Powered by Streamlit + Pukki DBaaS")
st.markdown(f"Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")