#!/usr/bin/env bash
# Carga (o recarga) los dumps de MySQL dentro del container macro-mysql.
# Uso:  bash scripts/load_dumps.sh [--reset]
#
# --reset  destruye el volumen macro_mysql_data y reconstruye desde cero.
#          La BD es derivada de ./data/*.sql, asi que no se pierde nada propio.
set -euo pipefail
cd "$(dirname "$0")/.."

MYSQL="mysql -uroot -pmacro --default-character-set=utf8mb4 integration"

if [[ "${1:-}" == "--reset" ]]; then
  echo ">> Destruyendo volumen y recreando el stack..."
  docker compose down -v
  docker compose up -d
fi

echo ">> Esperando a que MySQL este sano..."
until [ "$(docker inspect -f '{{.State.Health.Status}}' macro-mysql 2>/dev/null)" = "healthy" ]; do
  sleep 3
done

# El chico primero: son catalogos (codigo_perfil, mac_station).
for f in integration2.sql integration.sql; do
  echo ">> Importando $f ..."
  time docker compose exec -T mysql sh -c "$MYSQL < /dump/$f"
done

echo ">> Conteos:"
docker compose exec -T mysql mysql -uroot -pmacro -t integration -e "
  SELECT TABLE_NAME, TABLE_ROWS, ROUND(DATA_LENGTH/1024/1024) AS data_mb
  FROM information_schema.TABLES
  WHERE TABLE_SCHEMA='integration' ORDER BY DATA_LENGTH DESC;"
