# -*- coding: utf-8 -*-
"""
Created on Thu Apr 15 00:05:32 2020

@author: hinsuasti

Este script se encarga del entrenamiento para modelo sustancial / no sustancial, utilizando
la base de datos generada por el script <01_loadDB.py> y guardada en la carpeta del proyecto
<data>. Este script guarda cada uno de los modelos entrenados en la carpeta <models> y un 
archivo de texto donde se reportan los rendimientos de cada uno de ellos en la carpeta raiz
"""

#%% cargar librerias necearias

import numpy as np
import pickle
from sklearn import svm
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
import time

#%% funcion para guardar reporte
def saveReport(fr, name, grid_search, ytest, y_pred, ts):
    fr.write(" -> training for {} classifier ...\n".format(name))
    fr.write("\nThe best hyperparameters from Grid Search are:\n")
    fr.write(str(grid_search.best_params_))
    fr.write("\nThe mean F1-score of a model with these hyperparameters is: ")
    fr.write(str(grid_search.best_score_))
    fr.write(
        "\nelapsed time {0:.2f} secs. \nDone!\n\n".format(time.time() - start)
    )
    fr.write(str(grid_search.best_estimator_))
    fr.write("\nThe test accuracy is: ")
    fr.write(str(accuracy_score(ytest, y_pred)))
    fr.write("\n\nClassification report\n")
    fr.write(str(classification_report(ytest, y_pred)))
    fr.write(
        "\nModel saved on " + ".\\models\\" + ts + "-" + name + ".pkl\n\n\n"
    )


#%% cargar los datos
print("loading data...")
data = pickle.load(open(".\\data\\04-15-2020_2356-data.pkl", "rb"))
X = data["data"]
y = data["labels"]
print("Done! \n")
#%% train -test split
print("spliting data")
Xtrain, Xtest, ytrain, ytest = train_test_split(
    X, y, test_size=0.15, random_state=10
)
print("Done! \n")

#%% Feature encoding by TF-IDF

# Parameter election
ngram_range = (1, 2)
min_df = 20
max_df = 1.0
max_features = 460

print("computing TF-IDF repreesentation...")
start = time.time()
tfidf = TfidfVectorizer(
    encoding="utf-8",
    ngram_range=ngram_range,
    stop_words=None,
    lowercase=False,
    max_df=max_df,
    min_df=min_df,
    max_features=max_features,
    norm="l2",
    sublinear_tf=True,
)


feat_train = tfidf.fit_transform(Xtrain).toarray()
feat_test = tfidf.transform(Xtest).toarray()
print("matrix shapes after TF-IDF")
print("train: ", feat_train.shape)
print("test:  ", feat_test.shape)
print("elapsed time {0:.2f} secs. \nDone!".format(time.time() - start))

#%% rutina de entrenamiento
"""
Classifier names:
    RF - Random Forest
    SVM - Suport Vector Machine
    KNN - K Nearest Neighbors
    MNB - Multinomial Naives Bayes
    MLR - Multinomial Logistic Regression
    GB - Gradient Boosting
"""
# crear archivo para guardar los logs
ts = time.strftime("%m-%d-%Y_%H%M", time.localtime())
fileReport = "report_" + ts + ".txt"
fr = open(fileReport, "w")

# lista de clasificadores
clf_names = ["RF", "SVM", "MNB", "MLR", "GB"]

clf_list = [
    RandomForestClassifier(random_state=10),
    svm.SVC(random_state=10),
    MultinomialNB(),
    LogisticRegression(random_state=10),
    GradientBoostingClassifier(random_state=10),
]

param_grid = {
    "RF": {
        "bootstrap": [True, False],
        "max_depth": [20, 30, 40, 50, 60, None],
        "max_features": ["auto", "sqrt"],
        "min_samples_leaf": [1, 2, 4],
        "min_samples_split": [10, 15, 20],
        "n_estimators": [1000, 1200, 1300, 1500, 2000],
    },
    "SVM": [
        {"C": [0.001, 0.01, 0.1, 0.5, 1.0, 2.0], "kernel": ["linear"]},
        {
            "C": [0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 3.0],
            "kernel": ["poly"],
            "degree": [2, 3, 4, 5, 6],
        },
        {
            "C": [0.8, 1.0, 1.2, 1.5],
            "kernel": ["rbf"],
            "gamma": [
                "auto",
                "scale",
                1e-3,
                1e-2,
                1e-1,
                1,
                2,
                2.5,
                2.8,
                3,
                3.2,
            ],
        },
    ],
    "MNB": {"alpha": [0.5, 1.0]},
    "MLR": {
        "C": [float(x) for x in np.linspace(start=0.1, stop=2, num=5)],
        "solver": ["newton-cg", "sag", "saga", "lbfgs"],
        "class_weight": ["balanced", None],
        "penalty": ["l2", "elasticnet"],
    },
    "GB": {
        "max_depth": [10, 15, 20, 30, 50],
        "max_features": ["auto", "sqrt"],
        "min_samples_leaf": [1, 2, 4],
        "min_samples_split": [10, 50, 100],
        "n_estimators": [1000, 1200, 1300, 1500, 2000],
        "learning_rate": [0.1, 0.5],
        "subsample": [0.5, 1.0, 2.0],
    },
}


for name, clf in zip(clf_names, clf_list):
    print(" -> training for {} classifier ...\n".format(name))
    start = time.time()
    grid_search = GridSearchCV(
        estimator=clf,
        param_grid=param_grid[name],
        scoring="f1",
        cv=5,
        verbose=1,
        n_jobs=-1,
    )
    grid_search.fit(feat_train, ytrain)

    print("The best hyperparameters from Grid Search are:")
    print(grid_search.best_params_)
    print("The mean F1-score of a model with these hyperparameters is:")
    print(grid_search.best_score_)
    print("elapsed time {0:.2f} secs. \nDone!".format(time.time() - start))

    # best model found
    best_clf = grid_search.best_estimator_
    best_clf

    # model fit and performance
    best_clf.fit(feat_train, ytrain)
    y_pred = best_clf.predict(feat_test)
    print("The test accuracy is: ")
    print(accuracy_score(ytest, y_pred))

    # classification report
    print("")
    print("Classification report")
    print(classification_report(ytest, y_pred))

    # save the best model
    print("")
    print("saving model...")

    with open(
        ".\\models\\" + ts + "-" + name + "_" + str(max_features) + ".pkl",
        "wb",
    ) as output:
        pickle.dump(best_clf, output)

    saveReport(
        fr, name + "_" + str(max_features), grid_search, ytest, y_pred, ts
    )

fr.close()
