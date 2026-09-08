"""Resolucion de identidad de unidades y rutas.

La BD usa espacios de identificadores distintos para lo mismo, y los nombres de
columna enganan. Verificado sobre el dump del 2026-09-02:

1. `in_device_history_location.id_route` NO es `route.id_route`, es
   `route.id_ruta_estacion`. La troncal Macrobus T1 aparece como 79001001, no como 2.

2. `in_device_history_location.id_bus` NO es `bus.id_bus`: viene corrido +10000.
   El GPS de la troncal usa 179020101..179020176 y la tabla `bus` 179010101..179010176.
   Resuelve 16,011,306 de 16,011,319 filas (13 huerfanas, 3 ids).

3. Las filas con `id_bus = 0` son todas de la ruta T01 (id_ruta_estacion 100),
   3.14 M filas. Ahi el enlace es `id_ebjdevice` -> `bus.id_oct`, 25 de 25 devices.
   Ojo: NO es `bus.id_ebjdevice`, que el diccionario marca como campo en desuso.

Cualquier join GPS -> bus que ignore esto devuelve cero filas en silencio.
"""
from __future__ import annotations

import pandas as pd

from db import q

GPS_ID_OFFSET = 10_000

# route.id_ruta_estacion de las rutas con GPS relevante
TRONCAL_T1 = 79001001   # route.id_route = 2
RUTA_T01 = 100          # route.id_route = 7


def catalogo_unidades(cache: bool = True) -> pd.DataFrame:
    """Una fila por unidad, con las tres llaves y el nombre de ruta."""
    return q(
        """
        SELECT b.id_bus, b.busnumber, b.plate, b.model, b.brand, b.status,
               b.id_oct, b.id_ms, b.id_route,
               r.name AS ruta, r.id_ruta_estacion
        FROM bus b
        JOIN route r ON r.id_route = b.id_route
        """,
        cache="catalogo_unidades" if cache else None,
    )


def sql_gps_con_unidad(where: str = "1=1") -> str:
    """SQL que enlaza el GPS con `bus` cubriendo los dos esquemas de identidad.

    `where` se aplica sobre el alias `g` del GPS.
    """
    return f"""
        SELECT g.id_history, g.time, g.latitude, g.longitude, g.speed,
               g.degree_course, g.id_route AS id_ruta_estacion,
               COALESCE(b1.id_bus, b2.id_bus)       AS id_bus,
               COALESCE(b1.busnumber, b2.busnumber) AS busnumber
        FROM in_device_history_location g
        LEFT JOIN bus b1 ON g.id_bus <> 0 AND b1.id_bus = g.id_bus - {GPS_ID_OFFSET}
        LEFT JOIN bus b2 ON g.id_bus  = 0 AND b2.id_oct = g.id_ebjdevice
        WHERE {where}
    """


def cobertura_identidad(cache: bool = True) -> pd.DataFrame:
    """Cuantas filas de GPS resuelve cada mecanismo. Sirve de prueba de regresion."""
    return q(
        f"""
        SELECT
          CASE WHEN g.id_bus <> 0 THEN 'id_bus - 10000' ELSE 'id_ebjdevice -> id_oct' END AS mecanismo,
          COUNT(*) AS filas,
          SUM(CASE WHEN COALESCE(b1.id_bus, b2.id_bus) IS NULL THEN 1 ELSE 0 END) AS huerfanas
        FROM in_device_history_location g
        LEFT JOIN bus b1 ON g.id_bus <> 0 AND b1.id_bus = g.id_bus - {GPS_ID_OFFSET}
        LEFT JOIN bus b2 ON g.id_bus  = 0 AND b2.id_oct = g.id_ebjdevice
        GROUP BY mecanismo
        """,
        cache="cobertura_identidad" if cache else None,
    )
