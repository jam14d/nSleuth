import streamlit as st
from power_analysis import run_power_analysis
from group_comparison import run_group_comparison

st.set_page_config(page_title="nSleuth", layout="wide")
st.title("nSleuth")

tab1, tab2= st.tabs([
    "Power Analysis",
    "Group Comparison",
])

with tab1:
    run_power_analysis()

with tab2:
    run_group_comparison()

