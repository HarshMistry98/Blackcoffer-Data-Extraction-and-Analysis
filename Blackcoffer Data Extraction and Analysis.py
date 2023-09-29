#!/usr/bin/env python
# coding: utf-8

# #                                                   Blackcoffer

# ## Data Extraction and NLP

# In[16]:


import numpy as np
import pandas as pd


# In[17]:


import requests
from bs4 import BeautifulSoup


# In[18]:


df = pd.read_excel('Input.xlsx')


# In[19]:


df


# In[20]:


len(df.index)


# ## Extracting text from the links and storing in the file

# In[8]:


df['File_name'] = ' '
for i in range(0, len(df.index)):
    df['File_name'][i] = str(df['URL_ID'][i]).replace('.','_') + '.txt'


# In[9]:


df


# In[10]:


import requests
from bs4 import BeautifulSoup


# In[12]:


for i in range(0, len(df.index)):
    url = df['URL'][i]

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find and extract the title
        title = soup.title.string.strip() if soup.title else "No title found"

        # Find and extract the article content (adjust the HTML element and class/id as needed)
        article = soup.find('div', class_='td-post-content tagdiv-type')  # Replace with the appropriate element and class/id

        if article:
            article_text = article.get_text()
        else:
            article_text = "No article content found"
            
        with open(df['File_name'][i],'a+',encoding='utf-8') as txt:
            txt.write(title)
            txt.write(article_text)
    else:
        with open(df['File_name'][i],'a+',encoding='utf-8') as txt:
            txt.write(' ')


# In[15]:


df['Filedata'] = ' '
for i in range(0, len(df.index)):
    with open(df['File_name'][i],'r',encoding='utf-8') as txt:
        data = txt.read().replace('/n',' ')
        df['Filedata'][i] = data


# In[16]:


df


# ## Creating stop words list from given stop words files

# In[17]:


# Step 1: Define a list of stop word file paths
stop_words_files = ["StopWords_Auditor.txt", "StopWords_Currencies.txt","StopWords_DatesandNumbers.txt","StopWords_Generic.txt","StopWords_GenericLong.txt","StopWords_Geographic.txt","StopWords_Names.txt"]  # Replace with the paths to your stop word files

# Step 2: Read stop words from each file and store them in separate lists
stop_words_lists = []

for file_path in stop_words_files:
    with open(file_path, "r") as file:
        stop_words = [line.strip() for line in file]
        stop_words_lists.append(stop_words)


# In[18]:


stop_words_lists


# ## Cleaning data by removing  stop words

# In[19]:


import spacy
nlp = spacy.load('en_core_web_lg')


# In[20]:


def clean_text(text):
    #words = text.split()  # You can use a more advanced tokenizer if needed
    
    doc = nlp(text)
    
    # Remove stop words and punctuation
    words = [token.text for token in doc if token.text.lower() not in stop_words]
    
    # Join the remaining words back into a cleaned text
    cleaned_text = ' '.join(words)
    
    return cleaned_text


# In[22]:


df['Clean_data'] = ' '
for i in range(0, len(df.index)):
    df['Clean_data'][i] = clean_text(df['Filedata'][i])


# In[23]:


df


# ## Creating list of given positive and negative words 

# In[25]:


positive_words = []
negative_words = []


# In[26]:


with open('positive-words.txt', "r") as file:
        word = [line.strip() for line in file]
        positive_words.append(word)


# In[27]:


with open('negative-words.txt', "r") as file:
        word = [line.strip() for line in file]
        negative_words.append(word)


# In[78]:


positive_words


# In[74]:


negative_words


# ## Calculating the variables

# #### POSITIVE SCORE, NEGATIVE SCORE, POLARITY SCORE, SUBJECTIVITY SCORE, AVG SENTENCE LENGTH, PERCENTAGE OF COMPLEX WORDS, FOG INDEX, AVG NUMBER OF WORDS PER SENTENCE, COMPLEX WORD COUNT, WORD COUNT, SYLLABLE PER WORD, PERSONAL PRONOUNS, AVG WORD LENGTH
# 

# In[ ]:


import pyphen


# In[79]:


