from gensim import corpora
import glob
import sys
import os
sys.path.append('../')
from util import util
import pickle
ROOT_DIR = '.'
DATA_PATH = '/text'
FILE_NAME= '/*.wakati'
DICTIONARY_NAME = '/dictionary.txt'
LABEL_NAME = '/labels'
WORD_LIST = '/word_list'

label = util.get_path_list(ROOT_DIR+ROOT_DIR+DATA_PATH)
labels = []
word_list = []
for l in label:
    for path in glob.glob(ROOT_DIR+ROOT_DIR+DATA_PATH+'/'+l+FILE_NAME, recursive=True):
        if os.path.isdir(path):
            continue
        text = open(path, "r", encoding='utf-8').read()
        text = text.split('/n')
        for txt in text:
            word_list.append(txt.split())
        labels.append(label.index(l))
        print(path)

with open(ROOT_DIR+LABEL_NAME, "wb") as f:
    pickle.dump(labels, f)

with open(ROOT_DIR+WORD_LIST, "wb") as f:
    pickle.dump(word_list, f)
dictionary = corpora.Dictionary(word_list)
dictionary.filter_extremes(no_below = 200, no_above = 0.2)
dictionary.save_as_text(ROOT_DIR+DICTIONARY_NAME)
courpus = [dictionary.doc2bow(word) for word in word_list]

