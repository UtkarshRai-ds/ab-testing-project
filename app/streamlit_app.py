import streamlit as st
import numpy as np
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

st.set_page_config(
    page_title="A/B Test Toolkit",
    layout="wide"
)

# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🧪 A/B Test Toolkit")
    st.caption("Experiment Design & Analysis")
    st.divider()

    page = st.radio(
        "Navigate",
        [
            "📋 Project Overview",
            "📐 Sample Size Calculator",
            "📊 Results Analyzer",
            "📈 Power Curve"
        ],
        label_visibility="collapsed"
    )

    st.divider()
    st.caption("Built by Utkarsh Rai")
    st.caption("A/B Testing · 2026")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — PROJECT OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "📋 Project Overview":
    st.title("A/B Testing Project")
    st.markdown("*End-to-end experiment design and analysis from power analysis to business recommendation*")
    st.divider()

    # ── What this project demonstrates ───────────────────────────────────────
    st.header("What This Project Demonstrates")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
**Phase 1 — Simulation**

A statistical pipeline validated against data with a known ground truth.
Power analysis computed the required sample size, 1,000 experiments
empirically verified the 80% power guarantee, and a peeking simulation
showed the false positive rate tripling under early stopping.
        """)

    with col2:
        st.markdown("""
**Phase 2 — Real Data**

The same validated pipeline applied to a real e-commerce A/B test
(~290,000 rows, Kaggle). Data quality issues, 3,894 mismatched
assignments and duplicate user IDs were surfaced and cleaned before
any analysis ran.
        """)

    st.divider()

    # ── Key findings ──────────────────────────────────────────────────────────
    st.header("Key Findings")

    col1, col2 = st.columns(2)
    with col1:
        st.success("**Phase 1 — Simulation verified:** 777/1,000 experiments detected a genuine 2% lift. Theoretical power was 80% empirical result: 77.7%.")
        st.error("**Type II error demonstrated:** Same 2% lift returned p=0.27 at half the required sample size. B was genuinely better but the test lacked power to see it.")

    with col2:
        st.warning("**Peeking tripled false positive rate:** 14.7% vs 5.1% with five interim checks on null data that nearly 3x of the intended rate.")
        st.info("**Real dataset — practical vs statistical significance:** Experiment was 32x overpowered (145,274 vs 4,444 required). Result: p=0.19, CI [-0.49pp, +0.18pp]. Effect negligible, not just undetectable.")

    st.divider()

    # ── Phase 2 deep dive ─────────────────────────────────────────────────────
    st.header("Phase 2 — Real Dataset Analysis")

    col1, col2, col3 = st.columns(3)
    col1.metric("Original Rows", "294,478")
    col2.metric("Rows Removed", "3,894", delta="-1.32% mismatched/duplicate", delta_color="inverse")
    col3.metric("Clean Dataset", "290,584")

    st.markdown("")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Control Rate", "12.04%")
    col2.metric("Treatment Rate", "11.88%", delta="-0.16 pp", delta_color="inverse")
    col3.metric("P-value", "0.1899", help="Not significant at α=0.05")
    col4.metric("Required N (MDE=2pp)", "4,444", help="Actual N was 145,274 — 32x overpowered")

    st.markdown("")
    st.markdown("""
**Business Recommendation: Do Not Ship**

The 95% confidence interval on lift is [-0.49pp, +0.18pp]. The entire interval
sits below the pre-stated MDE of 2pp. Even the most optimistic plausible outcome
(+0.18pp) is 11x below the threshold defined as business-relevant.

The new page is functionally equivalent to the old one. Equivalence at this scale
means no business case for switching engineering cost and rollout risk are not
justified by an effect this small.

**Key lesson:** With a 32x overpowered experiment, statistical significance becomes
almost irrelevant — the test detects effects too small to matter. Always evaluate
practical significance (does the effect exceed MDE?) alongside p-values.
    """)

    st.divider()

    # ── Limitations and future work ───────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Limitations")
        st.markdown("""
- Simulation uses a simplified binomial model — real experiments involve returning visitors, session effects, and non-independent observations
- MDE of 2pp assumed for Phase 2, not derived from revenue modelling
- No novelty effect correction short-term lifts may reflect curiosity, not genuine preference
- Frequentist only and no sequential testing implemented
- Independence between users assumed and network effects could violate this
        """)

    with col2:
        st.subheader("Future Work")
        st.markdown("""
- Bayesian A/B testing: Beta-Binomial conjugate model alongside frequentist comparison
- Sequential testing (SPRT) for statistically valid early stopping
- Segment analysis: mobile vs desktop, new vs returning users, time-of-day
- Multi-metric testing with Bonferroni/Benjamini-Hochberg correction
- Uplift modelling on Criteo dataset — individual treatment effect heterogeneity
- Interactive peeking demo showing false positive rate climbing in real time
        """)

       
    st.divider()
    st.subheader("Conclusion")
    st.markdown("""