df['POSITIVE SCORE'] = 0
df['NEGATIVE SCORE'] = 0
df['POLARITY SCORE'] = 0
df['SUBJECTIVITY SCORE'] = 0
df['AVG SENTENCE LENGTH'] = 0
df['PERCENTAGE OF COMPLEX WORDS'] = 0
df['FOG INDEX'] = 0
df['AVG NUMBER OF WORDS PER SENTENCE'] = 0
df['COMPLEX WORD COUNT'] = 0
df['WORD COUNT'] = 0
df['SYLLABLE PER WORD'] = 0
df['PERSONAL PRONOUNS'] = 0
df['AVG WORD LENGTH'] = 0

for i in range(0, len(df.index)):
    
    
    Positive_Score = 0
    Negative_Score = 0
    doc = nlp(df['Clean_data'][i])
    
    #Positive Score and Negative Score
    for token in doc:
        if token.text.lower() in positive_words[0]:
            Positive_Score += 1
        elif token.text.lower() in negative_words[0]:
            Negative_Score += 1
    
    #Polarity Score
    Polarity_Score = (Positive_Score - Negative_Score)/ ((Positive_Score + Negative_Score) + 0.000001)
    
    #Word Count
    total_words = len(doc)
    
    #Subjectivity Score
    Subjectivity_Score = (Positive_Score + Negative_Score)/ ((total_words) + 0.000001)
    
    #Sentence Count
    total_sentences = len(list(doc.sents))
    
    #Average Sentence Length
    Average_Sentence_Length = total_words / total_sentences
    
    #Average Syllable Count Per Word
    #Complex Word Count
    dic = pyphen.Pyphen(lang='en')
    complex_word_count = 0
    syllable_count = 0
    for token in doc:
        
        syllables = dic.inserted(token.text).split('-')
        
        if len(syllables)>2:
            complex_word_count += 1  #Complex words are words in the text that contain more than two syllables
        
        syllable_count += len(syllables) 
    
    Average_Syllable_Count_Per_Word = syllable_count / total_words
    
    #Percentage of Complex words
    Percentage_of_Complex_words = complex_word_count / total_words
    
    #Fog Index
    Fog_Index = 0.4 * (Average_Sentence_Length + Percentage_of_Complex_words)
    
    #Average Number of Words Per Sentence
    Average_Number_of_Words_Per_Sentence = total_words / total_sentences
    
    #Personal Pronoun Count
    personal_pronouns = set(['i', 'me', 'my', 'mine', 'myself',
                             'you', 'your', 'yours', 'yourself',
                             'he', 'him', 'his', 'himself',
                             'she', 'her', 'hers', 'herself',
                             'it', 'its', 'itself',
                             'we', 'us', 'our', 'ours', 'ourselves',
                             'they', 'them', 'their', 'theirs', 'themselves'])
    pronoun_count = 0
    for token in doc:
        # Check if the token is a personal pronoun
        if token.text.lower() in personal_pronouns:
            pronoun_count += 1
              
    #Characters Count
    total_characters = 0
    for token in doc:
        total_characters += len(token.text)
    
    #Average Word Length
    Average_Word_Length = total_characters / total_words
    
    
    df['POSITIVE SCORE'][i] = Positive_Score
    df['NEGATIVE SCORE'][i] = Negative_Score
    df['POLARITY SCORE'][i] = Polarity_Score
    df['SUBJECTIVITY SCORE'][i] = Subjectivity_Score
    df['AVG SENTENCE LENGTH'][i] = Average_Sentence_Length
    df['PERCENTAGE OF COMPLEX WORDS'][i] = Percentage_of_Complex_words
    df['FOG INDEX'][i] = Fog_Index
    df['AVG NUMBER OF WORDS PER SENTENCE'][i] = Average_Number_of_Words_Per_Sentence
    df['COMPLEX WORD COUNT'][i] = complex_word_count
    df['WORD COUNT'][i] = total_words
    df['SYLLABLE PER WORD'][i] = Average_Syllable_Count_Per_Word
    df['PERSONAL PRONOUNS'][i] = pronoun_count
    df['AVG WORD LENGTH'][i] = Average_Word_Length
    


# In[80]:


df


# In[81]:


df = df.drop(['File_name','Filedata','Clean_data'],axis=1)


# In[82]:


df


# ## Storing final result in the excel file 

# In[87]:


df.to_excel('output.xlsx', index=False)

