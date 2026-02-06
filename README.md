# 🔄 Migração MySQL → PostgreSQL - Guia Completo

## 📊 Análise do Banco de Dados

### ✅ Status: **PODE SER MIGRADO**

O banco de dados MySQL foi analisado e **pode ser convertido** para PostgreSQL com sucesso!

### Estatísticas

| Item | Quantidade |
|------|------------|
| Bancos de Dados | 1 (`Unico_Database`) |
| Tabelas | 27 |
| Views | 3 |
| Problemas Críticos | **0** ✅ |
| Avisos | 23 (menores, resolúveis automaticamente) |

## 📁 Estrutura do Banco

### Tabelas Principais

**Gestão Estrutural:**
- `Empresas` - Dados das empresas
- `Areas` - Áreas das empresas
- `Equipes` - Equipes de trabalho

**Recursos Humanos:**
- `RH_Pessoas` - Pessoas cadastradas
- `RH_Colaboradores` - Colaboradores ativos
- `RH_Contratacoes` - Histórico de contratações
- `RH_Cargos` - Cargos disponíveis
- `RH_Niveis` - Níveis hierárquicos
- `RH_Contratos` - Tipos de contratos
- `RH_Contratacoes_Motivos` - Motivos de saída
- `RH_Cargo_Regras` - Regras de cargos

**Marketing - Meta:**
- `Meta_Forms` - Formulários Meta
- `Meta_Leads` - Leads gerados
- `Marketing_Meta_Campanhas` - Campanhas publicitárias
- `Marketing_Meta_Costs` - Custos de marketing

**Marketing - RD Station:**
- `Marketing_RD_DealsInProgress` - Negócios em andamento
- `Marketing_RD_DealsWin` - Negócios ganhos
- `Marketing_RD_DealsLost` - Negócios perdidos
- `Marketing_RD_Funis` - Funis de vendas
- `Marketing_RD_EtapasFunil` - Etapas do funil
- `Marketing_RD_Users` - Usuários RD Station
- `Marketing_RD_Teams` - Equipes RD Station

**Staging:**
- `stg_RH_Colaboradores` - Área de staging para colaboradores
- `stg_RH_Cargo_Regras` - Área de staging para regras

**Views:**
- `vw_Areas` - View de áreas com empresas
- `vw_Equipes` - View de equipes com áreas/empresas
- `vw_RH_Colaborador_Atual` - View de colaboradores ativos

## ⚠️ Avisos Encontrados

Todos os 23 avisos são sobre colunas `AUTO_INCREMENT` que no PostgreSQL usam `SERIAL` ou `BIGSERIAL`. Isso é resolvido **automaticamente** pelo pgloader.

**Exemplo:**
- MySQL: `ID int(10) unsigned AUTO_INCREMENT`
- PostgreSQL: `ID integer SERIAL PRIMARY KEY`

## 🚀 Método de Migração Recomendado

### Opção 1: pgloader (Recomendado ✅)

**Vantagens:**
- Automático e confiável
- Trata tipos, índices e constraints
- Converte AUTO_INCREMENT para SERIAL
- Preserva dados
- Relatório detalhado de erros

**Instalação:**
```bash
# Arch Linux
sudo pacman -S pgloader
# ou
yay -S pgloader
```

**Comando de migração:**
```bash
pgloader mysql://willkoga:Sucesso2026@46.62.152.123/Unico_Database \
  postgresql://postgres@localhost:5432/Unico_Database
```

**Com options avançadas:**
```bash
pgloader --verbose \
  --cast-rule-typename "auto_increment to serial" \
  mysql://willkoga:Sucesso2026@46.62.152.123/Unico_Database \
  postgresql://postgres@localhost:5432/Unico_Database
```

### Opção 2: Script Python (mysql2pgsql)

```bash
pip install mysql2pgsql

mysql2pgsql \
  -u willkoga \
  -p Sucesso2026 \
  -h 46.62.152.123 \
  -d Unico_Database \
  -f migration_script.sql
```

### Opção 3: Migração Manual via Dump

```bash
# 1. Backup MySQL
mysqldump -h 46.62.152.123 -u willkoga -p \
  --single-transaction \
  --routines \
  --triggers \
  Unico_Database > mysql_dump.sql

# 2. Converter dump (ferramentas online ou scripts)
# 3. Importar no PostgreSQL
psql -U postgres -d Unico_Database < converted_dump.sql
```

## 📋 Checklist de Migração

### Pré-Migração

- [ ] Fazer backup completo do MySQL
- [ ] Instalar PostgreSQL
- [ ] Instalar pgloader
- [ ] Criar banco PostgreSQL vazio
- [ ] Testar conexão com ambos os bancos
- [ ] Verificar espaço em disco

### Migração

