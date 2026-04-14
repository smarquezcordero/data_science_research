import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load experiment results
df = pd.read_excel("complete_test_sizes.xlsx", sheet_name="Raw_Data")

print(df.head())

alg1 = df[df["Algorithm"].str.contains("Random")]

optimal = alg1.loc[alg1["Total_Tests"].idxmin()]

print("Optimal test size for Random Algorithm:")
print(optimal)

plt.figure()

for d in sorted(alg1["Defective_Size"].unique()):
    subset = alg1[alg1["Defective_Size"] == d]
    plt.plot(subset["Test_Size"], subset["Total_Tests"], marker='o', label=f"d={d}")

plt.xlabel("Test Size")
plt.ylabel("Total Tests")
plt.title("Algorithm 1 Optimization")
plt.legend()
plt.show()


alg2 = df[df["Algorithm"].str.contains("Rectangle")]

overlap_measure = alg2.groupby("Test_Size")["Total_Tests"].var()

print("Variance in Total Tests (proxy for overlap instability):")
print(overlap_measure)

plt.figure()

plt.plot(overlap_measure.index, overlap_measure.values, marker='o')

plt.xlabel("Test Size")
plt.ylabel("Variance of Total Tests")
plt.title("Algorithm 2 Instability")

plt.show()

def factor_pairs(n):
    factors = []
    for i in range(1, int(np.sqrt(n)) + 1):
        if n % i == 0:
            factors.append((i, n // i))
    return factors

aspect_ratios = []

test_sizes = sorted(df["Test_Size"].unique())

for t in test_sizes:
    pairs = factor_pairs(t)

    for a, b in pairs:
        ratio = max(a, b) / min(a, b)
        aspect_ratios.append((t, ratio))

aspect_df = pd.DataFrame(aspect_ratios, columns=["Test_Size", "Aspect_Ratio"])

aspect_summary = aspect_df.groupby("Test_Size")["Aspect_Ratio"].mean()

print(aspect_summary)

alg3 = df[df["Algorithm"].str.contains("Rectangle200")]

merged = alg3.merge(aspect_summary, on="Test_Size")

plt.figure()

plt.scatter(merged["Aspect_Ratio"], merged["Total_Tests"])

plt.xlabel("Aspect Ratio")
plt.ylabel("Total Tests")
plt.title("Aspect Ratio vs Total Tests")

plt.show()

alg3_sorted = alg3.sort_values("Test_Size")

prev_tests = None

for _, row in alg3_sorted.iterrows():

    if prev_tests is not None:
        if row["Total_Tests"] < prev_tests:
            print("Non-monotonic behavior detected:")
            print(row)

    prev_tests = row["Total_Tests"]

for alg in ["Rectangle", "Rectangle200"]:

    subset = df[df["Algorithm"] == alg]

    corr = subset["Test_Size"].corr(subset["FP_Ratio"])

    print(f"{alg} correlation between Test Size and FP:", corr)

alg1_sorted = alg1.sort_values("Test_Size")

diff = alg1_sorted["Total_Tests"].diff()

plt.figure()

plt.plot(alg1_sorted["Test_Size"], diff, marker='o')

plt.xlabel("Test Size")
plt.ylabel("Change in Total Tests")
plt.title("Marginal Benefit of Increasing Pool Size")

plt.show()

best = df.loc[df.groupby(["Test_Size","Defective_Size"])["Total_Tests"].idxmin()]

print(best[["Test_Size","Defective_Size","Algorithm"]])