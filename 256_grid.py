import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
import random
from collections import Counter

def create_model(size=256, num_ones=32, seed=1):
    if seed is not None:
        np.random.seed(seed)

    grid = np.zeros((size, size), dtype=int)

    indices = np.random.choice(size * size, num_ones, replace=False)
    rows, cols = np.unravel_index(indices, (size, size))
    grid[rows, cols] = 1

    return grid

model = create_model()
print("Model grid:")
print(model)

size = model.shape[0]

positions = [
    (r + 1, c + 1)
    for r in range(size)
    for c in range(size)
]

S = set()
for r in range(size):
    for c in range(size):
        if model[r, c] == 1:
            S.add((r + 1, c + 1))

print("\nDefected items:")
print(S)

class Test_Experiment:
    def __init__(self, positions, infected_set, test_size, label="", seed=None):
               self.positions = positions
               self.infected_set = infected_set
               self.test_size = test_size
               self.label = label
               self.seed = seed

               self.tests = []
               self.results = []
               self.history = []
               self.rectangle_stats = []
               self.rectangles_200_info = []

               self.negative_points = set()
               self.positive_points = set()
               self.positive_counter = Counter()
               self.repeated_positive_points = set()
               self.candidates = set()
    
    
    def clasify_tests(self, test):
            return "positive" if any (item in self.infected_set for item in test) else "negative"
    
    #algorithm 1
    def random_test(self):
            indices = np.random.choice(len(self.positions), self.test_size, replace= False)
            test= [self.positions[i] for i in indices]
            return test
         
    #algorithm 2
    def rectangle_test(self):
        grid_size = int(len(self.positions) ** 0.5)

        #if we don't want to use mulriples of 200 and use x1 randomly (x2 rounding up)
        x1 = np.random.randint(1, grid_size + 1)
        x2 = int(np.ceil(self.test_size / x1))
        #keeping in mind that test can be bigger (ex. x1=33, x2=7, rec=231)

        r = np.random.randint(0, grid_size)
        c = np.random.randint(0, grid_size)

        rectangle = []
        for i in range(x1):
            for j in range(x2):
                new_r = r + i
                new_c = c + j
                if new_r < grid_size and new_c < grid_size:
                    rectangle.append((new_r + 1, new_c + 1))

        actual_size = len(rectangle)
        shrunk = actual_size < self.test_size

        self.rectangle_stats.append({
            "intended_size": self.test_size,
            "actual_size": actual_size,
            "shrunk": shrunk,
            "shape": (x1, x2)
        })

        return rectangle
    
    def get_shrunk_sizes(self, sample_size=50):
       
        shrunk_sizes = [s["actual_size"] for s in self.rectangle_stats if s["shrunk"]]
        if not shrunk_sizes:
            print("No shrunk rectangles found.")
            return

        sample_size = min(sample_size, len(shrunk_sizes))
        sample = random.sample(shrunk_sizes, sample_size)

        print("Total tests:", len(self.rectangle_stats))
        print("Not shrunk:", len(self.rectangle_stats) - len(shrunk_sizes))

        return sample
    
    def run(self, mode = "random", strategy="eliminate_negatives",max_tests = 100000):
            if self.seed is not None:
                np.random.seed(self.seed)

            self.tests.clear()
            self.results.clear()
            self.history.clear()
            self.negative_points.clear()
            self.positive_points.clear()
            self.positive_counter.clear()
            self.candidates.clear()

            self.candidates = set(self.positions)
            
            num_defective = len(self.infected_set)
        
            for t in range(1, max_tests + 1):
                # Select test based on mode
                if mode == "random":
                    test = self.random_test()
                elif mode == "rectangle":
                    test = self.rectangle_test()
                elif mode == "rectangle_200":
                    test = self.rectangle_200()
            
                result = self.clasify_tests(test)
                self.tests.append(test)
                self.results.append(result)

                # Update candidates using the eliminate_negatives logic
                if strategy == "eliminate_negatives":
                    if result == "negative":
                        self.candidates -= set(test)

                elif strategy == "positive_minus_negative":
                    if result == "negative":
                        self.negative_points.update(test)
                    else:
                        self.positive_points.update(test)

                    self.candidates = self.positive_points - self.negative_points

                false_positives = self.candidates - self.infected_set
                false_negatives = self.infected_set - self.candidates
            
                ## Calculate FP Ratio (Ratio of extra items to real defective items)
                
                fp_ratio_0 = len(false_positives) / num_defective if num_defective > 0 else 0
                
                fp_ratio = len(self.candidates) / num_defective if num_defective > 0 else 0
                self.history.append({
                    "tests so far": t,
                    "false positives": len(false_positives),
                    "false negatives": len(false_negatives),
                    "fp_ratio": fp_ratio,
                    "fp_ratio_0": fp_ratio_0
                })

                # New Stop Condition: stop when ratio...
                if fp_ratio < 2:
                    break
            
                if t >= max_tests:
                    break
    
    def compare_candidates(self):
        return self.infected_set.intersection(self.candidates)

    def summary(self):
            print(f"\nSummary: {self.label}")
            print("-" * 40)
            print(f"Number of tests      : {len(self.tests)}")
            print(f"Test size            : {self.test_size}")
            print(f"Number of candidates : {len(self.candidates)}")
            print(f"True positives       : {len(self.compare_candidates())}")
            print(f"TP set               : {self.compare_candidates()}")
            print(f"Final FP             : {self.history[-1]['false positives']}")
            print(f"Final FN             : {self.history[-1]['false negatives']}")
    
