# -*- coding: utf-8 -*-
"""
Created on Sun May 17 03:52:06 2020

@author: hinsuasti

Script para realizar la clasificación de los txt guardados en la base de datos generada
por <01_loadDB.py> y clasificarlos por sustancial - no sustancial, paso siguiente si el
documento es clasificado como sustancial este pasa por la clasificación de los 9 sectores
productivos. Este script carga el modelo generado por <03_generate_model_S_NS.py> para
la clasificación sustancial/np-sustancial y el modelo generado por <05_generate_model_sector.py>
para la clasificación en los 9 sectores productivos. Ambos modelos guardados en la carpeta <models> 
"""
# %% librerias necesarias
import pickle
import pandas as pd
from func_aux import get_terminos_vinculantes
from func_aux import get_cuentas_condicionales
from func_aux import get_shannon_entropy
from func_aux import get_dale_chall

# %% cargar datos
# sustancial -no sustancial
df = pd.DataFrame.from_dict(
    pickle.load(open(".\\data\\08-24-2022_1250-91-2014-data_all.pkl", "rb"))
)
# filtrar textos de longutud 0
df = df[df["data"].apply(len) > 0]

df["n_terms_vinc"], df["n_words"] = get_terminos_vinculantes(df["texto"])
df["cuentas_condicionales"] = get_cuentas_condicionales(df["texto2"])
df["entropia_shannon"] = get_shannon_entropy(df["texto2"])
df["dale_chall"] = get_dale_chall(df["texto2"], df["texto"])
# %% cargar el modelo de sustancial no sustancial y hacer las predicciones para
#   cada texto den la base de textos
pip_sus_nosus = pickle.load(
    open(".\\models\\03-04-2022_1059-final_model_s_ns.pkl", "rb")
)
df["Sustancial"] = (
    pip_sus_nosus.decision_function(df["data"]) > 0.00415236
).astype(int)

# %% Cargar el modelo de sectores y hacer prediccion para cada uno de los textos
#   que se clasificó previamente como sustancial

pip_sectores = pickle.load(
    open(".\\models\\03-04-2022_1513-final_model_sectors.pkl", "rb")
)

# textos clasificados como sustanciales
df_sectores = df[df["Sustancial"] == 1].copy()

# realizar las predicciones para cada texto segun su probabilidad de tema
y = pip_sectores.predict_proba(df_sectores["data"])
y_pred = pip_sectores.predict(df_sectores["data"])
df_sectores["Sector"] = y_pred
df_sectores["Prob"] = y.max(1)
# organizar las predicciones en tuplas de tema y probabilidad pertencia al tema
# de mayor a menor pertenencia
bysector = [
    sorted(enumerate(row, 1), key=lambda x: x[1], reverse=True)
    for row in (100 * y).astype(int)
]
df_sectores["bySector"] = bysector

# resultado uniendo todo el dataframe
result = df.join(df_sectores[["Sector", "Prob", "bySector"]])
result.drop(columns=["data", "texto"], inplace=True)

final_ = result[
    [
        "anio",
        "names",
        "Sustancial",
        "Sector",
        "Prob",
        "bySector",
        "n_terms_vinc",
        "cuentas_condicionales",
        "entropia_shannon",
        "dale_chall",
        "n_words",
        "filepaths",
    ]
]
final_.sort_values(by=["anio", "filepaths"], inplace=True)
final_.rename(columns={"names": "Nombre", "anio": "Anio"}, inplace=True)
final_.drop(columns=["filepaths"], inplace=True)
final_.to_csv("reporte_1991-2014.csv", index=False, sep=";", encoding="utf-8")

# # %% unir con validaciones de Jose Libardo
# del bysector, df, df_sectores, y, y_pred

# # creando key para emparejar datos con excel de jose
# # result['document_id'] = result['filepaths'].apply(lambda x:x.split('\\')[-1][:-4])
# # result.drop(['data','labels','filepaths','sectors','description'],axis=1, inplace = True)

# # cargando datos de Jose
# path = ".\\data\\validacion_jose.xlsx"
# data = pd.read_excel(path)
# data.drop(columns=["Sectores"], inplace=True)
# # añadiendo la información de clasificación
# final = data.join(result.set_index("document_id"), on="document_id")

# # guardando reporte
# final.to_excel("reporte_sectores.xlsx", index=False, header=True)


# # %% reporte final con todos los docs
# final_ = result[
#     [
#         "anio",
#         "names",
#         "Sustancial",
#         "Sector",
#         "Prob",
#         "bySector",
#         "n_terms_vinc",
#         "n_words",
#     ]
# ]


# anio = str(1998)
# final = final_[final_["anio"] == anio]
# # width_cols = [5,38,13,10,64,12,9]
# # writer = pd.ExcelWriter('reporte_sectores_1991-1998.xlsx', engine='xlsxwriter')
# final.to_excel(writer, sheet_name=anio, index=False)
# worksheet = writer.sheets[anio]
# for idx, col in enumerate(final):
#     worksheet.set_column(idx, idx, width_cols[idx])

# writer.save()

# # %% funciones para reporte
# anio = str(1998)
# final = final_[final_["anio"] == anio]
# print(len(final))
# print(final.groupby("Sustancial")["anio"].count())
# print(final.groupby("Sector")["anio"].count())
