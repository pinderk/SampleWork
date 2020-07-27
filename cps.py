# CS121: Current Population Survey (CPS) 
#
# Functions for mining CPS data 

import pandas as pd
import numpy as np
import csv
import os
import sys
import math
import tabulate

# Constants 
HID = "h_id" 
AGE = "age"
GENDER = "gender" 
RACE = "race" 
ETHNIC = "ethnicity" 
STATUS = "employment_status"
HRWKE = "hours_worked_per_week" 
EARNWKE = "earnings_per_week" 

FULLTIME_MIN_WORKHRS = 35

# CODE_TO_FILENAME: maps a code to the name for the corresponding code
# file
CODE_TO_FILENAME = {"gender_code":"data/gender_code.csv",
                    "employment_status_code": "data/employment_status_code.csv",
                    "ethnicity_code":"data/ethnic_code.csv",
                    "race_code":"data/race_code.csv"}


# VAR_TO_FILENAME: maps a variable-of-interest to the name for the
# corresponding code file
VAR_TO_FILENAME = {GENDER: CODE_TO_FILENAME["gender_code"],
                   STATUS: CODE_TO_FILENAME["employment_status_code"],
                   ETHNIC: CODE_TO_FILENAME["ethnicity_code"],
                   RACE: CODE_TO_FILENAME["race_code"]}


def build_morg_df(morg_filename):
    '''
    Construct a DF from the specified file.  Resulting dataframe will
    use names rather than coded values.
    
    Inputs:
        morg_filename: (string) filename for the morg file.

    Returns: pandas dataframe
    '''
    #https://stackoverflow.com/questions/82831/how-do-i-check-whether
    #-a-file-exists-using-python
    file_exists = os.path.exists(morg_filename)
    if file_exists == False:
        return None

    morg_df = pd.read_csv(morg_filename)
    
    for c in morg_df.columns:
        if c in CODE_TO_FILENAME:
            c_df = pd.read_csv(CODE_TO_FILENAME[c])
            columns = c_df.columns
            if c_df[columns[0]][0] > 0:
                morg_df.loc[:, c] -= 1

            morg_df[c] = morg_df[c].fillna(0)
            string = columns[-1]
            categories = c_df[string]
            morg_df.loc[:, c] = pd.Categorical.from_codes\
            (morg_df.loc[:, c], categories)
            morg_df.rename(columns={c:c[:-5]}, inplace=True)

    return morg_df


def calculate_weekly_earnings_stats_for_fulltime_workers(df, gender, race, ethnicity):
    '''
    Calculate statistics for different subsets of a dataframe.

    Inputs:
        df: morg dataframe
        gender: "Male", "Female", or "All"
        race: specific race from a small set, "All", or "Other",
            where "Other" means not in the specified small set
        ethnicity: "Hispanic", "Non-Hispanic", or "All"

    Returns: (mean, median, min, max) for the rows that match the filter.
    '''
    gender_values = ["Male", "Female"]
    if gender == "All":
        gender_df = df
    else:
        if gender in gender_values:
            gender_df = df[df.gender == gender]
        if gender not in gender_values:
            return (0, 0, 0, 0)
    

    race_values = ["WhiteOnly", "BlackOnly", \
    "AmericanIndian/AlaskanNativeOnly", "AsianOnly", \
    "Hawaiian/PacificIslanderOnly"]
    if race == "All":
        race_df = gender_df
    else:
        if race == "Other":
            race_df = gender_df
            for r in range(len(race_values)):
                race_df = race_df[race_df.race != race_values[r]]
        if race in race_values:
            race_df = gender_df[gender_df.race == race]
        if race != "Other":
            if race not in race_values:
                return (0, 0, 0, 0)

    ethnicity_values = ["All", "Hispanic", "Non-Hispanic"]
    if ethnicity == "All":
        ethnicity_df = race_df
    else:
        if ethnicity == "Hispanic":
            ethnicity_df = race_df[race_df.ethnicity != "Non-Hispanic"]
        if ethnicity == "Non-Hispanic":
            ethnicity_df = race_df[race_df.ethnicity == "Non-Hispanic"]
        if ethnicity not in ethnicity_values:
            return (0, 0, 0, 0)

    if_employed = ethnicity_df[ethnicity_df.employment_status == "Working"]
    above_35 = if_employed[if_employed.hours_worked_per_week >= \
    FULLTIME_MIN_WORKHRS]
    earnings_df = above_35["earnings_per_week"]

    if len(earnings_df) == 0:
        return (0, 0, 0, 0)

    earnings_mean = earnings_df.mean()
    earnings_median = earnings_df.median()
    earnings_min = earnings_df.min()
    earnings_max = earnings_df.max()
    
    return (earnings_mean, earnings_median, earnings_min, earnings_max)


