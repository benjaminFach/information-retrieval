
# coding: utf-8

# In[140]:


#  Imports
import re
import string
import sys
import operator
from struct import pack


# In[141]:


#  Constants

#  a regex pattern for extracting the document ID
DOC_ID_PATTERN = '(?<=ID=)(.*)(?=>)'

#  a conversion table for remvoving punctuation from strings
CONV_TABLE = str.maketrans({key: None for key in string.punctuation})


# In[142]:


#  Global data structures

#  a dictionary to store results
#  key: term
#  value:  dictionary: (docID, numOccurences)
postings_lists = dict()

#  dictionary is list of 3-tuples
#  (term, document frequency, byte offset)
#
#  term: represents a word in the collection
#  document frequency: how many docs term appears in
#  byte offset: starting position of posting list in
#           in the inverted file

dictionary = list()

#  inverted file is a sequence of bytes
#  in the pattern of 4 bytes doc id, 4 byte term frequency
#  this repeats until the end of the file
inverted_file = open("inverted_file", 'wb')

#  int to track number of unique terms
unique_terms = 0

#  int to track total number of terms
total_terms = 0


# In[143]:


#  Utility functions

#  grab the document ID from a paraph ID line
def get_doc_id(line):
    match = re.search(DOC_ID_PATTERN, line)
    return match.group(1)

#  check if this should count as a term
#  empty strings and hyperlinks are not terms
def is_not_term(str):
    if len(str) == 0 or str == "\n" or is_link(str):
        return True
    
    return False

#  check if this string represents a link
def is_link(str):
    if str.startswith("http") or str.endswith("jpg")     or str.endswith("pdf") or str.endswith("hk"):
        return True
    
    return False

#  calculate number of bytes posting list will
#  take up in an inverted file
#  4 bytes for each doc id, 4 bytes for each term freq
def calc_post_bytes(post_len):
    return post_len * 8


# In[144]:


#  Document parser

#  reads a document and gets each term
#  by splitting on space and adds the term to the postings lists
def process_document_content(doc_id, document):
    global total_terms
    global unique_terms
    
    terms = document.split(" ")
    for term in terms:
        term = term.translate(CONV_TABLE).rstrip().lower()
        
        #  skip blank words, usually from a separated punctuation. 
        #  Links, images too
        if is_not_term(term):
            continue
        
        total_terms = total_terms + 1
        if term in postings_lists:
            if doc_id in postings_lists[term]:
                #  word is already in this document, increase its document occurence
                postings_lists[term][doc_id] = postings_lists[term][doc_id] + 1
            #  word is already found in collection but new to the document
            else:
                postings_lists[term][doc_id] = 1
                
        #  word is new to collection
        else:
            unique_terms = unique_terms + 1
            postings_lists[term] = {doc_id: 1}


# In[145]:


#  read in the file
current_line = 0
doc_id = 0
with open('headlines.txt', 'r') as headlines:
    for line in headlines:
        current_line = current_line + 1
        
        #  document ID is the first line
        if current_line % 4 == 1:
            doc_id =  get_doc_id(line)
        
        #  document content is the second, process for each term
        elif current_line %4 == 2:
            process_document_content(doc_id, line)
            
        #  third and fourth lines are closed p tags and empty lines


# In[146]:


#  break lexicon into a dictionary and inverted file

curr_byte_pos = 0

#  process each term
for term in postings_lists:
    #  based on length of posting list for term
    #  calculate number of bytes it will take
    #  in the inverted file
    
    dictionary.append((term, len(postings_lists[term]), curr_byte_pos))
    
     #  keep pointer updated
    post_byte_len = calc_post_bytes(len(postings_lists[term]))
    curr_byte_pos = curr_byte_pos + post_byte_len
    
    #  write all doc ids and term freq
    
    for doc_id in postings_lists[term]:
        inverted_file.write(pack('II', int(doc_id), int(postings_lists[term][doc_id])))
            
#  sort dictionary, needed for query evaluation
dictionary.sort()

#  flush to disk and close inverted file opening
#  no sort in inverted file contents!
inverted_file.flush()
inverted_file.close()

with open('dictionary.txt', 'w') as dict_file:
    for tup in dictionary:
        dict_file.write("{}\n".format(str(tup)))


# In[147]:


#  outputs
print("{} unique terms".format(unique_terms))
print("{} total terms".format(total_terms))
print("{} documents".format(doc_id))

