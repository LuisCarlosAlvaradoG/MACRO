"""Eventos por estación en la troncal T1: entradas de personas y pasos de camión.

Alcance: SÓLO la troncal Macrobús T1 (route.id_route = 2, id_ruta_estacion 79001001).

Por qué T01 queda fuera pese a estar en el brief. En T01 la validación es **a bordo**,
no en estación: `transaction_5.idDispositivo` toma los valores 64, 65, 66… que son
exactamente `bus.id_bus` de las unidades T01, y `transaction_5.idRutaEstacion` tiene un
único valor (100, la ruta). Además `afc_bus_total` reporta 818 519 pasajeros para
id_route = 7 y **cero** para id_route = 2. Es decir: en T01 el evento AFC ES el abordaje,
así que no existe una cola de espera observable que reconstruir. En T1 ocurre al revés:
cero pasajeros a bordo y el 100 % de las validaciones caen en torniquetes de estación.

Cadena de identidad para llegar de una validación a su estación (ninguna es obvia):

    transaction_1.idDispositivo
      -> afc_station_device_total.id_vehicle
      -> afc_station_device_total.id_station
      -> mac_station.id / .name

`transaction_1.idRutaEstacion` NO es la estación pese al nombre: es
`route.id_ruta_estacion`, o sea la ruta. `idUbicacion` es 0 en toda la troncal.

Geometría: `in_route_point_control` con id_route = 2 trae 25 estaciones en direction = 3,
y las dos de los extremos (Fray Angélico y Mirador) en direction 1 y 2. Juntas dan las 27
estaciones que aparecen en el AFC. Las Juntas existe en `mac_station` pero no tiene
torniquetes, así que no participa.
"""
from __future__ import annotations

import unicodedata

import numpy as np
import pandas as pd

from db import q
from fleet import GPS_ID_OFFSET, TRONCAL_T1

ID_ROUTE_TRONCAL = 2

# Separación mínima entre estaciones: 336 m (Esculturas <-> Fray Angélico). Con 150 m los
# discos no se traslapan. Por abajo, el GPS muestrea cada ~20 s: a 50 km/h la unidad
# avanza 278 m entre pings, así que un radio menor dejaría pasar unidades sin registrar.
RADIO_M = 150

# Separación mínima entre visitas de la MISMA unidad a la MISMA estación para contarlas
# como pasos distintos. Una vuelta completa no baja de ~30 min.
GAP_VISITA_MIN = 15


