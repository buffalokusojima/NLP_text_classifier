import os as os
import pickle as pkl
os.chdir('C:\\Users\\localadmin\\Desktop\\AIコンテスト2019')
f = open('vovab_list','rb')
vocab_list_mecab = pkl.load(f)
f.close()


import pandas as pd
company_profile = pd.read_csv('profile.csv')

#### とりあえず、各文書に含まれる単語数をカウントして可視化

from sklearn.feature_extraction.text import CountVectorizer

bow_model = CountVectorizer()
bow_result = bow_model.fit_transform(vocab_list_mecab)

import numpy as np
import matplotlib.pyplot as plt
tmp = np.sum(bow_result.toarray()>0,axis=1)
plt.hist(tmp,bins=100)
plt.show()

np.min(tmp)

np.max(tmp)

#### 単語の分布を統計モデル化

import scipy.stats as stats

##### 単語数を対数に変換してガンマ分布でフィッティング

param = stats.gamma.fit(np.log(tmp))

#### 学習の邪魔になりそうな文書（単語数が過大または過少）を除外したい場合、この分布をもとに閾値を決定する
#### 今回はとりあえず使用しない

X = np.arange(19,2200,0.5)
Y = stats.gamma.pdf(np.log(X),*param)

plt.plot(np.log(X),Y)

plt.hist(np.log(tmp),bins=100,density=True)

plt.show()


##### 閾値の算定例

#### 上下の10％を除外したい

stats.gamma.interval(0.9,*param)

#### Tf-Idfの計算

from sklearn.feature_extraction.text import TfidfVectorizer     ### 関数のインポート

#### 参考BoWの場合

from sklearn.feature_extraction.text import CountVectorizer

#### 過剰のものを除外するため、影響を調べる


MAX = [0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09]
num_of_vocab=[]
for i in MAX :
    tfidf_model = TfidfVectorizer(max_df=i)
    result = tfidf_model.fit_transform(vocab_list_mecab)
    num_of_vocab.append(len(tfidf_model.get_feature_names()))
plt.plot(MAX,num_of_vocab)
plt.show()


#### 過少のものを除外するため、影響を調べる


MIN = [100,150,200,500,1000,1200,2000]
num_of_vocab=[]
for i in MIN :
    tfidf_model = TfidfVectorizer(max_df=1.0,min_df=i)
    result = tfidf_model.fit_transform(vocab_list_mecab)
    num_of_vocab.append(len(tfidf_model.get_feature_names()))
plt.plot(MIN,num_of_vocab)
plt.show()

#### 上記を参考にパラーメタを設定してTf-Idfを計算する

tfidf_model = TfidfVectorizer(max_df=0.05,min_df=150)
result = tfidf_model.fit_transform(vocab_list_mecab)


plt.hist(np.log(np.mean(result.toarray(),axis=0)),bins=100)
plt.show()


#### One-Hot表現にしたものを予測対象データ化しておく

target = pd.get_dummies(company_profile['業種']).values

#### 簡易的なテストデータとトレーニングデータの分離

np.random.seed(123)
train_idx = np.random.choice(a=np.arange(11471),size=7000)   ### トレーニング用のインデックスを取り出してデータを分離
target_train = target[train_idx,:]
feature_train = result.toarray()[train_idx,:]
np.random.seed()


feature_train.shape

import tensorflow as tf    #### tensorflowによるニューラスネットの作成

#### Model本体の定義

tf.reset_default_graph()

X1 = tf.placeholder(tf.float32,[None,1392])
Y1 = tf.placeholder(tf.float32,[None,33])

w1 = tf.Variable(tf.truncated_normal([1392,65]))
b1 = tf.Variable(tf.zeros([65]))

w2 = tf.Variable(tf.truncated_normal([65,33]))
b2 = tf.Variable(tf.zeros([33]))

h1 = tf.nn.relu(tf.matmul(X1,w1)+b1)
h1_drop = tf.nn.dropout(h1,keep_prob=0.65)
P  = tf.nn.softmax(tf.matmul(h1_drop,w2)+b2)

cost = -tf.reduce_mean(Y1*tf.log(P))

train_step = tf.train.AdamOptimizer().minimize(cost)

#### 学習処理

sess = tf.Session()
sess.run(tf.global_variables_initializer())

cost_result = []
batch_size = 400

for i in range(200) :          ### バッチサイズ400、学習回数200で繰り返す
    pos = 0
    for j in np.arange(len(feature_train) // batch_size) :
        
        if len(target_train) > pos+batch_size :
            batch_feature = feature_train[pos:pos+batch_size,:]
            batch_target  = target_train[pos:pos+batch_size,:]
            pos=pos+batch_size
        else :
            batch_feature = feature_train[pos:,:]
            batch_target = target_train[pos:,:]
            pos = pos+batch_size
        
        sess.run(train_step,feed_dict={X1:batch_feature,Y1:batch_target})
    tmp = sess.run(cost,feed_dict={X1:batch_feature,Y1:batch_target})
    cost_result.append(tmp)


plt.plot(cost_result)    #### 収束状況の確認
plt.show()

predict_prob = sess.run(P,feed_dict={X1:result.toarray()[train_idx,:]}) ### 各クラスに属する確率の計算

predict_label = np.argmax(predict_prob,axis=1)   ### 最大確率を予測ラベルとする（第１候補に相当）
obs_label = np.argmax(target[train_idx],axis=1)


tmp = pd.crosstab(index=obs_label,columns=predict_label)   ### ざっくりとマトリックス表を作成
plt.figure(figsize=(10,10))
sns.heatmap(tmp,cmap='Blues',annot=True)
plt.show()


import sklearn.metrics as metrics   ### 手軽にメトリクスを算出するモジュールのインポート

print(metrics.classification_report(obs_label,predict_label))

#### 集合の演算を利用してテストデータのインデックスを取り出す


test_idx = np.array(list(set(np.arange(11518)) - set(train_idx)))

#### テストデータでも同じことを実施する

predict_prob = sess.run(P,feed_dict={X1:result.toarray()[test_idx,:]})

predict_label = np.argmax(predict_prob,axis=1)
obs_label = np.argmax(target[test_idx],axis=1)

print(metrics.classification_report(obs_label,predict_label))
