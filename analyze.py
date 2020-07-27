# Kyle Pinder
# CS121: Analyzing Election Tweets
# Part 2: Tasks 1-7

import argparse
import emoji
import json
import string
import sys
import unicodedata
from util import sort_count_pairs, grab_year_month, pretty_print_by_month, get_json_from_file
from basic_algorithms import find_top_k, find_min_count, find_frequent

##################### DO NOT MODIFY THIS CODE ##################### 

# Find all characters that are classifed as punctuation in Unicode
# (except #, @, &) and combine them into a single string.
def keep_chr(c):
    return (unicodedata.category(c).startswith('P') and \
                (c != "#" and c != "@" and c != "&"))
PUNCTUATION = " ".join([chr(i) for i in range(sys.maxunicode) if keep_chr(chr(i))])

# When processing tweets, ignore words, symbols, and emoji in this set.
WORDS = ["a", "an", "the", "this", "that", "of", "for", "or", 
         "and", "on", "to", "be", "if", "we", "you", "in", "is", 
         "at", "it", "rt", "mt", "with"]

SYMBOLS = [chr(i) for i in range(sys.maxunicode) if 
           unicodedata.category(chr(i)) in ("Sm", "Sc", "Sk", "So")] + ["\n"]

EMOJI = list(emoji.UNICODE_EMOJI.keys())

STOP_WORDS = set(WORDS + SYMBOLS + EMOJI)

# When processing tweets, ignore words that start with a prefix that
# appears in this tuple.
STOP_PREFIXES  = ("@", "#", "http", "&amp")

#####################  MODIFY THIS CODE ##################### 

#Pre-processing Task
def pre_process_tweets(tweets, n):
    '''
    Pre-processes the tweets for tasks 4 and 5.

    Inputs:
        tweets: (list) list of tweets
        n: (int) the length of the ngrams

    Returns: the processed list of tweets
    '''
    l = range(len(tweets))
    final_list = [] 

    for i in l:
        a = tweets[i]['text']
        word_list = a.split()
        w_range = range(len(word_list))
        for w in w_range:
            if word_list[w] in PUNCTUATION:
                word_list[w] = 'a'
            word_list[w] = word_list[w].strip(PUNCTUATION)
            if word_list[w].startswith('$'):
                word_list[w] = 'a'
            word_list[w] = word_list[w].lower()
            if word_list[w] in STOP_WORDS:
                word_list[w] = 'a'
            for r in range(len(STOP_PREFIXES)):
                if word_list[w].startswith(STOP_PREFIXES[r]):
                    word_list[w] = 'a'

        new_word_list = []
        for u in w_range:
            if word_list[u] not in STOP_WORDS:
                new_word_list.append(word_list[u])
        
        m = range(len(new_word_list) - (n - 1))
        for j in m:
            final_list.append((tuple(new_word_list[j : j + n])))

    return final_list

#Pre-processing Task 6
def find_frequent_6(items, k):
    '''
    Find items where the number of times the item occurs is at least
    1/k * len(items).

    Input: 
        items: list of items
        k: integer

    Returns: sorted list of tuples
    '''
   
    N = len(items)
    items_dict = {z : 0 for z in items}
    new_dict = {}
    overall_dict = {z : 0 for z in items}
    
    for a in items:
        if a in new_dict:
            items_dict[a] += 1
        if a not in new_dict:
            new_dict[a] = 0
            if len(new_dict) < k - 1:
                items_dict[a] += 1
            if len(new_dict) == k - 1:
                items_dict[a] += 1
                for b in new_dict:
                    items_dict[b] -= 1
                for b in overall_dict:
                    if b in new_dict:
                        if items_dict[b] == 0:
                            del new_dict[b]
     
    for a in overall_dict:
        if items_dict[a] == 0:
            del items_dict[a] 
        
    l = items_dict.items()

    return sort_count_pairs(l)


#Pre-processing Task 7
def separate_monthly_tweets(tweets, n):
    '''
    Pre-processes the tweets for task 7.

    Inputs:
        tweets: (list) list of tweets
        n: (int) the length of the ngrams

    Returns: three lists of tweets separated by month
    '''
    l = range(len(tweets))
    april_tweets = []
    may_tweets = []
    june_tweets = []

    for i in l:
        b = grab_year_month(tweets[i]['created_at'])
        if b == (2017, 4):
            april_tweets.append(tweets[i])
        if b == (2017, 5):
            may_tweets.append(tweets[i])
        if b == (2017, 6):
            june_tweets.append(tweets[i])

    return april_tweets, may_tweets, june_tweets


# Task 1
def find_top_k_entities(tweets, entity_key, k):
    '''
    Find the K most frequently occuring entitites.

    Inputs:
        tweets: a list of tweets
        entity_key: a pair ("hashtags", "text"), 
          ("user_mentions", "screen_name"), etc
        k: integer

    Returns: list of entity, count pairs
    '''
    z1, z2 = entity_key
    c = []
    l = range(len(tweets))
    
    for i in l:
        a = tweets[i]['entities'][z1]
        range_a = range(len(a))
        for j in range_a:
            b = a[j]
            c.append(b[z2])

    entity_list = [d.lower() for d in c]
        
    return find_top_k(entity_list, k)


# Task 2
def find_min_count_entities(tweets, entity_key, min_count):
    '''
    Find the entitites that occur at least min_count times.

    Inputs:
        tweets: a list of tweets
        entity_key: a pair ("hashtags", "text"), 
          ("user_mentions", "screen_name"), etc
        min_count: integer 

    Returns: list of entity, count pairs
    '''

    z1, z2 = entity_key
    c = []
    l = range(len(tweets))

    for i in l:
        a = tweets[i]['entities'][z1]
        range_a = range(len(a))
        for j in range_a:
            b = a[j]
            c.append(b[z2])

    entity_list = [d.lower() for d in c]

    return find_min_count(entity_list, min_count)


