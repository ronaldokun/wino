import math
from pathlib import Path
from typing import *

import pandas as pd

from mip import *


def get_data():
    df = pd.read_csv(PATH / "all_wines_cleaned.csv").sort_values(
        ["Avaliações"], ascending=False
    )
    # Incluir somente os vinhos disponíveis e com alguma pontuação, pois essas serão nossas variáveis de decisão principais
    data = (
        df[df.Preço_Normal.notna() & df.Pontos_Total != 0].copy().reset_index(drop=True)
    )
    data["Temperatura"] = data.Temperatura.fillna(data.Temperatura.mean())
    data["Teor_Alcoólico"] = data.Temperatura.fillna(data.Temperatura.mean())
    data = data.drop(
        [
            "Tipo_Cat",
            "Preços_Cat",
            "Pontuação_Cat",
            "Estoque_Cat",
            "Pontos_Total",
            "Preço_Sócio",
        ],
        axis=1,
    )
    data["Custo"] = data["Preço_Normal"] / 1.25
    data.set_index("Nome", inplace=True)
    data.index.name = "Vinho"
    return data


PATH = Path.cwd() / "data"
DATA: pd.DataFrame = get_data()

NUM: List[str] = [
    "Custo",
    "Preço_Normal",
    "Pontuação",
    "Avaliações",
    "Temperatura",
    "Teor_Alcoólico",
    "Potencial_Guarda",
]
CAT: List[str] = ["Tipo", "País", "Puro"]
COLS = NUM + CAT
INTERVAL_NUM = [(0, math.ceil(DATA[m].max())) for m in NUM]
INTERVAL_CAT = [{k: (0, 1) for k in DATA.loc[DATA[m].notna(), m].unique()} for m in CAT]
BUDGET: int = 1000000
CONSTRAINTS = {k: v for k, v in zip(NUM + CAT, INTERVAL_NUM + INTERVAL_CAT)}
del CONSTRAINTS["Puro"][0]
VARIABLE = "Preço_Normal"


# +
def optimize_model(
    model: Model, max_gap: float = 0.05, max_seconds: int = 300
) -> Tuple[str, Dict[str, float]]:
    model.max_gap = max_gap
    status = model.optimize(max_seconds=max_seconds)
    if status == OptimizationStatus.OPTIMAL:
        solution = "OPTIMAL"
        print("Optimal solution cost {} found".format(model.objective_value))
    elif status == OptimizationStatus.FEASIBLE:
        solution = "FEASIBLE"
        print(
            "sol.cost {} found, best possible: {}".format(
                model.objective_value, model.objective_bound
            )
        )
    elif status == OptimizationStatus.NO_SOLUTION_FOUND:
        solution = "UNFEASIBLE"
        print(
            "No feasible solution found, lower bound is: {}".format(
                model.objective_bound
            )
        )
    if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
        return {v.name: v.x for v in model.vars if abs(v.x) > 1e-6}, solution
    return None, None


def safra_stats(df: pd.DataFrame) -> None:
    n = df.Quantidade.sum()
    print(f"Nº de Vinhos Distintos: {df.shape[0]}")
    print(f"Media dos Preços: {(df.Quantidade * df.Preço_Normal).sum() / n:.2f}")
    print(f"Media da Pontuação: {(df.Quantidade * df.Pontuação).sum() / n:.2f}")
    print(f"Media do nº de Avaliações: {(df.Quantidade * df.Avaliações).sum() / n:.2f}")
    print(
        f"Total do Orçamento Utilizado: {sum(r.Quantidade * r.Custo for r in df.itertuples()):.2f}"
    )
    print(
        f"\nDistribuição da Pontuação: \n{df.Pontuação.value_counts(ascending=False)}"
    )
    print(
        f"\nDistribuição dos Tipos de Vinho: \n{df.Tipo.value_counts(ascending=False)}"
    )
    print(f"\nDistribuição dos Países: \n{df.País.value_counts(ascending=False)}")
    print(
        f"\nDistribuição do Potencial de Guarda: \n{df.Potencial_Guarda.value_counts(ascending=False)}"
    )


