"""Acceso a la BD `integration` que corre en el container macro-mysql.

Las consultas pesadas se cachean en Parquet bajo data/cache/: reejecutar el
notebook no vuelve a golpear MySQL.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

DB_URL = os.environ.get(
    "MACRO_DB_URL",
    "mysql+pymysql://root:macro@127.0.0.1:3307/integration?charset=utf8mb4",
)

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "data" / "cache"

_engine = None


def engine():
    """Engine perezoso y reutilizado; abrir uno por consulta es caro."""
    global _engine
    if _engine is None:
        _engine = create_engine(DB_URL, pool_pre_ping=True)
    return _engine


def q(sql: str, params: dict | None = None, cache: str | None = None) -> pd.DataFrame:
    """Ejecuta `sql` y devuelve un DataFrame.

    Si `cache` trae un nombre, el resultado se guarda en data/cache/<nombre>.parquet
    y las siguientes llamadas leen de ahi. La clave incluye un hash del SQL y de los
    parametros, asi que editar la consulta invalida el cache automaticamente.
    """
    path = None
    if cache:
        key = hashlib.sha1(f"{sql}{sorted((params or {}).items())}".encode()).hexdigest()[:10]
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path = CACHE_DIR / f"{cache}__{key}.parquet"
        if path.exists():
            return pd.read_parquet(path)

    df = pd.read_sql(sql, engine(), params=params)

    if path is not None:
        df.to_parquet(path, index=False)
    return df


def scalar(sql: str, params: dict | None = None):
    """Primera celda del primer renglon. Util para conteos."""
    return q(sql, params).iloc[0, 0]
