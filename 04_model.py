# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.4
#   kernelspec:
#     display_name: wino
#     language: python
#     name: wino
# ---

# # Getting the Data

from typing import *
from pandas_profiling import ProfileReport
import pandas as pd
from mip import *
import numpy as np


def get_data():
    df = pd.read_csv('all_wines_cleaned.csv').sort_values(['Avaliações'], ascending=False)
    #Incluir somente os vinhos disponíveis e com alguma pontuação, pois essas serão nossas variáveis de decisão principais
    data = df[df.Preço_Normal.notna() & df.Pontos_Total != 0].copy().reset_index(drop=True)
    data = data.drop(['Tipo_Cat', 'Preços_Cat', 'Pontuação_Cat', 'Estoque_Cat', 'Pontos_Total', 'Preço_Sócio'], axis=1)
    data.set_index('Nome', inplace=True)
    return data


data = get_data()

# Os vinhos do catálogo possuem cerca de 15 por cento de desconto para os associados, i.e. `Preço_Normal ~ 0.85 * Preço_Sócio`
#
# Considerando como uma aproximação que no Preço Normal incida aproximadamente 25% do valor do Preço de Custo do Vinho, i.e. 10% do Preço_Sócio.
#
# Como o Preço Sócio não adiciona informação para o nosso problema eliminamos essa variável

data['Custo'] = data['Preço_Normal'] / 1.25

# Em problemas de otimização devemos ter somente variáveis numéricas,i.e. reais, ordinais e booleanas. Algumas variáveis numéricas no entanto tem muitos valores nulos, como Decantação por exemplo, outras como Safra na verdade são variáveis categóricas no formato de número. Não iremos utilizá-las em nosso problema de otimização.

NUM: List[str] = ['Custo', 'Preço_Normal', 'Pontuação', 'Avaliações', 'Temperatura', 'Teor_Alcoólico', 'Potencial_Guarda']

# Existem outras variáveis categóricas com baixa cardinalidade de potencialmente possam ser transformadas e utilizadas.

CAT: List[str] = ['Tipo', 'País', 'Puro']

df = data[NUM + CAT].copy()

df.isnull().sum()

df['Temperatura'] = df.Temperatura.fillna(df.Temperatura.mean())
df['Teor_Alcoólico'] = df.Temperatura.fillna(df.Temperatura.mean())
df.isnull().any()

# # Definição do Problema
# A variável de decisão é composta pelos vinhos. O Orcamento será utilizado como _constraint_, no entanto é ajustável.

BUDGET: int = 1000000
VINHOS = df.index.to_list()
N = range(len(VINHOS))


# ## Helper Functions

# +
def optimize_model(model:Model, max_gap: float=0.05, max_seconds: int=300)->Tuple[str, Dict[str, float]]:
    model.max_gap = max_gap
    status = model.optimize(max_seconds=max_seconds)
    if status == OptimizationStatus.OPTIMAL:
        solution = 'OPTIMAL'
        print('Optimal solution cost {} found'.format(model.objective_value))
    elif status == OptimizationStatus.FEASIBLE:
        solution = 'FEASIBLE'
        print('sol.cost {} found, best possible: {}'.format(model.objective_value, model.objective_bound))
    elif status == OptimizationStatus.NO_SOLUTION_FOUND:
        solution = 'UNFEASIBLE'
        print('No feasible solution found, lower bound is: {}'.format(model.objective_bound))
    if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
        return {v.name:v.x for v in model.vars if abs(v.x) > 1e-6}, solution
    return None, None