def _norm(s: str) -> str:
    """Nombre comparable: sin acentos, sin puntuación, espacios colapsados."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return " ".join(s.lower().replace(".", " ").split())


def catalogo_estaciones(cache: bool = True) -> pd.DataFrame:
    """Las 27 estaciones de la troncal con id del AFC, nombre, coordenadas y orden.

    Une la geometría de `in_route_point_control` con el id de `mac_station` por nombre
    normalizado. El emparejamiento se verifica: si no salen 27 filas, algo cambió en los
    catálogos y hay que revisarlo antes de seguir.
    """
    geo = q(
        """
        SELECT name, direction, AVG(latitude) AS lat, AVG(longitude) AS lon
        FROM in_route_point_control
        WHERE id_route = %(r)s AND direction IN (1, 2, 3)
        GROUP BY name, direction
        """,
        {"r": ID_ROUTE_TRONCAL},
        cache="geo_estaciones" if cache else None,
    )
    # Fray Angélico y Mirador aparecen en direction 1 y 2 (los extremos); el resto en 3.
    geo = geo.groupby("name", as_index=False)[["lat", "lon"]].mean()

    mac = q(
        "SELECT id AS id_station, sta_no AS orden, name FROM mac_station "
        "WHERE id_route = %(r)s AND sta_no <= 28",
        {"r": ID_ROUTE_TRONCAL},
        cache="mac_estaciones" if cache else None,
    )

    geo["k"], mac["k"] = geo["name"].map(_norm), mac["name"].map(_norm)

    # Los catálogos escriben distinto la misma estación. Verificado uno por uno contra
    # el listado de mac_station; se fija a mano para que no dependa de fuzzy matching.
    alias = {
        "esculturas": "escultura",
        "monte olivete": "monte olivette",
        "independencia norte": "independencia nte",
    }
    geo["k"] = geo["k"].replace(alias)

    cat = geo.merge(mac[["id_station", "orden", "k"]], on="k", how="inner")
    cat = cat[["id_station", "name", "orden", "lat", "lon"]].sort_values("orden")

    if len(cat) != 27:
        raise ValueError(
            f"se esperaban 27 estaciones y salieron {len(cat)}. "
            "Revisar el emparejamiento de nombres antes de usar estos datos."
        )
    return cat.reset_index(drop=True)


def _union_estaciones(cat: pd.DataFrame) -> str:
    """Las estaciones como tabla derivada, para no crear objetos en la BD."""
    filas = [
        f"SELECT {r.id_station} AS id_station, {r.lat} AS elat, {r.lon} AS elon"
        for r in cat.itertuples()
    ]
    return " UNION ALL ".join(filas)


def pings_en_estacion(radio_m: int = RADIO_M, cache: bool = True) -> pd.DataFrame:
    """Pings GPS de la troncal que caen dentro del disco de alguna estación.

    Prefiltra con un recuadro en grados (barato) y luego afina con distancia esférica.
    Si un ping cayera en dos discos se queda el más cercano, aunque con 150 m no ocurre.
    """
    cat = catalogo_estaciones()
    dlat = radio_m / 111_320
    dlon = radio_m / (111_320 * np.cos(np.radians(float(cat["lat"].mean()))))

    sql = f"""
        SELECT g.time,
               COALESCE(b1.id_bus, b2.id_bus) AS id_bus,
               e.id_station,
               g.speed,
               ST_Distance_Sphere(POINT(g.longitude, g.latitude), POINT(e.elon, e.elat)) AS dist_m
        FROM in_device_history_location g
        JOIN ({_union_estaciones(cat)}) e
          ON g.latitude  BETWEEN e.elat - {dlat} AND e.elat + {dlat}
         AND g.longitude BETWEEN e.elon - {dlon} AND e.elon + {dlon}
        LEFT JOIN bus b1 ON g.id_bus <> 0 AND b1.id_bus = g.id_bus - {GPS_ID_OFFSET}
        LEFT JOIN bus b2 ON g.id_bus  = 0 AND b2.id_oct = g.id_ebjdevice
        WHERE g.id_route = {TRONCAL_T1}
        HAVING dist_m <= {radio_m}
    """
    df = q(sql, cache=f"pings_estacion_{radio_m}" if cache else None)
    df["time"] = pd.to_datetime(df["time"])
    # El GPS es TIMESTAMP: viene en UTC y hay que bajarlo a hora local. El AFC no.
    df["t"] = df["time"] - pd.Timedelta(hours=6)
    df = df.dropna(subset=["id_bus"])
    df["id_bus"] = df["id_bus"].astype("int64")
    return df.sort_values(["id_bus", "t"]).reset_index(drop=True)


def pasos_de_camion(pings: pd.DataFrame, gap_min: int = GAP_VISITA_MIN) -> pd.DataFrame:
    """Agrupa pings contiguos en visitas: una fila por (unidad, estación, paso).

    Dos pings de la misma unidad en la misma estación separados por más de `gap_min`
    son visitas distintas — la unidad se fue y volvió en otra vuelta.
    """
    df = pings.sort_values(["id_bus", "id_station", "t"]).copy()
    g = df.groupby(["id_bus", "id_station"], sort=False)
    nueva = (g["t"].diff().dt.total_seconds() / 60 > gap_min) | g["t"].diff().isna()
    df["visita"] = nueva.groupby([df["id_bus"], df["id_station"]]).cumsum()

    pasos = (
        df.groupby(["id_bus", "id_station", "visita"])
        .agg(llegada=("t", "min"), salida=("t", "max"),
             pings=("t", "size"), vel_min=("speed", "min"))
        .reset_index()
    )
    pasos["parada_s"] = (pasos["salida"] - pasos["llegada"]).dt.total_seconds()
    pasos["fecha"] = pasos["llegada"].dt.date
    pasos["hora"] = pasos["llegada"].dt.hour
    return pasos.sort_values(["id_station", "llegada"]).reset_index(drop=True)


def con_sentido(pasos: pd.DataFrame, cat: pd.DataFrame) -> pd.DataFrame:
    """Marca el sentido de cada paso según si la unidad avanza o retrocede en el orden.

    `mac_station.sta_no` va de 1 (Mirador, norte) a 28 (Las Juntas, sur), así que orden
    creciente es rumbo al sur. El AFC no registra sentido, pero los pasos sí lo permiten
    inferir y sirve para saber con qué frecuencia se atiende cada dirección.
    """
    orden = cat.set_index("id_station")["orden"]
    p = pasos.sort_values(["id_bus", "llegada"]).copy()
    p["orden"] = p["id_station"].map(orden)
    d = p.groupby("id_bus")["orden"].diff()
    p["sentido"] = np.where(d > 0, "SUR", np.where(d < 0, "NORTE", None))
    p["sentido"] = p.groupby("id_bus")["sentido"].ffill().bfill()
    return p


def entradas_afc(cache: bool = True) -> pd.DataFrame:
    """Validaciones por estación y minuto, en hora local.

    `fechaHoraEvento` es DATETIME y MySQL lo guarda literal: ya viene en hora local y no
    se convierte. Se cuentan sólo los tipos de pago que representan a una persona
    entrando; recargas, ventas y errores mueven dinero, no gente.
    """
    return q(
        """
        SELECT m.id_station,
               DATE_FORMAT(t.fechaHoraEvento, '%%Y-%%m-%%d %%H:%%i:00') AS minuto,
               COUNT(*) AS entradas
        FROM transaction_1 t
        JOIN (SELECT DISTINCT id_vehicle, id_station FROM afc_station_device_total) m
          ON m.id_vehicle = t.idDispositivo
        WHERE t.idRutaEstacion = %(ruta)s
          AND t.payment_type IN (0, 1, 5, 6, 7, 23, 25, 98)
        GROUP BY m.id_station, minuto
        """,
        {"ruta": TRONCAL_T1},
        cache="entradas_afc_minuto" if cache else None,
    )


def completar_pasos(pasos: pd.DataFrame, cat: pd.DataFrame,
                    max_hueco_min: int = 25) -> pd.DataFrame:
    """Reconstruye los pasos que el GPS no alcanzó a registrar.

    Con muestreo de ~20 s una unidad rápida puede cruzar el disco de 150 m sin dejar
    ningún ping: las estaciones centrales detectan ~450 pasos/día contra ~526 vueltas,
    o sea ~86 %. Los pasos perdidos inflarían la cola estimada, porque el modelo creería
    que nadie recogió a esa gente.

    Si una unidad aparece en la estación de orden 5 y luego en la de orden 8, forzosamente
    pasó por 6 y 7: la ruta es fija y sin ramales. Se interpolan sus tiempos linealmente
    sobre el orden. Sólo se rellena cuando el hueco es compatible con marcha continua
    (`max_hueco_min`); un hueco mayor significa que la unidad salió de circulación y ahí
    no se inventa nada.

    Las filas reconstruidas se marcan con `interpolado = True` para poder medir cuánto del
    resultado descansa en ellas.
    """
    orden = cat.set_index("id_station")["orden"]
    inv = {int(v): k for k, v in orden.items()}

    p = pasos.copy()
    p["orden"] = p["id_station"].map(orden)
    p["interpolado"] = False
    p = p.sort_values(["id_bus", "llegada"])

    nuevas = []
    for id_bus, g in p.groupby("id_bus", sort=False):
        o = g["orden"].to_numpy()
        lle = g["llegada"].to_numpy()
        sal = g["salida"].to_numpy()
        for i in range(1, len(g)):
            salto = int(abs(o[i] - o[i - 1]))
            if salto <= 1:
                continue
            hueco = (lle[i] - sal[i - 1]) / np.timedelta64(1, "m")
            if not (0 < hueco <= max_hueco_min):
                continue
            paso = 1 if o[i] > o[i - 1] else -1
            faltan = list(range(int(o[i - 1]) + paso, int(o[i]), paso))
            for k, ordn in enumerate(faltan, start=1):
                t = sal[i - 1] + (lle[i] - sal[i - 1]) * (k / (salto))
                nuevas.append({
                    "id_bus": id_bus, "id_station": inv[ordn], "visita": -1,
                    "llegada": t, "salida": t, "pings": 0, "vel_min": np.nan,
                    "parada_s": 0.0, "fecha": pd.Timestamp(t).date(),
                    "hora": pd.Timestamp(t).hour, "orden": ordn, "interpolado": True,
                })

    if nuevas:
        p = pd.concat([p, pd.DataFrame(nuevas)], ignore_index=True)
    return p.sort_values(["id_station", "llegada"]).reset_index(drop=True)
