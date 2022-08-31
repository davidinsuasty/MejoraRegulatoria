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
from func_aux import get_terminos_vinculantes
from func_aux import get_cuentas_condicionales
from func_aux import get_shannon_entropy
from func_aux import get_dale_chall


#%% cargar datos
anio = 2022
# sustancial -no sustancial
df = pd.DataFrame.from_dict(
    pickle.load(open(f".\\data\\{anio}-data_all.pkl", "rb"))
)
# filtrar textos de longutud 0
df = df[df["data"].apply(len) > 0]
df["n_terms_vinc"], df["n_words"] = get_terminos_vinculantes(df["texts2"])
df["cuentas_condicionales"] = get_cuentas_condicionales(df["texts2"])
df["entropia_shannon"] = get_shannon_entropy(df["texts2"])
df["dale_chall"] = get_dale_chall(df["texts2"], df["texts"])
#%% cargar el modelo de sustancial no sustancial y hacer las predicciones para
#   cada texto den la base de textos
pip_sus_nosus = pickle.load(
    open(".\\models\\03-04-2022_1059-final_model_s_ns.pkl", "rb")
)
df["Sustancial"] = (
    pip_sus_nosus.decision_function(df["data"]) > 0.00415236
).astype(int)

#%% Cargar el modelo de sectores y hacer prediccion para cada uno de los textos
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

del bysector, df, df_sectores, y, y_pred
# guardando reporte
result.drop(["data"], axis=1, inplace=True)
final = result[
    [
        "year",
        "ids",
        "type",
        "Sustancial",
        "Sector",
        "Prob",
        "bySector",
        "n_terms_vinc",
        "cuentas_condicionales",
        "entropia_shannon",
        "dale_chall",
        "n_words",
    ]
]

final.rename(columns={"type": "Nombre", "year": "Anio"}, inplace=True)
final.sort_values(by=["Anio", "ids"], inplace=True)
final.drop(columns=["ids"], inplace=True)
final.to_csv(f"reporte_{anio}.csv", index=False, sep=";", encoding="utf-8")
#%%

# anio = str(2020)
# width_cols = [14, 5, 38, 13, 10, 64, 12, 9]
# writer = pd.ExcelWriter(
#     anio + "_reporte_sectores_wordFiles.xlsx", engine="xlsxwriter"
# )
# final.to_excel(writer, sheet_name=anio, index=False)
# worksheet = writer.sheets[anio]
# for idx, col in enumerate(final):
#     worksheet.set_column(idx, idx, width_cols[idx])
# writer.save()

# result.to_excel('2014_reporte_sectores_wordFiles.xlsx', index = False, header=True)
