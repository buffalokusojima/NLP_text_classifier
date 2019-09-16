import glob
import os
import random
import pickle

"""
   インプット下のフォルダをラベルとして返す
"""
def get_path_list(root):
    list = []
    for path in glob.glob(os.path.join(root,"*"), recursive=False):
        if not os.path.isdir(path):
            continue
        list.append(path.split('/')[-1])
    return list

"""
    word_list = {'label': ラベル, 'words': 文章}
"""
def data_equalization(word_list, count, label_key='label', words_key='words'):
    
    for words in word_list:
        if len(words[words_key]) > count:
            del_num = len(words[words_key]) - count
            random.shuffle(words[words_key])
            del words[words_key][:del_num]
        print(words[label_key], len(words[words_key]))

"""
    word_list => word_list{words, label, labels=[]}
"""
def devide_word_list(word_list, label, label_key='label', labels_key='labels', words_key='words'):
    
    for words in word_list:
        label_array = []
        for word in words[words_key]:
            label_array.append(label.index(words[label_key]))
        words[labels_key] = label_array
        print(words[label_key], words[labels_key])

def get_word_list(inputPath, word_list='word_list.pkl'):
    
    with open(os.path.join(inputPath,word_list), "rb") as f:
        word_list = pickle.load(f)
        
    return word_list


def get_word_list_folder(inputPath, file_name='word_list.pkl'):
    
    word_list = []
    for path in glob.glob(os.path.join(inputPath, "**", file_name), recursive=True):
        
        if os.path.isfile(path) and os.path.basename(path) == 'word_list.pkl':
            with open(path, "rb") as f:
                words = pickle.load(f)
                word_list.append({'label': path.split("/")[-2], 'words': words})
                
    return word_list


def get_word_list_folder_label(inputPath, file_name='word_list.pkl'):
    
    word_list = []
    label = get_path_list(inputPath)
    for path in glob.glob(os.path.join(inputPath, "**", file_name), recursive=True):
        
        if os.path.isfile(path) and os.path.basename(path) == 'word_list.pkl':
            label_array = []
            with open(path, "rb") as f:
                words = pickle.load(f)
                for word in words:
                    label_array.append(label.index(path.split("/")[-2]))
                word_list.append({'label': path.split("/")[-2], 'words': words, 'labels': label_array})
                
    return word_list


def write_word_list(inputPath, word_list, file_name='word_list.pkl'):
    
    with open(os.path.join(inputPath, file_name), "wb") as f:
        pickle.dump(word_list, f)
        
        
def check_word_list_type(word_list):
    
    if type(word_list[0]['text']) == 'str':
        for word in word_list:
            word['text'] = word['text'].split()
