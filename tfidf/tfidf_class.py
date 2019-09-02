import glob

import numpy as np
import os,sys
import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

#ROOT_DIR = 'C:\\Users\\9047247\\Documents\\AI_contest_2019\\学習用データ'
ROOT_DIR = '.'
DATA_PATH = '/text/*'
FILE_NAME = '/*.wakati'
TFIDF_RESULT = '/tfidf_result.pkl'
VECTOR_PATH = '/tfidf_vectorizer.pkl'

class TF_IDF():
    
    def __init__(self, inputPath, outputPath):
        self.INPUT_PATH = inputPath
        self.OUTPUT_PATH = outputPath
    
    def show_path(self):
        print(self.INPUT_PATH, self.OUTPUT_PATH)
    
    def __make_tfidf_medium(self):
        for path in glob.glob(self.inputPath, recursive=True):
            vectorizer = TfidfVectorizer()
            docs = []
            if not os.path.isdir(path):
                continue
            print(path)
            for file in glob.glob(path+FILE_NAME, recursive=True):
                text = open(file, "r", encoding='utf-8').read()
                doc = {'file': file, 'doc': text}
                docs.append(doc)

            vector = vectorizer.fit_transform([d.get('doc') for d in docs])
            feature_names = np.array(vectorizer.get_feature_names())

            with open(path+TFIDF_RESULT, 'wb') as f:
                pickle.dump(vector, f)
            with open(path+VECTOR_PATH, 'wb') as f:
                pickle.dump(vectorizer, f)

            num = 0
            for vec in vector:
                index = np.argsort(vec.toarray(), axis=1)[:,::-1]
                feature_words = feature_names[index]
                outputPath = docs[num]['file'].replace(".wakati", ".tf-idf")
                
                v = vec.toarray()[0]
                with open(outputPath, "w", encoding='utf-8') as f:
                    for i, idx in enumerate(index[0]):
                        f.write(feature_words[0][i] + ": " + str(v[idx])+", ")
                print(outputPath)
                num = num + 1

    def __make_tfidf_major(self, root):
        
        dataPath = '/text'
        for path in glob.glob(root+dataPath, recursive=True):
            vectorizer = TfidfVectorizer()
            docs = []
            if not os.path.isdir(path):
                continue
            
            for file in glob.glob(path+'/*'+FILE_NAME, recursive=True):
                if os.path.isdir(file):
                    continue
                text = open(file, "r", encoding='utf-8').read()
                docs.append(text)
                print(file)
            vector = vectorizer.fit_transform(docs)
            feature_names = np.array(vectorizer.get_feature_names())
            
            with open(root+dataPath+TFIDF_RESULT, 'wb') as f:
                pickle.dump(vector, f)
            with open(root+dataPath+VECTOR_PATH, 'wb') as f:
                pickle.dump(vectorizer, f)

            for vec in vector:
                index = np.argsort(vec.toarray(), axis=1)[:,::-1]
                feature_words = feature_names[index]

            outputPath = root+dataPath+'/total.tfidf'
            num = 0
            v = vec.toarray()[0]
            with open(outputPath, "w", encoding='utf-8') as f:
                for i, idx in enumerate(index[0]):
                    f.write(feature_words[0][i] + ": " + str(v[idx])+", ")
            print(outputPath)
            num = num + 1

    def tfidf_medium(self):
        self.tfidf_medium()

    def tfidf_major(self):
        self.__make_tfidf_major()


