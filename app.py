import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

st.title("Rover Telemetry Dashboard")

password = st.text_input("Enter passkey", type="password")

if password == st.secrets["passkey"]:

    conn = psycopg2.connect(
        host=st.secrets["db_host"],
        database=st.secrets["db_name"],
        user=st.secrets["db_user"],
        password=st.secrets["db_password"],
        port=5432
    )

    df = pd.read_sql("SELECT * FROM telemetry", conn)

    st.write("Telemetry Data")
    st.dataframe(df)

    fig = px.line(df, x="timestamp", y="battery")
    st.plotly_chart(fig)

else:
    st.warning("Enter correct passkey")