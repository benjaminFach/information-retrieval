
# coding: utf-8

# In[267]:


#  imports
import re
import string
import operator


# In[268]:


#  Utility functions, constants

#  create dictionary to store results
#  key: term
#  value:  dictionary: (docID, numOccurences)
postings_lists = dict()

#  A convenience dictionary to quickly get term frequencies
term_freqs = dict()

#  A convenience dictionary to quickly get term document counts
term_doc_counts = dict()

#  pattern to extract the document ID
doc_id_pattern = '(?<=ID=)(.*)(?=>)'

#  conversion table for removing puncutation
conv_table = str.maketrans({key: None for key in string.punctuation})

#  grab the document ID from a paraph ID line
def get_doc_id(line):
    match = re.search(doc_id_pattern, line)
    return match.group(1)

#  increment the term frequency for a term
def increment_term_freq(term):
    if term in term_freqs:
        term_freqs[term] = term_freqs[term] + 1
    else:
        term_freqs[term] = 1

#  increment the doc count for a term
def increment_doc_count(term):
    if term in term_doc_counts:
        term_doc_counts[term] = term_doc_counts[term] + 1
    else:
        term_doc_counts[term] = 1

#  reads each document, gets each term in the paragraph 
#  by splitting on space and adds the term to the postings lists
def process_document_content(doc_id, document):
    terms = document.split(" ")
    for term in terms:
        term = term.translate(conv_table).rstrip().lower()
        
        #  skip blank words, usually from a separated punctuation. 
        #  Links and usernames too
        if len(term) == 0 or term == "\n" or term.startswith("http") 
        or "u00" in term:
            continue
        increment_term_freq(term)
        if term in postings_lists:
            if doc_id in postings_lists[term]:
                #  word is already in this document, increase its document occurence
                postings_lists[term][doc_id] = postings_lists[term][doc_id] + 1
            #  word is already found in collection but new to the document
            else: 
                postings_lists[term][doc_id] = 1
                increment_doc_count(term)
                
        #  word is new to collection
        else:
            postings_lists[term] = {doc_id: 1}
            increment_doc_count(term)


# In[269]:


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


# In[270]:


#  sort our convenience dictionaries by creating sorted lists of tuples
sorted_freqs = sorted(term_freqs.items(),
                      key=lambda kv: kv[1], reverse=True)
sorted_doc_counts = sorted(term_doc_counts.items(),
                           key=lambda kv: kv[1], reverse=True)

#  write to file the 100 most-encountered words
with open('headlines_results.txt', 'w') as out:
    #  number of paragraphs processed
    out.write("Processed {} paragraphs\n".format(doc_id))

    #  vocabulary size
    out.write("Observed {} unique words\n".format(len(sorted_freqs)))

    #  collection size
    out.write("Observed {} words in total\n".format(sum(term_freqs.values())))
    
    out.write("\nTop 100 occurences:\n")
    for i in range(1, 101):
        curr_term = sorted_freqs[i][0]
        out.write("{}. {}, collection_freq={}, document_freq={}\n"
                  .format(i, curr_term, sorted_freqs[i][1],
                          len(postings_lists[curr_term])))
    
    out.write("\nThe 500th most frequent word is: {}, collection_freq={}, document_freq={}"
              .format(sorted_freqs[500][0], sorted_freqs[500][1], 
                      len(postings_lists[sorted_freqs[500][0]])))
    out.write("\nThe 1000th most frequent word is: {}, collection_freq={}, document_freq={}"
              .format(sorted_freqs[1000][0], sorted_freqs[1000][1], 
                      len(postings_lists[sorted_freqs[1000][0]])))
    out.write("\nThe 5000th most frequent word is: {}, collection_freq={}, document_freq={}\n"
              .format(sorted_freqs[5000][0], sorted_freqs[5000][1], 
                      len(postings_lists[sorted_freqs[5000][0]])))
    
    in_one_doc = set()
    for tup in sorted_doc_counts:
        if tup[1] == 1:
            in_one_doc.add(tup[0])
    out.write("There are {} words that appear in only one document\n"
              .format(len(in_one_doc)))
    out.write("{} percent of dictionary words appear in just one document"
              .format( 100* (len(in_one_doc)/ len(sorted_freqs))))

