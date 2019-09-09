import glob
import os
import random


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