def create_histogram(df, var_of_interest, num_buckets, min_val, max_val):
    '''
    Compute the number of full time workers who fall into each bucket
    for a specified number of buckets and variable of interest.

    Inputs:
        df: morg dataframe
        var_of_interest: one of EARNWKE, AGE, HWKE
        num_buckets: the number of buckets to use.
        min_val: minimal value (lower bound) for the histogram (inclusive)
        max_val: maximum value (lower bound) for the histogram (non-inclusive).

    Returns:
        list of integers where ith element is the number of full-time workers who fall into the ith bucket.

        empty list if num_buckets <= 0 or max_val <= min_val
    '''
    intervals = np.linspace(min_val, max_val, num=num_buckets, endpoint=False)
    if_employed = df[df.employment_status == "Working"]
    above_35 = if_employed[if_employed.hours_worked_per_week >= \
    FULLTIME_MIN_WORKHRS]
    interest_df = above_35[var_of_interest]
    buckets = []
    histogram = []

    if num_buckets <= 0:
        return buckets

    if max_val <= min_val:
        return buckets

    for r in range(len(intervals) - 1):
        buckets.append((intervals[r], intervals[r + 1]))
    buckets.append((intervals[-1], max_val))
    for b in buckets:
        new_df = interest_df[interest_df < b[1]]
        new_df_2 = new_df[new_df >= b[0]]
        histogram.append(len(new_df_2))

    return histogram


def calculate_unemployment_rates(filenames, age_range, var_of_interest):
    '''
    Calculate the unemployment rate for participants in a given age range (inclusive)
    by values of the variable of interest.

    Inputs:
        filenames: (list of tuples) list of (year, morg filename) tuples (both strings)
        age_range: (pair of ints) (lower_bound, upper_bound)
        var_of_interest: one of "gender", "race", "ethnicity"

    Returns: A dataframe with the unemployment rates of persons in the given
             age range in each category of the variable of interest.
    '''

    filenames.sort()

    if len(filenames) == 0:
        return None
    if age_range[0] >= age_range[1]:
        return None

    interest_var_file = pd.read_csv(VAR_TO_FILENAME[var_of_interest])
    string = interest_var_file.columns[-1]
    values = interest_var_file[string] 
    values_list = []
    for v in values:
        values_list.append(v)
    values_list.sort()

    labor_force_list = ["Working", "Layoff", "Looking"]
    unemployed_list = ["Layoff", "Looking"]

    interest_df = pd.DataFrame({var_of_interest:values_list})

    for f in filenames:
        unemployed_rates_list = []
        df = build_morg_df(f[1])
        new_df = df[df.age <= age_range[1]]
        new_df_2 = new_df[new_df.age >= age_range[0]]
        for v in range(len(values_list)):
            unemployed_count = 0
            labor_force_count = 0
            value_df = new_df_2[new_df_2[var_of_interest] == values_list[v]]
            employment_value_df = value_df["employment_status"]
      
            for e in employment_value_df:
                if e in unemployed_list:
                    unemployed_count += 1
                if e in labor_force_list:
                    labor_force_count += 1
            if labor_force_count == 0:
                unemployment_rate = 0
            else:
                unemployment_rate = unemployed_count / labor_force_count
            unemployed_rates_list.append(unemployment_rate)

        interest_df.loc[:, f[0]] = unemployed_rates_list

    interest_df.set_index(var_of_interest, inplace=True)

    return interest_df   
    
