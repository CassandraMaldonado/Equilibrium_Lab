# Equilibrium Lab

**A marketplace experimentation and policy simulator for two-sided products.**

I built Equilibrium Lab to answer a harder question than “did the metric go up?”: when a product change affects both sides of a marketplace, did it create real value or simply move wait time, earnings and availability from one group to another?

The included scenario evaluates a new matching policy across geographic zones using a switchback experiment. It measures rider conversion, pickup time, driver utilization, earnings, cancellations, marketplace efficiency and distributional impact before recommending whether to scale, iterate or stop.

## The questions

- Did the matching policy improve completed trips without harming marketplace health?
- Were gains caused by the policy or by time-of-day and zone differences?
- Did riders and drivers both benefit?
- Were improvements shared across neighborhoods and demand conditions?
- Which zones should receive the policy next?

## What makes this project different

- Uses a **zone bytime switchback design** to reduce interference between treatment and control.
- Estimates effects with **cluster uncertainty** instead of treating every event as independent.
- Runs **sample-ratio and pre-trend checks** before interpreting results.
- Measures both sides of the marketplace through rider, driver and system guardrails.
- Reports **heterogeneous effects** by demand pressure and neighborhood access level.
- Uses a constrained optimizer to recommend rollout while protecting minimum service coverage.
- Keeps the statistical evidence separate from the final product decision.


## Run the project

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
streamlit run streamlit_app.py
```

You can also run the analysis directly:

```bash
python -m equilibrium_lab.cli --seed 29 --zones 18
```
