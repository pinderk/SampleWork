# CS122 W'18: Markov models and hash tables
# Kyle Pinder


TOO_FULL = 0.5
GROWTH_RATIO = 2


class Hash_Table:

    def __init__(self,cells,defval):
        '''
        Construct a bnew hash table with a fixed number of cells equal to the
        parameter "cells", and which yields the value defval upon a lookup to a
        key that has not previously been inserted.
        '''
     
        self.defval = defval
        self.cells = cells
        self.data = [defval] * cells
        self.check_size = 0
    

    def lookup(self,key):
        '''
        Retrieve the value associated with the specified key in the hash table,
        or return the default value if it has not previously been inserted. 
        '''

        hash_index = self.create_hash(key) 
        if self.data[hash_index] == self.defval:
            return self.defval

        elif key in self.data[hash_index]:
            return self.data[hash_index][1]

        else:
            hash_index = self.find_slot(key, hash_index)
            if self.data[hash_index] != self.defval:
                return self.data[hash_index][1]            

        return self.defval  


    def update(self,key,val):
        '''
        Change the value associated with key "key" to value "val".
        If "key" is not currently present in the hash table,  insert it with
        value "val".
        '''
     
        if self.check_size / self.cells >= TOO_FULL:
            self.rehash()

        hash_index = self.create_hash(key)

        if self.data[hash_index] == self.defval:
            self.data[hash_index] = (key, val)
            self.check_size += 1

        elif key in self.data[hash_index]:
            self.data[hash_index] = (key, val)

        else:
            new_index = self.find_slot(key, hash_index)
            self.data[new_index] = (key, val)
            self.check_size += 1


    def find_slot(self, key, hash_index):
        '''
        Takes the key and the hash index and finds the next slot for the new
        hash index.
        '''

        while (self.data[hash_index] != self.defval and \
        self.data[hash_index][0] != key):
            hash_index = (hash_index + 1) % self.cells

        return hash_index


    def rehash(self):
        '''
        Increases the size of the hash table and updates the table with the new 
        values.
        '''
    
        self.cells *= GROWTH_RATIO
        hold_data = self.data
        self.data = [self.defval] * self.cells
        for d in hold_data:
            if d != self.defval:
                self.update(d[0], d[1])  
         

    def create_hash(self, string):
        '''
        Takes a string and returns the hash value of the string.
        '''
   
        letter_tot = 0 

        letter_tot = sum(ord(l) for l in string)

        letter_tot = (letter_tot * 37) % self.cells

        return letter_tot 
           

