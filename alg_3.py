import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
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

        #divisors = [d for d in range(1, self.test_size + 1)]
        #x1 = np.random.choice(divisors)
        #x2 = self.test_size // x1

        #if we don't want to use mulriples of 200 and use x1 randomly (x2 rounding up)
        x1 = np.random.randint(1, grid_size + 1)
        x2 = int(np.ceil(self.test_size / x1))
        #keeping in mind that test can be bigger (ex. x1=33, x2=7, rec=231)

        r = np.random.randint(0, grid_size )
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

    #alg 3
    def rectangle_200(self):
        grid_size = int(len(self.positions) ** 0.5)
        valid_widths = [2, 4, 5, 8, 10, 20, 25, 40, 50, 100]

        while True:
            x1 = random.choice(valid_widths)
            x2 = 200 // x1
            if x1 <= grid_size and x2 <= grid_size:
                r = np.random.randint(0, grid_size - x1 + 1)
                c = np.random.randint(0, grid_size - x2 + 1)
                break

        rectangle = [(r+i+1, c+j+1) for i in range(x1) for j in range(x2)]
        self.rectangle_stats.append({
            "intended_size": 200,
            "actual_size": len(rectangle),
            "shrunk": False,
            "shape": (x1, x2)
        })
        return rectangle
    
    def run(self, mode = "random", strategy="positive_minus_negative",max_tests = 50000):
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
            
            for t in range(1, max_tests + 1):
                
                if mode == "random":
                    test = self.random_test()
                elif mode == "rectangle":
                    test = self.rectangle_test()
                elif mode=="rectangle_200":
                     test = self.rectangle_200()
                else:
                    raise ValueError('needs to be random or rectangle')
                if test is None:
                    raise RuntimeError(f"{mode}_test returned None")
                
                result = self.clasify_tests(test)
                self.tests.append(test)
                self.results.append(result)

                if strategy == "positive_minus_negative":
                    if result == "negative":
                          self.negative_points.update(test)
                    else: 
                         self.positive_points.update(test)
                         self.positive_counter.update(test)

                    self.candidates = (self.positive_points)- self.negative_points

                elif strategy == "eliminate_negatives":
                     if result == "negative":
                          self.candidates -= set(test)
    

                false_positives = self.candidates - self.infected_set
                false_negatives = self.infected_set - self.candidates

                self.history.append({
                    "tests so far" : t,
                    "false positives" : len(false_positives),
                    "false negatives" : len(false_negatives)
                })

                if len(false_positives) == 0 and len(false_negatives) == 0:
                     print("Both false positive and negative are 0")
                     break
                if t >= max_tests:
                     print("Max tests are reached")
                     break

    def compare_candidates(self):
            return self.infected_set.intersection(self.candidates)

    def summary(self):
            print(f"\nSummary: {self.label}")
            print("-" * 40)
            print(f"Number of tests      : {len(self.tests)}")
            print(f"Test size            : {self.test_size}")
            print(f"Number of candidates : {len(self.candidates)}")
            #print(f"Candidates           : {self.candidates}")
            print(f"True positives       : {len(self.compare_candidates())}")
            print(f"TP set               : {self.compare_candidates()}")
            print(f"Final FP             : {self.history[-1]['false positives']}")
            print(f"Final FN             : {self.history[-1]['false negatives']}")

    def print_progress(self, step=250):
        print("\nProgress snapshot:")
        print("Tests | FP | FN")
        print("-" * 20)
        for h in self.history[::step]:
            print(f"{h['tests so far']:5d} | {h['false positives']:2d} | {h['false negatives']:2d}")
    
    def rectangle_summary(self):
        total = len(self.rectangle_stats)
        shrunk = sum(1 for s in self.rectangle_stats if s["shrunk"])

        print("\nRectangle test diagnostics")
        print("-" * 35)
        print(f"Total rectangle tests : {total}")
        
        sample = self.get_shrunk_sizes()

        if sample:
            print(f"\nSample of shrunk sizes ({len(sample)}):")
            print(sample)
            print(f"Min size: {min(sample)}")
            print(f"Max size: {max(sample)}")
        
    
    def plot_shrunk_histogram(self):
        """
     Plots a histogram of the shrunk rectangle sizes.
     """

        all_sizes = [s["actual_size"] for s in self.rectangle_stats]

        if not all_sizes:
            print("No shrunk rectangles found.")
            return

        plt.figure()
        plt.hist(all_sizes, density= True)
        plt.xlabel("Rectangle Sizes")
        plt.ylabel("Probability")
        plt.title("Distribution of Rectangle Sizes")
        plt.show()

        print(f"Total shrunk rectangles: {len(all_sizes)}")
        print(f"Average shrunk size: {sum(all_sizes)/len(all_sizes):.2f}")
        print(f"Min shrunk size: {min(all_sizes)}")
        print(f"Max shrunk size: {max(all_sizes)}")

    def plot_fp_ratio(self, defective_size):
        tests = [h["tests so far"] for h in self.history]
        ratios = [
            h["false positives"] / defective_size
            for h in self.history
        ]

        plt.plot(tests, ratios, label=self.label)
        plt.xlabel("Number of Tests")
        plt.ylabel("FP / Defective Size")
        plt.title("FP Ratio vs Number of Tests")

    def tests_until_fp_zero(self):
        """
        Returns the number of tests needed for false positives to reach 0.
        If never reaches 0, returns total tests performed.
        """
        for h in self.history:
            if h["false positives"] == 0:
                return h["tests so far"]
        return len(self.history)

    def plot_fp(self):
        tests = [h["tests so far"] for h in self.history]
        fps = [h["false positives"] for h in self.history]

        plt.plot(tests, fps, label=self.label)
        plt.xlabel("Number of tests")
        plt.ylabel("False Positives")
        plt.title("False positives vs Number of tests")
        plt.legend()
    
def plot_fp_vs_defective_size(positions, defective_sizes, strategy="eliminate_negatives"):

    algorithm_configs = [
        {"mode": "random", "label": "Algorithm 1"},
        {"mode": "rectangle", "label": "Algorithm 2"},
        {"mode": "rectangle_200", "label": "Algorithm 3"}
    ]

    results = {config["label"]: [] for config in algorithm_configs}

    for d_size in defective_sizes:

        print(f"\nRunning defective size {d_size}")

        model = create_model(size=100, num_ones=d_size, seed=1)

        infected_set = {
            (r + 1, c + 1)
            for r in range(100)
            for c in range(100)
            if model[r, c] == 1
        }

        for config in algorithm_configs:

            exp = Test_Experiment(
                positions=positions,
                infected_set=infected_set,
                test_size=200,
                label=config["label"],
                seed=1
            )

            exp.run(mode=config["mode"], strategy=strategy)

            tests_needed = exp.tests_until_fp_zero()

            results[config["label"]].append(tests_needed)

    # Plotting
    plt.figure()

    for label, values in results.items():
        plt.plot(defective_sizes, values, marker='o', label=label)

    plt.xlabel("Defective Set Size")
    plt.ylabel("Tests until FP = 0")
    plt.title("Tests Needed for False Positives to Reach Zero")
    plt.legend()
    plt.show()    

defective_sizes = [25, 50, 75, 100]

plot_fp_vs_defective_size(
    positions=positions,
    defective_sizes=defective_sizes,
    strategy="eliminate_negatives"
)




