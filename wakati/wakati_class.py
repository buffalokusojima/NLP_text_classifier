import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import sys, os, glob, platform
import xml.etree.ElementTree as ET

import MeCab

import string

import re

import pickle

import pprint

###########################koyamaフォルダの分かちクラス############################
class Wakati():
    
    def __init__(self, inputPath, outputPath, datafileExtension, dataExtensionListPath, useSectionListPath, binaryWakatiOutputPath):
        self.mecab = MeCab.Tagger('mecabrc')
        self.DATA_FILE_EXTENSION = datafileExtension
        self.DATA_EXTENSION_LIST_PATH=dataExtensionListPath
        self.outputWakatiFileExtension = 'wakati'
        self.outputHinshiFileExtension = 'hinshi'
        self.DATA_PATH = inputPath
        self.OUTPUT_PATH = outputPath
        self.USE_SECTION_LIST_PATH = useSectionListPath
        self.BINARY_WAKATI_OUTPUT_PATH=binaryWakatiOutputPath
        
        if platform.system() == 'Windows':
            self.PATH_SLASH = "\\"
        
        if not os.path.isdir(outputPath):
            os.mkdir(self.OUTPUT_PATH)
            print(self.OUTPUT_PATH, "made")

    def show_path(self):
        print("show_path(DATA_PATH,OUTPUT_PATH,DATA_FILE_EXTENSION):",self.DATA_PATH, self.OUTPUT_PATH, self.DATA_FILE_EXTENSION)

    def __text_cleaning(self,txt) :
        ##txt = txt.replace("\n",' ')
        ##txt = txt.replace("\t",' ')
        ##txt = txt.replace("\r",' ')
        for i in string.printable:       # 英数字・半角記号を取り除く
            txt = txt.replace(i,' ',)
        
        return txt

    #分かち書き
    def __separate_words(self,text):
        vocab_list_mecab = []
        sents = self.mecab.parse(text)
        sents = sents.split("\n") # 改行記号で解析結果を分割
        sents.remove('')
        sents.remove('EOS')
        tmp = ''
        
        #print('sentsを出力します！')
        #print(sents)
        text_hinshi=""
        #解析結果ごとに品詞を見て抽出するものを判断
        for i in sents:
            text_hinshi=text_hinshi+i+"\n"
            
            node1 = i.split("\t")
            node2 = node1[1].split(",")
            
            #固有名詞なら採用
            if (node2[0] == '名詞'):
                                    
                #名詞なら採用（数を除く）
                if node2[1] == '数':
                    continue
            
                #名詞なら採用（接尾語を除く）
                elif node2[1] == '接尾':
                    continue
                    
                #名詞なら採用（接続詞的を除く）
                elif node2[1] == '接続詞的':
                    continue
                    
                #名詞なら採用（引用文字列を除く）
                elif node2[1] == '引用文字列':
                    continue

                #名詞なら採用
                tmp = tmp+' '+node1[0]
                
            #動詞なら採用
            elif node2[0] == '動詞' :
                tmp = tmp+' '+node2[6]

                
        #品詞分解結果出力
        #path_wakati=outputFile.replace("."+FILE_NAME.split(".")[-1], ".hinshi")
        #with open(path_wakati, "a", encoding="utf-8") as f:
        #    f.write(text_hinshi)
        return tmp, text_hinshi

    # XMLファイルから文章を取り出す
    def __get_XMLtext(self,text):
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
    def __remove_words(self,text):
        text = text.replace('\u3000', '')
        
        #改行をカンマ区切りでリスト化
        text = text.split("\n")
        #removeHead(text)
        
        text = [self.__remove_empty_element_tag(x) for x in text if x]
        #print("\n"+"【ref切った結果】")
        #print(text)
        #pprint.pprint(text)

        text = [self.__remove_element_tag(x) for x in text if x]
        #print("\n"+"【ref2切った結果】")
        #pprint.pprint(text)
        #print(text)
        #text = re.sub()
        
        """
            ここに不要だと思う文章パターンを削除する関数を追記していく
        """
        text = [self.__remove_unnecessary_word(x) for x in text if x]
        
        return "\n".join(text)

    
    ###refタグを消す-空要素(Empty-element Tag)
    def __remove_empty_element_tag(self,text):
        tag_list=["ref","br","references"]
        for tag in tag_list:
            text=re.sub(r'<%s\b.*?/>'%tag, "", text)
        return text

    ###refタグを消す-開始タグと終了タグとその間(Tag Element)
    def __remove_element_tag(self,text):
        #return re.sub(r'<%s\b.*?</%s>'%"ref", "", text)
        return re.sub(r'<%s\b.*?</\b%s>'%("ref","ref"), "", text)

    ###不要な単語リストの単語を削除する
    def __remove_unnecessary_word(self,text):
        unnecessary_words=["脚注","ヘルプ","出典","Category"]
        for unnecessary_word in unnecessary_words:
            text = text.replace(unnecessary_word,'')
        return text

        #return [text.replace(unnecessary_word,'') for unnecessary_word in unnecessary_words if unnecessary_word]

    
    def __make_files_under_folders(self, inputPath, outputPath):
       
       
        for path in glob.glob(inputPath+ self.PATH_SLASH + "*", recursive=True):
            tmpPath = outputPath 
            if not os.path.isdir(path):
                continue
            
            print("tmpPath:",tmpPath)
            tmpPath = tmpPath + self.PATH_SLASH + path.split(self.PATH_SLASH)[-1]
            if not os.path.isdir(tmpPath):
                os.mkdir(tmpPath)
                print(tmpPath," made")
            
            self.__folder_wakati(path, tmpPath)
            self.__make_files_under_folders(path, tmpPath)
            
        return
    
    
    # フォルダ内のファイル全てを分かち書きするprivate関数
    def __folder_wakati(self, targetFolder, outputPath):
       
        print("targetFolder:",targetFolder)
        if not os.path.isdir(targetFolder):
            print("Folder:", targetFolder, "does not exist")
            return
        
        if not os.path.isdir(outputPath):
            os.mkdir(outputPath)
        
        for dataPath in glob.glob(targetFolder+ self.PATH_SLASH + "*"+"."+self.DATA_FILE_EXTENSION, recursive=True):
            #print(path)
            if not os.path.isfile(dataPath):
                continue
            self.__single_wakati(dataPath, outputPath)
           
            
           
    """
        最終的に完成した分かち書きプログラムをここにぶち込む！
        
        IN:　ファイルパス
        OUT:　分かち書きされた文字列,品詞分解ファイル
    """
    def __deal(self, file):
        
        #文章がXML形式であればXMLからTEXTを抽出する
        if file.split(".")[-1] == "xml":
            text = self.__get_XMLtext(file)
            if text == False:
                text=open(file,"r", encoding='utf-8').read() #エンコーディングに注意
        else:
            text=open(file,"r", encoding='utf-8').read() #エンコーディングに注意
        
        #URL的な要素削除
        text=re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", text)
        #wakatiに影響のある文字の削除
        text = re.sub(r'{|}\[\]+','',text)

        #不要な文章の削除
        words=self.__remove_words(text)

        #文章を句点毎に分ける
        words = words.replace("。", "\n")

        #文章毎に分かち書きする
        text = []
        hinshi=[]
        for word in words.split("\n"):
            tmp = self.__separate_words(word)
            #tmpの中身が空でなければ追加
            if tmp[0] != '':
                text.append(tmp[0])
            if tmp[1] != '':
                hinshi.append(tmp[1])
                
        #分かち書きした言葉のリストをスペースつながりで繋げていく
        wt="\n".join(text)
        #print(tmp[1])
        wt2="\n".join(hinshi)
        #print(wt2)
        return wt,wt2
    
    # 分かち書きファイルの書き込み関数
    def __write_text(self, text, outputFile):
    
         with open(outputFile, "w", encoding="utf-8") as f:
                f.write(text)
                
    # 単体のファイルを分かち書きするprivate関数            
    def __single_wakati(self, dataFile, outputPath):
        
        if not os.path.isfile(dataFile):
            print("File:", file, "does not exist")
            return
        if not os.path.isdir(outputPath):
            print("Path:", outputPath, "does not exist")
            return
        
        #print("outputPath:",outputPath)
        #print("dataFile:",dataFile)
        
        print("dataFile:",dataFile)
        
        print()
        outputWakatiFile = outputPath + self.PATH_SLASH + dataFile.split(self.PATH_SLASH)[-1].replace(self.DATA_FILE_EXTENSION, self.outputWakatiFileExtension)
        outputHinshiFile = outputPath + self.PATH_SLASH + dataFile.split(self.PATH_SLASH)[-1].replace(self.DATA_FILE_EXTENSION, self.outputHinshiFileExtension)
        
        #結果取得
        result=self.__deal(dataFile)
        wakati_text = result[0]
        hinshi_text = result[1]
       
        print("outputWakatiFile:",outputWakatiFile)
        print("outputHinshiFile:",outputHinshiFile)
        
        #分かち書きファイル書き込み
        self.__write_text(wakati_text, outputWakatiFile)
        #品詞分解ファイル書き込み
        self.__write_text(hinshi_text, outputHinshiFile)
        
    
    
    #階層を保持して指定した拡張子で分かち書きをする関数
    def __select_extension_wakati(self, extensionListPath):
        
        
        #拡張子リストごとにフォルダを分ける
        folderName=os.path.basename(self.DATA_EXTENSION_LIST_PATH).split(".")[0]
        folderPath=self.OUTPUT_PATH+self.PATH_SLASH+folderName
        
        if not os.path.isdir(folderPath):
            os.mkdir(folderPath)
        
        #拡張子のリストを取得
        extension_text=open(extensionListPath,"r", encoding='utf-8').read()
        print(extension_text)
        extension_list=[extension.strip() for extension in extension_text.split(',')]
        print(extension_list)
        
        #リストの要素ごとにフォルダを分ける
        for extension in extension_list:
            self.DATA_FILE_EXTENSION=extension
            outputPath=folderPath+self.PATH_SLASH+extension
            #print("sectionFolderPath:",outputPath)
            #アウトプットフォルダが存在しなければ作成
            if not os.path.isdir(outputPath):
                os.mkdir(outputPath)
                
            #階層を維持して分かち書き
            self.__make_files_under_folders(self.DATA_PATH, outputPath)
            
        #0byteのフォルダ、ファイルを削除
        #for self.__delete_zorobyte_files(folderPath)
        

        

        
    
    
    
    ############やり直し##########
    def __integrate_wakati_sections(self, sectionListPath, outputPath):
        
        
        #生データパス
        namaDataPath=self.DATA_PATH
        #wakatiデータパス
        wakatiPath = self.OUTPUT_PATH
        
        
        #生データを見に行く
        path=os.path.join(namaDataPath , "*"+self.PATH_SLASH+"*", "*.*")
        print("namaDataPath:",path)
        namaDataFiles=glob.glob(path)
        #namaDataFiles=glob.glob(os.path.join(namaDataPath , "**", "*"))
        #print("namaDataFiles:",namaDataFiles)
       
        #セクションリストの取得
        with open(sectionListPath, "r", encoding="utf-8") as f:
            section_text=f.read()
        sectionList=[section.strip() for section in section_text.split(',')] 
        
        
        
        #outputフォルダ
        mapedList = map(str, sectionList)  #mapで要素すべてを文字列に
        sectionName = '_'.join(mapedList)
        #sectionName=sectionName.replace('_','')
        
        #print("outputPath:",outputPath)
        
        if not os.path.isdir(outputPath):
            os.mkdir(outputPath)
            print(outputPath," made")
        outputPath = os.path.join(outputPath, sectionName)
        if not os.path.isdir(outputPath):
            os.mkdir(outputPath)
            print(outputPath," made")
        
        
        
        
        #ファイルの抽出
        #companyFileSet={}
        #for file in namaDataFiles:
        #    fileName=os.pth.basename(file).split(".")[0]
        #    companyFileSet.add(fileName)
        
        #社名の抽出
        #companyNameSet={}
        #for file in namaDataFiles:
        #    fileName=os.pth.basename(file).split(".")[0]
        #    companyNameSet.add(fileName)
            
       
        
        
        
        #階層を取得する
        ##################################################################################
        #生データのファイルを１つずつ実行
        
        
        
        
        
        
        #分類のセットを作成
        folderStructureSet=set()
        for file in namaDataFiles:
            #print("file:",file)
            folderStructureSet.add(os.path.dirname(file))
            #print("folderStructureSet：",folderStructureSet)
            
        
        
        #分類ごとに
        for bunruiFolder in folderStructureSet:
            
            #print("bunruiFolder:",bunruiFolder)
            
            wakatiAllList=[]
            #print("fairu!",file)
            
            #社名の取得
            ###
            #prefix=os.path.join(namaDataPath,bunruiFolder)
            #print("prefix:",prefix)
            #if file.startswith(prefix):
            #    companyName=os.path.basename(file).split(".")[0]
            #    print("companyName:",companyName)
            
            companySet=set()
            
             
            #この分類の中にあるファイルを抽出
            filesInBunrui = [file for file in namaDataFiles if file.startswith(bunruiFolder)]
            #print("filesInBunrui:",filesInBunrui)
            
            for bunruiFile in filesInBunrui:
                #print("aaaaaaaaaaaaaa")
                companyName=os.path.basename(bunruiFile).split(".")[0]
                
                #実行済みなら飛ばす
                if companyName in companySet:
                    continue
                companySet.add(companyName)
            
                
                #各セクションのファイルがあるかどうか
                text=""
                for section in sectionList:
                    #print("section:",section)
                    #print("bunruiFolder:",bunruiFolder)
                    path=os.path.join(bunruiFolder,companyName+"."+ section)
                    #print(path)
                    if os.path.isfile(path):
                        #wakatiファイルを取得
                        
                        #print("bunruiFile:",bunruiFile)
                        """
                        
                        print("namaDataPath:",namaDataPath)
                        print("階層：",section, bunruiFolder.replace(namaDataPath,''))
                        """
                        kaiso=bunruiFolder.replace(namaDataPath,'')
                        """
                        print("kaiso",kaiso)
                        print("wakatiPath:",wakatiPath)
                        
                        print(wakatiPath,section,kaiso,companyName)
                        """
                        
                        
                        
                        #wakatiFile=os.path.join(wakatiPath, "*", section, kaiso, companyName + "." + "wakati")
                        ###あとで変える！！
                        #wakatiFile=wakatiPath+self.PATH_SLASH+ kaiso+self.PATH_SLASH+ companyName + "." + "wakati"
                        wakatiFile=wakatiPath+self.PATH_SLASH+"*"+self.PATH_SLASH+ section+ kaiso+self.PATH_SLASH+ companyName + "." + "wakati"
                        #print("wakatiFile:",wakatiFile)
                        
                        wakatiFileList=glob.glob(wakatiFile)
                        #print("wakatiFileList:",wakatiFileList)
                        if wakatiFileList:
                        #if os.path.isfile(wakatiFileList[0]):
                            #読み込み
                            with open(wakatiFileList[0], "r", encoding="utf-8") as f:
                            #with open(wakatiFile, "r", encoding="utf-8") as f:
                                #print("wakati読み込み開始：",wakatiFileList[0])
                                text=text+"\n"+f.read()
                                
                            
                #nullでなかったら保存
                if text:
                    wakatiAllList.append({'text': text, 'file': companyName})
                    
                    #print("wakatiAllList:",wakatiAllList)
                    
            
            #リストが空なら保存しない
            if not wakatiAllList:
                continue
            print("保存")
            print("outputPath:",outputPath)
            print("bunruiFolder:",bunruiFolder)
            print(kaiso)
            outputFolder=outputPath+kaiso
            #フォルダが存在しなければ再帰的に作成
            os.makedirs(outputFolder,exist_ok=True)
            
            #保存
            binaryFile=outputFolder+self.PATH_SLASH+"word_list.pkl"
            self.__write_binary_file( binaryFile, wakatiAllList)
            
            
            
    
    #同じフォルダ構成を作成する
    def __make_folder_structure(self, outputPath, outputFolder):
       
        for path in glob.glob(inputPath+ self.PATH_SLASH + "*", recursive=True):
            tmpPath = outputPath 
            if not os.path.isdir(path):
                continue
            
            #print("tmpPath:",tmpPath)
            tmpPath = tmpPath + self.PATH_SLASH + path.split(self.PATH_SLASH)[-1]
            if not os.path.isdir(tmpPath):
                os.mkdir(tmpPath)
                print(tmpPath," made")
            
        
        
            
        
        return
    
    
   


    #リストをバイナリ化して保存する関数
    def __write_binary_file(self, filePath, data):
        print("バイナリのパス：",filePath)
        with open(filePath, "wb") as f:
            pickle.dump(data, f)
        
        
 
    #指定したパス配下の０バイトフォルダ、ファイルを削除する
    def __delete_zorobyte_files(self,path):
        
        for pathname, dirnames, filenames in os.walk(path,topdown=False):
            for filename in filenames:
                filePath=os.path.join(pathname,filename)
                if os.path.getsize(filePath)==0:
                    os.remove(filePath)
                    
            for dirname in dirnames:
                dirpath=os.path.join(pathname,dirname)
                try:
                    os.removedirs(dirpath)
                    print(dirpath)
                except:
                    pass
        

    
    
    
    
    #中分類のバイナリファイルを大分類にする
    def __make_major_form_midium(self,majorFolder):
        
        #大分類のフォルダを取得
        majorFolders=glob.glob(os.path.join(majorFolder,"*"))
        print(majorFolders)
        
        for major in majorFolders:
        
            #大分類の中にあるバイナリデータをすべて取得
            path="*"+self.PATH_SLASH+"*"
            print(path)
            mediumBinaryFiles=glob.glob(os.path.join(major,path))


            majorBinaryFiles=[]

            #
            for binaryFile in mediumBinaryFiles:
                #ファイルがあれば

                #バイナリデータの読み込み
                fileDataList = self.__read_binary(file)
                majorBinaryFiles.extend(fileDataList)



                #保存
                self.__write_binary_file(major,majorBinaryFiles)
            
        
        
        
        
        
        
    #バイナリ読み込み
    def __read_binary(self,file):
        fileData=""
        f=with open(file,'rb')
            return pickle.load(f)
        
    
    
    ######public関数#######
    
    #majorFolderは大分類の一個上のフォルダ
    def make_major_form_midium(self,majorFolder):
        self.__make_major_form_midium(majorFolder)
    
    #
    def make_integrated_binary(self):
        self.__integrate_wakati_sections(self.USE_SECTION_LIST_PATH, self.BINARY_WAKATI_OUTPUT_PATH)
    
    
    
    
    #OUTPUT_PATH配下の０バイトフォルダ、ファイルを削除する関数
    def delete_zorobyte_files(self):
        self.__delete_zorobyte_files(self.OUTPUT_PATH)
    
    
    #階層を保持して指定した拡張子で分かち書きをする関数
    def select_extension_wakati(self):
        self.__select_extension_wakati(self.DATA_EXTENSION_LIST_PATH)
        
    # クラス変数で保持しているアウトプットパスにインプットパス以下の階層で分かち書きしたファイルを保存していく
    def wakati(self):
        self.__make_files_under_folders(self.DATA_PATH, self.OUTPUT_PATH)
        
    # 単体のファイルを分かち書きする関数    
    def single_wakati(self, dataFile, outputPath):
        self.__single_wakati(dataFile, outputPath)
        
    # 指定したフォルダ内のファイルを全て分かち書きする
    def folder_wakati(self, targetFolder, outputPath):
        self.__folder_wakati(targetFolder, outputPath)