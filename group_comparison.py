import streamlit as st
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

def run_group_comparison():
    st.header("Group Comparison Tool")
    st.info(
        "**Note:** This tool currently works best with CSV files in long format, "
        "with one column for the group label (e.g., `Group`) and one for the numerical value (e.g., `Score`)."
    )
    st.markdown("""
Compare numerical outcomes between groups to see if they are statistically different.
    
**Options:**
- Upload your own dataset (CSV)
- Manually input summary statistics
    """)


    input_mode = st.radio("Select input method", ["Upload CSV", "Manual Entry"])

    if input_mode == "Upload CSV":
        uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write("Preview of data", df.head())

            numeric_col = st.selectbox("Choose numeric column", df.select_dtypes(include='number').columns)
            group_col = st.selectbox("Choose group column", df.select_dtypes(exclude='number').columns)

            groups = df[group_col].unique()
            group_values = [df[df[group_col] == g][numeric_col].dropna() for g in groups]

            if len(groups) == 2:
                stat, p = stats.ttest_ind(group_values[0], group_values[1])
                st.success(f"Independent t-test p-value: **{p:.4f}**")
            elif len(groups) > 2:
                stat, p = stats.f_oneway(*group_values)
                st.success(f"ANOVA p-value: **{p:.4f}**")
            else:
                st.warning("Need at least two groups.")

            st.subheader("Group Distribution Plot")
            fig, ax = plt.subplots()
            sns.boxplot(x=group_col, y=numeric_col, data=df, ax=ax)
            st.pyplot(fig)

    else:  # Manual Entry
        st.subheader("Manual Entry (Two Groups Only)")

        mean1 = st.number_input("Group 1 mean", value=50.0)
        std1 = st.number_input("Group 1 std dev", value=10.0)
        n1 = st.number_input("Group 1 sample size", min_value=2, value=30)

        mean2 = st.number_input("Group 2 mean", value=55.0)
        std2 = st.number_input("Group 2 std dev", value=10.0)
        n2 = st.number_input("Group 2 sample size", min_value=2, value=30)

        if st.button("Run comparison"):
            se = ((std1 ** 2) / n1 + (std2 ** 2) / n2) ** 0.5
            t_stat = (mean1 - mean2) / se
            df = ((std1**2/n1 + std2**2/n2)**2) / (((std1**2/n1)**2)/(n1-1) + ((std2**2/n2)**2)/(n2-1))
            p_val = stats.t.sf(abs(t_stat), df) * 2

            st.success(f"t-statistic: {t_stat:.3f}")
            st.success(f"Degrees of freedom: {df:.1f}")
            st.success(f"p-value: **{p_val:.4f}**")
