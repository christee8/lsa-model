#!/usr/bin/env python
# coding: utf-8

# # TODO
# 
# ## Major
# - [x] create term-by-document matrix (calculate words frequncies for each term-document pair)
#  - [ ] check that it's actually correct - especially if we don't map terms to wrong documents
# - [x] convert term-by-document frequencies to tf-idf (calcualte tf-idf for each term-document pair)
#  - [ ] check
# - [ ] we may need actual (numpy?) matrix?
# - [ ] LSI magic
# 
# ### Minor
# - [x] remove numbers from terms - done but not sure if it's good thing to do, maybe it's also important for relevancy of docs,
# like for example when there is year written?

# In[2]:


import pandas as pd
import numpy as np
import string
import nltk
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import RegexpTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer


# In[3]:


np.random.seed(42)


# In[4]:


bp_data = pd.read_csv("articles.csv", header=0)


# In[5]:


bp_data.head(1)


# In[6]:


def preprocess_docs(docs, use_lemmatizer = True):
    '''Tokenize and preprocess documents
    
    Parameters
    ----------
    use_lemmatizer : bool
                     Uses lemmazizer if True, othrerwise uses stemmer.
    '''
    preproccessed_docs = []
    
    # English stop words list
    en_stop = set(stopwords.words('english'))
    
    # Word tokenizer that removes punctuation
    tokenizer = RegexpTokenizer(r'\w+')
    
    # lemmatizer / Stemmer
    if use_lemmatizer:
        lemmatizer = WordNetLemmatizer()
    else:
        stemmer = SnowballStemmer("english")
    
    for row in docs.itertuples(index=True, name='Doc'):
        text = row.text
        
        # remove numbers
        text = re.sub(r'\d+', '', text)
        
        text_words = tokenizer.tokenize(text)
        
        if use_lemmatizer:
            text_words = [lemmatizer.lemmatize(word, pos="v").lower() for word in text_words
                          if word not in string.punctuation and word.lower() not in en_stop]
        else:
            text_words = [stemmer.stem(word).lower() for word in text_words
                         if word not in string.punctuation and word.lower() not in en_stop]
        
        preproccessed_docs.append({'words': text_words})
    
    pdocs = pd.DataFrame(preproccessed_docs)
    return pdocs


# In[39]:


preproccessed_docs = preprocess_docs(bp_data)
display(preproccessed_docs)


# In[8]:


def get_term_by_document_frequency(preprocessed_docs):
    document_by_term = {}
    
    for index, row in preprocessed_docs.iterrows():
        doc_id = index
        doc_words = row['words']
        
        document_by_term[doc_id] = {
            'total_words': len(doc_words)
        }
        
        
        for word in set(row['words']):
            document_by_term[doc_id][word] = doc_words.count(word)

    df = pd.DataFrame(document_by_term)
    
    return df


# In[54]:


df_frequency = get_term_by_document_frequency(preproccessed_docs)


# In[55]:


df_frequency


# In[105]:


def reduce_terms(df_frequency, max_df=1, min_df=0, max_terms=None):
    '''Remove unimportant terms from term-by-document matrix.
    
    Parameters
    ----------
    df : pd.DataFrame
    max_df : float , between [0, 1]
             Terms that appear in more % of documents will be ignored
    min_df : float , between [0, 1]
             Terms that appear in less % of documents will be ignored
    max_terms : int , None
                If not None, only top `max_terms` terms will be returned.
    '''
    df = df_frequency.copy()
    if 'doc_frequency' in df:
        df = df.drop(columns='doc_frequency')
    
    corpus_size = df.shape[1]
    
    df['doc_frequency'] = df_frequency.fillna(0).astype(bool).sum(axis=1) / corpus_size
    
    total_words = df.loc['total_words']
    
    df = df[df.doc_frequency <= max_df]
    df = df[df.doc_frequency >= min_df]
    
    if max_terms is not None:
        assert('not implementd' == False) # @TODO - implement or remove
    
    return df


# In[106]:


reduce_terms(df_frequency).sort_values('doc_frequency', ascending=False).shape


# In[108]:


reduce_terms(df_frequency, 0.8, 0.1).sort_values('doc_frequency', ascending=False)


# In[77]:


df_reduced = reduce_terms(df_frequency, 0.8, 0.1)


# In[75]:


def get_tf_idf(df_frequency):
    df = df_frequency.copy()
    # tf := word frequency / total frequency
    df = df.drop('total_words', inplace=False)[:] / df.loc['total_words']
    
    # idf := log ( len(all_documents) / len(documents_containing_word) )
    
    corpus_size = df.shape[1]

    # number of non-zero cols
    df['doc_frequency'] = df.fillna(0).astype(bool).sum(axis=1)
        
    df['idf'] = np.log( corpus_size / df['doc_frequency'] )
    
    # tf-idf := tf * idf
    _cols = df.columns.difference(['idf', 'doc_frequency'])
    df[_cols] = df[_cols].multiply(df["idf"], axis="index")
    
    df.drop(columns=['doc_frequency', 'idf'], inplace=True)
    
    return df


# In[78]:


df_tf_idf = get_tf_idf(df_reduced)
display(df_tf_idf)


# In[13]:


values = df_tf_idf.fillna(0).to_numpy()
values


# In[ ]:





# In[ ]:




