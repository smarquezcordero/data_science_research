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
    def __init__(self, positions, infected_set, test_size, label="", seed=None):
               self.positions = positions
               self.infected_set = infected_set
               self.test_size = test_size
               self.label = label
               self.seed = seed

               self.test = []
               self.results = []
               self.history = []

               self.negative_points = set()
               self.positive_points = set()
               self.positive_counter = Counter()
               self.repeated_positive_points = set()
               self.candidates = set()

    def clasify_tests(self, test):
            return "positive" if any (item in self.infected_set for item in test) else "negative"
    
    def run(self, max_tests = 10000):
            if self.seed is not None:
                  np.random.seed(self.seed)

            test_count = 0
            
            for t in range(1, max_tests + 1):
                
                test_count += 1

                indices = np.random.choice(len(self.positions), self.test_size, replace= False)
                test= [self.positions[i] for i in indices]
                self.test.append(test)

                result = self.clasify_tests(test)
                self.results.append(result)

                if result == "negative":
                    self.negative_points.update(test)
                else:
                    self.positive_points.update(test)
                    self.positive_counter.update(test)

                self.candidates = (self.positive_points) - self.negative_points 

                false_positives = self.candidates - self.infected_set
                false_negatives = self.infected_set - self.candidates

                self.history.append({
                    "tests so far" : test_count,
                    "false positives" : len(false_positives),
                    "false negatives" : len(false_negatives)
                })

                if len(false_positives) == 0 and len(false_negatives) == 0:
                     print("Both false positive and negative are 0")
                     break
                if test_count >= max_tests:
                     print("Max tests are reached")
                     break

    def compare_candidates(self):
            return self.infected_set.intersection(self.candidates)

    def summary(self):
            print(f"\nSummary: {self.label}")
            print("-" * 40)
            print(f"Number of tests      : {len(self.test)}")
            print(f"Test size            : {self.test_size}")
            print(f"Number of candidates : {len(self.candidates)}")
            print(f"Candidates           : {self.candidates}")
            print(f"True positives       : {len(self.compare_candidates())}")
            print(f"TP set               : {self.compare_candidates()}")
            print(f"Final FP             : {self.history[-1]['false positives']}")
            print(f"Final FN             : {self.history[-1]['false negatives']}")

    def print_progress(self, step=500):
        print("\nProgress snapshot:")
        print("Tests | FP | FN")
        print("-" * 20)
        for h in self.history[::step]:
            print(f"{h['tests so far']:5d} | {h['false positives']:2d} | {h['false negatives']:2d}")

    
    #def to_dataframe(self):
    #    rows = []
    #    for i, (test, result) in enumerate(zip(self.tests, self.results), start=1):
     #       row = {"Test": i}
#
 #           for j, item in enumerate(test, start=1):
  #              row[f"Item {j}"] = item
#
 #           row["Result"] = result 
  #          rows.append(row)
#
 #       return pd.DataFrame(rows)
    

exp_20x25 = Test_Experiment(
    positions=positions,
    infected_set=S,
    test_size=25,
    label="Test size of 25",
    seed=1
)



exp_20x25.run()
exp_20x25.print_progress()



#df_20x25 = exp_20x25.to_dataframe()
#df_20x29 = exp_20x29.to_dataframe()

#with pd.ExcelWriter("100grid_results.xlsx", engine="xlsxwriter") as writer:
 #   df_20x25.to_excel(writer, sheet_name="20x25", index=False)
  #  df_20x29.to_excel(writer, sheet_name="20x29", index=False)

for h in exp_20x25.history[::500]:
    print(h)


print(exp_20x25.print_progress())
print(exp_20x25.summary())
