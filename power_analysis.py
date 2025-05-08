import streamlit as st
import matplotlib.pyplot as plt
from statsmodels.stats.power import (
    TTestIndPower,
    TTestPower,
    FTestAnovaPower,
    GofChisquarePower,
    NormalIndPower
)

def get_power_analysis_object(test_type):
    return {
        "t-test (independent)": TTestIndPower(),
        "t-test (paired)": TTestPower(),
        "ANOVA": FTestAnovaPower(),
        "Proportion comparison": NormalIndPower(),
        "Chi-square test": GofChisquarePower()
    }.get(test_type, None)

def calculate_sample_size(test_type, effect_size, alpha, power, num_groups=2):
    analysis = get_power_analysis_object(test_type)
    if not analysis:
        return None
    if test_type == "ANOVA":
        return analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power, k_groups=num_groups)
    return analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power)

def plot_power_curve(test_type, effect_size, alpha, desired_power, num_groups=2):
    analysis = get_power_analysis_object(test_type)
    if not analysis:
        return None
    sample_sizes = range(10, 300)
    powers = []
    for n in sample_sizes:
        try:
            if test_type == "ANOVA":
                powers.append(analysis.power(effect_size=effect_size, nobs=n, alpha=alpha, k_groups=num_groups))
            elif test_type in ["t-test (independent)", "Proportion comparison"]:
                powers.append(analysis.power(effect_size=effect_size, nobs1=n, alpha=alpha))
            elif test_type in ["Chi-square test", "t-test (paired)"]:
                powers.append(analysis.power(effect_size=effect_size, nobs=n, alpha=alpha))
        except:
            powers.append(None)

    fig, ax = plt.subplots()
    ax.plot(sample_sizes, powers, label="Power Curve")
    ax.axhline(y=desired_power, color='r', linestyle='--', label="Desired Power")
    ax.set_xlabel("Sample Size")
    ax.set_ylabel("Power")
    ax.set_title("Power vs. Sample Size")
    ax.legend()
    return fig

def run_power_analysis():
    st.markdown("""
Welcome to **nSleuth**, a tool for researchers who want to detect the right effect — with the right sample size.

1. Pick your test  
2. Enter effect size, alpha, and desired power  
3. Get an estimate of the participants needed per group  
    """)

    st.subheader("1. Pick Your Test")
    test_type = st.selectbox("Test type:", [
        "t-test (independent)",
        "t-test (paired)",
        "ANOVA",
        "Proportion comparison",
        "Chi-square test"
    ])

    st.subheader("2. Enter Your Parameters")
    effect_size = st.number_input("Effect size (e.g., 0.5 = medium)", min_value=0.01, value=0.5)
    alpha = st.number_input("Significance level (alpha)", min_value=0.001, max_value=0.2, value=0.05)
    desired_power = st.number_input("Desired power", min_value=0.01, max_value=0.99, value=0.80)

    num_groups = 2
    if test_type == "ANOVA":
        num_groups = st.number_input("Number of groups (for ANOVA)", min_value=2, value=3)

    if st.button("Calculate Sample Size"):
        result = calculate_sample_size(test_type, effect_size, alpha, desired_power, num_groups)
        if result:
            per_group = int(result) + 1
            st.success(f"You need approximately **{per_group} participants per group**.")
            total = per_group * (num_groups if test_type == "ANOVA" else 2)
            st.write(f"**Total Sample Size:** {total}")
        else:
            st.error("Calculation failed. Please check your inputs or selected test type.")

    st.subheader("3. Optional: Power Curve")
    if st.checkbox("Show power vs. sample size plot"):
        fig = plot_power_curve(test_type, effect_size, alpha, desired_power, num_groups)
        if fig:
            st.pyplot(fig)
        else:
            st.warning("Power curve could not be generated.")
