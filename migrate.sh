#!/bin/bash
# Script de Migração MySQL → PostgreSQL
# Uso: ./migrate.sh

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
echo "🚀 Migração MySQL → PostgreSQL"
echo "============================================================"
echo ""

# 1. Backup do MySQL
echo "📦 Passo 1: Backup do MySQL..."
echo "   mysqldump -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PASSWORD \\"
echo "     --single-transaction --routines --triggers \\"
echo "     $MYSQL_DATABASE > backup_mysql_\$(date +%Y%m%d_%H%M%S).sql"
echo ""

# 2. Verificar se PostgreSQL está instalado
echo "🔍 Passo 2: Verificando PostgreSQL..."
if ! command -v psql &> /dev/null; then
    echo "   ❌ PostgreSQL não encontrado"
    echo "   Instale com: sudo pacman -S postgresql"
    exit 1
fi
echo "   ✅ PostgreSQL encontrado"
echo ""

# 3. Verificar se pgloader está instalado
echo "🔍 Passo 3: Verificando pgloader..."
if ! command -v pgloader &> /dev/null; then
    echo "   ⚠️ pgloader não encontrado"
    echo "   Instale com: sudo pacman -S pgloader"
    echo "   Ou use: yay -S pgloader"
    echo ""
    read -p "Deseja instalar pgloader agora? (s/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        yay -S pgloader --noconfirm
    else
        echo "   Instale pgloader manualmente e execute este script novamente"
        exit 1
    fi
fi
echo "   ✅ pgloader encontrado"
echo ""

# 4. Criar banco PostgreSQL
echo "🗄️ Passo 4: Criando banco PostgreSQL..."
echo "   CREATE DATABASE $PG_DATABASE;"
echo "   Ou execute:"
echo "   sudo -u postgres createdb $PG_DATABASE"
echo ""

# 5. Migração com pgloader
echo "🚀 Passo 5: Executando migração com pgloader..."
echo ""
echo "   pgloader mysql://$MYSQL_USER:$MYSQL_PASSWORD@$MYSQL_HOST/$MYSQL_DATABASE \\"
echo "     postgresql://$PG_USER@$PG_HOST:$PG_PORT/$PG_DATABASE"
echo ""

# Confirmar
read -p "Executar migração agora? (s/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo "Iniciando migração..."
    pgloader mysql://$MYSQL_USER:$MYSQL_PASSWORD@$MYSQL_HOST/$MYSQL_DATABASE \
      postgresql://$PG_USER@$PG_HOST:$PG_PORT/$PG_DATABASE

    echo ""
    echo "✅ Migração concluída!"
    echo ""
    echo "🔍 Validar migração:"
    echo "   psql -U $PG_USER -d $PG_DATABASE -c '\dt'"
    echo "   psql -U $PG_USER -d $PG_DATABASE -c 'SELECT COUNT(*) FROM areas;'"
else
    echo "Migração cancelada. Execute novamente quando estiver pronto."
fi

echo ""
echo "============================================================"
echo "📝 Notas importantes:"
echo "============================================================"
echo "1. AUTO_INCREMENT foi convertido para SERIAL/BIGSERIAL"
echo "2. Views precisam ser recriadas manualmente"
echo "3. Stored procedures/triggers precisam ser convertidos"
echo "4. Execute ANALYZE após a migração para otimizar performance"
echo "============================================================"