- [ ] Executar pgloader
- [ ] Verificar relatório de erros
- [ ] Validar contagem de registros
- [ ] Verificar índices criados
- [ ] Recriar views manualmente
- [ ] Recriar stored procedures/triggers

### Pós-Migração

- [ ] Executar `ANALYZE` no PostgreSQL
- [ ] Testar aplicação conectada ao PostgreSQL
- [ ] Validar dados críticos
- [ ] Performance tuning
- [ ] Atualizar strings de conexão na aplicação
- [ ] Manter backup do MySQL por período seguro

## 🔧 Tarefas Manuais Necessárias

### 1. Recriar Views

As 3 views precisam ser recriadas manualmente no PostgreSQL:

```sql
-- Exemplo: vw_Areas
CREATE VIEW vw_Areas AS
SELECT
    a.ID,
    a.AREA_NOME,
    a.ID_EMPRESA,
    e.EMPRESA_NOME
FROM Areas a
JOIN Empresas e ON a.ID_EMPRESA = e.ID;
```

**Veja o código completo das views no arquivo `views_postgresql.sql`**

### 2. Stored Procedures e Triggers

O banco analisado não tem stored procedures visíveis, mas se houverem, precisam ser convertidas manualmente.

### 3. Performance Tuning

Após a migração:

```sql
-- Analisar tabelas para otimizar queries
ANALYZE;

-- Vacuum para reclaim space
VACUUM ANALYZE;

-- Verificar tamanho das tabelas
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## 🛡️ Backup e Rollback

### Backup MySQL

```bash
# Backup completo
mysqldump -h 46.62.152.123 -u willkoga -p \
  --single-transaction \
  --routines \
  --triggers \
  --all-databases > backup_completo_$(date +%Y%m%d).sql

# Backup apenas do banco Unico_Database
mysqldump -h 46.62.152.123 -u willkoga -p \
  --single-transaction \
  --routines \
  --triggers \
  Unico_Database > backup_unico_$(date +%Y%m%d).sql
```

### Rollback (se necessário)

```bash
# Dropar banco PostgreSQL e重新começar
psql -U postgres -c "DROP DATABASE Unico_Database;"
psql -U postgres -c "CREATE DATABASE Unico_Database;"

# Ou restaurar do backup MySQL
mysql -h 46.62.152.123 -u willkoga -p Unico_Database < backup_unico.sql
```

## 📊 Mapeamento de Tipos MySQL → PostgreSQL

| MySQL | PostgreSQL | Observação |
|-------|------------|------------|
| TINYINT | SMALLINT | ✅ Direto |
| SMALLINT | SMALLINT | ✅ Direto |
| INT/INTEGER | INTEGER | ✅ Direto |
| BIGINT | BIGINT | ✅ Direto |
| DECIMAL(m,d) | NUMERIC(m,d) | ✅ Direto |
| VARCHAR(n) | VARCHAR(n) | ✅ Direto |
| CHAR(n) | CHAR(n) | ✅ Direto |
| TEXT/LONGTEXT | TEXT | ✅ Direto |
| DATE | DATE | ✅ Direto |
| DATETIME | TIMESTAMP | ⚠️ Verificar fuso horário |
| TIMESTAMP | TIMESTAMP | ✅ Direto |
| BLOB/BINARY | BYTEA | ✅ Direto |
| JSON | JSONB | ✅ Melhor no PostgreSQL |

## 🚦 Comandos Úteis PostgreSQL

```sql
-- Listar tabelas
\dt

-- Estrutura da tabela
\d nome_tabela

-- Contagem de registros
SELECT COUNT(*) FROM nome_tabela;

-- Tamanho do banco
SELECT pg_size_pretty(pg_database_size('Unico_Database'));

-- Índices de uma tabela
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'nome_tabela';

-- Conexões ativas
SELECT count(*) FROM pg_stat_activity WHERE datname = 'Unico_Database';

-- Kill connection
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'Unico_Database';
```

## 📚 Referências

- [pgloader Documentation](http://pgloader.io/)
- [PostgreSQL Migration Guide](https://www.postgresql.org/docs/current/migration.html)
- [MySQL to PostgreSQL Migration](https://wiki.postgresql.org/wiki/Converting_from_other_Databases_to_PostgreSQL)

## 🎯 Conclusão

✅ **O banco pode ser migrado com segurança usando pgloader**

**Estimativa de tempo:**
- Preparação: 30 minutos
- Migração (pgloader): 5-15 minutos
- Validação: 30 minutos
- Total: **~1-2 horas**

**Risco:** Baixo - pgloader é ferramenta madura e testada

---

**Data da Análise:** 06/02/2026
**Arquivo de Relatório Completo:** `migration_report.md`
**Script de Migração:** `migrate.sh`