def plot_combined_analysis(df):

        df["FP_Ratio"] = df["Final_FP_Ratio"]

        algorithms = df["Algorithm"].unique()

        fig, axes = plt.subplots(3, 3, figsize=(18, 15))

        for col, algo in enumerate(algorithms):

            subset = df[df["Algorithm"] == algo]

            # --- Row 1: Total Tests vs Defective Size ---
            ax = axes[0, col]

            for t in sorted(df["Test_Size"].unique())[:4]:
                t_data = subset[subset["Test_Size"] == t]

                ax.plot(
                    t_data["Defective_Size"],
                    t_data["Total_Tests"],
                    marker="o",
                    label=f"t={t}"
                )

            ax.set_title(algo)
            ax.set_xlabel("Defective Size")
            ax.set_ylabel("Total Tests")
            ax.legend()

            # --- Row 2: Total Tests vs Test Size ---
            ax = axes[1, col]

            for d in sorted(df["Defective_Size"].unique()):
                d_data = subset[subset["Defective_Size"] == d]

                ax.plot(
                    d_data["Test_Size"],
                    d_data["Total_Tests"],
                    marker="o",
                    label=f"d={d}"
                )

            ax.set_xlabel("Test Size")
            ax.set_ylabel("Total Tests")
            ax.legend()

            # --- Row 3: FP Ratio vs Test Size ---
            ax = axes[2, col]

            for d in sorted(df["Defective_Size"].unique()):
                d_data = subset[subset["Defective_Size"] == d]

                ax.plot(
                    d_data["Test_Size"],
                    d_data["FP_Ratio"],
                    marker="o",
                    label=f"d={d}"
                )

            ax.set_xlabel("Test Size")
            ax.set_ylabel("FP Ratio")
            ax.legend()

        plt.suptitle("Group Testing Algorithm Comparison", fontsize=16)
        plt.tight_layout()
        plt.show()

def plot_fp_ratio_vs_tests(all_histories):

    plt.figure(figsize=(10,6))

    for key, df in all_histories.items():
        plt.plot(
            df["tests so far"],
            df["fp_ratio"],
            label=key
        )

    plt.axhline(y=2, color="black", linestyle="--", label="Stopping condition = 2")

    plt.xlabel("Number of Tests")
    plt.ylabel("FP Ratio = Candidates / Defective Size")
    plt.title("FP Ratio Convergence Over Tests")
    plt.legend(fontsize=7)
    plt.grid(True)
    plt.show()

