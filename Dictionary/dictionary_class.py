#!/usr/bin/env python
# coding: utf-8

from gensim import corpora
import glob
import sys
import os
import pickle

sys.path.append('../')
from util import util

# 定数宣言

ROOT_DIR = '.'
DATA_PATH = '/text'
FILE_NAME= '*.wakati'
DICTIONARY_NAME = 'dictionary.txt'
LABEL_NAME = '/labels'
WORD_LIST = '/word_list'
WORD_LIST_FILE = 'word_list.pkl'
WORD_LIST_FILENAME = '/word_list_file_name' 

class Dictionary():

    def __init__(self, inputPath, outputPath):
        
        self.INPUT_PATH = inputPath
        self.OUTPUT_PATH = outputPath
        
        self.LABEL = self.__get_label(self.INPUT_PATH)
        
        if not os.path.isdir(outputPath):
            os.mkdir(self.OUTPUT_PATH)
            print(self.OUTPUT_PATH, "made")

        self.PATH_SLASH = "/"
            

    def show_path(self):
        print(self.INPUT_PATH, self.OUTPUT_PATH)


    def __get_label(self, inputPath):

        return util.get_path_list(inputPath)


    def __deal():
        word_list = []
        for l in label:
            w_list = []
            for path in glob.glob(ROOT_DIR+ROOT_DIR+DATA_PATH+'/'+l+FILE_NAME, recursive=True):
                if os.path.isdir(path):
                    continue
                text = open(path, "r", encoding='utf-8').read()
                word_list.append(text.split())
                #f_list.append(path.split("/")[-1].split(".")[0])
                w_list.append({'text': text.split(), 'file': path.split("/")[-1].split(".")[0]})
            with open(ROOT_DIR+ROOT_DIR+DATA_PATH+"/"+l+"/"+WORD_LIST_FILE, "wb") as f:
                pickle.dump(w_list, f)
    
        with open(ROOT_DIR+WORD_LIST, "wb") as f:
            pickle.dump(word_list, f)


    def __make_medium_word_list(self, inputPath, outputPath):
    
        if not os.path.isdir(inputPath):
            print("Folder:",inputPath,"does not exist")
            return
        
        for path in glob.glob(os.path.join(inputPath, "*"), recursive=False):
            if not os.path.isdir(path):
                continue
            print(outputPath)
            self.__make_word_list_folder(path, outputPath)
            self.__write_word_list(os.path.join(outputPath,WORD_LIST_FILE), word_list)

    def __make_medium_dictionary(self, inputPath, outputPath):

        if not os.path.isdir(inputPath):
            print("Folder:",inputPath,"does not exist")
            return
        
        word_list = []
        for path in glob.glob(os.path.join(inputPath, "*"), recursive=False):
            if not os.path.isdir(path):
                continue
            print(outputPath)
            w_list, t_list = self.__make_word_list_folder(path, outputPath)
            
            if w_list is not None and w_list is not []:
                word_list.extend(t_list)
        self.__make_dictionary(outputPath, word_list)

    def __make_word_list_folder(self, inputPath, outputPath):
        
        if not os.path.isdir(inputPath):
            print("Folder:",inputPath,"does not exist")
            return
        outputPath = os.path.join(outputPath, inputPath.split(self.PATH_SLASH)[-1])
        if not os.path.isdir(outputPath):
            os.mkdir(outputPath)
        print(outputPath)
        
        word_list = self.__make_word_list(inputPath, outputPath)
        text_list = [word['text'] for word in word_list]
        return word_list, text_list


    def __make_word_list(self, inputPath, outputPath):
    
        word_list = []
        for file in glob.glob(os.path.join(inputPath, FILE_NAME), recursive=False):
            if os.path.isdir(file):
                continue
            text = open(file, "r", encoding='utf-8').read()
            word_list.append({'text': text.split(), 'file': file.split(self.PATH_SLASH)[-1].split(".")[0]})
        
        return word_list

    def __write_word_list(self, file, word_list):
        with open(file, "wb") as f:
            pickle.dump(word_list, f)

    # 辞書作成
    def __make_dictionary(self, outputPath, word_list):
        
        dictionary = corpora.Dictionary(word_list)

        dictionary.filter_extremes(no_below = 200, no_above = 0.2)

        dictionary.save_as_text(os.path.join(outputPath, DICTIONARY_NAME))

                             
    def make_word_list_folder(self, inputPath, outputPath):
        
        self.__make_word_list_folder(inputPath, outputPath)

    def make_medium_word_list(self):

        self.__make_medium_word_list(self.INPUT_PATH, self.OUTPUT_PATH)

    def make_medium_dictionary(self):

        self.__make_medium_dictionary(self.INPUT_PATH, self.OUTPUT_PATH)
