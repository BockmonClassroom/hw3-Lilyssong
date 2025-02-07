import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind, ttest_rel

# Load datasets
t1 = pd.read_csv("Data/t1_user_active_min.csv")
t2 = pd.read_csv("Data/t2_user_variant.csv")
t3 = pd.read_csv("Data/t3_user_active_min_pre.csv")
t4 = pd.read_csv("Data/t4_user_attributes.csv")

# Merge experiment assignment with post-experiment active minutes
df = t1.merge(t2, on="uid")
df_total = df.groupby(["uid", "variant_number"])["active_mins"].sum().reset_index()

# Save initial summary
with open("results.txt", "w") as f:
    f.write("### Initial Data Summary ###\n")
    f.write(str(df_total.describe()) + "\n\n")

# Split control & treatment groups
control = df_total[df_total['variant_number'] == 0]['active_mins']
treatment = df_total[df_total['variant_number'] == 1]['active_mins']

# Compute mean and median
control_mean, control_median = control.mean(), control.median()
treatment_mean, treatment_median = treatment.mean(), treatment.median()

# Perform independent t-test
t_stat, p_value = ttest_ind(control, treatment, equal_var=False)

# Save results
with open("results.txt", "a") as f:
    f.write("### T-Test Results ###\n")
    f.write(f"Control Group - Mean: {control_mean}, Median: {control_median}\n")
    f.write(f"Treatment Group - Mean: {treatment_mean}, Median: {treatment_median}\n")
    f.write(f"T-statistic: {t_stat}, P-value: {p_value}\n\n")

# Detect Outliers using IQR method
Q1 = df_total['active_mins'].quantile(0.25)
Q3 = df_total['active_mins'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

df_clean = df_total[(df_total['active_mins'] >= lower_bound) & (df_total['active_mins'] <= upper_bound)]

# Save cleaned summary
with open("results.txt", "a") as f:
    f.write("### Data After Outlier Removal ###\n")
    f.write(str(df_clean.describe()) + "\n\n")

# Merge pre-experiment data
t3_total = t3.groupby("uid")["active_mins"].sum().reset_index()
df_final = df_clean.merge(t3_total, on="uid", suffixes=("_post", "_pre"))

# Compute change in active minutes
df_final["change"] = df_final["active_mins_post"] - df_final["active_mins_pre"]

# Perform paired t-test
t_stat_pre, p_value_pre = ttest_rel(df_final["active_mins_pre"], df_final["active_mins_post"])

# Save results
with open("results.txt", "a") as f:
    f.write("### Pre vs. Post Experiment Analysis ###\n")
    f.write(f"Paired T-Test - T-statistic: {t_stat_pre}, P-value: {p_value_pre}\n\n")

# Merge with user attributes
df_user = df_final.merge(t4, on="uid")

# Compute mean change by user type
user_type_means = df_user.groupby("user_type")["change"].mean()

# Save user analysis
with open("results.txt", "a") as f:
    f.write("### User Attribute Analysis ###\n")
    f.write(str(user_type_means) + "\n\n")

# Box plot visualization
plt.figure(figsize=(8, 5))
plt.boxplot([control, treatment], labels=["Control", "Treatment"])
plt.title("User Active Minutes Distribution (Before Outlier Removal)")
plt.savefig("boxplot_before.png")
plt.close()

plt.figure(figsize=(8, 5))
plt.boxplot([df_clean[df_clean['variant_number'] == 0]['active_mins'], df_clean[df_clean['variant_number'] == 1]['active_mins']], labels=["Control", "Treatment"])
plt.title("User Active Minutes Distribution (After Outlier Removal)")
plt.savefig("boxplot_after.png")
plt.close()

print("Analysis completed! Results are saved in results.txt and boxplot images.")