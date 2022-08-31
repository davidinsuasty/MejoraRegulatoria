"""
Script con funciones utiles para la limpieza de texto utilizadas en el proyecto.
"""
#%%
import itertools
import re
import unicodedata
import pkg_resources
####### Definición de funciones para limpiar el texto  #########
#%%
# Quita acentos (tildes y 'ñ'), reemplazándolos por su versión sin acento
def remover_acentos(texto):
    try:
        texto = unicode(texto, 'utf-8')
    except NameError: # unicode is a default on python 3 
        pass
    texto = unicodedata.normalize('NFD', texto)\
           .encode('ascii', 'ignore')\
           .decode("utf-8")
    return str(texto)

# Quita ciertas palabras y expresiones previamente indicadas
def remover_stopwords(texto, lista_palabras=[], lista_expresiones=[], ubicacion_archivo=None):
    # Si se pasa como argumento la ubicación de un archivo plano que contiene la lista de palabras y expresiones
    # no deseadas separadas por comas, espacios o por enters.
    #if ubicacion_archivo:
    #    lista_palabras, lista_expresiones = cargar_stopwords(ubicacion_archivo)
    # Quitar las expresiones no deseadas
    for expresion in set(lista_expresiones):
        texto = texto.replace(expresion,' ')
    # Dejar solo las palabras que no aparecen en la lista de palabras no deseadas
    texto = ' '.join([palabra for palabra in texto.split() if palabra not in set(lista_palabras)])
    # Reemplaza espacios múltiples por un solo espacio
    texto = re.sub(r" +"," ", texto)
    return texto

# Quita palabras de menos de n caracteres
def remover_palabras_cortas(texto, n_min):
    palabras =  texto.split(' ')
    return ' '.join([palabra for palabra in palabras if len(palabra) >= n_min])

# Limpieza básica del texto
def limpieza_basica(texto, quitar_numeros=True):
    """Limpieza básica del texto. Esta función realiza una limpieza básica del texto de entrada, \
    transforma todo el texto a letras minúsculas, quita signos de puntuación y caracteres \
    especiales, remueve espacios múltiples dejando solo espacio sencillo y caracteres \
    de salto de línea o tabulaciones.

    :param texto: (str) Texto de entrada al que se le aplicará la limpieza básica.
    :param quitar_numeros: (bool) {True, False} Valor por defecto: True. \
        Indica si desea quitar los números dentro del texto.
    :return: (str) Texto después de la limpieza básica.
    """
    # Texto a minúsculas
    texto = texto.lower()
    # Pone un espacio antes y después de cada signo de puntuación
    texto = re.sub(r"([\.\",\(\)!\?;:])", " \\1 ", texto)
    # Quita caracteres especiales del texto.
    # RegEx adaptada de https://stackoverflow.com/a/56280214
    if quitar_numeros:
        texto = re.sub(r'[^ a-zA-ZÀ-ÖØ-öø-ÿ]+', ' ', texto)
    else:
        texto = re.sub(r'[^ a-zA-ZÀ-ÖØ-öø-ÿ0-9]+', ' ', texto)
    # Reemplaza espacios múltiples por un solo espacio
    texto = re.sub(r" +", " ", texto)
    # Quitar espacios, tabs y enters en los extremos del texto
    texto = texto.strip(' \t\n\r')
    return texto

# Limpieza básica + remover palabras de menos de n caracteres y stopwords
def limpieza_texto(texto, lista_palabras=[], lista_expresiones=[], ubicacion_archivo=None, n_min=3, 
                    quitar_numeros=True, quitar_acentos=True, min_frecuencia_palabras=0):
    # Quitar palabras y expresiones no deseadas. Se hace al texto original porque la palabra/expresión
    # a remover puede tener tildes/mayúsculas/signos o estar compuesta por palabras cortas
    texto = remover_stopwords(texto,lista_palabras,lista_expresiones,ubicacion_archivo)
    # Se verifica si se desean quitar acentos/tildes
    if quitar_acentos:
        texto = remover_acentos(texto)
    # Limpieza básica del texto
    texto = limpieza_basica(texto, quitar_numeros)
    # Quita palabras cortas y palabras pertenecientes a una lista específica
    texto = remover_palabras_cortas(texto, n_min)
    # Quita palabras que aparecen n veces o menos en el texto
    if min_frecuencia_palabras>0:
        texto = remover_frecuencia(texto, min_frecuencia_palabras)
    # Se hace esto de nuevo, por si habían palabras que después de su limpieza quedan en 
    # la lista de palabras/expresiones no deseadas
    texto = remover_stopwords(texto,lista_palabras,lista_expresiones,ubicacion_archivo)    
    return texto


# Quita palabras que aparezcan en el texto menos o igual a n veces
from collections import Counter 
def remover_frecuencia (texto, min_frecuencia_palabras=1):
    """ Función que remueve las palabras que aparecen el texto
    n veces o menos:

    :param str texto: Ingresar el texto

    :returns: Texto sin palabras que aparecen n veces o menos
    :rtype: str
    """
    listaPalabras=texto.split()
    freq=Counter(listaPalabras)
    return (" ".join([ele for ele in listaPalabras if freq[ele] > min_frecuencia_palabras]))