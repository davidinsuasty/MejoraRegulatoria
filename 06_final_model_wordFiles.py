# -*- coding: utf-8 -*-
"""
Created on Sun May 17 03:52:06 2020

@author: hinsuasti

Script para realizar la clasificación de los archivos de word que han sido separados y
procesados por <parseWordFiles.py> y guardados en la carpeta <data> y clasificarlos por 
sustancial - no sustancial, paso siguiente si el documento es clasificado como sustancial 
este pasa por la clasificación de los 9 sectores productivos. Este script carga el modelo 
generado por <03_generate_model_S_NS.py> para la clasificación sustancial/np-sustancial y 
el modelo generado por <05_generate_model_sector.py> para la clasificación en los 9 sectores 
productivos. Ambos modelos guardados en la carpeta <models> 
"""
#%% librerias necesarias
import pickle
import pandas as pd

#%% cargar datos
# sustancial -no sustancial
df =  pd.DataFrame.from_dict(pickle.load(open(".\\data\\05-20-2020_0028-data_wordFiles.pkl",'rb')))
#filtrar textos de longutud 0
df = df[df['data'].apply(len)>0]
#%% cargar el modelo de sustancial no sustancial y hacer las predicciones para
#   cada texto den la base de textos
pip_sus_nosus = pickle.load(open(".\\models\\06-04-2020_1914-final_model_s_ns.pkl",'rb'))
df['suntancialPred'] = (pip_sus_nosus.decision_function(df['data']) >  0.23).astype(int)

#%% Cargar el modelo de sectores y hacer prediccion para cada uno de los textos
#   que se clasificó previamente como sustancial

pip_sectores = pickle.load(open(".\\models\\06-04-2020_1934-final_model_sectors.pkl",'rb'))    

#textos clasificados como sustanciales
df_sectores = df[df['suntancialPred'] == 1].copy()

#realizar las predicciones para cada texto segun su probabilidad de tema
y = pip_sectores.predict_proba(df_sectores['data'])
y_pred = pip_sectores.predict(df_sectores['data'])
df_sectores['sectorPred'] = y_pred
#organizar las predicciones en tuplas de tema y probabilidad pertencia al tema
#de mayor a menor pertenencia 
bysector = [sorted(enumerate(row,1), key=lambda x:x[1], reverse=True) for row in (100*y).astype(int)]
df_sectores['bySector'] = bysector

# resultado uniendo todo el dataframe
result = df.join(df_sectores[['sectorPred','bySector']])

del bysector, df, df_sectores, y, y_pred
#guardando reporte
result.drop(['data'],axis = 1, inplace = True)
result.to_excel('reporte_sectores_wordFiles.xlsx', index = False, header=True)