This project started with a simple question: how do you know if a change actually works?
The answer turned out to be more nuanced than running a single test and checking a p-value.
Good experimentation means deciding what you care about before collecting data, understanding
that statistical significance and practical significance are two different things, and knowing
that how you collect and inspect data is just as important as how you analyse it. The real
dataset result was not significant despite 145,000 users per group that is arguably the most
valuable finding.
""")

    st.divider()
    st.markdown("📓 [View full notebook on GitHub](https://github.com/UtkarshRai-ds/ab-testing-project) · Built with Python · statsmodels · scipy · plotly · streamlit")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — SAMPLE SIZE CALCULATOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📐 Sample Size Calculator":
    st.title("Sample Size Calculator")
    st.markdown("Set your experiment parameters **before** collecting any data.")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        baseline = st.slider(
            "Baseline conversion rate (%)",
            min_value=1.0, max_value=50.0,
            value=10.0, step=0.5
        ) / 100

        mde = st.slider(
            "Minimum Detectable Effect (pp)",
            min_value=0.5, max_value=10.0,
            value=2.0, step=0.5
        ) / 100

    with col2:
        alpha = st.select_slider(
            "Significance level (α)",
            options=[0.01, 0.05, 0.10],
            value=0.05
        )

        power = st.select_slider(
            "Statistical power",
            options=[0.70, 0.75, 0.80, 0.85, 0.90],
            value=0.80
        )

    effect_size = proportion_effectsize(baseline + mde, baseline)
    n = NormalIndPower().solve_power(
        effect_size=effect_size,
        alpha=alpha,
        power=power,
        alternative='two-sided'
    )
    n_per_group = int(np.ceil(n))
    n_total     = n_per_group * 2

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Per Group",   f"{n_per_group:,}")
    c2.metric("Total Users", f"{n_total:,}")
    c3.metric("Effect Size", f"{effect_size:.4f}")

    st.info(
        f"To detect a **{mde*100:.1f} pp lift** on a **{baseline*100:.1f}% baseline** "
        f"with **{power*100:.0f}% power** and **α={alpha}**, "
        f"you need **{n_per_group:,} users per group** before looking at results."
    )

    with st.expander("What do these numbers mean?"):
        st.markdown(f"""
- **Baseline rate ({baseline*100:.1f}%):** your current conversion rate before the test
- **MDE ({mde*100:.1f} pp):** smallest lift worth detecting — a business decision, not a statistical one
- **Alpha ({alpha}):** false positive tolerance — {alpha*100:.0f}% chance of declaring a winner when there isn't one
- **Power ({power*100:.0f}%):** probability of detecting a real effect of your MDE size
- **Per group ({n_per_group:,}):** users needed in each arm — commit to this before peeking
        """)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — RESULTS ANALYZER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Results Analyzer":
    st.title("Results Analyzer")
    st.markdown("Enter your experiment results to get a significance test and business recommendation.")
    st.divider()

    from statsmodels.stats.proportion import proportions_ztest, proportion_confint

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Control (A)")
        visitors_a    = st.number_input("Visitors",    min_value=1, value=3835, key="va")
        conversions_a = st.number_input("Conversions", min_value=0, value=368,  key="ca")

    with col2:
        st.subheader("Treatment (B)")
        visitors_b    = st.number_input("Visitors",    min_value=1, value=3835, key="vb")
        conversions_b = st.number_input("Conversions", min_value=0, value=450,  key="cb")

    mde_analyzer = st.slider(
        "Your pre-set MDE (pp) — for practical significance check",
        min_value=0.5, max_value=10.0, value=2.0, step=0.5
    ) / 100

    st.divider()

    if conversions_a > visitors_a or conversions_b > visitors_b:
        st.error("Conversions cannot exceed visitors.")
    else:
        rate_a = conversions_a / visitors_a
        rate_b = conversions_b / visitors_b
        lift   = rate_b - rate_a

        stat, p_value = proportions_ztest(
            np.array([conversions_b, conversions_a]),
            np.array([visitors_b, visitors_a]),
            alternative='two-sided'
        )

        ci_a    = proportion_confint(conversions_a, visitors_a, alpha=0.05, method='normal')
        ci_b    = proportion_confint(conversions_b, visitors_b, alpha=0.05, method='normal')
        ci_low  = (ci_b[0] - ci_a[1]) * 100
        ci_high = (ci_b[1] - ci_a[0]) * 100

        c1, c2, c3 = st.columns(3)
        c1.metric("Rate A", f"{rate_a*100:.2f}%")
        c2.metric("Rate B", f"{rate_b*100:.2f}%", delta=f"{lift*100:+.2f} pp")
        c3.metric("P-value", f"{p_value:.4f}")

        st.write(f"**95% CI on lift:** [{ci_low:.2f} pp, {ci_high:.2f} pp]")

        stat_sig = p_value < 0.05
        prac_sig = abs(lift) >= mde_analyzer

        if stat_sig and prac_sig and lift > 0:
            st.success("✅ SHIP IT — Statistically AND practically significant positive lift.")
        elif stat_sig and prac_sig and lift < 0:
            st.error("🚫 DO NOT SHIP — Statistically significant NEGATIVE lift exceeds MDE.")
        elif stat_sig and not prac_sig:
            st.warning("⚠️ DO NOT SHIP — Significant but lift is below your MDE. Practically meaningless.")
        elif not stat_sig and ci_low > 0:
            st.info("🔍 INCONCLUSIVE — Not significant but CI is entirely positive. Consider more data.")
        else:
            st.warning("⚠️ DO NOT SHIP — No sufficient evidence of meaningful improvement.")

        with st.expander("How to interpret this"):
            st.markdown(f"""
