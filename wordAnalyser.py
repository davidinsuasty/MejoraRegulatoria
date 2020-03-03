"""
Este es el módulo que contiene todas las funciones que están relacionadas
con el procesamiento de los archivos word hasta dejar los archivos separados
en texto plano para su posterior análisis con mineria de texto.
Autor: David Insuasti
Fecha: 28/02/2020
"""
from docx import Document

def splitWordFile(path=None):
    """ Función que separa el documento word en una lista de textos
    planos por cada tipo de ley, decreto, resolución, entre otros:

    :param str path: Ruta completa en donde está guardado el archivo *.dox

    :returns: Lista de textos planos separados por tipo de ley, decreto, entre otros.
    :rtype: list
    """

    doc = Document(path)
    titles = []
    for p in doc.paragraphs:
        if (p.style.name == 'Heading 3'):
            if p.text == '* * * ':
                continue
        
            titles.append(p.text)
    
    return titles
       