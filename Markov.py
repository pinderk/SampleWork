# CS122 W'18: Markov models and hash tables
# Kyle Pinder

import sys
import math
import Hash_Table

HASH_CELLS = 57

class Markov:

    def __init__(self,k,s):
        '''
        Construct a new k-order Markov model using the statistics of string "s"
        '''

        self.k = k
        self.s = s
        self.ht = self.create_hash_table(k, s)
        self.num_char_used = self.get_char_used(s)
        

    def log_probability(self,s):
        '''
        Get the log probability of string "s", given the statistics of
        character sequences modeled by this particular Markov model
        This probability is *not* normalized by the length of the string.
        '''

        prob = 0
        k = self.k
        S = self.num_char_used
        
        sps_k = s + s[:k]

        sps_k1 = s + s[:k+1]

        for r in range(len(s)):
            N = self.ht.lookup(sps_k[r:r+k])
            M = self.ht.lookup(sps_k1[r:r+k+1])

            prob += math.log((M+1)/(N+S))

        return prob

 
    def get_char_used(self, s):
        ''' 
        Appends a character to a list if it has not been seen before and returns
        the length of the used character list.
        '''

        char_used = []

        for char in s:
            if char not in char_used:
                char_used.append(char)

        return len(char_used)

        
    def create_hash_table(self, k, s):
        '''
        Creates the hash table from a given key and string.
        '''

        ht = Hash_Table.Hash_Table(HASH_CELLS, 0)

        sps_k = s + s[:k]

        sps_k1 = s + s[:k+1]

        for r in range(len(s)):
            val1 = ht.lookup(sps_k[r:r+k])
            ht.update(sps_k[r:r+k], val1+1)

            val2 = ht.lookup(sps_k1[r:r+k+1])
            ht.update(sps_k1[r:r+k+1], val2+1)

        return ht
        

def identify_speaker(speech1, speech2, speech3, order):
    '''
    Given sample text from two speakers, and text from an unidentified speaker,
    return a tuple with the *normalized* log probabilities of each of the speakers
    uttering that text under a "order" order character-based Markov model,
    and a conclusion of which speaker uttered the unidentified text
    based on the two probabilities.
    '''
    
    conslusion = ""

    speech1_markov = Markov(order, speech1)
    speech2_markov = Markov(order, speech2)
    likelihood1 = speech1_markov.log_probability(speech3)/len(speech3)
    likelihood2 = speech2_markov.log_probability(speech3)/len(speech3)

    if likelihood1 > likelihood2:
        conclusion = "A"

    elif likelihood2 > likelihood1:
        conclusion = "B"

    else:
        conclusion = "A or B"

    return (likelihood1, likelihood2, conclusion)


def print_results(res_tuple):
    '''
    Given a tuple from identify_speaker, print formatted results to the screen
    '''

    (likelihood1, likelihood2, conclusion) = res_tuple
    
    print("Speaker A: " + str(likelihood1))
    print("Speaker B: " + str(likelihood2))

    print("")

    print("Conclusion: Speaker " + conclusion + " is most likely")


if __name__=="__main__":
    num_args = len(sys.argv)

    if num_args != 5:
        print("usage: python3 " + sys.argv[0] + " <file name for speaker A> " +
              "<file name for speaker B>\n  <file name of text to identify> " +
              "<order>")
        sys.exit(0)
    
    with open(sys.argv[1], "rU") as file1:
        speech1 = file1.read()

    with open(sys.argv[2], "rU") as file2:
        speech2 = file2.read()

    with open(sys.argv[3], "rU") as file3:
        speech3 = file3.read()

    res_tuple = identify_speaker(speech1, speech2, speech3, int(sys.argv[4]))

    print_results(res_tuple)

