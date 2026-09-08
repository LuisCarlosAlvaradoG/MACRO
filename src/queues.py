"""Estimación de la cola de espera por estación en la troncal T1.

Idea. En la troncal la validación ocurre al entrar a la estación cerrada, no al abordar,
así que cada fila de `transaction_1` es una persona que **empieza a esperar**. Los pasos
de camión reconstruidos desde el GPS (`src/stations.py`) son los momentos en que esa
espera puede terminar. La cola es la diferencia acumulada entre ambos flujos.

Como los dos flujos sólo interactúan en los instantes de paso, no hace falta simular
minuto a minuto: basta contar cuántas personas entraron entre paso y paso.

    llegadas_i  = validaciones entre el paso i-1 y el paso i
    cola_i      = personas presentes cuando llega el camión i

Dos modelos de lo que hace el camión al llegar:

  (a) VACIADO TOTAL — supuesto del brief. Cada camión se lleva a todos:
          cola_i = llegadas_i
      Es un piso: si esto ya da colas grandes, la realidad es peor.

  (b) CAPACIDAD FINITA C. El camión se lleva a lo más C personas y el resto se queda:
          cola_i = max(0, cola_{i-1} - C) + llegadas_i
      Con C -> infinito se recupera (a).

No existe dato de capacidad en la BD (ver CLAUDE.md), así que (b) no se puede fijar en un
número. Lo que sí se puede hacer es barrer C y encontrar a partir de qué capacidad las
colas dejan de acumularse: eso convierte el dato faltante en una pregunta concreta y
acotada para el cliente.

Limitación de fondo. El AFC no registra el sentido en que va cada persona, y por la
estación pasan camiones en ambas direcciones. Contar todos los pasos como si sirvieran a
toda la cola supone que cualquiera aborda lo que llegue primero, lo cual sobreestima la
capacidad de desalojo. Ver `docs/cola-de-espera.md`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# El servicio corre de 05 h a 22 h. Fuera de esa franja no hay camiones y la cola no
# significa nada, así que cada día se simula por separado y arranca en cero.
HORA_INI, HORA_FIN = 5, 23


def llegadas_entre_pasos(entradas: pd.DataFrame, pasos: pd.DataFrame) -> pd.DataFrame:
    """Cuenta las validaciones ocurridas entre cada par de pasos consecutivos.

    Devuelve una fila por paso de camión, con las personas que se le acumularon encima.
    """
    ent = entradas.copy()
    ent["minuto"] = pd.to_datetime(ent["minuto"])
    ent["fecha"] = ent["minuto"].dt.normalize()

    pas = pasos[["id_station", "llegada"]].copy()
    pas["llegada"] = pd.to_datetime(pas["llegada"])
    pas["fecha"] = pas["llegada"].dt.normalize()
    pas = pas[pas["llegada"].dt.hour.between(HORA_INI, HORA_FIN)]

    # Se preagrupa el AFC por (estación, día): filtrar el DataFrame completo dentro del
    # bucle costaba un barrido de 1.3 M filas por cada uno de los ~1 700 grupos.
    por_clave = {k: v for k, v in ent.groupby(["id_station", "fecha"], sort=False)}

    salida = []
    for (est, fecha), gp in pas.groupby(["id_station", "fecha"], sort=False):
        tp = np.sort(gp["llegada"].to_numpy())
        ge = por_clave.get((est, fecha))
        if ge is None or len(ge) == 0:
            llegadas = np.zeros(len(tp), dtype="int64")
        else:
            # searchsorted da, para cada validación, el índice del primer paso posterior.
            idx = np.searchsorted(tp, ge["minuto"].to_numpy(), side="left")
            llegadas = np.bincount(idx, weights=ge["entradas"].to_numpy(),
                                   minlength=len(tp) + 1)[:len(tp)].astype("int64")
        salida.append(pd.DataFrame({
            "id_station": est, "fecha": fecha, "paso": np.arange(len(tp)),
            "llegada_bus": tp, "llegadas": llegadas,
        }))

    df = pd.concat(salida, ignore_index=True)
    df["hora"] = pd.to_datetime(df["llegada_bus"]).dt.hour
    df["dow"] = pd.to_datetime(df["llegada_bus"]).dt.dayofweek
    df["finde"] = df["dow"] >= 5
    return df.sort_values(["id_station", "llegada_bus"]).reset_index(drop=True)


def cola_vaciado_total(flujo: pd.DataFrame) -> pd.DataFrame:
    """Modelo (a): cada camión se lleva a todos. La cola es lo llegado desde el paso previo."""
    out = flujo.copy()
    out["cola"] = out["llegadas"]
    out["residual"] = 0
    out["modelo"] = "vaciado total"
    return out


def cola_capacidad(flujo: pd.DataFrame, capacidad: int) -> pd.DataFrame:
    """Modelo (b): el camión se lleva a lo más `capacidad`; lo que sobra se queda.

    La recursión no es vectorizable porque cada paso depende del anterior, pero sólo corre
    sobre los instantes de paso (no minuto a minuto), así que es barata.
    """
    out = flujo.sort_values(["id_station", "fecha", "llegada_bus"]).copy()
    cola = np.empty(len(out), dtype="float64")
    residual = np.empty(len(out), dtype="float64")

    llegadas = out["llegadas"].to_numpy()
    claves = (out["id_station"].astype(str) + "|" + out["fecha"].astype(str)).to_numpy()

    q = 0.0
    anterior = None
    for i in range(len(out)):
        if claves[i] != anterior:      # nuevo día o nueva estación: la cola arranca vacía
            q = 0.0
            anterior = claves[i]
        q = q + llegadas[i]
        cola[i] = q
        abordan = min(q, capacidad)
        q -= abordan
        residual[i] = q

    out["cola"] = cola
    out["residual"] = residual
    out["modelo"] = f"capacidad {capacidad}"
    return out


def barrido_capacidad(flujo: pd.DataFrame, capacidades) -> pd.DataFrame:
    """Corre (b) para varias capacidades y resume qué tanto se sostiene el vaciado total.

    `pct_no_desaloja` es la fracción de pasos que dejan gente en el andén, y
    `residual_p95` cuánta gente queda. Si ambos son ~0, el supuesto (a) es defendible
    para esa capacidad.
    """
    filas = []
    for c in capacidades:
        r = cola_capacidad(flujo, c)
        cierre = r.groupby(["id_station", "fecha"])["residual"].last()
        filas.append({
            "capacidad": c,
            "cola_media": r["cola"].mean(),
            "cola_p95": r["cola"].quantile(.95),
            "pct_no_desaloja": 100 * (r["residual"] > 0).mean(),
            "residual_p95": r["residual"].quantile(.95),
            "residual_cierre_medio": cierre.mean(),
        })
    return pd.DataFrame(filas)