def plot_best_test_size(df):

    plt.figure(figsize=(10,6))

    for algo in df["Algorithm"].unique():
        subset = df[df["Algorithm"] == algo]

        plt.plot(
            subset["Test_Size"],
            subset["Total_Tests"],
            marker="o",
            label=algo
        )

    plt.xlabel("Test Size")
    plt.ylabel("Total Tests Needed to Stop")
    plt.title("Best Test Size by Algorithm")
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_by_test_size(all_histories):

    for test_size in [32, 64, 96, 128, 160, 192, 224]:

        plt.figure(figsize=(8,5))

        for key, df in all_histories.items():
            if f"t{test_size}" in key:
                plt.plot(df["fp_ratio"], df["tests so far"], label=key)

        plt.xscale("log")
        plt.title(f"Test Size = {test_size}")
        plt.xlabel("FP Ratio (log)")
        plt.ylabel("Total Tests")
        plt.legend()
        plt.grid()
        plt.show()

def plot_fp_ratio_vs_tests(all_histories):

    plt.figure(figsize=(10,6))

    for key, df in all_histories.items():

        df_filtered = df 

        plt.plot(
            df_filtered["fp_ratio"],
            df_filtered["tests so far"],
            label=key
        )

    plt.xlim(1, 2)   # enforce theory range

    plt.xlabel("FP Ratio (1 to 2)")
    plt.ylabel("Total Tests")
    plt.title("FP Ratio Convergence ")
    plt.legend(fontsize=8)
    plt.grid()
    plt.show()

def plot_test_size_bar_comparison(df):

    pivot = df.pivot(
        index="Test_Size",
        columns="Algorithm",
        values="Total_Tests"
    )

    ax = pivot.plot(kind="bar", figsize=(10,6))

    # Highlight failures
    for i, row in df.iterrows():
        if row["Final_FP_Ratio"] >= 2:
            print(f"⚠️ No convergence: {row['Algorithm']} t={row['Test_Size']}")

    plt.xlabel("Test Size")
    plt.ylabel("Total Tests Needed")
    plt.title("Tests Needed to Reach FP Ratio < 2")
    plt.xticks(rotation=0)
    plt.grid(axis="y")
    plt.show()

def run_full_experiment_suite(positions, infected_set, test_size):

    results_summary = []
    all_histories = {}

    algorithm_modes = {
        "Algorithm 1 (Random)": "random",
        "Algorithm 2 (Rectangle)": "rectangle",
    }

    for algo_name, mode in algorithm_modes.items():

        exp = Test_Experiment(
            positions=positions,
            infected_set=infected_set,
            test_size=test_size,
            label=f"{algo_name}_t{test_size}",
            seed=1
        )

        exp.run(mode=mode, strategy="eliminate_negatives", max_tests=100000)

        results_summary.append({
            "Algorithm": algo_name,
            "Defective_Size": len(infected_set),
            "Test_Size": test_size,
            "Total_Tests": len(exp.tests),
            "Final_FP": exp.history[-1]["false positives"],
            "Final_FN": exp.history[-1]["false negatives"],
            "Final_FP_Ratio": exp.history[-1]["fp_ratio"],
            "Stopped": exp.history[-1]["fp_ratio"] < 2
        })

        all_histories[f"{algo_name}_t{test_size}"] = pd.DataFrame(exp.history)

    return results_summary, all_histories

def compare_best_test_sizes(df):

    print("\nBest Test Size for Each Algorithm")
    print("-" * 50)

    best_rows = df.loc[df.groupby("Algorithm")["Total_Tests"].idxmin()]

    print(best_rows[[
        "Algorithm",
        "Test_Size",
        "Total_Tests",
        "Final_FP",
        "Final_FN",
        "Final_FP_Ratio"
    ]])

    return best_rows

