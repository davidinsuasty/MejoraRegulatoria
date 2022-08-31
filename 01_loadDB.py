""" script para cargar la base de datos de Mejora regulatoria desde 1991-2014
    en formato txt (ver variable path) y la lista de documentos que se encuentra
    en el archivo csv (ver variable dicc)
    Este script carga los documentos y aplica un proceso de limpieza de texto
"""
# %% Cargar librerias necesarias
import glob
import pandas as pd
from load_stopwords import load_stopwords
from limpieza_texto import limpieza_texto, limpieza_basica
from itertools import repeat
import time
import pickle
import sys
import re

# %% util function


def message():
    msj = """Debido a que se utiliza una paralelización del proceso de limpieza
    de texto, es NECESARIO REINICIAR EL KERNEL si se esta trabajando en 
    spyder o en juputer de vscode
    El proceso no se puede correr linea por linea"""
    print(msj)


if __name__ == "__main__":
    # verificando nucleos del computador
    message()
    nprocess = 12
    print("corriendo con {} nucleos!".format(nprocess))
    # %% Leer los nombres de los archivos de la base de datos y diccionario

    # path relativo de la base de datos
    # path = "..\..\Insumos\BD/"
    path = "..\..\Insumos/txt_planos_91-2014/"
    # diccionario
    # dicc = pd.read_csv(path+'diccionario_DB_all.csv', sep=';')
    filepaths = []
    labels = []
    sectors = []
    texts = []
    #anio = []
    directorios = glob.glob(path + "/*.txt")
    print("Reading text directories...")
    for count, foldername in enumerate(directorios):
        sys.stderr.write("\r {0:3.1%}".format(count / len(directorios)))
        #year = foldername.split("\\")[-1].split(".")[0][-2:]
        #year = str(1900 + int(year))
        # filename = foldername.split(sep='\\')[-1].split(sep='.')[0].lower()
        # if (dicc['document_id'].isin([filename]).any()):
        #     filepaths.append(foldername)
        #     with (open(foldername,'r')) as file:
        #           texts.append(file.read())
        #     labels.append(dicc[dicc['document_id'].isin([filename])]['Sustancial'].values[0])
        #     sectors.append(dicc[dicc['document_id'].isin([filename])]['Sector'].values[0])
        #anio.append(year)
        filepaths.append(foldername)
        try:
            with (open(foldername, "r", encoding="utf-8")) as file:
                print(foldername)
                texts.append(file.read())
        except:
            with (open(foldername, "r", encoding="latin-1")) as file:
                print(foldername)
                texts.append(file.read())

    print("\nDone!")
    # %% limpieza de texto

    # cargar stopwords
    lp, le = load_stopwords(".\listas_stopwords")

    # remover stopwords
    print("Cleaning text...")
    start = time.time()
    cleanText = parmap.map(
        limpieza_texto,
        texts,
        lp,
        le,
        pm_processes=nprocess,
        pm_pbar=True,
    )
    print(
        "Done! - elapsed time : {:5.2f} minutes".format(
            (time.time() - start) / 60.0
        )
    )

    # %% guardar base de datos limpia para proceso de entrenamiento y validación
    summary = """Datos para entrenamiento sustancial / no sustancial
        samples: 1474
        label 0 - No sustancial (753)
        label 1- Sustancial (positve class, 705)
        Estructura: 
        data - textos
        labels - etiqueta para cada texto (0 o 1)
        sectors - pertenencia a un sector 1-9 o 10
        filepaths - ruta donde se encuentra cada archivo de texto en formato *.txt
        """
    names = [
        re.search(
            "=?.*(decreto\s.*\n|ley\s.*\n|resoluci[oó]n\s.*\n)", t.lower()
        )
        for t in texts
    ]
    names = [n.group().strip() if n else "" for n in names]
    names = [re.sub("\(.*\):|\.", "", n, 1).strip() for n in names]
    anio = [n[-4:] for n in names]
    data = {
        "names": names,
        "anio": anio,
        "data": cleanText,
        "texto": texts,
        "filepaths": filepaths,
    }

    # ts = time.strftime("%m-%d-%Y_%H%M", time.localtime())
    # pickle.dump(data, open(".\\data\\" + ts + "-91-2014-data_all.pkl", "wb"))

    # #%% En esta parte se carga la estrutura de datos en data y se hace limpieza
    # #   básica pa calcular las metricas de complejidad
    # # data = pickle.load(
    # #     open(".\\data\\02-25-2022_1900-91-2014-data_all.pkl", "rb")
    # # )
    # data = pickle.load(
    #     open(".\\data\\02-25-2022_1900-91-2014-data_all.pkl", "rb")
    # )
    texts2 = parmap.map(
        limpieza_basica, data["texto"], pm_parallel=True, pm_pbar=True
    )
    data["texto2"] = texts2
    ts = time.strftime("%m-%d-%Y_%H%M", time.localtime())
    pickle.dump(data, open(".\\data\\" + ts + "-91-2014-data_all.pkl", "wb"))