# Task 3
def find_frequent_entities(tweets, entity_key, k):
    '''
    Find entities where the number of times the specific entity occurs
    is at least fraction * the number of entities in across the tweets.

    Input: 
        tweets: a list of tweets
        entity_key: a pair ("hashtags", "text"), 
          ("user_mentions", "screen_name"), etc
        k: integer

    Returns: list of entity, count pairs
    '''

    z1, z2 = entity_key
    c = []
    l = range(len(tweets))

    for i in l:
        a = tweets[i]['entities'][z1]
        range_a = range(len(a))
        for j in range_a:
            b = a[j]
            c.append(b[z2])

    entity_list = [d.lower() for d in c]

    return find_frequent(entity_list, k)


# Task 4
def find_top_k_ngrams(tweets, n, k):
    '''
    Find k most frequently occurring n-grams
    
    Inputs:
        tweets: a list of tweets
        n: integer
        k: integer

    Returns: list of ngram/value pairs
    '''

    final_list = pre_process_tweets(tweets, n)

    return find_top_k(final_list, k)


# Task 5
def find_min_count_ngrams(tweets, n, min_count):
    '''
    Find n-grams that occur at least min_count times.
    
    Inputs:
        tweets: a list of tweets
        n: integer
        min_count: integer


    Returns: list of ngram/value pairs
    '''

    final_list = pre_process_tweets(tweets, n)

    return find_min_count(final_list, min_count)


# Task 6
def find_frequent_ngrams(tweets, n, k):
    '''
    Find frequently occurring n-grams

    Inputs:
        tweets: a list of tweets
        n: integer
        k: integer

    Returns: list of ngram/value pairs
    '''

    final_list = pre_process_tweets(tweets, n)

    return find_frequent_6(final_list, k)


# Task 7

def find_top_k_ngrams_by_month(tweets, n, k):
    '''                                                                                                            
    Find the top k ngrams for each month.

    Inputs:
        tweets: list of tweet dictionaries
        n: integer
        k: integer

    Returns: sorted list of pairs.  Each pair has the form: 
        ((year,  month), (sorted top-k n-grams for that month with their counts))
    '''

    final_list = []
    april_tweets, may_tweets, june_tweets = separate_monthly_tweets(tweets, n)

    april = ((2017, 4), (find_top_k_ngrams(april_tweets, n, k)))
    may = ((2017, 5), (find_top_k_ngrams(may_tweets, n, k)))
    june = ((2017, 6), (find_top_k_ngrams(june_tweets, n, k)))

    if len(april_tweets) > 0:
        final_list.append((april))
    if len(may_tweets) > 0:
        final_list.append((may))
    if len(june_tweets) > 0:
        final_list.append((june))
    
    return final_list


def parse_args(args):
    '''                                                                                                                
    Parse the arguments

    Inputs:
        args: list of strings

    Result: parsed argument object.

    '''
    s = 'Analyze presidential candidate tweets .'
    parser = argparse.ArgumentParser(description=s)
    parser.add_argument('-t', '--task', nargs=1, 
                        help="<task number>", 
                        type=int, default=[0])
    parser.add_argument('-k', '--k', nargs=1, 
                        help="value for k", 
                        type=int, default=[1])
    parser.add_argument('-c', '--min_count', nargs=1, 
                        help="min count value", 
                        type=int, default=[1])
    parser.add_argument('-n', '--n', nargs=1, 
                        help="number of words in an n-gram", 
                        type=int, default=[1])
    parser.add_argument('-e', '--entity_key', nargs=1, 
                        help="entity key for task 1", 
                        type=str, default=["hashtags"])
    parser.add_argument('file', nargs=1, 
                        help='name of JSON file with tweets')

    try:
        return parser.parse_args(args[1:])
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)


def go(args):
    '''
    Call the right function(s) for the task(s) and print the result(s).

    Inputs:
        args: list of strings
    '''

    task = args.task[0]
    if task <= 0 or task > 7:
        print("The task number needs to be a value between 1 and 7 inclusive.",
              file=sys.stderr)
        sys.exit(1)

    if task in [1, 2, 3]:
        ek2vk = {"hashtags":"text", 
                 "urls":"url", 
                 "user_mentions":"screen_name"}

        ek = args.entity_key[0]
        if ek not in ek2vk:
            print("Invalid entitity key:", ek)
            sys.exit(1)
        entity_type = (args.entity_key[0], ek2vk.get(ek, ""))

    tweets = get_json_from_file(args.file[0])

    if task == 1:
        print(find_top_k_entities(tweets, entity_type, args.k[0]))
    elif task == 2:
        print(find_min_count_entities(tweets, entity_type, args.min_count[0]))
    elif task == 3:
        print(find_frequent_entities(tweets, entity_type, args.k[0]))
    elif task == 4:
        print(find_top_k_ngrams(tweets, args.n[0], args.k[0]))
    elif task == 5:
        print(find_min_count_ngrams(tweets, args.n[0], args.min_count[0]))
    elif task == 6:
        print(find_frequent_ngrams(tweets, args.n[0], args.k[0]))
    else:
        result = find_top_k_ngrams_by_month(tweets, args.n[0], args.k[0])
        pretty_print_by_month(result)
        

if __name__=="__main__":
    args = parse_args(sys.argv)
    go(args)



