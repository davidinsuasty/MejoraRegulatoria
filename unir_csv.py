"""
Archivo para unir todos los pkl de los años y verificar año
de los decretos y leyes
"""

import pickle
import re
import pandas as pd
import time



def read_csv(path):
    return pd.read_csv(path, sep=";")


#%% unir csv de los años separados
paths = [
    "reporte_1991-2014.csv",
    "reporte_2014.csv",
    "reporte_2015.csv",
    "reporte_2016.csv",
    "reporte_2017.csv",
    "reporte_2018.csv",
    "reporte_2019.csv",
    "reporte_2020.csv",
    "reporte_2021.csv",
    "reporte_2022.csv",
]

print("** Merging multiple csv files into a single pandas dataframe **")
# Merge files by joining all files
dataframe = pd.concat(map(read_csv, paths), ignore_index=True)
dataframe.sort_values(
    by=["Anio"],
    inplace=True,
)
# dataframe.to_csv("reporte_all.csv", index=False, sep=";", encoding="utf-8")
dataframe.drop_duplicates(subset="Nombre",inplace=True)
#%% Pegar los sectores de numero a texto
num2sec = {
    1: "Agricultura, caza, forestal y pesca",
    2: "Minería y extracción",
    3: "Manufacturas",
    4: "Electricidad, gas y suministros de agua",
    5: "Construcción",
    6: "Comercio, hoteles y restaurantes",
    7: "Transporte, almacenaje y comunicaciones",
    8: "Finanzas, negocios y bienes raíces",
    9: "Servicios personales, administración pública, salud, educación",
    10: "Otros",
}

# data = pd.read_csv("reporte_all.csv", sep=";", encoding="utf-8")
dataframe["Sector_name"] = dataframe["Sector"].map(num2sec)
dataframe.to_csv("reporte_all.csv", index=False, sep=";", encoding="utf-8")
