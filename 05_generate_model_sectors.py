# -*- coding: utf-8 -*-
"""
Created on Thu May 14 17:56:26 2020

@author: hinsuasti

Script que genera el modelo con mejor desempeño encontrado en el script 
<04_training_sectors.py>. Este modelo se guarda en la carpeta <models> con la
etiqueta timestamp-final_model_sectors.pkl. la variable timestamp es la fecha y
hora en la que se generó el modelo.
"""

#%% cargar librerias necearias
import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
import time

#%% main processs
if __name__ == '__main__':
    #Load data
    print('loading data...')
    data = pickle.load(open(".\\data\\06-04-2020_1854-data_all.pkl",'rb'))
    df = pd.DataFrame.from_dict(data)
    # solo tomar los sustanciales
    df = df[df['Sustancial'] == 1]
    #eliminar los nan de la base de datos
    df.dropna(inplace = True)
    #filtrar textos de longutud 0
    df = df[df['data'].apply(len)>0]
    # resumen de base de datos por etiqueta
    print(df.groupby(['Sector'])['Sustancial'].count())
   
    #%% dividir la base de datos en train - test
    X = list(df['data'])
    y = list(df['Sector'].apply(int))
    print('spliting data')
    Xtrain, Xtest, ytrain, ytest = train_test_split(X, y, test_size = 0.15,
                                                    stratify = y, random_state = 10)
    print('Done! \n')
    
    #%% Pipeline generation with the best combination of parameters

    # TFIDF parameters
    ngram_range = (1,2)
    min_df = 23
    max_df = 1.
    max_features = 465
    
    print('computing TF-IDF repreesentation...')
    tfidf = TfidfVectorizer(encoding='utf-8', ngram_range=ngram_range, stop_words=None, 
                            lowercase = False, max_df=max_df, min_df=min_df,
                            max_features=max_features, norm='l2', sublinear_tf=True)

    # Classifier parameters
    C = 1.8
    kernel = 'linear'
    gamma = 'scale'
    clf = SVC(C=C, gamma=gamma, kernel=kernel, probability = True,
              class_weight= None, random_state=10)

    # generating pipeline
    print('generating final model')
    pipeline = Pipeline(steps=[('tfidf',tfidf),('clf',clf)])
    pipeline.fit(Xtrain,ytrain)
    print('Done!')

    ts = time.strftime('%m-%d-%Y_%H%M', time.localtime())
    print('saving model...')
    with open('.\\models\\_'+ts+'-final_model_sectors.pkl', 'wb') as output:
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
# from sklearn.metrics import roc_curve, auc
# import matplotlib.pyplot as plt
# y_score = pipeline.decision_function(Xtest)

# # Compute ROC curve and ROC area for each class
# fpr, tpr, thr = roc_curve(ytest, y_score)
# roc_auc = auc(fpr, tpr)

# plt.figure()
# plt.plot(fpr, tpr, color='darkorange',
#          lw=1, label='ROC curve (area = %0.2f)' % roc_auc)
# plt.plot([0, 1], [0, 1], color='navy', lw=1, linestyle='--')
# plt.xlim([0.0, 1.0])
# plt.ylim([0.0, 1.05])
# plt.xlabel('False Positive Rate')
# plt.ylabel('True Positive Rate')
# plt.title('Receiver operating characteristic example')
# plt.legend(loc="lower right")
# plt.show()

