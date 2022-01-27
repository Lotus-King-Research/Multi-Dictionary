import subprocess
import sys

import pandas as pd
import zipfile

import warnings
warnings.simplefilter('ignore')

# extract and open the source data
with zipfile.ZipFile('sources/Multi-Dictionaries-2016.zip') as zip:
    zip.extractall()
dicts = open('Multi-Dictionaries-2016.tab', 'r').readlines()

subprocess.run(["rm", "-f", "Multi-Dictionaries-2016.tab"])

# read the dictionary in to dataframe
l = []
for i in dicts:
    l.append(i.split('\t'))

df = pd.DataFrame(l)
df.columns = ['word', 'meaning', 'source']

# drop rows where both the word and meaning are duplicates
df = df.drop_duplicates(['word', 'meaning'])

# remove the newlines from the source field
df.source = df.source.str.replace('\n','')

# drop entries with cyrillic definition
df = df[df.meaning.str.contains(u'[\u0401-\u04f9]') == False]

# drop only Russian dictionaries
df = df[df.source.str.contains('BB|MWSK') == False]

# convert the source field in to categorical
df.source = df.source.astype('category')

# remove words where the word contains latin characters (note this might lose something)
df = df[df.word.str.contains('[a-z]') == False]
df['word'] = df['word'].str.rstrip()

df['source'] = df['source'].str.replace('-', '')
df['source'] = df['source'].str.replace('[', '')
df['source'] = df['source'].str.replace(']', '')

sources = ['MV',
           'TD',
           'EP|EP+',
           'IW|IW+',
           'HP|HP |HP+',
           'ML|ML+',
           'JW|JW+',
           'TS|TT|TS+|TT+|DK|MVP',
           'DR|DR+',
           'VD']

out = {}

names = []

for source in sources:
    
    if source == 'MV':
        name = 'Mahavyutpatti'
        names.append(name)
    if source == 'TD':
        name = 'Tony-Duff'
        names.append(name)
    if source == 'EP|EP+':
        name = 'Erik-Pema-Kunsang'
        names.append(name)
    if source == 'IW|IW+':
        name = 'Ives-Waldo'
        names.append(name)
    if source == 'HP|HP |HP+':
        name = 'Jeffrey-Hopkins'
        names.append(name)
    if source == 'ML|ML+':
        name = 'Lobsang-Monlam'
        names.append(name)
    if source == 'JW|JW+':
        name = 'Jim-Welby'
        names.append(name)
    if source == 'TS|TT|TS+|TT+|DK|MVP':
        name = 'Tibetan-Multi'
        names.append(name)
    if source == 'DR|DR+':
        name = 'Tibetan-Medicine'
        names.append(name)
    if source == 'VD':
        name = 'Verb-Lexicon'
        names.append(name)
        
    temp = df[df.source.str.contains(source) == True]
    temp = temp.drop_duplicates()
    temp.reset_index(inplace=True)
    temp = temp.drop(['index', 'source'], 1)
    temp.columns = ['Tibetan', 'Description']
    temp['Tibetan'] = temp['Tibetan'].str.replace(' ', '')
    temp = temp.dropna()
    temp.to_csv('data/' + name + '.csv', index=None, sep='\t')

# Handle custom dictionaries
import os

from os import listdir
from os.path import isfile, join
filenames = [f for f in listdir('sources/') if isfile(join('sources/', f))]

for filename in filenames:
    if filename != 'Multi-Dictionaries-2016.zip':
        os.system('cp sources/' + filename + ' data/' + filename)

        names.append(filename.split('.')[0])

dictionaries_df = pd.DataFrame()
dictionaries_df['Name'] = [name + '.csv' for name in names]
dictionaries_df['Title'] = [name.replace('-', ' ') for name in names]
dictionaries_df['Label'] = [name.lower().replace('-', '_') for name in names]

dictionaries_df.to_csv('data/dictionaries.csv', index=None)
