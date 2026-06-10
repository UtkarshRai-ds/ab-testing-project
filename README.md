# A/B Testing Project

End-to-end experiment design and analysis — from power analysis to business recommendation.

## Live Demo
[A/B Test Toolkit](your-deployed-link-here)

## Project Summary
This project demonstrates the full lifecycle of a statistically rigorous A/B test. Built in two phases: Phase 1 validates the statistical pipeline against simulated data with a known ground truth. Phase 2 applies the same pipeline to a real e-commerce dataset with unknown outcomes.

## Key Findings
- Empirical power matched theoretical: 777/1,000 simulated experiments detected a genuine 2% lift (theoretical: 80%)
- Underpowered test missed a real effect: same 2% lift returned p=0.27 at half the sample size (Type II error)
- Peeking tripled false positive rate: 14.7% vs 5.1% with five interim checks on null data
- Real dataset: experiment was 32x overpowered yet returned p=0.19 i.e. the effect was genuinely negligible and not just undetectable.

## Project Structure
ab-testing-project/
├── notebook/ab_analysis.ipynb   # Full analysis: simulation + real data
├── app/streamlit_app.py         # Interactive toolkit: calculator, analyzer, power curve
├── data/                        # Dataset not committed — see Data section below
└── requirements.txt

## Setup
conda create -n ab-testing python=3.11 -y
conda activate ab-testing
pip install -r requirements.txt

Run the notebook: open notebook/ab_analysis.ipynb in VS Code and select the ab-testing kernel.

Run the app: streamlit run app/streamlit_app.py

## Data
Phase 2 uses the E-commerce A/B Test dataset from Kaggle (https://www.kaggle.com/datasets/zhangluyuan/ab-testing), approximately 290,000 rows. Download ab_data.csv and place it in the data/ folder.

## Limitations
- Simulated data uses a simplified binomial model. Real experiments involve more complex user behaviour returning visitors, session effects, and non-independent observations.
- The real dataset (Phase 2) has an unknown true effect. Conclusions are based on inference, not ground truth verification as in Phase 1.
- MDE of 2 percentage points is assumed for Phase 2. A real business would derive this from revenue modelling, not assumption.
- The significance test assumes independence between users. In practice, network effects or shared sessions can violate this assumption.
- No novelty effect correction applied. Short-term lifts may reflect user curiosity about a changed design rather than genuine preference.
- Sequential testing (SPRT, Bayesian methods) is not implemented. The frequentist framework used here requires full sample collection before inference.

## Future Work
- Bayesian A/B testing: implement a Beta-Binomial conjugate model alongside the frequentist pipeline and compare conclusions particularly on the real dataset where the frequentist result was borderline
- Sequential testing: add a SPRT (Sequential Probability Ratio Test) implementation that allows statistically valid early stopping, directly addressing the peeking problem demonstrated in Phase 1
- Segment analysis: break down results by user segment (new vs returning, mobile vs desktop, time of day) to surface heterogeneous treatment effects, the case where overall significance masks harm to a subgroup
- Multi-metric testing: extend beyond conversion rate to handle multiple metrics simultaneously with appropriate corrections (Bonferroni, Benjamini-Hochberg) to control family-wise error rate
- Uplift modelling: apply the Criteo Uplift dataset to model individual treatment effect heterogeneity , identifying which users benefit most from a change rather than estimating an average effect
- Streamlit peeking demo: add an interactive simulation showing false positive rate climbing in real time as the user adjusts the number of interim checks

## Stack
Python · statsmodels · scipy · numpy · pandas · plotly · streamlit · Jupyter
