import streamlit as st
import numpy as np
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="A/B Test Toolkit",
    layout="centered"
)

st.title("A/B Test Toolkit")
st.caption("Power analysis · Results analyzer · Power curve")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📐 Sample Size Calculator",
    "📊 Results Analyzer",
    "📈 Power Curve"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SAMPLE SIZE CALCULATOR
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.header("Sample Size Calculator")
    st.write("Set your experiment parameters before collecting any data.")

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

    # ── Calculation ───────────────────────────────────────────────────────────
    effect_size = proportion_effectsize(baseline + mde, baseline)
    n = NormalIndPower().solve_power(
        effect_size=effect_size,
        alpha=alpha,
        power=power,
        alternative='two-sided'
    )
    n_per_group = int(np.ceil(n))
    n_total     = n_per_group * 2

    # ── Output ────────────────────────────────────────────────────────────────
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Per Group",  f"{n_per_group:,}")
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
- **Alpha ({alpha}):** your false positive tolerance — {alpha*100:.0f}% chance of declaring a winner when there isn't one
- **Power ({power*100:.0f}%):** probability of detecting a real effect of your MDE size
- **Per group ({n_per_group:,}):** users needed in EACH arm — commit to this before peeking
        """)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — RESULTS ANALYZER
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.header("Results Analyzer")
    st.write("Enter your experiment results to get a significance test and business recommendation.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Control (A)")
        visitors_a = st.number_input("Visitors", min_value=1, value=3835, key="va")
        conversions_a = st.number_input("Conversions", min_value=0, value=368, key="ca")

    with col2:
        st.subheader("Treatment (B)")
        visitors_b = st.number_input("Visitors", min_value=1, value=3835, key="vb")
        conversions_b = st.number_input("Conversions", min_value=0, value=450, key="cb")

    mde_analyzer = st.slider(
        "Your pre-set MDE (pp) — for practical significance check",
        min_value=0.5, max_value=10.0, value=2.0, step=0.5
    ) / 100

    st.divider()

    # ── Validation ────────────────────────────────────────────────────────────
    if conversions_a > visitors_a or conversions_b > visitors_b:
        st.error("Conversions cannot exceed visitors.")
    else:
        rate_a = conversions_a / visitors_a
        rate_b = conversions_b / visitors_b
        lift   = rate_b - rate_a

        # ── Significance test ─────────────────────────────────────────────────
        from statsmodels.stats.proportion import proportions_ztest, proportion_confint
        import numpy as np

        stat, p_value = proportions_ztest(
            np.array([conversions_b, conversions_a]),
            np.array([visitors_b, visitors_a]),
            alternative='two-sided'
        )

        ci_a = proportion_confint(conversions_a, visitors_a, alpha=0.05, method='normal')
        ci_b = proportion_confint(conversions_b, visitors_b, alpha=0.05, method='normal')
        ci_low  = (ci_b[0] - ci_a[1]) * 100
        ci_high = (ci_b[1] - ci_a[0]) * 100

        # ── Metrics ───────────────────────────────────────────────────────────
        c1, c2, c3 = st.columns(3)
        c1.metric("Rate A", f"{rate_a*100:.2f}%")
        c2.metric("Rate B", f"{rate_b*100:.2f}%",
                  delta=f"{lift*100:+.2f} pp")
        c3.metric("P-value", f"{p_value:.4f}")

        st.write(f"**95% CI on lift:** [{ci_low:.2f} pp, {ci_high:.2f} pp]")

        # ── Decision ──────────────────────────────────────────────────────────
        stat_sig  = p_value < 0.05
        prac_sig  = abs(lift) >= mde_analyzer

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
- **P-value ({p_value:.4f}):** {'Below 0.05 — result is statistically significant' if stat_sig else 'Above 0.05 — cannot rule out random chance'}
- **Lift ({lift*100:+.2f} pp):** {'Exceeds' if prac_sig else 'Below'} your MDE of {mde_analyzer*100:.1f} pp — {'business relevant' if prac_sig else 'NOT business relevant'}
- **CI [{ci_low:.2f}, {ci_high:.2f}] pp:** {'Entirely above zero — strong evidence of positive effect' if ci_low > 0 else 'Crosses zero — true effect direction is uncertain' if ci_high > 0 else 'Entirely below zero — B is likely worse'}
            """)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — POWER CURVE
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.header("Power Curve")
    st.write("See how required sample size changes as your MDE changes. Move the sliders to explore the trade-off.")

    import plotly.graph_objects as go

    col1, col2 = st.columns(2)
    with col1:
        pc_baseline = st.slider(
            "Baseline conversion rate (%)",
            min_value=1.0, max_value=50.0,
            value=10.0, step=0.5,
            key="pc_base"
        ) / 100
        pc_alpha = st.select_slider(
            "Significance level (α)",
            options=[0.01, 0.05, 0.10],
            value=0.05,
            key="pc_alpha"
        )
    with col2:
        pc_power = st.select_slider(
            "Statistical power",
            options=[0.70, 0.75, 0.80, 0.85, 0.90],
            value=0.80,
            key="pc_power"
        )
        highlight_mde = st.slider(
            "Highlight MDE (pp)",
            min_value=0.5, max_value=10.0,
            value=2.0, step=0.5,
            key="pc_mde"
        ) / 100

    # ── Compute curve ─────────────────────────────────────────────────────────
    mde_range = np.arange(0.5, 10.5, 0.5) / 100
    n_values  = []

    for mde_val in mde_range:
        es  = proportion_effectsize(pc_baseline + mde_val, pc_baseline)
        n_v = NormalIndPower().solve_power(
            effect_size=es,
            alpha=pc_alpha,
            power=pc_power,
            alternative='two-sided'
        )
        n_values.append(int(np.ceil(n_v)))

    # ── Highlighted point ─────────────────────────────────────────────────────
    es_highlight = proportion_effectsize(pc_baseline + highlight_mde, pc_baseline)
    n_highlight  = int(np.ceil(NormalIndPower().solve_power(
        effect_size=es_highlight,
        alpha=pc_alpha,
        power=pc_power,
        alternative='two-sided'
    )))

    # ── Plot ──────────────────────────────────────────────────────────────────
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=mde_range * 100,
        y=n_values,
        mode='lines',
        name='Required N per group',
        line=dict(color='#2E75B6', width=3)
    ))

    fig.add_trace(go.Scatter(
        x=[highlight_mde * 100],
        y=[n_highlight],
        mode='markers+text',
        name=f'Your MDE: {highlight_mde*100:.1f}pp',
        marker=dict(color='#C00000', size=12),
        text=[f"  N={n_highlight:,}"],
        textposition='middle right',
        textfont=dict(color='#C00000', size=13)
    ))

    fig.update_layout(
        xaxis_title="Minimum Detectable Effect (percentage points)",
        yaxis_title="Required users per group",
        template="plotly_dark",
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    st.plotly_chart(fig, width="stretch")

    st.metric(
        f"N per group at MDE = {highlight_mde*100:.1f}pp",
        f"{n_highlight:,}",
        delta=f"Total: {n_highlight*2:,}"
    )

    st.info(
        f"At a **{pc_baseline*100:.1f}% baseline**, detecting a **{highlight_mde*100:.1f}pp lift** "
        f"with **{pc_power*100:.0f}% power** requires **{n_highlight:,} users per group**. "
        f"Halving the MDE roughly quadruples the required sample size."
    )