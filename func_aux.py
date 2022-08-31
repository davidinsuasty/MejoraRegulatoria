from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import numpy as np
import re


def get_terminos_vinculantes(texts):
    """
    Terminos vinculantes sobre un texto

    :param texts: Lista de textos, cada texto debe haber pasado por \\
        `limpieza_basica`.
    :type texts: list
    :return: Lista de términos vinculantes para cada texto de la \\
        lista de entrada. 
    :rtype: list
    """
    # Lista de palabras vinculantes
    vinculantes = (
        open("..\..\Insumos\expresiones_vinculantes.txt", encoding="utf-8")
        .read()
        .split("\n")
    )
    max_vin = max([len(v.split()) for v in vinculantes])
    nterms = 0
    for n in range(max_vin):
        n_i = n + 1
        ngram = [p for p in vinculantes if len(p.split()) == n_i]
        nvec = CountVectorizer(
            ngram_range=(n_i, n_i),
            vocabulary=ngram,
            token_pattern=r"(?u)\b\w+\b",
        )
        nterms += nvec.transform(texts).sum(axis=1)

    n_words = [len(t.split()) for t in texts]
    return nterms, n_words


def get_cuentas_condicionales(texts):
    """
    Cuentas condicionales sobre un texto

    :param texts: Lista de textos, cada texto debe haber pasado por \\
        `limpieza_basica`.
    :type texts: list
    :return: Lista de términos condicionales para cada texto de la \\
        lista de entrada. 
    :rtype: list
    """
    # Lista de palabras vinculantes
    condicionales = (
        open("..\..\Insumos\expresiones_condicionales.txt", encoding="utf-8")
        .read()
        .split("\n")
    )
    max_con = max([len(cond.split()) for cond in condicionales])
    nterms = 0
    for n in range(max_con):
        n_i = n + 1
        ngram = [p for p in condicionales if len(p.split()) == n_i]
        nvec = CountVectorizer(
            ngram_range=(n_i, n_i),
            vocabulary=ngram,
            token_pattern=r"(?u)\b\w+\b",
        )
        nterms += nvec.transform(texts).sum(axis=1)

    return nterms


def get_shannon_entropy(texts):
    """
    Cálculo de entropia de shannon para una lista de textos
    :param texts: Lista de textos, estos deben ser pasados por la \\
        función de `limpieza_basica`.
    :type texts: list
    :return: lista de entropias de shannon para cada uno de los \\
        textos de entrada
    :rtype: list
    """
    prob_words = TfidfVectorizer(use_idf=False).fit_transform(texts)
    shannon_entropy = -np.sum(
        prob_words.toarray() * np.log2(prob_words.toarray() + 1e-4),
        axis=1,
    )
    return shannon_entropy.astype(int)


def get_dale_chall(texts, raw_texts):
    """
    Cáclula la métrica de complejidad dale chall para una lista de \\
    textos de entrada

    :param texts: Lista de textos, estos deben haber pasado por la \\
        función `limpieza_basica`.
    :type texts: list
    :param raw_texts: Lista de textos sin ningún procesamiento.
    :type raw_texts: list
    """

    def avg_len_senteces(x):
        l = [len(y.split()) for y in x]
        if len(l) > 0:
            avg = sum(l) / len(l)
        else:
            avg = 0
        return avg

    words = (
        open("..\..\Insumos\expresiones_dale_chall.txt", encoding="utf-8")
        .read()
        .split(",")
    )
    # número maximo de palabras en una palabra
    max_comp = max([len(w.split()) for w in words])
    nterms = 0
    total_words = (
        CountVectorizer(token_pattern=r"(?u)\b\w+\b")
        .fit_transform(texts)
        .sum(axis=1)
    )

    nterms = 0
    for n in range(max_comp):
        n_i = n + 1
        ngram = set([p for p in words if len(p.split()) == n_i])
        nvec = CountVectorizer(
            ngram_range=(n_i, n_i),
            vocabulary=ngram,
            token_pattern=r"(?u)\b\w+\b",
        )
        temp = nvec.transform(texts).sum(axis=1)
        nterms += n_i * temp
        total_words -= temp
    fa = 1 - (nterms / total_words)
    raw_texts = [re.sub("\s+", " ", t) for t in raw_texts]
    raw_sentences = [re.split("\;|\.|\n", t) for t in raw_texts]
    sl = np.array([avg_len_senteces(s) for s in raw_sentences])
    dale_chall = 0.1579 * fa + 0.0496 * sl[:, np.newaxis] + 3.6365

    return dale_chall
