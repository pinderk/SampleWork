# CS122: Linking restaurant records in Zagat and Fodor's list
#
# Kyle Pinder


import numpy as np
import pandas as pd
import jellyfish
import util
import collections
import itertools

def find_matches(mu, lambda_, block_on_city=False):
    '''
    Creates the match, possible, and unmatch dataframes of the restaurants
    from zagat and fodors based on a maximum false positive and negative rate
    and whether or not the city should be blocked.

    Inputs:
        mu: (float) The maximum false positive rate.
        lambda: (float) The maximum false negative rate.
        block_on_city: (boolean) Whether or not to block on the city.

    Outputs: The three pandas dataframes indicating matches, possible matches,
             and unmatches.
    '''

    zagat = create_df('zagat.csv', ['z_Restaurant', 'z_City', 'z_Address'])
    fodors = create_df('fodors.csv', ['f_Restaurant', 'f_City', 'f_Address'])
    known_links = create_df('known_links.csv', ['z_id', 'f_id'])
    
    matches = create_matches(zagat, fodors, known_links) 
    unmatches = create_unmatches(zagat, fodors)

    tuples_m = create_tuples(matches)
    tuples_m_frequency = collections.Counter(tuples_m)

    tuples_u = create_tuples(unmatches)
    tuples_u_frequency = collections.Counter(tuples_u)

    all_tuples_list = list(itertools.product(["low", "medium", "high"],\
    repeat = 3))

    match_tuples_list, possible_tuples_list, unmatch_tuples_list = \
    create_category_tuples(tuples_m_frequency, tuples_u_frequency, \
    all_tuples_list, mu, lambda_)

    match_df, possible_df, unmatch_df = create_final_dataframes(zagat, \
    fodors, match_tuples_list, possible_tuples_list, unmatch_tuples_list,\
    block_on_city)

    return match_df, possible_df, unmatch_df


def create_final_dataframes(zagat, fodors, match_tuples_list, 
    possible_tuples_list, unmatch_tuples_list, block_on_city):
    '''
    Creates the match, possible, and unmatch dataframes from lists.

    Inputs:
        zagat: (dataframe) The zagat dataframe.
        fodors: (dataframe) The fodors dataframe.
        match_tuples_list: (list) The list of tuples that indicate matches.
        possible_tuples_list: (list) The list of tuples that indicate 
                              possible matches.
        unmatch_tuples_list: (list) The list of tuples that indicate 
                             unmatches.
        block_on_city: (boolean) Whether or not to block on the city.

    Outputs: The match, possible, and unmatch dataframes.
    '''

    match_dict_list = []
    possible_dict_list = []
    unmatch_dict_list = []
    cols = ['z_Restaurant', 'z_City', 'z_Address', 'f_Restaurant',\
    'f_City', 'f_Address']

    for z in zagat.itertuples():
        for f in fodors.itertuples():
            if (not block_on_city) or (block_on_city and z[2] == f[2]):
                jw_name = get_jw(z[1], f[1])
                jw_city = get_jw(z[2], f[2])
                jw_address = get_jw(z[3], f[3])
                jw_tuple = jw_name, jw_city, jw_address

                val = z[1:4] + f[1:4]
                dict_val = dict(zip(cols, val))
                
                if jw_tuple in match_tuples_list:
                    match_dict_list.append(dict_val)

                elif jw_tuple in possible_tuples_list:
                    possible_dict_list.append(dict_val)

                elif jw_tuple in unmatch_tuples_list:
                    unmatch_dict_list.append(dict_val)

    match_df = pd.DataFrame(match_dict_list, columns = cols)
    possible_df = pd.DataFrame(possible_dict_list, columns = cols)
    unmatch_df = pd.DataFrame(unmatch_dict_list, columns = cols)

    return match_df, possible_df, unmatch_df
    
               
def create_df(csv_file, column_names):
    '''
    Creates a dataframe from a given csv file and a list of column names.

    Inputs:
        csv_file: (csv) The csv file.
        column_names: (list) The list of column names.

    Outputs: The new dataframe.
    '''

    df = pd.read_csv(csv_file, names = column_names)

    return df


def create_matches(zagat, fodors, known_links):
    '''
    Creates the dataframe that matches the zagat and fodors data based on 
    the indices given in the known_links file.

    Inputs:
        zagat: (dataframe) The zagat dataframe.
        fodors: (dataframe) The fodors dataframe.
        known_links: (dataframe) The dataframe showing the matching indices
                     from zagat and fodors.

    Outputs: The new matches dataframe.
    '''

    matches = known_links.merge(zagat, right_index = True, left_on = "z_id").\
    merge(fodors, right_index = True, left_on = "f_id")\
    .drop(["z_id", "f_id"], axis = 1)

    return matches


