import streamlit as st
import pandas as pd

# Get the data
@st.cache_data
def get_data():
    df = pd.read_csv("https://raw.githubusercontent.com/mwaskom/seaborn-data/refs/heads/master/titanic.csv")
    st.write("dataset import done")
    return df

df = get_data()

# Display the data
st.dataframe(df.head(5))

# Select column
option = st.selectbox("Select column", ("survived", "sex", "class"))
# Display selectec column
st.write(option)
# Count values in the column
selected_count = df[option].value_counts()
# Display value_count data
st.write(selected_count)
# Display bar chart horizontally
st.bar_chart(selected_count, horizontal=True)