def safra_stats(df: pd.DataFrame)-> None:
    n = df.Quantidade.sum()
    print(f'Nº de Vinhos Distintos: {df.shape[0]}')
    print(f'Media dos Preços: {(df.Quantidade * df.Preço_Normal).sum() / n:.2f}')
    print(f'Media da Pontuação: {(df.Quantidade * df.Pontuação).sum() / n:.2f}')
    print(f'Media do nº de Avaliações: {(df.Quantidade * df.Avaliações).sum() / n:.2f}')
    print(f'Total do Orçamento Utilizado: {sum(r.Quantidade * r.Custo for r in df.itertuples()):.2f}')
    print(f'\nDistribuição da Pontuação: \n{df.Pontuação.value_counts(ascending=False)}')
    print(f'\nDistribuição dos Tipos de Vinho: \n{df.Tipo.value_counts(ascending=False)}')
    print(f'\nDistribuição dos Países: \n{df.País.value_counts(ascending=False)}')
    print(f'\nDistribuição do Potencial de Guarda: \n{df.Potencial_Guarda.value_counts(ascending=False)}')    


# -

def run_model(variable: List, 
             constraints: Dict[str, Tuple[float, float]],
             sense: str = 'MAX',
             lb: int=0,
             ub: int=1000,
             is_uniform: bool=False
             ):
    """Constructs a MIP model to optimize variable subject to `constraints. Sense of Optimization defaults to MAX
    If `is_uniform` is True, it turns the main variable `vinhos` into a binary decision variable
    which if True is equivalent to one batch of `ub` 
    """
    m = Model(sense=sense)
    
    if lb == ub:
        is_uniform = True
    
    if is_uniform:
        wines = [m.add_var(name=vinho, var_type=BINARY) for vinho in VINHOS]    
    else:
        wines = [m.add_var(name=vinho, var_type=INTEGER, lb=lb, ub=ub) for vinho in VINHOS]    
        
    ALL = set(NUM).union(CAT)    
    assert variable in ALL, f'A variável de decisão deve pertencer ao conjunto {ALL}' 
    assert set(constraints.keys()).issubset(ALL), f'As variáveis do problema devem pertencer do conjunto {ALL}'
    
    var = df[variable].to_list()
    
    #Objective Function
    m += xsum(wines[i] * var[i] for i in N)
    
    const = constraints.copy()
    
    budget = BUDGET / ub if is_uniform else BUDGET
    
    # Main constraint is budget
    custo = df['Custo'].to_list()
    m += xsum(wines[i] * custo[i] for i in N) <= budget
    m += xsum(wines[i] * custo[i] for i in N) >= budget - df.Custo.min()

    cat = set(constraints.keys()).intersection(CAT)
    num = set(constraints.keys()).intersection(NUM)

    cat = {k: constraints[k] for k in cat}
    num = {k: constraints[k] for k in num}
    
    if not all([isinstance(val, tuple) and len(val)==2 for val in num.values()]):
        raise ValueError(f'Os constraints {num.values()} devem ser tuplas com os valores (mínimo, máximo) das variáveis')    
    
    if len(cat):
        for col, col_dict in cat.items():
            if not all([isinstance(val, tuple) and len(val) == 2 for val in col_dict.values()]):
                raise ValueError(f'Os constraints {col_dict.values()} devem ser tuplas com os valores (mínimo, máximo) das variáveis')            
            
            df_dummies = pd.get_dummies(df[col])
            for k, (minimo, maximo) in col_dict.items():
                assert minimo >= 0 and maximo <= 1, f'As variáveis categóricas são proporcionais e devem estar no intervalo [0,1]'
                m += xsum(wines[i] * df_dummies[k].to_list()[i] for i in N) >= minimo * xsum(wines[i] for i in N)
                m += xsum(wines[i] * df_dummies[k].to_list()[i] for i in N) <= maximo * xsum(wines[i] for i in N)
    for i in N:        
        for key, (minimo, maximo) in num.items():
            m += wines[i] * df[key].to_list()[i] >= minimo * wines[i]
            m += wines[i] * df[key].to_list()[i] <= maximo * wines[i]
            
            
    solution, status = optimize_model(m)
    
    if solution is not None:
        multiplier = ub if is_uniform else 1
        result = data.loc[solution.keys()].copy()
        result['Quantidade'] = [v* multiplier for v in solution.values()]        
        return result, status
    
    print('!!!No result was found for the Optimization Problem with the Variable and Constraints provided!!!')
    return None, status

