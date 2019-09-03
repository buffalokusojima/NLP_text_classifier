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
    
    def __init__(self, root, inputPath, outputPath):
        self.ROOT_DIR = root
        self.INPUT_PATH = inputPath
        self.OUTPUT_PATH = outputPath
    
        if not os.path.isdir(outputPath):
            os.mkdir(self.OUTPUT_PATH)
            print(self.OUTPUT_PATH, "made")
    
    def show_path(self):
        print(self.ROOT_DIR, self.INPUT_PATH, self.OUTPUT_PATH)
    
    def __make_tfidf_medium(self):
        
        for path in glob.glob(self.INPUT_PATH+"/*", recursive=False):
            if not os.path.isdir(path):
                continue
        
            outputPath = self.OUTPUT_PATH+"/"+path.split("/")[-1]
        
            if not os.path.isdir(outputPath):
                os.mkdir(outputPath)
            print(path)
            docs = self.__collect_documents(path)
            self.__make_tfidf(docs, outputPath)

    def __make_tfidf_major(self):
        
        for midium_path in glob.glob(self.INPUT_PATH+"/*", recursive=False):
            if not os.path.isdir(midium_path):
                continue
            
            outputPath = self.OUTPUT_PATH+"/"+midium_path.split("/")[-1]
            if not os.path.isdir(outputPath):
                os.mkdir(outputPath)
            print(midium_path)
            self.__make_folder_tfidf(path)


    def __make_single_tfidf(self):
        self.__make_tfidf(self.INPUT_PATH)

    def __make_folder_tfidf(self):
        
        docs = []
        for path in glob.glob(self.INPUT_PATH+"/*", recursive=False):
            if not os.path.isdir(path):
                continue
            docs.extend(self.__collect_documents(path))

        outputPath = self.OUTPUT_PATH+"/"
        print(outputPath)
        if not os.path.isdir(outputPath):
            os.mkdir(outputPath)
        outputFile = outputPath + self.INPUT_PATH.split("/")[-1]
        self.__make_tfidf_folder(docs, outputPath, outputFile)
        


    def __collect_documents(self, path):
        docs = []
        
        for file in glob.glob(path+FILE_NAME, recursive=True):
            
            text = open(file, "r", encoding='utf-8').read()
            doc = {'file': file, 'doc': text}
            docs.append(doc)
        return docs

    def __write_vectorizer_transforms(self, vec, trans, outputPath):
    
        with open(outputPath+TFIDF_RESULT, 'wb') as f:
            pickle.dump(trans, f)
        with open(outputPath+VECTOR_PATH, 'wb') as f:
            pickle.dump(vec, f)

    def __write_tfidf_file(self, file, feature_words, vector, index):
        with open(file, "w", encoding='utf-8') as f:
            for i, idx in enumerate(index[0]):
                f.write(feature_words[0][i] + ": " + str(vector[idx])+", ")

    def __make_tfidf(self, docs, outputPath):
        
        vectorizer = TfidfVectorizer()
        vector = vectorizer.fit_transform([d.get('doc') for d in docs])
        feature_names = np.array(vectorizer.get_feature_names())
            
        self.__write_vectorizer_transforms(vectorizer, vector, outputPath)
            
        num = 0
        for vec in vector:
            index = np.argsort(vec.toarray(), axis=1)[:,::-1]
            feature_words = feature_names[index]
            outputFile = ""
            outputFile = docs[num]['file'].replace(".wakati", ".tf-idf")
            outputFile = outputPath + "/" + outputFile.split("/")[-1]
            v = vec.toarray()[0]
            self.__write_tfidf_file(outputFile, feature_words, v, index)
            num = num + 1

    def __make_tfidf_folder(self, docs, outputPath, outputFile):
    
        vectorizer = TfidfVectorizer()
        vector = vectorizer.fit_transform([d.get('doc') for d in docs])
        feature_names = np.array(vectorizer.get_feature_names())
        
        self.__write_vectorizer_transforms(vectorizer, vector, outputPath)
        outputFile = outputFile + ".tf-idf"
        print(outputFile)
        num = 0
        with open(outputFile, "w") as f:
            for vec in vector:
                index = np.argsort(vec.toarray(), axis=1)[:,::-1]
                feature_words = feature_names[index]
                v = vec.toarray()[0]
                for i, idx in enumerate(index[0]):
                    f.write(feature_words[0][i] + ": " + str(v[idx])+", ")
                num = num + 1

    def tfidf_medium(self):
        self.__make_tfidf_medium()

    def tfidf_major(self):
        self.__make_tfidf_major()

    def make_single_tfidf(self):
        self.__make_single_tfidf()

    def make_folder_tfidf(self):
        self.__make_folder_tfidf()
