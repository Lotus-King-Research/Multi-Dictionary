import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install('pandas')

import pandas as pd
import zipfile

# extract and open the source data
with zipfile.ZipFile('Multi-Dictionaries-2016.zip') as zip:
    zip.extractall()
dicts = open('Multi-Dictionaries-2016.tab', 'r').readlines()

# delete the files now that they are no longer needed
subprocess.run(["rm", "-f", "Multi-Dictionaries-2016.zip"])
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

for source in sources:
    
    if source == 'MV':
        name = 'Mahavyutpatti'
    if source == 'TD':
        name = 'TonyDuff'
    if source == 'EP|EP+':
        name = 'ErikPemaKunsang'
    if source == 'IW|IW+':
        name = 'IvesWaldo'
    if source == 'HP|HP |HP+':
        name = 'JeffreyHopkins'
    if source == 'ML|ML+':
        name = 'LobsangMonlam'
    if source == 'JW|JW+':
        name = 'JimWelby'
    if source == 'TS|TT|TS+|TT+|DK|MVP':
        name = 'TibetanMulti'
    if source == 'DR|DR+':
        name = 'TibetanMedicine'
    if source == 'VD':
        name = 'VerbLexicon'
        
    temp = df[df.source.str.contains(source) == True]
    temp = temp.drop_duplicates()
    temp.reset_index(inplace=True)
    temp = temp.drop(['index', 'source'], 1)
    temp.columns = ['Tibetan', 'Description']
    temp['Tibetan'] = temp['Tibetan'].str.replace(' ', '')
    
    if name == 'TibetanMulti':
        temp.iloc[:40000].to_csv('data/' + name + '-Part1-Dictionary.csv')
        temp.iloc[40000:80000].to_csv('data/' + name + '-Part2-Dictionary.csv')
        temp.iloc[80000:].to_csv('data/' + name + '-Part3-Dictionary.csv')
        
    else:
        temp.to_csv('data/' + name + '-Dictionary.csv')
