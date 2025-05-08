import streamlit as st
from power_analysis import run_power_analysis
from group_comparison import run_group_comparison
from PIL import Image

st.set_page_config(page_title="nSleuth", layout="wide")

with st.sidebar:
    st.header("Reference Guide")

    st.markdown("### Effect Size (Cohen's d)")
    st.markdown("""
    | Size | Interpretation       |
    |------|----------------------|
    | 0.2  | Small effect         |
    | 0.5  | Medium effect        |
    | 0.8  | Large effect         |
    | 1.2+ | Very large effect    |
    """, unsafe_allow_html=True)

    st.markdown("### Common Statistical Tests")
    st.markdown("""
    | Test                 | Use Case                                | Parametric? |
    |----------------------|------------------------------------------|-------------|
    | t-test (independent) | Compare 2 unrelated group means         | Yes       |
    | t-test (paired)      | Compare pre/post or matched samples     | Yes       |
    | ANOVA                | Compare 3+ group means                  | Yes       |
    | Chi-square           | Test association between categories     | No        |
    | Proportion test      | Compare success rates (e.g. A/B)        | Yes       |
    | Mann-Whitney U       | Compare 2 groups, non-parametric alt.   | No        |
    | Kruskal-Wallis       | ANOVA alternative for ranked data       | No        |
    """, unsafe_allow_html=True)

    st.markdown("### Assumptions to Watch For")
    st.markdown("""
    - **Parametric tests** assume:
      - Normal distribution of the outcome variable
      - Equal variances between groups (for t-tests, ANOVA)
      - Independent observations  
    - **Non-parametric tests** do **not** require normality, but often have less power
    """)

    st.markdown("### Key Terms")
    st.markdown("""
    - **Effect size**: How big the difference is
    - **Power**: Probability of detecting a true effect (commonly 0.80)
    - **Alpha (α)**: Significance level (commonly 0.05)
    - **p-value**: Probability of observing the result (or more extreme) if the null is true
    """)

    st.markdown("---")
    st.header("Educational Resources")
    st.markdown("""
    - [UCLA Effect Size Guide](https://stats.oarc.ucla.edu/)
    - [Statsmodels Documentation](https://www.statsmodels.org/)
    - [Harvard Power Analysis Guide](https://projects.iq.harvard.edu/rtc/tools/power)
    - [StatQuest YouTube (simple stats)](https://www.youtube.com/user/joshstarmer)
    """)






st.markdown("""
<h1 style='text-align: center; font-family: "Georgia", monospace; color: #555;'>
nSleuth
</h1>""", unsafe_allow_html=True)


tab0, tab1, tab2 = st.tabs([
    "Home",
    "Power Analysis",
    "Group Comparison"
])

# Home page content
with tab0:
    st.markdown("""
Not sure where to start with statistical tests? You're not alone — and you're in the right place.

**nSleuth** was created for researchers, students, and curious thinkers who want to do things right, even if stats feels a bit overwhelming at first. Whether you're planning your first experiment or double-checking your analysis, nSleuth helps you:

- Estimate sample sizes
- Visualize power curves
- Compare group differences

Let’s figure it out together.

""")
    st.markdown("---")
    st.caption("Developed by Jamie Anne Mortel")

# Power analysis tab
with tab1:
    run_power_analysis()

# Group comparison tab
with tab2:
    run_group_comparison()
