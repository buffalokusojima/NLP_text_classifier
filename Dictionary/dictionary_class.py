#!/usr/bin/env python
# coding: utf-8

from gensim import corpora
import glob
import sys
import os
import pickle
import platform

sys.path.append('../')
from util import util

# 定数宣言
DICTIONARY_NAME = 'dictionary.txt'
WORD_LIST = 'word_list.pkl'


class Dictionary():

    # 必要なパラメータを設定
    def __init__(self, inputPath, outputPath, no_below=200, no_above=0.5, keep_n=10000):
        
        self.INPUT_PATH = inputPath
        self.OUTPUT_PATH = outputPath + "-no_below" + str(no_below) + "-no_above" + str(no_above) + "-keep_n" + str(keep_n)
        self.NO_BELOW = no_below #最低頻出回数
        self.NO_ABOVE = no_above #最高頻出割合
        self.KEEP_N = keep_n     #辞書の最大長
        
        if not os.path.isdir(self.OUTPUT_PATH):
            os.mkdir(self.OUTPUT_PATH)
            print(self.OUTPUT_PATH, "made")

        if platform.system() == 'Windows':
            self.PATH_SLASH = "\\"
        else:
            self.PATH_SLASH = "/"
            
    #パスの確認
    def show_path(self):
        print(self.INPUT_PATH, self.OUTPUT_PATH)

            
    #中分類の辞書作成
    def __make_medium_dictionary(self, inputPath=None, outputPath=None):

        if inputPath is None:
            inputPath = self.INPUT_PATH
        
        if outputPath is None:
            outputPath = self.OUTPUT_PATH
            
        
        #パラメータであるインプットフォルダの存在を確認
        if not os.path.isdir(inputPath):
            print("Folder:",inputPath,"does not exist")
            return
        
        #パラメータであるアウトプットフォルダーの作成
        if not os.path.isdir(outputPath):
            os.mkdir(outputPath)

        
        #パラメータであるインプットフォルダの直下を捜査
        word_list = []
        for path in glob.glob(os.path.join(inputPath, "*"), recursive=False):
            
            #ファイルは飛ばす
            if not os.path.isdir(path):
                continue
           
            #指定したフォルダ内のファイルにある内容をすべて並べたリストを取得
            w_list = self.__get_word_list_folder(path)
            
            #Noneまたは空でなければword_listに結合する
            if w_list:
                word_list.extend(w_list)
        
        #Noneまたは空でなければ辞書作成を行う
        if word_list:
            
            
            #大分類用にword_listを保存しておく
            util.write_word_list(outputPath, word_list)
            
            word_list = [word['text'] for word in word_list]
            
            #中分類のファイル全ての内容をリストにしたものから辞書を作成する
            dictionary = self.__make_dictionary(outputPath, word_list, self.NO_BELOW, self.NO_ABOVE, self.KEEP_N)
        
            return word_list, dictionary
            
        return word_list
        
        
    #大分類の辞書作成
    def __make_major_dictionary(self):
        
        #パラメータであるインプットフォルダの存在を確認
        if not os.path.isdir(self.INPUT_PATH):
            print("Folder:",self.INPUT_PATH,"does not exist")
            return
        
        
        word_list = []
        for path in glob.glob(os.path.join(self.INPUT_PATH, "*"), recursive=True):
            w_list = os.path.join(path, WORD_LIST)
            if os.path.isfile(w_list):
                word_list.extend(w_list)
                continue
                
            outputPath = os.path.join(self.OUTPUT_PATH, os.path.basename(path))
            print(outputPath)
            
            #アウトプットフォルダーの作成
            if not os.path.isdir(outputPath):
                os.mkdir(outputPath)
                
            w_list = self.__make_medium_dictionary(inputPath=path, outputPath=outputPath)
            
            util.write_word_list(outputPath, word_list)
            if w_list:
                word_list.extend(w_list)
            
        if not word_list:
            print("Cannot make Dictionary")
            return
        
        dictionary = self.__make_dictionary(self.OUTPUT_PATH, word_list)
        
        return dictionary

    
    #指定したフォルダ内のファイルの内容をリストにしたものを返す
    def __get_word_list_folder(self, inputPath):
    
        #指定したフォルダが存在しなければ終了
        if not os.path.isdir(inputPath):
            print("Folder:",inputPath,"does not exist")
            return
        
        #引数のパス直下にあるword_listを取得する
        try:
            word_list = util.get_word_list(inputPath)
        except:
            print("Word list Not Found:", inputPath)
            return
        
        #word_listを辞書作成用にテキスト部のみを抽出する
        if not word_list:
            return
        
        
        #word_listの内容がstrの場合、リストに変換して配列に格納
        util.check_word_list_type(word_list)
        
        return word_list
    
            
    # 辞書作成
    def __make_dictionary(self, outputPath, word_list, no_below=None, no_above=None, keep_n=None):
        
        if no_below is None:
            no_below = self.NO_BELOW
        
        if no_above is None:
            no_above = self.NO_ABOVE
            
        if keep_n is None:
            keep_n = self.KEEP_N
            
        
        #辞書作成
        dictionary = corpora.Dictionary(word_list)

        #辞書精査
        dictionary.filter_extremes(no_below = no_below, no_above = no_above, keep_n=keep_n)

        #辞書保存
        dictionary.save_as_text(os.path.join(outputPath, DICTIONARY_NAME))

        print("Dictionary made:", outputPath)
        
        return dictionary
        
    def make_medium_dictionary(self):

        word_list, dictionary = self.__make_medium_dictionary()
        
        return word_list, dictionary
        
    def make_major_dictionary(self):
        
        dictionary = self.__make_major_dictionary()