# -


def run_model(
    variable: str = VARIABLE,
    constraints: Dict = CONSTRAINTS,
    sense: str = "MAX",
    budget: int = BUDGET,
    lb: int = 0,
    ub: int = 50000,
    is_uniform: bool = False,
):
    """Constructs a MIP model to optimize `variable` subject to `constraints. Sense of Optimization defaults to MAX
    If `is_uniform` is True or lb == ub it turns the main variable `wines` into a binary decision variable
    """
    VINHOS = DATA.index.to_list()
    N = range(len(VINHOS))

    m = Model(sense=sense)

    if lb == ub:
        is_uniform = True

    if is_uniform:
        budget /= ub
        wines = [m.add_var(name=vinho, var_type=BINARY) for vinho in VINHOS]
    else:
        wines = [
            m.add_var(name=vinho, var_type=INTEGER, lb=lb, ub=ub) for vinho in VINHOS
        ]

    ALL = set(NUM).union(CAT)
    assert variable in ALL, f"A variável de decisão deve pertencer ao conjunto {ALL}"
    assert set(constraints.keys()).issubset(
        ALL
    ), f"As variáveis do problema devem pertencer do conjunto {ALL}"

    var = DATA[variable].to_list()

    # Objective Function
    m += xsum(wines[i] * var[i] for i in N)

    const = constraints.copy()

    # Main constraint is budget
    custo = DATA["Custo"].to_list()
    m += xsum(wines[i] * custo[i] for i in N) <= budget
    m += xsum(wines[i] * custo[i] for i in N) >= budget - DATA.Custo.min()

    cat = set(constraints.keys()).intersection(CAT)
    num = set(constraints.keys()).intersection(NUM)

    cat = {k: constraints[k] for k in cat}
    num = {k: constraints[k] for k in num}

    if not all([isinstance(val, tuple) and len(val) == 2 for val in num.values()]):
        raise ValueError(
            f"Os constraints {num.values()} devem ser tuplas com os valores (mínimo, máximo) das variáveis"
        )

    if len(cat):
        for col, col_dict in cat.items():
            if not all(
                [isinstance(val, tuple) and len(val) == 2 for val in col_dict.values()]
            ):
                raise ValueError(
                    f"Os constraints {col_dict.values()} devem ser tuplas com os valores (mínimo, máximo) das variáveis"
                )

            df_dummies = pd.get_dummies(DATA[col])
            for k, (minimo, maximo) in col_dict.items():
                assert (
                    minimo >= 0 and maximo <= 1
                ), f"As variáveis categóricas são proporcionais e devem estar no intervalo [0,1]"
                m += xsum(
                    wines[i] * df_dummies[k].to_list()[i] for i in N
                ) >= minimo * xsum(wines[i] for i in N)
                m += xsum(
                    wines[i] * df_dummies[k].to_list()[i] for i in N
                ) <= maximo * xsum(wines[i] for i in N)
    for i in N:
        for key, (minimo, maximo) in num.items():
            m += wines[i] * DATA[key].to_list()[i] >= minimo * wines[i]
            m += wines[i] * DATA[key].to_list()[i] <= maximo * wines[i]

    solution, status = optimize_model(m)

    if solution is not None:
        multiplier = ub if is_uniform else 1
        result = DATA.loc[solution.keys()].copy()
        result["Quantidade"] = [int(v * multiplier) for v in solution.values()]
        return result, status

    print(
        "!!!No result was found for the Optimization Problem with the Variable and Constraints provided!!!"
    )
    return None, status


__ALL__ = [
    PATH,
    DATA,
    COLS,
    BUDGET,
    CONSTRAINTS,
    VARIABLE,
    get_data,
    safra_stats,
    run_model,
]

# +
# resultado, status = run_model(constraints={'Avaliações': (777, 10000)})
# if status:
#     safra_stats(resultado)
#     resultado[COLS]
