import numpy as np
import pandas as pd
from collections import Counter

def create_model(size=100, num_ones=50, seed=1):
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

            self.candidates = (self.positive_points) - self.negative_points 

    def compare_candidates(self):
            return self.infected_set.intersection(self.candidates)

    def summary(self):
            print(f"\nSummary: {self.label}")
            print("-" * 40)
            print(f"Number of tests      : {self.num_tests}")
            print(f"Test size            : {self.test_size}")
            print(f"Number of candidates : {len(self.candidates)}")
            print(f"Candidates           : {self.candidates}")
            print(f"True positives       : {len(self.compare_candidates())}")
            print(f"TP set               : {self.compare_candidates()}")
    
    def to_dataframe(self):
        rows = []
        for i, (test, result) in enumerate(zip(self.tests, self.results), start=1):
            row = {"Test": i}

            for j, item in enumerate(test, start=1):
                row[f"Item {j}"] = item

            row["Result"] = result 
            rows.append(row)

        return pd.DataFrame(rows)
    

exp_20x25 = Test_Experiment(
    positions=positions,
    infected_set=S,
    num_tests=20,
    test_size=25,
    label="20 test with 25 items",
    seed=1
)
exp_20x29 = Test_Experiment(
    positions=positions,
    infected_set=S,
    num_tests=64,
    test_size=15,
    label="20 Test with 29 items",
    seed=1
)



exp_20x25.run()
exp_20x29.run()


df_20x25 = exp_20x25.to_dataframe()
df_20x29 = exp_20x29.to_dataframe()

with pd.ExcelWriter("100grid_results.xlsx", engine="xlsxwriter") as writer:
    df_20x25.to_excel(writer, sheet_name="20x25", index=False)
    df_20x29.to_excel(writer, sheet_name="20x29", index=False)

 

print(exp_20x25.summary())
print(exp_20x29.summary())
