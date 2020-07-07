# -*- coding: utf-8 -*-
"""
Created on Tue May 19 21:04:11 2020

@author: hinsuasti

script donde se encuentran las funcionalidades para leer los archivos word y 
devolver los textos planos separadados para su posterior analisis
"""
from docx import Document
from itertools import repeat
from load_stopwords  import load_stopwords
from limpieza_texto  import limpieza_texto
import glob
import parmap
import pickle
import re
import time
def splitWordFile(path=None):
    """ Función que separa el documento word en una lista de textos
    planos por cada tipo de ley, decreto, resolución, entre otros:

    :param str path: Ruta completa en donde está guardado el archivo *.dox

    :returns: Lista de textos planos separados por tipo de ley, decreto, entre otros.
    :rtype: list
    """
    name_file = path.split('\\')[-1][:-5]
    doc = Document(path)
    
    # Variables locales
    document_id, types, years, texts = [], [], [], []
    control_archivos, conteo = 0, 0
    strings=""
    
    # Lectura de las categorias que no tendrán en cuenta en los análisis
    # Para el análisis se tendrá en cuenta resoluciones, decretos y leyes
    categorias= open(".\categorias_1.txt",encoding='utf-8', errors='ignore').read()
    categorias=set(categorias.lower().split("\n"))
    
    # Este bucle recorre todo el texto línea a línea
    for p in doc.paragraphs:
        if (p.style.name == 'Heading 3'):
            if p.text == '* * * ':
                if conteo==1:
                    texts.append(strings)
                    strings=""
                control_archivos,conteo=0,0
                continue
            
            listacat=set(p.text.lower().split(" "))
            interseccion=(listacat & categorias)
            
            if len(interseccion)>0:
                document_id.append(name_file)
                match = re.match(r'.*([1-3][0-9]{3})', p.text)
                years.append(match.group(1))
                types.append(p.text)
                control_archivos,conteo=1,1
            
        elif (p.style.name != 'Heading 3'):
            if p.text=='* * * ' or p.text=='* * *':                
                if conteo==1:
                    texts.append(strings)
                    strings=""
                control_archivos,conteo=0,0
                continue
            if (control_archivos==1):
                strings=strings + p.text
    return document_id, types, years, texts

def load_docx_files(directorios):
    document_id_all=[]
    text_all=[]
    types_all=[]
    years_all=[]
    for doc_file in directorios:
        document_id, types, years, texts = splitWordFile(doc_file)
        document_id_all+=document_id
        types_all+= types
        years_all+=years
        text_all+=texts
    return document_id_all, types_all, years_all, text_all

#use example
if __name__ == '__main__':
    
    #path de los documentos word
    path = "..\..\Insumos\diario_oficial/"
    directorios = glob.glob(path+'/*.docx')
    print('parsing word files...')
    doc_ids, types, year, texts = load_docx_files(directorios)
    print('Done!')
    #%% limpieza de texto 
    
    # cargar stopwords
    lp,le=load_stopwords(".\listas_stopwords")
    
    #remover stopwords
    print('Cleaning text...')
    cleanText = parmap.starmap(limpieza_texto, list(zip(texts,repeat(lp),repeat(le))),
                               pm_processes=12, pm_pbar=True, pm_chunksize=1)
    
    data ={'data': cleanText, 'ids':doc_ids, 'type':types, 'year':year,}
    ts = time.strftime('%m-%d-%Y_%H%M', time.localtime())
    pickle.dump(data, open( '.\\data\\'+ ts +'-data_all.pkl', "wb" ) )