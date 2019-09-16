import glob

import numpy as np
import os,sys,platform
import json
import pickle
import traceback
from sklearn.feature_extraction.text import TfidfVectorizer

#ROOT_DIR = 'C:\\Users\\9047247\\Documents\\AI_contest_2019\\学習用データ'

FILE_NAME = '*.wakati'
TFIDF_RESULT = 'tfidf_result.pkl'
VECTOR_PATH = 'tfidf_vectorizer.pkl'
WORD_LIST = 'word_list.pkl'

class TF_IDF():
    
    def __init__(self, inputPath, outputPath, min_df=0.01, max_df=0.5, max_features=10000, vectorizer=None):
        self.INPUT_PATH = inputPath
        self.OUTPUT_PATH = outputPath + "-min_df" + str(min_df) + "-max_df" + str(max_df) + "-max_feature" + str(max_features)
        self.MIN_DF = min_df
        self.MAX_DF = max_df
        self.MAX_FEATURES = max_features
        self.VECTORIZER = vectorizer
        
        if not os.path.isdir(self.OUTPUT_PATH):
            os.mkdir(self.OUTPUT_PATH)
            print(self.OUTPUT_PATH, "made")
            
        if platform.system() == 'Windows':
            self.PATH_SLASH = "\\"
            
        else:
            self.PATH_SLASH = "/"
    
    def show_path(self):
        print(self.INPUT_PATH, self.OUTPUT_PATH)
    
    """
    中分類のtfidfを行う関数
    指定したフォルダ(inputPath)以下のフォルダ内のファイル分、tfidf値の大きさ順で単語が記載されたファイル(ファイル名.tf-idf)が作成される。
    文章内の単語をtfidf値に変換したリスト(ファイル名.tf-idf-b)が作成される。
    また、フォルダ毎にtfidfのベクトルとvectorizerを保存する。(tfidf_result.pklとtfidf_vectorizer.pkl)
    
    保存先はoutputPathであり、それ以下にinputPathの以下のフォルダ構成を同様に構築する。
    
    
    以下実行前のフォルダ構成(例)
    
    inputPath---A-----
                | |
                | ------01.wakati
                | ------02.wakati
                |
                B-----
                | |
                | -------01.wakati
                | -------02.wakati
    
      本関数、実行後
      
   outputPath---A-----
                | |
                | ------01.tf-idf
                | ------02.tf-idf
                | ------tfidf_result.pkl
                | ------tfidf_vectorizer.pkl
                |
                B-----
                | |
                | -------01.wakati
                | -------02.wakati    
                | ------tfidf_result.pkl
                | ------tfidf_vectorizer.pkl
    
    """
    def __make_tfidf_medium(self):
        
        for path in glob.glob(os.path.join(self.INPUT_PATH,self.SLASH_ASTA), recursive=False):
            if not os.path.isdir(path):
                continue
            print(path)
            self.__make_single_tfidf(path, self.OUTPUT_PATH)
    
    """
    
    大分類のtfidfを行う関数
    指定したフォルダ(inputPath)以下のフォルダ内のファイル分、tfidf値の大きさ順で単語が記載されたファイル(ファイル名.tf-idf)が作成される。
    文章内の単語をtfidf値に変換したリスト(ファイル名.tf-idf-b)が作成される。
    また、フォルダ毎にtfidfのベクトルとvectorizerを保存する。(tfidf_result.pklとtfidf_vectorizer.pkl)
    
    保存先はoutputPathであり、それ以下にinputPathの以下のフォルダ構成を同様に構築する。
    
    
    以下実行前のフォルダ構成(例)
    
    inputPath---A-----
                | |
                | ------A'
                |       |
                |       ------01.wakati
                |       ------02.wakati
                | |
                | ------A''
                |       |
                |       ------01.wakati
                |       ------02.wakati
                |
                B-----
                | |
                | -------B'
                |        |
                |        -----01.wakati
                |        -----02.wakati
                | |
                | -------B''
                |        |
                |        -----01.wakati
                |        -----02.wakati      
    
      本関数、実行後
      
   outputPath---A-----
                | |
                | ------01.tf-idf
                | ------02.tf-idf
                | ------tfidf_result.pkl
                | ------tfidf_vectorizer.pkl
                |
                B-----
                | |
                | -------01.wakati
                | -------02.wakati    
                | ------tfidf_result.pkl
                | ------tfidf_vectorizer.pkl
    
    """
    def __make_tfidf_major(self):
        
        for midium_path in glob.glob(os.path.join(self.INPUT_PATH,"*"), recursive=False):
            if not os.path.isdir(midium_path):
                continue
            self.__make_folder_tfidf(midium_path, self.OUTPUT_PATH)
            
            
    def __make_folder_tfidf(self, inputPath, outputPath):
        
        if not os.path.isdir(outputPath):
            os.mkdir(outputPath)
            
        outputPath = os.path.join(outputPath,os.path.basename(inputPath))
        if not os.path.isdir(outputPath):
            os.mkdir(outputPath)
        
        docs = []
        
        if os.path.isfile(os.path.join(inputPath,WORD_LIST)):
            with open(os.path.join(inputPath,WORD_LIST), "rb") as f:
                docs = pickle.load(f)
        else:        
            for path in glob.glob(os.path.join(inputPath, "*"), recursive=False):

                if not os.path.isdir(path):
                    continue
                docs.extend(self.__collect_documents(path))
                
        if docs == [] or docs == None:
            print("Word_list Empty")
            return
        
        self.__make_tfidf(docs, outputPath)
        
        
    def __make_single_tfidf(self, inputPath, outputPath):
        
        outputPath = os.path.join(outputPath, os.path.basename(inputPath))
        if not os.path.isdir(outputPath):
            os.mkdir(outputPath)
        
        docs = self.__collect_documents(inputPath)
            
        if docs == [] or docs == None:
                return
        self.__make_tfidf(docs, outputPath)
        
        
    def __make_tfidf(self, docs, outputPath):
        
        try:
            vectorizer = TfidfVectorizer(min_df=self.MIN_DF,max_df=self.MAX_DF,max_features=self.MAX_FEATURES)
            vector = vectorizer.fit_transform([d.get('text') for d in docs])
            feature_names = np.array(vectorizer.get_feature_names())
        except:
            print("Vectorizer Error:", traceback.print_exc())
            return
        
        self.__write_vectorizer_transforms(vectorizer, vector, outputPath)
        
        self.__make_feature_words(docs, vector, feature_names, outputPath)
        
        self.__make_tfidf_list(docs, vector, feature_names, outputPath)
        

    def __collect_documents(self, path):
        docs = []
        
        
        for doc in docs:

            #テキストがlistの場合、スペース区切りのstr変換
            if type(doc['text']) == type([]):
                doc['text'] = " ".join(doc['text'])

            #テキストがstrの場合、改行コード等を取り除いたスペース区切りのstr変換
            elif type(docs) == str:
                doc['text'] = doc['text'].split()
                doc['text'] = " ".join(doc['text'])

        return docs

        for file in glob.glob(os.path.join(path,FILE_NAME), recursive=True):
            
            text = open(file, "r", encoding='utf-8').read()
            doc = {'file': file, 'text': text}
            
             #テキストがlistの場合、スペース区切りのstr変換
            if type(doc['text']) == type([]):
                doc['text'] = " ".join(doc['text'])
                    
            #テキストがstrの場合、改行コード等を取り除いたスペース区切りのstr変換
            elif type(docs) == str:
                doc['text'] = doc['text'].split()
                doc['text'] = " ".join(doc['text'])
            docs.append(doc)
        return docs
    
    
    def __write_vectorizer_transforms(self, vec, trans, outputPath):
    
        with open(os.path.join(outputPath,TFIDF_RESULT), 'wb') as f:
            pickle.dump(trans, f)
        with open(os.path.join(outputPath,VECTOR_PATH), 'wb') as f:
            pickle.dump(vec, f)

            
    def __write_feature_words(self, file, feature_words, vector, index):
        with open(file, "w", encoding='utf-8') as f:
            for i, idx in enumerate(index):
                f.write(feature_words[i] + ": " + str(vector[idx])+", ")

                
    def __make_feature_words(self, docs, vector, feature_names, outputPath):
            
        # vec = 1文章のベクトル
        for i, vec in enumerate(vector):
            
            # ベクトル内のtfidf値を昇順にならべたインデックスを降順に並べる
            # つまりはtfidf値が高い単語順にその単語の辞書上でのインデックスを取得する
            # argsort = 配列要素を昇順に並べ、それらの元のインデックを返す
            # [:,::-1] = 配列要素を降順にする
            index = np.argsort(vec.toarray(), axis=1)[:,::-1]
            
            # 1文章内での特徴語を取得する
            feature_words = feature_names[index]
            
            outputFile = ""
            #outputFile = docs[i]['file'].replace(".wakati", ".tf-idf")
            outputFile = docs[i]['file'] + ".tf-idf"
            outputFile = os.path.join(outputPath, outputFile.split(self.PATH_SLASH)[-1])
            print(outputFile)
            
            # 1文章のtfidf値を取得
            v = vec.toarray()[0]
            
            # １文章とそのtfidf結果を紐づけてファイルに書き込む
            # index = [[]]となっていて１文章内の単語のインデックス達なので基本要素は１つである
            # 故にindex[0]としている（feature_wordsも同様）
            self.__write_feature_words(outputFile, feature_words[0], v, index[0])
            
    
    def __make_tfidf_list(self, docs, vector, feature_names, outputPath):
        
        for i, vec in enumerate(vector.toarray()):
            outputFile = ""
            #outputFile = docs[i]['file'].replace(".wakati", ".tf-idf-b")
            outputFile = docs[i]['file'] + ".tf-idf-b"
            outputFile = os.path.join(outputPath, outputFile.split(self.PATH_SLASH)[-1])
            print(outputFile)
            with open (outputFile, "wb") as f:
                pickle.dump(vec, f)
        
    
    def tfidf_medium(self):
        self.__make_tfidf_medium()

    def tfidf_major(self):
        self.__make_tfidf_major()

    def make_single_tfidf(self, inputPath, outputPath):
        self.__make_single_tfidf(inputPath, outputPath)
   
    def make_folder_tfidf(self, inputPath, outputPath):
        self.__make_folder_tfidf(inputPath, outputPath)
        