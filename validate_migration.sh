#!/bin/bash
# Script de Validação de Migração MySQL → PostgreSQL
# Compara contagem de registros e estrutura entre os bancos

set -e

# Configurações
MYSQL_HOST="46.62.152.123"
MYSQL_USER="willkoga"
MYSQL_PASSWORD="Sucesso2026"
MYSQL_DATABASE="Unico_Database"

PG_HOST="localhost"
PG_PORT="5432"
PG_USER="postgres"
PG_DATABASE="Unico_Database"

echo "============================================================"
echo "🔍 Validação de Migração MySQL → PostgreSQL"
echo "============================================================"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para contar tabelas MySQL
count_mysql_tables() {
    mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PASSWORD -D $MYSQL_DATABASE -N -e "
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = '$MYSQL_DATABASE'
        AND table_type = 'BASE TABLE';
    " 2>/dev/null
}

# Função para contar tabelas PostgreSQL
count_pg_tables() {
    psql -h $PG_HOST -p $PG_PORT -U $PG_USER -d $PG_DATABASE -t -c "
        SELECT COUNT(*)
        FROM pg_tables
        WHERE schemaname = 'public';
    " 2>/dev/null | xargs
}

# Função para obter lista de tabelas MySQL
get_mysql_tables() {
    mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PASSWORD -D $MYSQL_DATABASE -N -e "SHOW TABLES;" 2>/dev/null | grep -v "^vw_"
}

# Função para contar registros em tabela MySQL
count_mysql_rows() {
    local table=$1
    mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PASSWORD -D $MYSQL_DATABASE -N -e "SELECT COUNT(*) FROM $table;" 2>/dev/null
}

# Função para contar registros em tabela PostgreSQL
count_pg_rows() {
    local table=$1
    psql -h $PG_HOST -p $PG_PORT -U $PG_USER -d $PG_DATABASE -t -c "SELECT COUNT(*) FROM $table;" 2>/dev/null | xargs
}

# Início da validação
echo "📊 Comparando Estrutura dos Bancos"
echo "=================================="
echo ""

# Contar tabelas
MYSQL_TABLES=$(count_mysql_tables)
PG_TABLES=$(count_pg_tables)

echo -e "Tabelas MySQL: ${GREEN}$MYSQL_TABLES${NC}"
echo -e "Tabelas PostgreSQL: ${GREEN}$PG_TABLES${NC}"

if [ "$MYSQL_TABLES" -eq "$PG_TABLES" ]; then
    echo -e "${GREEN}✅ OK${NC}: Número de tabelas coincide"
else
    echo -e "${RED}❌ ERRO${NC}: Diferença no número de tabelas!"
fi

echo ""
echo "📊 Comparando Registros por Tabela"
echo "=================================="
echo ""

# Obter tabelas e comparar
TABLES=$(get_mysql_tables)
TOTAL_DIFF=0

for table in $TABLES; do
    MYSQL_COUNT=$(count_mysql_rows "$table")
    PG_COUNT=$(count_pg_rows "$table")

    if [ "$MYSQL_COUNT" -eq "$PG_COUNT" ]; then
        echo -e "${GREEN}✅${NC} $table: $MYSQL_COUNT registros"
    else
        DIFF=$((PG_COUNT - MYSQL_COUNT))
        TOTAL_DIFF=$((TOTAL_DIFF + DIFF))
        echo -e "${RED}❌${NC} $table: MySQL=$MYSQL_COUNT, PG=$PG_COUNT (diferença: $DIFF)"
    fi
done

echo ""
echo "📊 Resumo"
echo "========"
echo ""

if [ "$TOTAL_DIFF" -eq 0 ]; then
    echo -e "${GREEN}✅ Migração bem-sucedida!${NC} Todos os registros foram migrados corretamente."
    exit 0
else
    echo -e "${YELLOW}⚠️ Atenção:${NC} Diferença total de $TOTAL_DIFF registros encontrada."
    echo "   Revise as tabelas marcadas com ❌ acima."
    exit 1
fi
