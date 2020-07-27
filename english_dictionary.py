# CS122: Auto-completing keyboard using Tries
# Distribution
#
# Matthew Wachs
# Autumn 2014
#
# Revised: August 2015, AMR
#   December 2017, AMR
#
# Kyle Pinder

import os
import sys
from sys import exit

import autocorrect_shell


class EnglishDictionary(object):
    def __init__(self, wordfile):
        '''
        Constructor

        Inputs:
          wordfile (string): name of the file with the words.
        '''
        self.words = TrieNode()

        with open(wordfile) as f:
            for w in f:
                w = w.strip()
                if w != "" and not self.is_word(w):                   
                    self.words.add_word(w)


    def is_word(self, w):
        '''
        Is the string a word?

        Inputs:
           w (string): the word to check

        Returns: boolean
        '''
        if w not in self.words.search_word(w):
            return False
        return True


    def num_completions(self, prefix):
        '''
        How many words in the dictionary start with the specified
        prefix?

        Inputs:
          prefix (string): the prefix

        Returns: int
        '''
        completions = self.words.search_word(prefix, "Count")

        if completions == []:
            return 0
        
        return completions[0]


    def get_completions(self, prefix):
        '''
        Get the suffixes in the dictionary of words that start with the
        specified prefix.

        Inputs:
          prefix (string): the prefix

        Returns: list of strings.
        '''        
        
        return self.words.search_word(prefix, "Completions")


class TrieNode(object):
    def __init__(self):
        '''
        Constructor (initiaties the TrieNode class).     
        '''
        self.node_count = 0
        self.node_completion = False 
        self.node_children = {}


    def add_word(self, word):
        '''
        Adds a word to the trie.

        Inputs:
            word: (string) The word that is added to the trie.

        Returns: No explicit output; adds the word to the trie.
        '''        
        if len(word) == 0:
            self.node_completion = True
            self.node_count += 1
            return

        key = word[0]
        word = word[1:]
               
        if key in self.node_children:               
            self.node_children[key].add_word(word)
            self.node_count += 1
           
        else:
            trienode = TrieNode()
            self.node_children[key] = trienode
            trienode.add_word(word)
            self.node_count += 1
        

    def get_suffix(self, prefix=None, prefix_length=0):
        '''
        Creates the possible suffixes of the given prefix.

        Inputs:
            prefix: (string) The given prefix.
            prefix_length: (int) The length of the given prefix.

        Returns: The list of suffixes.
        '''
        word_sublist = []

        if self.node_children.keys() == []:
            return

        if self.node_completion:
            word_sublist.append(prefix[prefix_length:])
        for key in self.node_children:
            word_sublist.extend(self.node_children[key].get_suffix\
            (prefix + key, prefix_length))

        return word_sublist
        

    def search_word(self, word, action="Find", word_list=[], 
        current_prefix=""):
        '''
        Creates a list based on the required action and the given word.

        Inputs:
            word: (string) The given word.
            action: (string) The action necessary for each task 
                    (either Find, Count, or Completions).
            word_list: Initiates the list that is later returned.
            current_prefix: The prefix that is currently being used
                            for the task.

        Returns: A list based on the required action and the given word.

        '''
        if len(word) > 0:
            key = word[0]
            word = word[1:]

            if key in self.node_children:
                current_prefix += key
                self.node_children[key].search_word\
                (word, action, word_list, current_prefix)

            else:
                word_list[:] = []
                return word_list

        else:
            word_list[:] = []
            if action == "Count":
                word_list.append(self.node_count)
  
            elif action == "Find":
                if self.node_completion:
                    word_list.append(current_prefix)

            elif action == "Completions":
                prefix_length = len(current_prefix)                
                if self.node_completion:
                    word_list.append(current_prefix[prefix_length:])                
                for key in self.node_children:
                    word_list.extend(self.node_children[key].get_suffix\
                    (current_prefix + key, prefix_length))                                   

        return word_list
          

if __name__ == "__main__":
    autocorrect_shell.go("english_dictionary")
