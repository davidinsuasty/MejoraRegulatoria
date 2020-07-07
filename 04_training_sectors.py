# -*- coding: utf-8 -*-
"""
Created on Tue May 12 19:26:22 2020

@author: hinsuasti

Script para realizar el proceso de entrenamiento de modelos para la clasificación de
las normas en 9 sectores productivos y un sector transversal. El script carga la base
de datos generada por <01_loadDB.py> almacenada en la carpeta <data> del repositorio. 
EL script prueba diferentes modelos y los guarda en la carpeta <models>, también genera
un archivo txt donde se reportan los rendimientos de cada clasificador para escoger los
mejores parametros

"""


#%% cargar librerias necearias

import numpy as np
import pandas as pd
import pickle
from sklearn import svm
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
import time 

#%% funcion para guardar reporte
def saveReport(fr, name, grid_search, ytest, y_pred,ts):
    fr.write(' -> training for {} classifier ...\n'.format(name))
    fr.write("\nThe best hyperparameters from Grid Search are:\n")
    fr.write(str(grid_search.best_params_))
    fr.write("\nThe mean F1-score of a model with these hyperparameters is: ")
    fr.write(str(grid_search.best_score_))
    fr.write('\nelapsed time {0:.2f} secs. \nDone!\n\n'.format(time.time()-start))
    fr.write(str(grid_search.best_estimator_))
    fr.write("\nThe test accuracy is: ")
    fr.write(str(accuracy_score(ytest, y_pred)))
    fr.write("\n\nClassification report\n")
    fr.write(str(classification_report(ytest, y_pred)))
    fr.write("\n\nConfusion matrix\n")
    fr.write(str(confusion_matrix(ytest, y_pred)))
    fr.write('\nModel saved on ' + '.\\models\\'+ts+'-'+name+'.pkl\n\n\n')

