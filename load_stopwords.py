"""
Script que carga y quita las stopwords de un texto, útil para la limpieza de texto.
"""
#%%
import os
from os import listdir

#%%
def load_stopwords(my_path, listaNoIncluirSW = [], save_txt_name = None,save_path = None):    
    
    lista_palabras = []
    lista_expresiones = []
    stop_words=set()
    lista_archivos=os.listdir(my_path)

    # Cargar archivos .txt desde la carpeta seleccionada
    cargar_archivos_txt=list(set([w for w in lista_archivos if w.endswith(".txt")])-set(listaNoIncluirSW))
    for w in cargar_archivos_txt:
        lectura_archivo=set(open((my_path+"\\"+w), encoding='utf-8', errors='ignore').read().split("\n"))
        stop_words=(stop_words|lectura_archivo)
    
    # Guarda el documento en el path por defecto o en un path definido por el usuario
    # Solo guardará en caso de que el usuario escriba un nombre para el archivo
    stop_words=list(stop_words)
    if save_path!=None and save_txt_name!=None:
        crear_archivo=open(save_path+"\\"+save_txt_name, "w",encoding='utf-8', errors='ignore')
        for i in stop_words:
            crear_archivo.write(i+"\n")
    elif save_txt_name!=None:
        crear_archivo=open((my_path+"\\"+save_txt_name),"w",encoding='utf-8', errors='ignore')
        for i in stop_words:
            crear_archivo.write(i+"\n")
    
    # Separa la lista de Stopwords en lista de expresiones y lista de palabras
    for i in stop_words:
        if len(i.split(' ')) > 1:
            lista_expresiones.append(i)
        else:
            lista_palabras.append(i)
    return lista_palabras,lista_expresiones
