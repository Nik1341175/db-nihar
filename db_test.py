import streamlit as st
import pandas as pd
import numpy as np
import psycopg2

@st.cache_resource
def connect_to_pukki():
    return psycopg2.connect(
        host=st.secrets["db"]["host"],
        port=st.secrets["db"]["port"],
        dbname=st.secrets["db"]["dbname"],
        user=st.secrets["db"]["user"],
        password=st.secrets["db"]["password"],
        sslmode="require"
    )

conn = connect_to_pukki()
df = pd.read_sql("SELECT * FROM demo", conn)
st.dataframe(df)