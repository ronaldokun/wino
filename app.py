# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import pandas as pd
from model import *


def safra_stats(df: pd.DataFrame)-> None:
    n = df.Quantidade.sum()
    st.write(f'Nº de Vinhos Distintos: {df.shape[0]}')
    st.write(f'Media dos Preços: {(df.Quantidade * df.Preço_Normal).sum() / n:.2f}')
    st.write(f'Media da Pontuação: {(df.Quantidade * df.Pontuação).sum() / n:.2f}')
    st.write(f'Media do nº de Avaliações: {(df.Quantidade * df.Avaliações).sum() / n:.2f}')
    st.write(f'Total do Orçamento Utilizado: {sum(r.Quantidade * r.Custo for r in df.itertuples()):.2f}')
    st.write(f'\nDistribuição da Pontuação: \n{df.Pontuação.value_counts(ascending=False)}')
    st.write(f'\nDistribuição dos Tipos de Vinho: \n{df.Tipo.value_counts(ascending=False)}')
    st.write(f'\nDistribuição dos Países: \n{df.País.value_counts(ascending=False)}')
    st.write(f'\nDistribuição do Potencial de Guarda: \n{df.Potencial_Guarda.value_counts(ascending=False)}')    


st.title("Wino - Otimização do Estoque de Vinhos")

st.markdown(
"""
A Wine Brasil, além de ser uma loja online de vinhos, também funciona como um clube.\n

Seus associados mantém uma assinatura mensal ou anual cujos benefícios são:
 * Recebimento de 2 vinhos por mês em casa 
 * Desconto de cerca de 15% no catálogo. 

Numa possível tentativa de montar um negócio nos moldes da Wine Brasil, um dos problemas iniciais e 
fundamentais é como fazer a compra dos vinhos com o maior potencial de agradar os consumidores, i.e. como
otimizar a montagem do estoque e maximizar o nosso potencial como competidor.

Esse tipo de problema é do tipo **Programação Inteira Mista**, com aplicabilidade em diversos segmentos.

[Código-Fonte](https://github.com/ronaldokun/wino/blob/master/app.py)
""")

st.subheader('Conjunto de Dados')
if st.checkbox("Mostrar Dados?"):
    st.dataframe(DATA)

variables = set(CONSTRAINTS.keys())
variables.remove('Custo')

st.markdown("""
Os dados utilizados nesta modelagem foram retirados diretamente do site [Wine](wine.com.br),
limpos e formatados para melhor atender o propósito do problema.""")
st.subheader('Variáveis do Problema')
st.write("Somente as variáveis numéricas não nulas foram utilizadas, além de algumas categóricas com baixa cardinalidade") # list(variables))
st.markdown("""
Num negócio real, o preço final repassado ao consumidor consiste:
`Preço = Lucro + Custos.`

Como só temos o valor do preço final, consideramos um taxa arbitrária de `25%` sobre o preço de custo, 
sendo assim adicionamos a coluna `Custo` aos dados que será utilizada para alocar o Orçamento.

A criação dessa varíavel não é necessária, poderíamos simplesmente alocar um valor considerando o Preço do Catálogo, 
no entanto trabalhar sobre um preço de custo reflete melhor um modelo de negócio e não altera o problema de Otimização.
""") 

# +
sense = st.sidebar.radio("Sense", ['MAX', 'MIN'], 0)
budget = st.sidebar.number_input(label="Orçamento", min_value=0, value=BUDGET)
num = set(NUM)
num.remove('Custo')
cat = set(CAT)
variable = st.sidebar.radio("Variável de Decisão", tuple(variables))
is_uniform = st.sidebar.checkbox("Quantidade Uniforme de Vinhos?")

if not is_uniform:
    n_vinhos = st.sidebar.slider("Total de Vinhos", 0, 100000, (0,100000))
else:
    n_vinhos = (0, st.sidebar.number_input("Quantidade por Vinho", 0, 100000, 5000))

lb, ub = n_vinhos
n_const = st.sidebar.multiselect("Restrições Numéricas", tuple(num))
constraints = {}

for c in n_const:
    constraints[c] = st.sidebar.slider(c, CONSTRAINTS[c][0], CONSTRAINTS[c][1], CONSTRAINTS[c])

c_const = st.sidebar.multiselect("Restrições Categóricas (Percentual)", tuple(cat))
# -

for c in c_const:
    dict_const = {}
    st.sidebar.markdown(c)
    for k,v in CONSTRAINTS[c].items():
        if c == 'Puro':
            label = 'Puro' if k else 'Blend'
        else:
            label = k
        min_label, max_label = st.sidebar.slider(f'{label} (%)', 0, 100, (0,100))
        dict_const[k] = (min_label/100, max_label/100)
    constraints[c] =  dict_const

if st.button("Run Model"):   
    df, status = run_model(variable, constraints, sense, budget, lb, ub, is_uniform)
    if status:
        st.balloons()
        st.markdown(f"## Status: {status}")        
        st.table(df[['Quantidade']+COLS])
        #if st.checkbox("Estatísticas do Resultado"):
        #    safra_stats(df)            
    else:
        st.warning('!!!No result was found for the Optimization Problem with the Variable and Constraints provided!!!')
