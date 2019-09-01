from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from gensim import matutils
from gensim import corpora
import pickle
import matplotlib.pyplot as plt

ROOT_DIR = '.'
DICTIONARY_NAME = '/dictionary.txt'
LABEL_NAME = '/labels'
WORD_LIST = '/word_list'

def vec2dense(vec, num_terms):
    return list(matutils.corpus2dense([vec], num_terms=num_terms).T[0])

with open(ROOT_DIR+WORD_LIST, "rb") as f:
    words = pickle.load(f)

with open(ROOT_DIR+LABEL_NAME, "rb") as f:
    labels = pickle.load(f)
print(len(words))
dictionary = corpora.Dictionary.load_from_text(ROOT_DIR+DICTIONARY_NAME)
#print(dictionary)
data_all = [vec2dense(dictionary.doc2bow(words[i]),len(dictionary)) for i in range(len(words))]

X_train, X_test, y_train, y_test = train_test_split(data_all, labels, test_size=0.1, random_state=1, shuffle=True)

#データの標準化
sc = StandardScaler()
sc.fit(X_train)
X_train_std = sc.transform(X_train)
X_test_std = sc.transform(X_test)

plt.scatter(X_train_std[:, 0], X_train_std[:, 1], c='blue', marker='x')
plt.show()
# ラベルのScatter図作りたい
"""
plt.figure(figsize=(5, 6))
plt.subplot(2,1,1)
plt.title('StandardScaler')
plt.xlim([-4, 10])
plt.ylim([-4, 10])
plt.scatter(X_train[:, 0], data[:, 1], c='red', marker='x', s=30, label='origin')
plt.scatter(X_train_std[:, 0], X_train_std[:, 1], c='blue', marker='x', s=30, label='standard ')
plt.legend(loc='upper left')
plt.hlines(0,xmin=-4, xmax=10, colors='#888888', linestyles='dotted')
plt.vlines(0,ymin=-4, ymax=10, colors='#888888', linestyles='dotted')
plt.show()
"""
#学習モデルの作成
clf = SVC(C = 1, kernel = 'rbf')
clf.fit(X_train_std, y_train)

score = clf.score(X_test_std, y_test)
print("{:.3g}".format(score))

