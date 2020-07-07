""" script para cargar la base de datos de Mejora regulatoria desde 1991-2014
    en formato txt (ver variable path) y la lista de documentos que se encuentra
    en el archivo csv (ver variable dicc)
    Este script carga los documentos y aplica un proceso de limpieza de texto
"""
#%% Cargar librerias necesarias 
import glob
import pandas as pd
from load_stopwords  import load_stopwords
from limpieza_texto  import limpieza_texto
from itertools import repeat
import time
import pickle
import sys
import parmap

#%% util function
def message():
    msj ="""Debido a que se utiliza una paralelización del proceso de limpieza
    de texto, es NECESARIO REINICIAR EL KERNEL si se esta trabajando en 
    spyder o en juputer de vscode
    El proceso no se puede correr linea por linea"""
    print(msj)

if __name__ == '__main__':
    # verificando nucleos del computador
    message()
    nprocess = 16
    print('corriendo con {} nucleos!'.format(nprocess))
    #%% Leer los nombres de los archivos de la base de datos y diccionario
    
    #path relativo de la base de datos
    path = "..\..\Insumos\BD/"
    #diccionario
    dicc = pd.read_csv(path+'diccionario_DB_all.csv', sep=';')
    filepaths = []
    labels =[]
    sectors = []
    texts = []
    directorios = glob.glob(path+'/*/*.txt')
    print('Reading text directories...')
    for count,foldername in enumerate(directorios):
        sys.stderr.write('\r {0:3.1%}'.format(count/len(directorios)))
        filename = foldername.split(sep='\\')[-1].split(sep='.')[0].lower()
        if (dicc['document_id'].isin([filename]).any()):
            filepaths.append(foldername)
            with (open(foldername,'r')) as file:
                  texts.append(file.read())
            labels.append(dicc[dicc['document_id'].isin([filename])]['Sustancial'].values[0])
            sectors.append(dicc[dicc['document_id'].isin([filename])]['Sector'].values[0])
    print('\nDone!')
    #%% limpieza de texto 
    
    # cargar stopwords
    lp,le=load_stopwords(".\listas_stopwords")
    
    #remover stopwords
    print('Cleaning text...')
    start = time.time()
    cleanText = parmap.starmap(limpieza_texto, list(zip(texts,repeat(lp),repeat(le))),
                               pm_processes=12, pm_pbar=True, pm_chunksize=1)
    print('Done! - elapsed time : {:5.2f} minutes'.format((time.time()-start)/60.0))
    
    #%% guardar base de datos limpia para proceso de entrenamiento y validación
    summary =\
        '''Datos para entrenamiento sustancial / no sustancial
        samples: 1474
        label 0 - No sustancial (753)
        label 1- Sustancial (positve class, 705)
        Estructura: 
        data - textos
        labels - etiqueta para cada texto (0 o 1)
        sectors - pertenencia a un sector 1-9 o 10
        filepaths - ruta donde se encuentra cada archivo de texto en formato *.txt
        '''
    data = {'data':cleanText, 'labels':labels, 'filepaths': filepaths, 'sectors':sectors,'description':summary}
    
    ts = time.strftime('%m-%d-%Y_%H%M', time.localtime())
    pickle.dump(data, open( '.\\data\\'+ ts +'-data_all.pkl', "wb" ) )