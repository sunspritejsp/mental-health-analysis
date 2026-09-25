from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

# path set up
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "survey.csv"
FIG_DIR = BASE_DIR / "figures"
FIG_DIR.mkdir(exist_ok=True)

# load and clean dataset
df = pd.read_csv(DATA_PATH)
df = df[(df["Age"] > 10) & (df["Age"] < 100)].copy()

features = ["Age", "Gender", "treatment", "family_history", "work_interfere"]
df = df[features].dropna().copy()

df["treatment_num"] = df["treatment"].map({"Yes": 1, "No": 0})
df["family_history_num"] = df["family_history"].map({"Yes": 1, "No": 0})
df["work_interfere_num"] = df["work_interfere"].map(
    {"Never": 0, "Rarely": 1, "Sometimes": 2, "Often": 3}
)

print(f"Dataset ready. Sample size: N = {len(df)}")
print(f"Overall mean age: {df['Age'].mean():.2f}")

# ---------------------------------------------------------
# Hypothesis 1: Age vs Treatment (Welch's t-test)
# ---------------------------------------------------------
treated = df[df["treatment_num"] == 1]["Age"]
untreated = df[df["treatment_num"] == 0]["Age"]

t_stat, p_val1 = stats.ttest_ind(treated, untreated, equal_var=False)
print(f"\nH1 (t-test): t = {t_stat:.4f} | p = {p_val1:.4f}")
print("H1 Decision:", "Reject H0" if p_val1 < 0.05 else "Fail to reject H0")

plt.figure(figsize=(7, 4))
plt.hist(
    untreated, bins=20, alpha=0.5, label="Untreated", color="salmon", ec="black"
)
plt.hist(treated, bins=20, alpha=0.5, label="Treated", color="teal", ec="black")
plt.title("Age Distribution by Treatment Status")
plt.xlabel("Age")
plt.ylabel("Frequency")
plt.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "age_distribution.png")
plt.close()


# ---------------------------------------------------------
# Hypothesis 2: Family History vs Treatment (Proportions)
# ---------------------------------------------------------
def get_ci(successes, n):
  p = successes / n
  margin = 1.96 * np.sqrt(p * (1 - p) / n)
  return p, p - margin, p + margin


group_fam = df[df["family_history_num"] == 1]
group_nofam = df[df["family_history_num"] == 0]

p_fam, low_fam, high_fam = get_ci(
    group_fam["treatment_num"].sum(), len(group_fam)
)
p_nofam, low_nofam, high_nofam = get_ci(
    group_nofam["treatment_num"].sum(), len(group_nofam)
)

print(f"\nH2 (Proportions): With History = {p_fam:.1%}, No History = {p_nofam:.1%}")
overlaps = not (high_fam < low_nofam or high_nofam < low_fam)
print(
    "H2 Decision:",
    "Fail to reject H0" if overlaps else "Reject H0 (Significant difference)",
)

plt.figure(figsize=(6, 4))
plt.bar(
    ["No Family History", "With Family History"],
    [p_nofam * 100, p_fam * 100],
    color=["#95a5a6", "#3498db"],
)
plt.ylabel("Treatment Seeking Rate (%)")
plt.title("Treatment by Family History")
plt.ylim(0, 100)
plt.tight_layout()
plt.savefig(FIG_DIR / "family_history_treatment.png")
plt.close()

# ---------------------------------------------------------
# Hypothesis 3: Age vs Workplace Interference (Pearson Correlation)
# ---------------------------------------------------------
corr, p_val3 = stats.pearsonr(df["Age"], df["work_interfere_num"])
print(f"\nH3 (Pearson): r = {corr:.4f} | p = {p_val3:.4f}")

print(
    "H3 Decision:",
    "Reject H0"
    if p_val3 < 0.05
    else "Fail to reject H0 (No significant correlation)",
)

plt.figure(figsize=(6, 4))
plt.scatter(df["Age"], df["work_interfere_num"], alpha=0.3, color="navy")
plt.yticks([0, 1, 2, 3], ["Never", "Rarely", "Sometimes", "Often"])
plt.xlabel("Age")
plt.ylabel("Interference Level")
plt.title("Age vs Workplace Interference")
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig(FIG_DIR / "age_vs_work_interference.png")
plt.close()

print("\nDone! Visualizations saved to /figures.")