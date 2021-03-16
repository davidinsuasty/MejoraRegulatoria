# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 09:07:32 2020

@author: hinsuasti
lectura RTF de mejora regulatoria 
"""

from contexto.escritura import escribir_texto
from contexto import lectura
import glob
import parmap


path = './../../Insumos/DB1991_2014_full'
path_out = './../../Insumos/txt_planos_91-98_/'
all_docs = glob.glob(path + '/*/*.rtf')
n = len(all_docs)
if __name__=='__main__':
    texto = parmap.map(lectura.leer_texto,all_docs,'rtf','false','','True',pm_pbar=True, pm_processes=8)
    for i,file in enumerate(all_docs):
        escribir_texto(path_out + file.split('\\')[-1].split('.')[0].upper() + '.txt' ,texto[i],tipo='txt')
    
    