# Maximizar o Preço sem Constraint

var = 'Preço_Normal'
const = {'Pontuação': (0, 5)}
resultado, status = run_model(var, const, lb=10, ub=50)
safra_stats(resultado)
resultado[["Quantidade", 'Custo', 'Pontuação', 'Avaliações', 'Puro', 'País', 'Tipo', 'Potencial_Guarda']]

# Minimizar o Preço sem Constraint

var = 'Preço_Normal'
const = {'Pontuação': (0, 5)}
resultado, status = run_model(var, const, lb=0, ub=100000, sense='MIN')
safra_stats(resultado)
resultado[["Quantidade", 'Custo', 'Preço_Normal', 'Pontuação', 'Avaliações', 'Puro', 'País', 'Tipo', 'Potencial_Guarda']]

# Minimizar Preço com Constraint de Pontuação e Avaliações e a distribuição dos vinhos uniforme com 1000 garrafas

var = 'Preço_Normal'
const = {'Pontuação': (4, 5), 'Avaliações': (10, 10000)}
resultado, status = run_model(var, const, sense='MIN')
safra_stats(resultado)
resultado[["Quantidade", 'Custo', 'Preço_Normal', 'Pontuação', 'Avaliações', 'Puro', 'País', 'Tipo', 'Potencial_Guarda']]

# * Minimizar Preço 
#  * Pontuação entre (4,5)
#  * No Mínimo 10 Avaliações
#  * Distribuição Uniforme de 1000 garrafas por vinho
#  * Metade dos Vinhos Puros (Somente 1 uva)

var = 'Preço_Normal'
const = {'Pontuação': (4,5), 'Avaliações': (10, 10000), 'Puro':{1: (0.5, 0.5)}}
resultado, status = run_model(var, const, sense='MIN', ub=2000)
safra_stats(resultado)
resultado[["Quantidade", 'Custo', 'Preço_Normal', 'Pontuação', 'Avaliações', 'Puro', 'País', 'Tipo', 'Potencial_Guarda']]

var = 'Preço_Normal'
const = {'Pontuação': (4,5), 'Avaliações': (10, 10000), 'Puro':{1: (0.33, 0.66)}}
resultado, status = run_model(var, const, sense='MIN', ub=2000)
safra_stats(resultado)
resultado[["Quantidade", 'Custo', 'Preço_Normal', 'Pontuação', 'Avaliações', 'Puro', 'País', 'Tipo', 'Potencial_Guarda']]

var = 'Preço_Normal'
const = {'Pontuação': (4,5), 'Avaliações': (10, 10000), 'Puro':{1: (0.5, 1)}, 'País':{'França': (0.33, 1)}}
resultado, status = run_model(var, const, sense='MIN', lb=1, ub=25000)
if status:
    safra_stats(resultado)
    resultado[["Quantidade", 'Custo', 'Preço_Normal', 'Pontuação', 'Avaliações', 'Puro', 'País', 'Tipo', 'Potencial_Guarda']]

var = 'Preço_Normal'
const = {'Pontuação': (4,5), 
         'Avaliações': (10, 10000), 
         'Puro':{1: (0.33, 1)}, 
         'País': {'França': (0.33, 1), 'Argentina': (0.2, 1)},
         'Tipo': {'Frisante': (0.2, 1), 'Tinto': (0.5, 1)}}
         #'Potencial_Guarda': (3, 50)}
resultado, status = run_model(var, const, sense='MIN', is_uniform=False)
print(f'Orçamento Utilizado: {sum(r.Quantidade * r.Custo for r in resultado.itertuples()):.2f}')
resultado[["Quantidade", 'Custo', 'Pontuação', 'Avaliações', 'Puro', 'País', 'Tipo', 'Potencial_Guarda']]

# %debug