def create_unmatches(zagat, fodors):
    '''
    Creates a dataframe of unmatches from a random sample of 1000 from 
    both zagat and fodors.

    Inputs:
        zagat: (dataframe) The zagat dataframe.
        fodors: (dataframe) The fodors dataframe.
    
    Outputs: The unmatches dataframe.  
    '''

    zagat_u = zagat.sample(1000, replace = True, random_state = 1234)
    fodors_u = fodors.sample(1000, replace = True, random_state = 5678)

    zagat_u.index = range(len(zagat_u))
    fodors_u.index = range(len(fodors_u))

    unmatches = pd.concat([zagat_u, fodors_u], axis = 1, ignore_index = True)

    return unmatches


def create_tuples(df):
    '''
    Creates all of the sets of tuples based on the Jaro-Winkler scores of the
    combined zagat and fodors dataframe.

    Inputs:
        df: (dataframe) The combined zagat and fodors dataframe.

    Outputs: The list of tuples.
    '''

    tuple_list = []

    for row in df.itertuples():
        jw_name = get_jw(row[1], row[4])
        jw_city = get_jw(row[2], row[5])
        jw_address = get_jw(row[3], row[6])
        jw_tuple = jw_name, jw_city, jw_address
        tuple_list.append(jw_tuple)

    return tuple_list  

    
def get_jw(string_1, string_2):
    '''
    Calculates the Jaro-Winkler score based on the two given strings.

    Inputs:
        string_1: (string) The first given string.
        string_2: (string) The first given string.

    Returns: The Jaro-Winkler score of the two strings.
    '''

    jw_score = jellyfish.jaro_winkler(string_1, string_2)

    jw_category = util.get_jw_category(jw_score)

    return jw_category


def create_category_tuples(tuples_m_frequency, tuples_u_frequency, 
    all_tuples_list, mu, lambda_):
    '''
    Creates the tuples indicating the category of the Jaro-Winkler score 
    (high, medium, low) from the frequency of the match and unmatch tuples 
    and the maximum false positive and negative rates.

    Inputs:
        tuples_m_frequency: (dictionary) The dictionary of the frequencies 
                            of the match tuples.
        tuples_u_frequency: (dictionary) The dictionary of the frequencies 
                            of the unmatch tuples. 
        all_tuples_list: (list) The list of all of the possible tuples.
        mu: (float) The maximum false positive rate.
        lambda: (float) The maximum false negative rate.

    Outputs: The lists of match, possible, and unmatch tuples.
    '''

    match_tuples_list = []
    matching_sum = 0
    possible_tuples_list = []
    unmatch_tuples_list = []
    unmatching_sum = 0
    tuples_dictionary = {}

    for t in all_tuples_list:
        if t not in tuples_m_frequency and t not in tuples_u_frequency:
            possible_tuples_list.append(t)
   
        elif t in tuples_m_frequency and t in tuples_u_frequency:
            tuples_dictionary[t] =  (tuples_m_frequency[t]/50)\
            /(tuples_u_frequency[t]/1000)

        elif t not in tuples_m_frequency:
            tuples_dictionary[t] = (tuples_u_frequency[t])*(-1)

        elif t not in tuples_u_frequency:
            tuples_dictionary[t] = (tuples_m_frequency[t])+(1000)

    descending_probability = collections.Counter(tuples_dictionary).\
    most_common()
    ascending_probability = descending_probability[::-1]

    desc_prob_list = [x[0] for x in descending_probability]
    asc_prob_list = [x[0] for x in ascending_probability]

    for d in desc_prob_list:
        if d not in tuples_u_frequency:
            match_tuples_list.append(d)
        elif unmatching_sum + (tuples_u_frequency[d]/1000) <= mu:
            match_tuples_list.append(d)
            unmatching_sum += (tuples_u_frequency[d]/1000)
        else:
            break

    for a in asc_prob_list:
        if a not in match_tuples_list:
            if a not in tuples_m_frequency:
                unmatch_tuples_list.append(a)
            elif matching_sum + (tuples_m_frequency[a]/50) <= lambda_:
                unmatch_tuples_list.append(a)
                matching_sum += (tuples_m_frequency[a]/50)
            else:
                break
        else:
            break

    for r in desc_prob_list:
        if r not in match_tuples_list and r not in unmatch_tuples_list:
            possible_tuples_list.append(r)

    return match_tuples_list, possible_tuples_list, unmatch_tuples_list


if __name__ == '__main__':
    matches, possibles, unmatches = \
        find_matches(0.005, 0.005, block_on_city=False)

    print("Found {} matches, {} possible matches, and {} "
          "unmatches with no blocking.".format(matches.shape[0],
                                               possibles.shape[0],
                                               unmatches.shape[0]))
