import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#import seaborn as sns

import sys, os, glob
import xml.etree.ElementTree as ET

import MeCab

mecab = MeCab.Tagger('mecabrc')

import string

import re


def text_cleaning(txt) :
    ##txt = txt.replace("\n",' ')
    ##txt = txt.replace("\t",' ')
    ##txt = txt.replace("\r",' ')
    for i in string.printable:       # 英数字・半角記号を取り除く
        txt = txt.replace(i,' ',)
    
    return txt

#分かち書き
def separate_words(text):
    vocab_list_mecab = []
    sents = mecab.parse(text)
    sents = sents.split("\n") # 改行記号で解析結果を分割    
    sents.remove('')
    sents.remove('EOS')
    tmp = ''
    
    #解析結果ごとに品詞を見て抽出するものを判断
    for i in sents:
        node1 = i.split("\t")
        node2 = node1[1].split(",")
        if (node2[0] == '名詞') & (node2[1] != '固有名詞') :
            tmp = tmp+' '+node1[0]
        elif node2[0] == '動詞' :
            tmp = tmp+' '+node2[6]
    return tmp

# XMLファイルから文章を取り出す
def get_XMLtext(text):
    data = []
    try:
        tree = ET.parse(text)
    except:
        return False

    page = tree.getroot()
    num = len(page.getchildren())    # ルートに紐付く子供のタグ数を取り出す
    for k in np.arange(num) :        # 順番に処理して目当ての部分であれば、dataとして取り出す。
        tmp = page.getchildren()[k].findtext('text')
        if tmp !=None :
            #tmp = text_cleaning(tmp)
            data.append(tmp)
    return "\n".join(data)

# 不要な文章の削除
def removeWords(text):
    text = text.replace('\u3000', '')
    text = text.split("\n")
    removeHead(text)
    
    text = re.sub()
    #無駄な改行削除
    text = [x for x in text if x]
    
    """
    ここに不要だと思う文章パターンを削除する関数を追記していく
    """
    
    return "\n".join(text)

# ヘッダ削除
def removeHead(text):
    del text[:2]

#ファイル結合
def file_join():
    for path in glob.glob(ROOT_DIR+DATA_PATH):
        docs = []
        if not os.path.isdir(path):
            continue
        print(path)
        path_wakati = path+"/total.wakati"
        for file in glob.glob(path+OUTPUT_FILE_NAME):
            docs.append(open(file,"r", encoding='utf-8').read())
        wt="\n".join(docs)
        open(path_wakati, "w", encoding="utf-8").write(wt)

def make_files():
    for path in glob.glob(ROOT_DIR + ROOT_DIR + DATA_PATH + FILE_NAME, recursive=True):
        if os.path.isdir(path):
            continue
        #分ち書き変換するファイルの拡張子を設定
        path_wakati=path.replace("."+FILE_NAME.split(".")[-1], ".wakati")
        print(path_wakati)
        #if os.path.exists(path_wakati): continue #ファイルができているときはスルー
        
        #文章がXML形式であればXMLからTEXTを抽出する
        if FILE_NAME.split(".")[-1] == "xml":
            text = get_XMLtext(path)
            if text == False:
                text=open(path,"r", encoding='utf-8').read() #エンコーディングに注意
        else:
            text=open(path,"r", encoding='utf-8').read() #エンコーディングに注意
    
        #URL的な要素削除
        text=re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", text)

        #不要な文章の削除
        words=removeWords(text)
    
        #文章を句点毎に分ける
        words = words.replace("。", "\n")
    
        #文章毎に分かち書きする
        text = []
        for word in words.split("\n"):
            tmp = separate_words(word)
            #tmpが空欄の場合もあるのでそれは排除
            if tmp != '':
                text.append(tmp)
        #スペースつながりで分かち書きした言葉を繋げていく
        wt="\n".join(text)
        open(path_wakati, "w", encoding="utf-8").write(wt)

#ROOT_DIR = 'C:\\Users\\9047247\\Documents\\AI_contest_2019\\学習用データ'
ROOT_DIR = '.'
DATA_PATH = '/text/*'
FILE_NAME = '/*.txt'
OUTPUT_FILE_NAME = '/*.wakati'

argv = sys.argv
args = len(argv)
if args != 2:
    print("not correct number of the argument")
    exit(1)

if argv[1] == '-m':
    make_files()
    exit(0)
elif argv[1] == '-a':
    file_join()
    exit(0)
else:
    print("not correct argument")
    exit(1)
