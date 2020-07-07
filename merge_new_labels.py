# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 16:11:49 2020

@author: hinsuasti

Archivo para unir la base de datos pickle de los 11,110 documentos
que ya tienen la limpieza de texto  con una nueva revision de etiquetas
por parte del experto.
"""

#%% Cargar librerias necesarias
import pickle
import pandas as pd
import time
#%% cargando archivos

# archivo con las etiquetas anteriores
data_prev = pd.DataFrame.from_dict(pickle.load(open('.\\data\\'+ '05-17-2020_1307-data_all.pkl','rb')))
data_prev['document_id'] = data_prev['filepaths'].apply(lambda x:x.split('\\')[-1][:-4])
# borrando fila de labels  y sectores para unir las nuevas clasificaciones
data_prev.drop(columns=['labels','sectors', 'description'], inplace= True)

#cargar archivo actualizado 
data_new = pd.read_excel('..\..\\Insumos\\BD\\diccionario_DB_all_2020-05-20.xlsx')
#borrando informacion no relavante
cols = [c for c in list(data_new.columns) if c not in ['document_id', 'Sustancial','Sector']]
data_new.drop(columns=cols, inplace = True)

# uniendo los archivos
final = data_prev.join(data_new.set_index('document_id'), on = 'document_id')
final_dict = pd.DataFrame.to_dict(final, orient = 'list')

    
ts = time.strftime('%m-%d-%Y_%H%M', time.localtime())
pickle.dump(final_dict, open( '.\\data\\'+ ts +'-data_all.pkl', "wb" ) )