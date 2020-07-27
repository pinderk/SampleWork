# CS121 Linear regression assignment
# Print text answers.
#
import sys
from model import *
from dataset import DataSet

import matplotlib.pyplot as plt
import numpy as np


def go(dataset):
    '''
    Put together the work for all the tasks

    Inputs: the dataset
    '''
    ds = dataset
    md = Model(ds, ds.pvi)
    
    print()
    print(ds.dataset_name, "Task 1a:")
    print()
    md.construct_p_models()
    print()
    print(ds.dataset_name, "Task 1b:")
    print()
    md.construct_single_model()
    print()
    print()
    print(ds.dataset_name, "Task 2:")
    print()
    md.construct_bivariate_model()
    print()
    print()
    print(ds.dataset_name, "Task 3:")
    print()
    md.print_complex_model()
    print()
    print(ds.dataset_name, "Task 4:")
    print()
    md.print_best_k()
    print()
    print()
    print(ds.dataset_name, "Task 5:")
    print()
    md.test_data()
    print()
    

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 output <dataset directory name>", file=sys.stderr)
        sys.exit(0)

    dataset = DataSet(sys.argv[1])
    go(dataset)

