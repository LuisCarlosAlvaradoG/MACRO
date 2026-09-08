"""Perfiles de demanda a partir de las validaciones AFC.

Cuidado con el reloj: `transaction_*.fechaHoraEvento` es DATETIME y MySQL lo guarda
tal cual, asi que YA viene en hora local. En cambio `in_device_history_location.time`
es TIMESTAMP y si esta normalizado a UTC. Son dos relojes distintos en la misma BD.
Comprobado con `dev_date`/`dev_time`, la hora local que reporta el equipo GPS.

Por eso aqui no se convierte nada, y en departures.py si.
"""
from __future__ import annotations

import pandas as pd

from db import q

# payment_type de in_payment_type que representan a una persona abordando.
# Se excluyen recargas, ventas de tarjeta, errores y ajustes: mueven dinero, no gente.
PAGOS_PASAJERO = (0, 1, 5, 6, 7, 23, 25, 98)


def demanda_por_hora(tabla: str = "transaction_1", cache: bool = True) -> pd.DataFrame:
    """Validaciones por hora local y tipo de dia."""
    return q(
        f"""
        SELECT HOUR(fechaHoraEvento) AS hora,
               (DAYOFWEEK(fechaHoraEvento) IN (1,7)) AS finde,
               COUNT(*) AS validaciones,
               COUNT(DISTINCT DATE(fechaHoraEvento)) AS dias
        FROM {tabla}
        WHERE payment_type IN {PAGOS_PASAJERO}
        GROUP BY hora, finde
        """,
        cache=f"demanda_hora_{tabla}" if cache else None,
    )


def demanda_por_dia(tabla: str = "transaction_1", cache: bool = True) -> pd.DataFrame:
    """Validaciones por dia, para ver estacionalidad y huecos de captura."""
    return q(
        f"""
        SELECT DATE(fechaHoraEvento) AS fecha, COUNT(*) AS validaciones
        FROM {tabla} WHERE payment_type IN {PAGOS_PASAJERO}
        GROUP BY fecha ORDER BY fecha
        """,
        cache=f"demanda_dia_{tabla}" if cache else None,
    )


def mix_pago(tabla: str = "transaction_1", cache: bool = True) -> pd.DataFrame:
    """Distribucion por tipo de pago, con su etiqueta legible."""
    return q(
        f"""
        SELECT t.payment_type, COALESCE(p.name,'(sin catalogo)') AS tipo, COUNT(*) AS n
        FROM {tabla} t LEFT JOIN in_payment_type p ON p.id = t.payment_type
        GROUP BY t.payment_type, tipo ORDER BY n DESC
        """,
        cache=f"mix_pago_{tabla}" if cache else None,
    )