def plot_test_size_bar_comparison(df):

    pivot = df.pivot(
        index="Test_Size",
        columns="Algorithm",
        values="Total_Tests"
    )

    pivot.plot(kind="bar", figsize=(10,6))

    plt.xlabel("Test Size")
    plt.ylabel("Total Tests Needed")
    plt.title("Comparison of Test Sizes for Both Algorithms")
    plt.xticks(rotation=0)
    plt.grid(axis="y")
    plt.show()

def save_summary_append(summary, filename="grid_256_ratio_2.xlsx"):

    import pandas as pd
    import os

    df_new = pd.DataFrame(summary)


    # Clean new columns
    df_new.columns = df_new.columns.str.replace(" ", "_")
    df_new.columns = df_new.columns.str.replace("=", "")

    if os.path.exists(filename):

        df_old = pd.read_excel(filename, sheet_name="Raw_Data")

        # Clean old columns too
        df_old.columns = df_old.columns.str.replace(" ", "_")
        df_old.columns = df_old.columns.str.replace("=", "")

        df = pd.concat([df_old, df_new], ignore_index=True)

    else:
        df = df_new
    
    df.columns = df.columns.map(str)
    df.columns = df.columns.str.replace(" ", "_")
    df.columns = df.columns.str.replace("=", "")

    df = df.loc[:, ~df.columns.duplicated()]


    print(df.columns)

    # --------- Create clean comparison tables ---------

    table_alg_def = df.pivot_table(
        values="Total_Tests",
        index="Defective_Size",
        columns="Algorithm",
        aggfunc="mean"
    )

    table_alg_test = df.pivot_table(
        values="Total_Tests",
        index="Test_Size",
        columns="Algorithm",
        aggfunc="mean"
    )

    table_fp = df.pivot_table(
        values="Final_FP",
        index="Defective_Size",
        columns="Algorithm",
        aggfunc="mean"
    )

    table_alg_def = table_alg_def.sort_index()
    table_alg_test = table_alg_test.sort_index()
    table_fp = table_fp.sort_index()

    table_alg_def = table_alg_def.round(2)
    table_alg_test = table_alg_test.round(2)
    table_fp = table_fp.round(2)

    # Add averages
    table_alg_def.loc["Average"] = table_alg_def.mean()
    table_alg_test.loc["Average"] = table_alg_test.mean()

    # --------- Write to Excel ---------
    print("Summary length:", len(summary))
    print(df.head())
    with pd.ExcelWriter(filename, engine="openpyxl", mode="w") as writer:

        df.to_excel(writer, sheet_name="Raw_Data", index=False)

        table_alg_def.to_excel(writer, sheet_name="Algorithm_vs_Defective")

        table_alg_test.to_excel(writer, sheet_name="Algorithm_vs_TestSize")

        table_fp.to_excel(writer, sheet_name="False_Positive_Comparison")

    print("✅ Clean experiment tables saved.") 

if __name__ == "__main__":

    test_sizes = [32, 64, 96, 128, 160, 192, 224]

    # Create ONE model (fixed)
    model = create_model(size=256, num_ones=32, seed=1)

    infected_set = {
        (r + 1, c + 1)
        for r in range(256)
        for c in range(256)
        if model[r, c] == 1
    }

    all_summaries = []
    all_histories_total = {}

    for test_size in test_sizes:

        print(f"\nRunning test size {test_size}")

        summary, histories = run_full_experiment_suite(
            positions,
            infected_set,
            test_size
        )

        all_summaries.extend(summary)
        all_histories_total.update(histories)
        
    df = pd.DataFrame(all_summaries)
    plot_best_test_size(df)
    save_summary_append(all_summaries, filename="grid_256_ratio_2.xlsx")
    best_results = compare_best_test_sizes(df)
    plot_test_size_bar_comparison(df)
    # Plot new requirement
    plot_fp_ratio_vs_tests(all_histories_total)
    plot_by_test_size(all_histories_total)
