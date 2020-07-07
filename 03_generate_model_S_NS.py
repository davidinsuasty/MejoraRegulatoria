# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 21:45:51 2020

@author: hinsuasti

Script para generar modelo de clasificación sustancial (S) / No sustancial (NS) con los
mejores parametros encontrados por el sript <02_training.py>. Este script guarda el
modelo en la carpeta <models> con la etiqueta timestamp-final_model_s_ns.pkl
"""

#%% cargar librerias necearias
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
import time
#%% cargar los datos
print('loading data...')
# data = pickle.load(open(".\\data\\04-15-2020_2356-data.pkl",'rb'))
# X = data['data']
# y = data['labels']
# print('Done! \n')

##Version por dataframe para datos completos
df =  pd.DataFrame.from_dict(pickle.load(open(".\\data\\06-04-2020_1854-data_all.pkl",'rb')))
#filtrar textos de longutud 0
df = df[df['data'].apply(len)>0]
df = df[~df['Sustancial'].isna()]
X = list(df['data'])
y = list(map(int,list(df['Sustancial'])))
#%% train -test split
#dejando un 1% para probar el desempeño
print('spliting data')
Xtrain, Xtest, ytrain, ytest = train_test_split(X, y, test_size = 0.15,
                                                random_state = 20)
print('Done! \n')

#%% Pipeline generation with the best combination of parameters

# TFIDF parameters
ngram_range = (1,2)
min_df = 20
max_df = 1.
max_features = 460

tfidf = TfidfVectorizer(encoding='utf-8', ngram_range=ngram_range, stop_words=None, 
                        lowercase = False, max_df=max_df, min_df=min_df,
                        max_features=max_features, norm='l2', sublinear_tf=True)

# Classifier parameters
C = 0.8
kernel = 'rbf'
gamma = 2.8
clf = SVC(C=C, gamma=gamma, kernel=kernel, probability = True, random_state=10)

# generating pipeline
print('generating final model')
pipeline = Pipeline(steps=[('tfidf',tfidf),('clf',clf)])
pipeline.fit(Xtrain,ytrain)
print('Done!')

ts = time.strftime('%m-%d-%Y_%H%M', time.localtime())
print('saving model...')
with open('.\\models\\'+ts+'-final_model_s_ns.pkl', 'wb') as output:
    pickle.dump(pipeline, output)

print('Done!')
#%% show model performance
from sklearn.metrics import classification_report, accuracy_score

y_pred = pipeline.predict(Xtest)

print("The test accuracy is: ")
print(accuracy_score(ytest, y_pred))

#classification report
print('')
print("Classification report")
print(classification_report(ytest, y_pred))


#%% roc curve
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt
y_score = pipeline.decision_function(Xtest)

# Compute ROC curve and ROC area for each class
fpr, tpr, thr = roc_curve(ytest, y_score)
roc_auc = auc(fpr, tpr)

plt.figure()
plt.plot(fpr, tpr, color='darkorange',
         lw=1, label='ROC curve (area = %0.2f)' % roc_auc)
plt.plot([0, 1], [0, 1], color='navy', lw=1, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic example')
plt.legend(loc="lower right")
plt.show()
