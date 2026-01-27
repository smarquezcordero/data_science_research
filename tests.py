import numpy as np
import pandas as pd
from collections import Counter

def create_model(size=10, num_ones=8, seed=1):
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
    def __init__(self, positions, infected_set, num_tests, test_size, label="", seed=None):
               self.positions = positions
               self.infected_set = infected_set
               self.num_tests = num_tests
               self.test_size = test_size
               self.label = label
               self.seed = seed

               self.test = []
               self.results = []

               self.negative_points = set()
               self.positive_points = set()
               self.positive_counter = Counter()
               self.repeated_positive_points = set()
               self.candidates = set()
    
    def generate_tests(self):
            self.tests = []
            if self.seed is not None:
                np.random.seed(self.seed)
            for x in range(self.num_tests):
                    indices = np.random.choice(len(self.positions), self.test_size, replace = False)
                    test = [self.positions[i] for i in indices]
                    self.tests.append(test)


    def clasify_tests(self, test):
            return "positive" if any (item in self.infected_set for item in test) else "negative"
    
    def run(self):
            self.generate_tests()
            self.results = [self.clasify_tests(test) for test in self.tests]

            for test, result in zip(self.tests, self.results):
                    if result == "negative":
                            self.negative_points.update(test)
                    else:
                            self.positive_points.update(test)
                            self.positive_counter.update(test)
            
            self.repeated_positive_points = {
                    item for item, count in self.positive_counter.items() if count >=2
            }

            self.candidates = (self.repeated_positive_points) - self.negative_points 

    def summary(self):
            return {
                    "Tests #: ": self.num_tests,
                    "Test size:": self.test_size,
                    "Number of candidates: ": len(self.candidates),
                    "Candidates: ": self.candidates
            }
    def to_dataframe(self):
        rows = []
        for i, (test, result) in enumerate(zip(self.tests, self.results), start=1):
            row = {"Test": i}

            for j, item in enumerate(test, start=1):
                row[f"Item {j}"] = item

            row["Result"] = result 
            rows.append(row)

        return pd.DataFrame(rows)
    

exp_64x8 = Test_Experiment(
    positions=positions,
    infected_set=S,
    num_tests=64,
    test_size=8,
    label="30 Test with 8 items",
    seed=1
)
exp_64x15 = Test_Experiment(
    positions=positions,
    infected_set=S,
    num_tests=64,
    test_size=15,
    label="64 Test with 15 items",
    seed=1
)

exp_30x8 = Test_Experiment(
    positions=positions,
    infected_set=S,
    num_tests=30,
    test_size=8,
    label="64 Test with 8 items",
    seed=1
)

exp_30x10 = Test_Experiment(
    positions=positions,
    infected_set=S,
    num_tests=30,
    test_size=10,
    label="30 Test with 10 items",
    seed=1
)

exp_30x15 = Test_Experiment(
    positions=positions,
    infected_set=S,
    num_tests=30,
    test_size=15,
    label="30 Tests with 15 items",
    seed=1
)

exp_64x8.run()
exp_64x15.run()
exp_30x8.run()
exp_30x10.run()
exp_30x15.run()


df_64x8 = exp_64x8.to_dataframe()
df_64x15 = exp_64x15.to_dataframe()
df_30x8 = exp_30x8.to_dataframe()
df_30x10 = exp_30x10.to_dataframe()
df_30x15 = exp_30x15.to_dataframe()

with pd.ExcelWriter("test_results.xlsx", engine="xlsxwriter") as writer:
    df_64x8.to_excel(writer, sheet_name="64x8", index=False)
    df_64x15.to_excel(writer, sheet_name="64x15", index=False)
    df_30x8.to_excel(writer, sheet_name="30x8", index=False)
    df_30x10.to_excel(writer, sheet_name="30x10", index=False)
    df_30x15.to_excel(writer, sheet_name="30x15", index=False)

 
print("\nSummary 64x8:")
print(exp_64x8.summary())

print("\nSummary 64x15:")
print(exp_64x8.summary())

print("\nSummary 30x8:")
print(exp_30x8.summary())

print("\nSummary 30x10:")
print(exp_30x10.summary())

print("\nSummary 30x15:")
print(exp_30x15.summary())