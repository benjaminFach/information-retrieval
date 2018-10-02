
# coding: utf-8

# In[ ]:


#  imports
import operator
import string
from struct import unpack


# In[ ]:


#  constants
BYTE_LEN = 8
ID_LEN = 4
FREQ_LEN = 4

#  a conversion table for remvoving punctuation from strings
CONV_TABLE = str.maketrans({key: None for key in string.punctuation})


# In[ ]:


#  open inverted index for retrieval
index = open("inverted_file", 'rb')


# In[ ]:


#  global data structures
#  key: term
#  value: (term_frequency, byte_offset)
dictionary = dict()


# In[ ]:


#  Utility functions

#  given a term, return the doc ids
#  and term freqs
def query_term(term):
    #  dict data structure for storing results
    #  key: doc ID
    #  value: term freq
    results = dict()
    
    #  apply same rules to query as indexing
    term = term.translate(CONV_TABLE).rstrip().lower()
    
    #  grab byte offset from dictionary
    try:
        byte_offset = int(dictionary[term][1])
    
    except KeyError:
        return None
    
    #  move file pointer to this offset
    index.seek(byte_offset)
    
    #  we need to read 8 bytes for each doc
    #  4 byte doc id, 4 byte term freq
    doc_count = int(dictionary[term][0])
    
    for i in range(0, doc_count * BYTE_LEN, BYTE_LEN):
        doc_id = unpack('I', index.read(ID_LEN))[0]
        term_freq = unpack('I', index.read(FREQ_LEN))[0]
        results[doc_id] = term_freq
    
    return results

#  given test (query) results
#  print the doc freq and postings list
def print_test_all(term, results):
    if not print_test_freq(term, results):
        return False
    
    print("Posting list: ")
    print(", ".join(map(str, sorted(results.keys()))))
        
#  given test (query) results
#  print only the document frequency
def print_test_freq(term, results):
    print("\nTest results for {}:".format(term))
    
    #  if no results, print none and quit
    if results is None:
        print("No results found")
        return False
    
    print("{} documents returned".format(len(results.keys())))
    return True


# In[ ]:


#  load in dictionary from file
#  each line is tuple
#  (term, document frequency, byte offset)
key = ""
val = tuple()
with open("dictionary.txt", "r") as dictionary_file:
    for tup in dictionary_file:
        entry = tup[1:-1].split()
        key = entry[0].translate(CONV_TABLE).rstrip().lower()
        val = (entry[1][0:-1], entry[2][:-1])
        dictionary[key] = val


# In[ ]:


#  Testing

#  doc freqs and postings list
print_test_all("Heidelberg", query_term("Heidelberg"))
print_test_all("plutonium", query_term("plutonium"))
print_test_all("Omarosa", query_term("Omarosa"))
print_test_all("octopus", query_term("octopus"))

#  doc freq only
print_test_freq("Hopkins", query_term("Hopkins"))
print_test_freq("Harvard", query_term("Harvard"))
print_test_freq("Stanford", query_term("Stanford") )
print_test_freq("college", query_term("college"))

#  Jeff Bezos test
jeff_results = query_term("Jeff")
bezos_results = query_term("Bezos")
jeff_bezos_test = {x:jeff_results[x] for x in jeff_results if x in bezos_results}
print_test_all("Jeff Bezos", jeff_bezos_test)