- **P-value ({p_value:.4f}):** {'Below 0.05 — statistically significant' if stat_sig else 'Above 0.05 — cannot rule out random chance'}
- **Lift ({lift*100:+.2f} pp):** {'Exceeds' if prac_sig else 'Below'} your MDE of {mde_analyzer*100:.1f} pp — {'business relevant' if prac_sig else 'NOT business relevant'}
- **CI [{ci_low:.2f}, {ci_high:.2f}] pp:** {'Entirely above zero — strong evidence of positive effect' if ci_low > 0 else 'Crosses zero — true effect direction is uncertain' if ci_high > 0 else 'Entirely below zero — B is likely worse'}
            """)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — POWER CURVE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Power Curve":
    st.title("Power Curve")
    st.markdown("See how required sample size changes as your MDE changes.")
    st.divider()

    import plotly.graph_objects as go

    col1, col2 = st.columns(2)
    with col1:
        pc_baseline = st.slider(
            "Baseline conversion rate (%)",
            min_value=1.0, max_value=50.0,
            value=10.0, step=0.5, key="pc_base"
        ) / 100
        pc_alpha = st.select_slider(
            "Significance level (α)",
            options=[0.01, 0.05, 0.10],
            value=0.05, key="pc_alpha"
        )
    with col2:
        pc_power = st.select_slider(
            "Statistical power",
            options=[0.70, 0.75, 0.80, 0.85, 0.90],
            value=0.80, key="pc_power"
        )
        highlight_mde = st.slider(
            "Highlight MDE (pp)",
            min_value=0.5, max_value=10.0,
            value=2.0, step=0.5, key="pc_mde"
        ) / 100

    mde_range = np.arange(0.5, 10.5, 0.5) / 100
    n_values  = []
    for mde_val in mde_range:
        es  = proportion_effectsize(pc_baseline + mde_val, pc_baseline)
        n_v = NormalIndPower().solve_power(
            effect_size=es, alpha=pc_alpha,
            power=pc_power, alternative='two-sided'
        )
        n_values.append(int(np.ceil(n_v)))

    es_h = proportion_effectsize(pc_baseline + highlight_mde, pc_baseline)
    n_h  = int(np.ceil(NormalIndPower().solve_power(
        effect_size=es_h, alpha=pc_alpha,
        power=pc_power, alternative='two-sided'
    )))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=mde_range * 100, y=n_values,
        mode='lines', name='Required N per group',
        line=dict(color='#2E75B6', width=3)
    ))
    fig.add_trace(go.Scatter(
        x=[highlight_mde * 100], y=[n_h],
        mode='markers+text',
        name=f'Your MDE: {highlight_mde*100:.1f}pp',
        marker=dict(color='#C00000', size=12),
        text=[f"  N={n_h:,}"],
        textposition='middle right',
        textfont=dict(color='#C00000', size=13)
    ))
    fig.update_layout(
        xaxis_title="Minimum Detectable Effect (percentage points)",
        yaxis_title="Required users per group",
        template="plotly_dark",
        height=440,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    st.plotly_chart(fig, width="stretch")

    c1, c2 = st.columns(2)
    c1.metric(f"N per group at MDE = {highlight_mde*100:.1f}pp", f"{n_h:,}")
    c2.metric("Total users needed", f"{n_h*2:,}")

    st.info(
        f"At a **{pc_baseline*100:.1f}% baseline**, detecting a **{highlight_mde*100:.1f}pp lift** "
        f"with **{pc_power*100:.0f}% power** requires **{n_h:,} users per group**. "
        f"Halving the MDE roughly quadruples the required sample size."
    )