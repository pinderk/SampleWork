# CS121: Benford's Law
#
# Kyle Pinder
#
# Functions for evaluating data using Benford's Law.

import math
import os.path
import pylab as plt
import sys
import util

def extract_amount(currency_symbol, amount_str):
    '''
   
    "Given a currency symbol and an amount in that currency, extract
    the numeric amount as a float."

    Inputs:
        currency_symbol: (string) a currency symbol 
          e.g. '$', 'C$', '\u00A3'
        amount_str: (string) amount with currency symbol
          e.g. '$1.23' or 'C$1.23'

    Returns: float
    '''
    
    n = len(currency_symbol)
    
    return float(amount_str[n:])


def extract_leading_digits(amount, num_digits):
    '''
    "Given an amount and a number of desired leading digits, extract 
    the leading digits as an integer."

    Inputs: 
        amount: (integer or float) an amount
          e.g. 2.34, 0.002034, 1000
        num_digits: (integer) the number of desired digits in the new amount
          e.g. 1, 2, 3

    Returns: integer
    '''
    
    leading_digit = math.trunc(10**(-math.floor(math.log10(amount))\
    + num_digits - 1) * amount)

    return leading_digit


def get_leading_digits_range(num_digits):
    '''
    "Given a number of digits, return the range of numbers with 
    the desired amount of digits as a tuple."

    Input:
        num_digits: (integer) a number of digits 
          e.g. 1, 2, 3

    Returns: tuple
    '''
    
    n = int(num_digits)
    
    return (10**(n - 1), 10**n)


def compute_expected_benford_dist(num_digits):
    '''
    "Given a number of digits, compute the expected Benford
    Distribution of the numbers with the desired number of digits
    as a list of floats."

    Inputs:
        num_digits: (integer) a number of digits
          e.g. 1 or 2

    Returns: list of floats
    '''
    
    dist_list = []
    a1, a2 = get_leading_digits_range(num_digits)
    
    for d in list(range(a1, a2)):
        dist_list.append(math.log10(1 + 1 / d))
        
    return dist_list


def compute_benford_dist(currency_symbol, amount_strs, num_digits):
    '''
    "Given a currency symbol, a list of amounts in that currency, and a 
    number of digits, compute the Benford Distribution as a list of floats
    containing the ratio of the numbers with the same leading digit(s) based
    on the number of specified digits."

    Inputs: 
        currency_symbol: (string) a currency symbol
          e.g. '$', 'C$', '\u00A3'
        amount_strs: (list of strings) a list of amounts with currency symbol
          e.g. ['$2.34'] or ['C$1.01', 'C$2.20', 'C$0.000055']
        num_digits: (integer) the number of desired digits in each amount
          e.g. 1 or 2

    Returns: list of floats
    '''
    
    benford_list = []
    a1, a2 = get_leading_digits_range(num_digits)
    M = len(list(range(a1, a2)))
    N = len(amount_strs)
    
    benford_list.append(0.0)
    benford_list_2 = benford_list * M
    
    for s in amount_strs:
        g = float(extract_amount(currency_symbol, str(s)))
        h = ((extract_leading_digits(g, num_digits)))
        benford_list_2[h - a1] = benford_list_2[h - a1] + 1 / N
        
    return benford_list_2


def compute_benford_MAD(currency_symbol, amount_strs, num_digits):
    '''
    "Given a currency symbol, a list of amounts in that currency, and a 
    number of digits, compute the mean absolute difference (MAD) of the 
    expected Benford Distribution and the actual Benford distribution of 
    a list of amounts with the desired number of digits as a float."

        Inputs:
            currency_symbol: (string) a currency symbol
              e.g. '$', 'C$', '\u00A3'
            amount_strs: (list of strings) a list of amounts 
            with currency symbol
              e.g. ['$2.34'] or ['C$1.01', 'C$2.20', 'C$0.000055']
            num_digits: (integer) the number of desired digits in each amount
              e.g. 1 or 2

        Returns: float
    '''
    MAD = 0.0
    c1, c2 = get_leading_digits_range(num_digits)
    z = list(range(c1, c2))
    N = len(range(c1, c2))
    a = compute_expected_benford_dist(num_digits)
    b = compute_benford_dist(currency_symbol, amount_strs, num_digits)
    
    for y in z:
        MAD = MAD + abs(a[y - c1] - b[y - c1])

    return MAD / N


################ Do not change the code below this line ################

def plot_benford_dist(currency_symbol, amount_strs, num_digits, output_filename):
    '''
    Plot the actual and expected benford distributions

    Inputs:
        currency_symbol: (string) a currency symbol e.g. '$', 'C$', '\u00A3'
        amount_strs: (list of strings) a non-empty list of positive
            amounts as strings
        num_digits: (int) number of leading digits
    '''
    assert num_digits > 0, \
        "num_digits must be greater than zero {:d}".format(num_digits)

    n = len(amount_strs)
    assert n > 0, \
        "amount_strs must be a non-empty list"

    # compute range of leading digits
    (lb, ub) = get_leading_digits_range(num_digits)
    if lb == 0 and ub == 0:
        print("Skipping plot:invalid return value from get_leading_digits_range")
        return
    digits = range(lb,ub)

    # start a new figure
    f = plt.figure()

    # plot expected distribution
    expected = compute_expected_benford_dist(num_digits)
    plt.scatter(digits, expected, color="red", zorder=1)

    # plot actual distribution
    actual = compute_benford_dist(currency_symbol, amount_strs, num_digits)
    plt.bar(digits, actual, align="center", color="blue", zorder=0)

    # set hash marks for x axis.
    plt.xticks(range(lb, ub, lb))

    # compute limits for the y axis
    max_val = max(max(expected), max(actual))
    y_ub = max_val * 1.1
    plt.ylim(0,y_ub)

    # add labels
    plt.title("Actual (blue) and expected (red) Benford distributions")
    if num_digits ==1: 
        plt.xlabel("Leading digit")
    else:
        plt.xlabel("Leading digits")
    plt.ylabel("Proportion")

    if output_filename:
        # save the plot
        plt.savefig(output_filename)
    else:
        # show the plot
        plt.show()


def go():
    '''
    Process the arguments and do the work.
    '''
    usage = ("usage: python benford.py <input filename> <column number>"
             "<currency symbol> <num digits>")

    if len(sys.argv) < 5 or len(sys.argv) > 6:
        print(usage)
        return

    input_filename = sys.argv[1]
    if not os.path.isfile(input_filename):
        print(usage)
        print("error: file not found: {}".format(input_filename))
        return

    # convert column number argument to an integer
    try:
        col_num = int(sys.argv[2])
    except ValueError:
        s = "error: column number must be an integer: {}"
        print(usage)
        print(s.format(sys.argv[2]))
        return

    data = util.read_column_from_csv(input_filename, col_num, True)
    currency_symbol = sys.argv[3]

    # convert number of digits argument to an integer
    try:
        num_digits = int(sys.argv[4])
    except ValueError:
        s = "error: number of digits must be an integer: {}".format(sys.argv[4])
        print(usage)
        print(s.format(sys.argv[4]))
        return

    # grab the name for the PNG file, if exists.
    if len(sys.argv) == 5:
        output_filename = None
    else:
        output_filename = sys.argv[5]

    plot_benford_dist(currency_symbol, data, num_digits, output_filename)

    # print only four digits after the decimal point
    print("MAD: {:.4}".format(compute_benford_MAD(currency_symbol, data, num_digits)))

if __name__=="__main__":
    go()