if __name__ == '__main__':
    #%% cargar los datos
    print('loading data...')
    data = pickle.load(open(".\\data\\05-06-2020_0252-data.pkl",'rb'))
    df = pd.DataFrame.from_dict(data)
    # solo tomar los sustanciales
    df = df[df['labels'] == 1]
    #eliminar los nan de la base de datos
    df.dropna(inplace = True)
    #filtrar textos de longutud 0
    df = df[df['data'].apply(len)>0]
    # resumen de base de datos por etiqueta
    print(df.groupby(['sectors'])['labels'].count())
    
    #%% dividir la base de datos en train - test
    X = list(df['data'])
    y = list(df['sectors'].apply(int))
    print('spliting data')
    Xtrain, Xtest, ytrain, ytest = train_test_split(X, y, test_size = 0.20,
                                                    stratify = y, random_state = 5)
    print('Done! \n')
    
    
    #%% Feature encoding by TF-IDF
    
    # Parameter election
    ngram_range = (1,2)
    min_df = 23
    max_df = 1.
    max_features = 465
    
    print('computing TF-IDF repreesentation...')
    start = time.time()
    tfidf = TfidfVectorizer(encoding='utf-8', ngram_range=ngram_range, stop_words=None, 
                            lowercase = False, max_df=max_df, min_df=min_df,
                            max_features=max_features, norm='l2', sublinear_tf=True)
    
    
    feat_train = tfidf.fit_transform(Xtrain).toarray()
    feat_test = tfidf.transform(Xtest).toarray()
    print('matrix shapes after TF-IDF')
    print('train: ', feat_train.shape)
    print('test:  ', feat_test.shape)
    print('elapsed time {0:.2f} secs. \nDone!'.format(time.time()-start))
    
    #%% rutina de entrenamiento
    """
    Classifier names:
        KNN - K-nearest neighbors
        RF - Random Forest
        SVM - Suport Vector Machine
        KNN - K Nearest Neighbors
        MNB - Multinomial Naives Bayes
        MLR - Multinomial Logistic Regression
        GB - Gradient Boosting
    """
    #crear archivo para guardar los logs
    ts = time.strftime('%m-%d-%Y_%H%M', time.localtime())
    fileReport = 'report_'+ts+'.txt'
    fr = open(fileReport, 'w')
    
    #lista de clasificadores
    clf_names = ['KNN','RF', 'SVM', 'MNB', 'MLR','GB']
    clf_list = [
        KNeighborsClassifier(),
        RandomForestClassifier(random_state=10),
        svm.SVC(random_state=10),
        MultinomialNB(),
        LogisticRegression(random_state = 10),
        GradientBoostingClassifier(random_state = 10)
        ]
    
    param_grid = {
        'KNN':{'n_neighbors' : [3, 5, 7, 9],
               'weights' : ['uniform', 'distance'],
               'p': [1,2,3]},
        'RF': {'bootstrap' : [True, False],
               'max_depth' : [20, 30 , 40, 50, 60, None],
               'max_features': ['auto', 'sqrt'],
               'min_samples_leaf' : [1, 2, 4],
               'min_samples_split': [5, 10, 20],
               'n_estimators': [1000, 1200, 1300, 1500, 2000]
            },
        'SVM': [ {'C': [.01, .1, .5, 1., 2., 3, 5], 'kernel':['linear'], 'class_weight':['None']},
                 #{'C': [.001, .01, .1, .5, 1., 2., 3.], 'kernel':['poly'], 'degree':[2, 3,4,5,6]},
                 {'C': [1., 1.2, 1.5, 2, 2.5, 3], 'kernel':['rbf'], 'gamma':['auto','scale', 1e-1, 1, 1.2, 1.5, 1.7, 2, 2.5,2.8, 3], 'class_weight':['None','balanced']}
            ],
        'MNB': {'alpha':[0.5, 1.] 
            },
        'MLR': {'C':[float(x) for x in np.linspace(start = 1, stop = 5, num = 5)],
                'solver': ['newton-cg', 'sag', 'saga', 'lbfgs'],
                'class_weight': ['balanced', None],
                'penalty': ['l2', 'elasticnet']
            },
        'GB': {'max_depth': [15, 20, 25, 30],
               'max_features': ['auto', 'sqrt'],
               'min_samples_leaf': [1, 2, 4],
               'min_samples_split': [50, 100, 150,200],
               'n_estimators': [1000, 1200, 1300, 1500, 2000],
               'learning_rate': [.1, .5],
               'subsample': [.5, 1., 2.]
            }
        }
    
    
    for name, clf in zip(clf_names, clf_list):
        print(' -> training for {} classifier ...\n'.format(name))
        start = time.time()
        grid_search = GridSearchCV(estimator=clf, param_grid=param_grid[name],
                                   scoring = 'f1_micro', cv=5, verbose=1, n_jobs = 16)
        grid_search.fit(feat_train, ytrain)
        
        
        print("The best hyperparameters from Grid Search are:")
        print(grid_search.best_params_)
        print("The mean F1-score of a model with these hyperparameters is:")
        print(grid_search.best_score_)
        print('elapsed time {0:.2f} secs. \nDone!'.format(time.time()-start))
        
        #best model found
        best_clf = grid_search.best_estimator_
        best_clf
        
        #model fit and performance
        best_clf.fit(feat_train, ytrain)
        y_pred = best_clf.predict(feat_test)
        print("The test accuracy is: ")
        print(accuracy_score(ytest, y_pred))
        
        #classification report
        print('')
        print("Classification report")
        print(classification_report(ytest, y_pred))
        
        #confusion matrix
        print('')
        print("Classification report")
        print(confusion_matrix(ytest, y_pred))
        #save the best model
        print('')
        print('saving model...')
        
        with open('.\\models\\'+ts+'-'+name+'_'+str(max_features)+'.pkl', 'wb') as output:
            pickle.dump(best_clf, output)
            
        saveReport(fr, name+ '_'+str(max_features), grid_search, ytest,y_pred,ts)
     
    fr.close()
        
        