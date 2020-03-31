# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import pandas as pd
from model import *

st.title("Otimização do Estoque de Vinhos")

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
""")
# [See source code](https://github.com/streamlit/demo-uber-nyc-pickups/blob/master/app.py)
# """)

st.subheader('Conjunto de Dados')
st.dataframe(DATA)

# +
st.markdown("""
Os dados utilizados nesta modelagem foram retirados diretamente do site [Wine](wine.com.br),
limpos e formatados para melhor atender o propósito do problema.""")

st.subheader('Variáveis do Problema')

st.markdown("""
Num negócio real, o preço final repassado ao consumidor consiste:
`Preço = Lucro + Custos.`

Como só temos o valor do preço final, consideramos um taxa arbitrária de `25%` sobre o preço de custo, 
sendo assim adicionamos a coluna `Custo` aos dados que será utilizada para alocar o Orçamento.

A criação dessa varíavel não é necessária, poderíamos simplesmente alocar um valor considerando o Preço do Catálogo, 
no entanto trabalhar sobre um preço de custo reflete melhor um modelo de negócio e não altera o problema de Otimização.

""") 
# -

st.write("Somente as variáveis numéricas não nulas foram utilizadas, além de algumas categóricas com baixa cardinalidade: ", list(CONSTRAINTS.keys()))

st.sidebar.number_input(label="Orçamento", min_value=0, value=BUDGET)

constraints = set(CONSTRAINTS.keys())
constraints.remove('Custo')

variable = st.sidebar.radio("Variável de Decisão", tuple(constraints))

st.sidebar.number_input(label="Preço")
