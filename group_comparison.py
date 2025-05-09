import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import tempfile
import os

def explain_test(test_name):
    if test_name == "t-test":
        st.markdown("""
### Explanation: Independent Samples t-test
The t-test compares the means of two independent groups.

- **Null hypothesis (H₀)**: Group means are equal (μ₁ = μ₂)
- **Alternative hypothesis (H₁)**: Group means are not equal (μ₁ ≠ μ₂)
- **Used when**: Comparing 2 groups, numeric outcome
""")
    elif test_name == "anova":
        st.markdown("""
### Explanation: One-Way ANOVA
ANOVA tests whether 3 or more group means differ.

- **Null hypothesis (H₀)**: All group means are equal
- **Alternative hypothesis (H₁)**: At least one group differs
- **Used when**: Comparing ≥3 groups, numeric outcome
""")

def generate_pdf_report(title, explanation, summary, formulas):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, title, ln=True)
    pdf.set_font("Arial", "", 12)

    pdf.multi_cell(0, 8, explanation)
    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Results Summary", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, summary)
    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Calculation Details", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, formulas)

    temp_path = tempfile.mktemp(suffix=".pdf")
    pdf.output(temp_path)
    return temp_path

def run_group_comparison():
    st.title("Group Comparison Tool (t-test and ANOVA)")

    input_mode = st.radio("Select data input method:", ["Upload CSV", "Manual Entry", "Simulate Example Data"])

    if input_mode == "Upload CSV":
        uploaded_file = st.file_uploader("Upload your CSV file (long format)", type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write("Data Preview:", df.head())

            numeric_col = st.selectbox("Select numeric column (outcome):", df.select_dtypes(include='number').columns)
            group_col = st.selectbox("Select grouping column:", df.select_dtypes(exclude='number').columns)

            groups = df[group_col].unique()
            group_values = [df[df[group_col] == g][numeric_col].dropna() for g in groups]

            if len(groups) == 2:
                explain_test("t-test")
                stat, p = stats.ttest_ind(group_values[0], group_values[1])
                st.subheader("Results")
                st.write(f"t-statistic: {stat:.4f}")
                st.write(f"p-value: {p:.4f}")
            elif len(groups) > 2:
                explain_test("anova")
                stat, p = stats.f_oneway(*group_values)
                st.subheader("Results")
                st.write(f"F-statistic: {stat:.4f}")
                st.write(f"p-value: {p:.4f}")
            else:
                st.warning("You need at least two groups for comparison.")

            st.subheader("Group Boxplot")
            fig, ax = plt.subplots()
            sns.boxplot(x=group_col, y=numeric_col, data=df, ax=ax)
            st.pyplot(fig)
    

    elif input_mode == "Manual Entry":
        st.subheader("Manual Entry of Summary Statistics")
        st.markdown("Enter the mean, standard deviation, and sample size for each group.")

        num_groups = st.slider("Number of groups", 2, 5, 2)
        group_data = []

        for i in range(num_groups):
            st.markdown(f"**Group {i+1}**")
            mean = st.number_input(f"Mean (Group {i+1})", key=f"mean_{i}")
            std = st.number_input(f"Standard Deviation (Group {i+1})", min_value=0.0, key=f"std_{i}")
            n = st.number_input(f"Sample Size (Group {i+1})", min_value=2, key=f"n_{i}")
            group_data.append((mean, std, n))

        if st.button("Run Comparison"):
            if any(std == 0 for _, std, _ in group_data):
                st.error("Standard deviation cannot be zero in any group.")
                return

            if num_groups == 2:
                explain_test("t-test")
                mean1, std1, n1 = group_data[0]
                mean2, std2, n2 = group_data[1]

                se = np.sqrt((std1**2)/n1 + (std2**2)/n2)
                t_stat = (mean1 - mean2) / se

                df_num = ((std1**2 / n1 + std2**2 / n2) ** 2)
                df_denom = ((std1**2 / n1)**2) / (n1 - 1) + ((std2**2 / n2)**2) / (n2 - 1)

                if df_denom == 0:
                    st.error("Unable to compute degrees of freedom (division by zero).")
                    return

                df_final = df_num / df_denom
                p_val = stats.t.sf(np.abs(t_stat), df_final) * 2

                summary = f"t = {t_stat:.4f}, df = {df_final:.2f}, p = {p_val:.4f}"
                formulas = (
                    f"SE = sqrt((s1²/n1) + (s2²/n2)) = sqrt(({std1:.2f}²/{int(n1)}) + ({std2:.2f}²/{int(n2)})) = {se:.4f}\n"
                    f"t = (mean1 - mean2) / SE = ({mean1:.2f} - {mean2:.2f}) / {se:.4f} = {t_stat:.4f}\n"
                    f"df (Welch's) = {df_final:.2f}"
                )

                st.subheader("Results")
                st.write(summary)
                st.text("Calculation Details")
                st.text(formulas)

                pdf_path = generate_pdf_report(
                    "Two-Group t-test Report",
                    "This report compares two groups using an independent samples t-test.",
                    summary,
                    formulas
                )
                with open(pdf_path, "rb") as f:
                    st.download_button("Download PDF Report", f, file_name="t_test_report.pdf")

            else:
                explain_test("anova")
                total_n = sum(g[2] for g in group_data)
                grand_mean = sum(g[0] * g[2] for g in group_data) / total_n

                ssb = sum(g[2] * (g[0] - grand_mean)**2 for g in group_data)
                dfb = num_groups - 1
                msb = ssb / dfb

                ssw = sum((g[2] - 1) * g[1]**2 for g in group_data)
                dfw = total_n - num_groups
                msw = ssw / dfw

                f_stat = msb / msw
                p_val = stats.f.sf(f_stat, dfb, dfw)

                summary = f"F = {f_stat:.4f}, df = ({dfb}, {dfw}), p = {p_val:.4f}"
                formulas = (
                    f"Grand Mean = {grand_mean:.4f}\n"
                    f"SSB = Σ n_i*(x̄_i - GM)² = {ssb:.4f}\n"
                    f"MSB = SSB / df_between = {msb:.4f}\n"
                    f"SSW = Σ (n_i - 1)*s_i² = {ssw:.4f}\n"
                    f"MSW = SSW / df_within = {msw:.4f}\n"
                    f"F = MSB / MSW = {f_stat:.4f}"
                )

                st.subheader("Results")
                st.write(summary)
                st.text("Calculation Details")
                st.text(formulas)

                pdf_path = generate_pdf_report(
                    "ANOVA Report",
                    "This report compares multiple groups using one-way ANOVA.",
                    summary,
                    formulas
                )
                with open(pdf_path, "rb") as f:
                    st.download_button("Download PDF Report", f, file_name="anova_report.pdf")
    
    elif input_mode == "Simulate Example Data":
        test_type = st.radio("Choose a test to simulate", ["Two-group t-test", "Three-group ANOVA"])

        if test_type == "Two-group t-test":
            explain_test("t-test")
            group_data = [
                (12.0, 2.0, 15),  # Group 1
                (14.5, 2.5, 15),  # Group 2
            ]
        else:
            explain_test("anova")
            group_data = [
                (10.0, 2.0, 12),  # Group 1
                (15.0, 3.0, 12),  # Group 2
                (20.0, 2.5, 12),  # Group 3
            ]

        num_groups = len(group_data)
        st.write("Simulated group summary:")
        for i, (m, s, n) in enumerate(group_data, 1):
            st.write(f"Group {i}: mean = {m}, std = {s}, n = {n}")

        if st.button("Run Simulated Comparison"):
            if any(std == 0 for _, std, _ in group_data):
                st.error("Standard deviation cannot be zero in any group.")
                return

            if num_groups == 2:
                mean1, std1, n1 = group_data[0]
                mean2, std2, n2 = group_data[1]

                se = np.sqrt((std1**2)/n1 + (std2**2)/n2)
                t_stat = (mean1 - mean2) / se

                df_num = ((std1**2 / n1 + std2**2 / n2) ** 2)
                df_denom = ((std1**2 / n1)**2) / (n1 - 1) + ((std2**2 / n2)**2) / (n2 - 1)

                if df_denom == 0:
                    st.error("Unable to compute degrees of freedom (division by zero).")
                    return

                df_final = df_num / df_denom
                p_val = stats.t.sf(np.abs(t_stat), df_final) * 2

                summary = f"t = {t_stat:.4f}, df = {df_final:.2f}, p = {p_val:.4f}"
                formulas = (
                    f"SE = sqrt((s1²/n1) + (s2²/n2)) = sqrt(({std1:.2f}²/{n1}) + ({std2:.2f}²/{n2})) = {se:.4f}\n"
                    f"t = (mean1 - mean2) / SE = ({mean1:.2f} - {mean2:.2f}) / {se:.4f} = {t_stat:.4f}\n"
                    f"df (Welch's) = {df_final:.2f}"
                )

                st.subheader("Results")
                st.write(summary)
                st.text("Calculation Details")
                st.text(formulas)

                pdf_path = generate_pdf_report(
                    "Simulated Two-Group t-test Report",
                    "This is a simulated comparison of two groups using a t-test.",
                    summary,
                    formulas
                )
                with open(pdf_path, "rb") as f:
                    st.download_button("Download PDF Report", f, file_name="simulated_t_test.pdf")

            else:
                total_n = sum(g[2] for g in group_data)
                grand_mean = sum(g[0] * g[2] for g in group_data) / total_n

                ssb = sum(g[2] * (g[0] - grand_mean)**2 for g in group_data)
                dfb = num_groups - 1
                msb = ssb / dfb

                ssw = sum((g[2] - 1) * g[1]**2 for g in group_data)
                dfw = total_n - num_groups
                msw = ssw / dfw

                f_stat = msb / msw
                p_val = stats.f.sf(f_stat, dfb, dfw)

                summary = f"F = {f_stat:.4f}, df = ({dfb}, {dfw}), p = {p_val:.4f}"
                formulas = (
                    f"Grand Mean = {grand_mean:.4f}\n"
                    f"SSB = Σ n_i*(x̄_i - GM)² = {ssb:.4f}\n"
                    f"MSB = SSB / df_between = {msb:.4f}\n"
                    f"SSW = Σ (n_i - 1)*s_i² = {ssw:.4f}\n"
                    f"MSW = SSW / df_within = {msw:.4f}\n"
                    f"F = MSB / MSW = {f_stat:.4f}"
                )

                st.subheader("Results")
                st.write(summary)
                st.text("Calculation Details")
                st.text(formulas)

                pdf_path = generate_pdf_report(
                    "Simulated ANOVA Report",
                    "This is a simulated comparison of multiple groups using one-way ANOVA.",
                    summary,
                    formulas
                )
                with open(pdf_path, "rb") as f:
                    st.download_button("Download PDF Report", f, file_name="simulated_anova.pdf")

