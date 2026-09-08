"""Inferencia de horarios de salida a partir del GPS.

No existe tabla de despachos en la BD: la hora de salida hay que deducirla.

Metodo. Se define una zona circular alrededor de cada terminal. Una *salida* es el
ultimo ping GPS dentro de una zona antes de que la unidad desaparezca de toda zona
terminal durante al menos `gap_min` minutos. El siguiente ping en zona es la
*llegada*, y la diferencia es el tiempo de recorrido.

Ventaja de definirlo asi: solo requiere los pings dentro de las zonas, que son ~17%
del total, y no depende de umbrales de velocidad ni de suavizado de trayectoria.

Limite conocido: si el GPS se cae a media vuelta, la salida se detecta igual pero la
llegada queda corrida. Por eso `detectar_salidas` filtra recorridos fuera de rango.
"""
from __future__ import annotations

import pandas as pd

from db import q
from fleet import GPS_ID_OFFSET

# La BD guarda todo en UTC (los dumps traen TIME_ZONE='+00:00' y el container corre
# con default_time_zone=+00:00). Jalisco no observa horario de verano desde 2022, asi
# que el offset es -6 fijo, pero se usa zoneinfo por si el rango de datos crece.
TZ_LOCAL = "America/Mexico_City"


def a_local(s: pd.Series) -> pd.Series:
    """UTC -> hora local de Guadalajara, sin tz para poder agrupar comodo.

    Sin esto el analisis horario sale corrido 6 h: el servicio arranca a las 05:00
    locales y en UTC parece arrancar a las 11:00.
    """
    return s.dt.tz_localize("UTC").dt.tz_convert(TZ_LOCAL).dt.tz_localize(None)

# Radio de la zona terminal. 250 m cubre el patio de maniobras sin alcanzar
# la estacion siguiente (la mas cercana esta a ~700 m).
RADIO_M = 250

# Una vuelta completa de la troncal no baja de ~30 min; 20 min separa con holgura
# una salida real de un reacomodo dentro del patio.
GAP_MIN = 20


def terminales(id_route: int = 2) -> pd.DataFrame:
    """Terminales de la ruta, desde in_route_point_control (direction = 0)."""
    return q(
        "SELECT name, latitude, longitude FROM in_route_point_control "
        "WHERE id_route = %(r)s AND name LIKE 'Terminal%%' ORDER BY name",
        {"r": id_route},
    )


def pings_en_terminal(
    id_ruta_estacion: int,
    lat_sur: float, lon_sur: float,
    lat_norte: float, lon_norte: float,
    radio_m: int = RADIO_M,
    cache: str | None = "pings_terminal",
) -> pd.DataFrame:
    """Pings GPS dentro de alguna zona terminal, etiquetados con la zona."""
    d_sur = f"ST_Distance_Sphere(POINT(g.longitude,g.latitude),POINT({lon_sur},{lat_sur}))"
    d_nte = f"ST_Distance_Sphere(POINT(g.longitude,g.latitude),POINT({lon_norte},{lat_norte}))"
    sql = f"""
        SELECT g.time,
               COALESCE(b1.id_bus, b2.id_bus)       AS id_bus,
               COALESCE(b1.busnumber, b2.busnumber) AS busnumber,
               CASE WHEN {d_sur} <= {radio_m} THEN 'SUR' ELSE 'NORTE' END AS zona
        FROM in_device_history_location g
        LEFT JOIN bus b1 ON g.id_bus <> 0 AND b1.id_bus = g.id_bus - {GPS_ID_OFFSET}
        LEFT JOIN bus b2 ON g.id_bus  = 0 AND b2.id_oct = g.id_ebjdevice
        WHERE g.id_route = {id_ruta_estacion}
          AND ({d_sur} <= {radio_m} OR {d_nte} <= {radio_m})
    """
    df = q(sql, cache=cache)
    df["time"] = pd.to_datetime(df["time"])
    return df


def detectar_salidas(
    pings: pd.DataFrame,
    gap_min: int = GAP_MIN,
    recorrido_min: int = 15,
    recorrido_max: int = 180,
) -> pd.DataFrame:
    """Convierte pings en zona a eventos de salida.

    Devuelve una fila por salida: unidad, terminal de origen, hora de salida,
    terminal y hora de llegada, y duracion del recorrido en minutos.

    `recorrido_min` / `recorrido_max` descartan tramos imposibles, que casi siempre
    son cortes de senal y no viajes reales.
    """
    df = pings.dropna(subset=["id_bus"]).sort_values(["id_bus", "time"]).copy()
    df["id_bus"] = df["id_bus"].astype("int64")

    g = df.groupby("id_bus", sort=False)
    df["t_sig"] = g["time"].shift(-1)
    df["zona_sig"] = g["zona"].shift(-1)
    df["gap_min"] = (df["t_sig"] - df["time"]).dt.total_seconds() / 60

    sal = df[df["gap_min"] >= gap_min].dropna(subset=["t_sig"]).copy()
    sal = sal.rename(
        columns={"time": "salida", "zona": "desde",
                 "t_sig": "llegada", "zona_sig": "hasta", "gap_min": "recorrido_min"}
    )
    sal = sal[(sal["recorrido_min"] >= recorrido_min) & (sal["recorrido_min"] <= recorrido_max)]

    sal["salida_local"] = a_local(sal["salida"])
    sal["llegada_local"] = a_local(sal["llegada"])

    # Todo lo que se agrupa por tiempo usa la hora local, nunca la UTC cruda.
    sal["fecha"] = sal["salida_local"].dt.date
    sal["hora"] = sal["salida_local"].dt.hour
    sal["dow"] = sal["salida_local"].dt.dayofweek     # 0 = lunes
    sal["finde"] = sal["dow"] >= 5
    return sal[["id_bus", "busnumber", "desde", "salida_local", "hasta", "llegada_local",
                "recorrido_min", "fecha", "hora", "dow", "finde"]].reset_index(drop=True)


def headways(salidas: pd.DataFrame, terminal: str = "SUR") -> pd.DataFrame:
    """Intervalo en minutos entre salidas consecutivas desde una terminal.

    Es la variable que el agente termina controlando: despachar mas seguido sube
    costo y baja espera, y al reves.
    """
    s = salidas[salidas["desde"] == terminal].sort_values("salida_local").copy()
    s["headway_min"] = s.groupby("fecha")["salida_local"].diff().dt.total_seconds() / 60
    return s.dropna(subset=["headway_min"])
