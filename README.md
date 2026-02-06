# 🔄 Migração MySQL → PostgreSQL - Guia Passo a Passo

Este guia fornece instruções **completas e detalhadas** para migrar o banco de dados MySQL para PostgreSQL.

**⏱️ Tempo estimado:** 1-2 horas
**🎯 Dificuldade:** Intermediária
**✅ Status:** Banco analisado e pronto para migração

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Pré-requisitos](#pré-requisitos)
3. [Passo 1: Baixar os Arquivos](#passo-1-baixar-os-arquivos)
4. [Passo 2: Configurar Credenciais](#passo-2-configurar-credenciais)
5. [Passo 3: Instalar Dependências](#passo-3-instalar-dependências)
6. [Passo 4: Backup do MySQL](#passo-4-backup-do-mysql)
7. [Passo 5: Migração com pgloader](#passo-5-migração-com-pgloader)
8. [Passo 6: Recriar Views](#passo-6-recriar-views)
9. [Passo 7: Validação](#passo-7-validação)
10. [Passo 8: Testes Finais](#passo-8-testes-finais)
11. [Solução de Problemas](#solução-de-problemas)

---

## 📊 Visão Geral

### O que será migrado?

- **Banco de dados:** `Unico_Database`
- **Tabelas:** 27 tabelas
- **Views:** 3 views (recriadas após migração)
- **Problemas críticos:** 0 ✅
- **Avisos:** 23 (AUTO_INCREMENT → SERIAL, automático)

### Estrutura do Banco

**Gestão Estrutural:**
- Empresas, Áreas, Equipes

**Recursos Humanos:**
- Pessoas, Colaboradores, Contratações, Cargos, Níveis, Contratos

**Marketing:**
- Meta (Forms, Leads, Campanhas, Custos)
- RD Station (Deals, Funis, Usuários, Teams)

**Staging:**
- Tabelas temporárias para importação

---

## 📦 Pré-requisitos

### Sistema Operacional
- **Linux** (Arch, Ubuntu, Debian, Fedora, etc.)
- **macOS**
- **Windows** (com WSL2)

### Conhecimentos Necessários
- Comandos básicos de terminal
- Permissões sudo (para instalar pacotes)
- Acesso ao servidor MySQL

### Requisitos de Sistema
- **Espaço em disco:** 2x o tamanho do banco MySQL
- **RAM:** Mínimo 2GB (recomendado 4GB+)
- **Acesso internet:** Para baixar pacotes

---

## 🚀 Passo 1: Baixar os Arquivos

### Opção A: Clonar com Git (Recomendado)

```bash
# 1. Instalar git (se não tiver)
# Arch Linux
sudo pacman -S git

# Ubuntu/Debian
sudo apt install git

# Fedora
sudo dnf install git

# 2. Clonar o repositório
git clone https://github.com/niamwite/migracao-chico.git

# 3. Entrar no diretório
cd migracao-chico

# 4. Listar os arquivos
ls -lh
```

**Arquivos que você deve ver:**
```
✅ migrate.sh              - Script principal de migração
✅ validate_migration.sh   - Script de validação
✅ views_postgresql.sql    - Views para recriar
✅ README.md               - Este guia
✅ migration_report.md     - Relatório detalhado da análise
```

### Opção B: Baixar ZIP (Sem Git)

```bash
# 1. Baixar o arquivo
wget https://github.com/niamwite/migracao-chico/archive/refs/heads/main.zip

# 2. Descompactar
unzip main.zip

# 3. Entrar no diretório
cd migracao-chico-main
```

### Opção C: Baixar Arquivos Individuais

```bash
# Criar diretório
mkdir migracao-chico
cd migracao-chico

# Baixar os arquivos principais
wget https://raw.githubusercontent.com/niamwite/migracao-chico/main/migrate.sh
wget https://raw.githubusercontent.com/niamwite/migracao-chico/main/validate_migration.sh
wget https://raw.githubusercontent.com/niamwite/migracao-chico/main/views_postgresql.sql

# Dar permissão de execução
chmod +x migrate.sh validate_migration.sh
```

### ✅ Verificar Download

```bash
# Verificar se os arquivos foram baixados
ls -lh *.sh *.sql

# Deve mostrar:
# -rwxr-xr-x migrate.sh
# -rwxr-xr-x validate_migration.sh
# -rw-r--r-- views_postgresql.sql
```

---

## 🔐 Passo 2: Configurar Credenciais

**IMPORTANTE:** Por segurança, use **variáveis de ambiente** para senhas.

### 2.1 Configurar Variáveis de Ambiente

```bash
# Edite as variáveis abaixo com SEUS dados
export MYSQL_HOST="seu_host_mysql"        # Ex: 192.168.1.100
export MYSQL_USER="seu_usuario_mysql"      # Ex: willkoga
export MYSQL_PASSWORD="sua_senha_mysql"     # Ex: MinhaSenha123
export MYSQL_DATABASE="Unico_Database"

# PostgreSQL (configure se necessário)
export PG_HOST="localhost"
export PG_PORT="5432"
export PG_USER="postgres"
export PG_DATABASE="Unico_Database"
```

### 2.2 Tornar Persistente (Opcional)

```bash
# Adicionar ao ~/.bashrc
echo 'export MYSQL_HOST="seu_host_mysql"' >> ~/.bashrc
echo 'export MYSQL_USER="seu_usuario_mysql"' >> ~/.bashrc
echo 'export MYSQL_PASSWORD="sua_senha_mysql"' >> ~/.bashrc

# Recarregar o arquivo
source ~/.bashrc
```

### 2.3 Verificar Configuração

```bash
# Verificar se as variáveis estão configuradas
echo "Host: $MYSQL_HOST"
echo "User: $MYSQL_USER"
echo "Password: ${MYSQL_PASSWORD:0:3}..."  # Mostra só os 3 primeiros caracteres
echo "Database: $MYSQL_DATABASE"

# Deve mostrar seus valores, não vazio
```

---

## 📥 Passo 3: Instalar Dependências

### 3.1 Instalar Cliente PostgreSQL

```bash
# Arch Linux / Manjaro
sudo pacman -S postgresql postgresql-clients

# Ubuntu / Debian
sudo apt update
sudo apt install postgresql postgresql-client

# Fedora / CentOS
sudo dnf install postgresql postgresql-server

# macOS (Homebrew)
brew install postgresql
```

### 3.2 Instalar pgloader (Ferramenta de Migração)

```bash
# Arch Linux / Manjaro
sudo pacman -S pgloader

# Ou com yay (AUR)
yay -S pgloader

# Ubuntu / Debian
sudo apt install pgloader

# Fedora / CentOS
sudo dnf install pgloader

# macOS (Homebrew)
brew install pgloader
```

### 3.3 Iniciar PostgreSQL (Primeira vez)

```bash
# Arch Linux
sudo -u postgres initdb -D /var/lib/postgres/data
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Ubuntu / Debian
sudo service postgresql start

# Fedora
sudo systemctl start postgresql
sudo systemctl enable postgresql

# macOS
brew services start postgresql
```

### 3.4 Configurar Senha do PostgreSQL (Opcional)

```bash
# Acessar o PostgreSQL
sudo -u postgres psql

# No prompt do psql, digite:
ALTER USER postgres PASSWORD 'nova_senha';
\q

# Voltar ao terminal normal
```

### 3.5 Criar Banco PostgreSQL Vazio

```bash
# Criar o banco de dados
sudo -u postgres createdb $PG_DATABASE

# Verificar se foi criado
sudo -u postgres psql -l | grep Unico_Database

# Deve mostrar:
# Unico_Database | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 |
```

### 3.6 Verificar Instalações

```bash
# Verificar PostgreSQL
psql --version
# Deve mostrar: psql (PostgreSQL) 15.x ou similar

# Verificar pgloader
pgloader --version
# Deve mostrar: pgloader version 3.x.x

# Verificar cliente MySQL
mysql --version
# Deve mostrar: mysql  Ver 8.x.x ou similar
```

---

## 💾 Passo 4: Backup do MySQL

**⚠️ NUNCA pule o backup!**

### 4.1 Criar Diretório de Backup

```bash
mkdir -p backups
cd backups
```

### 4.2 Fazer Backup Completo

```bash
# Backup com data/hora
mysqldump -h $MYSQL_HOST \
          -u $MYSQL_USER \
          -p$MYSQL_PASSWORD \
          --single-transaction \
          --routines \
          --triggers \
          --all-databases > backup_completo_$(date +%Y%m%d_%H%M%S).sql

# Verifique se o arquivo foi criado
ls -lh backup_*.sql
```

### 4.3 Backup Apenas do Banco Unico_Database

```bash
mysqldump -h $MYSQL_HOST \
          -u $MYSQL_USER \
          -p$MYSQL_PASSWORD \
          --single-transaction \
          --routines \
          --triggers \
          $MYSQL_DATABASE > backup_unico_$(date +%Y%m%d_%H%M%S).sql
```

### 4.4 Comprimir Backup (Opcional)

```bash
# Comprimir com gzip
gzip backup_unico_$(date +%Y%m%d_%H%M%S).sql

# Verificar tamanho
ls -lh backup_*.sql.gz
```

### 4.5 Testar Backup

```bash
# Verificar se o arquivo não está corrompido
gunzip -t backup_unico_*.sql.gz

# Ou ver as primeiras linhas
head -20 backup_unico_*.sql
```

### ✅ Confirmar Backup

```bash
# Deve mostrar pelo menos 1 arquivo
ls -lh backups/
```

---

## 🚀 Passo 5: Migração com pgloader

### 5.1 Usar o Script Automatizado (Recomendado)

```bash
# Voltar ao diretório principal
cd ..

# Executar o script de migração
./migrate.sh
```

**O script fará:**
1. ✅ Verificar se PostgreSQL está instalado
2. ✅ Verificar se pgloader está instalado
3. ✅ Mostrar o comando de backup
4. ✅ Executar a migração
5. ✅ Validar o resultado

### 5.2 Migração Manual (Alternativa)

```bash
# Comando básico
pgloader mysql://$MYSQL_USER:$MYSQL_PASSWORD@$MYSQL_HOST/$MYSQL_DATABASE \
  postgresql://$PG_USER@$PG_HOST:$PG_PORT/$PG_DATABASE

# Com verbose para ver detalhes
pgloader --verbose \
  mysql://$MYSQL_USER:$MYSQL_PASSWORD@$MYSQL_HOST/$MYSQL_DATABASE \
  postgresql://$PG_USER@$PG_HOST:$PG_PORT/$PG_DATABASE

# Salvar log em arquivo
pgloader --verbose \
  mysql://$MYSQL_USER:$MYSQL_PASSWORD@$MYSQL_HOST/$MYSQL_DATABASE \
  postgresql://$PG_USER@$PG_HOST:$PG_PORT/$PG_DATABASE \
  > migration_log.txt 2>&1
```

### 5.3 O que Acontece Durante a Migração?

```
┌─────────────────────────────────────────┐
│  1. Conecta ao MySQL                    │
│  2. Lê esquema do banco                 │
│  3. Converte tipos de dados             │
│  4. Cria tabelas no PostgreSQL          │
│  5. Migra os dados (INSERT/COPY)        │
│  6. Cria índices                        │
│  7. Cria constraints (FK, PK, UNIQUE)   │
│  8. Gera relatório final                │
└─────────────────────────────────────────┘
```

### 5.4 Exemplo de Output Esperado

```
* summary of successful load:
     Table name     |   errors | rows  |    bytes  | total time | insert time |
                   |          |       |           |            |             ...
-------------------+----------+-------+-----------+------------+-------------
 areas             |        0 |    10 |     1.2KB |      0.05s |       0.02s |
 empresas          |        0 |     5 |   800.0B  |      0.04s |       0.01s |
 rh_colaboradores  |        0 |   150 |    25.6KB |      0.15s |       0.08s |
                   |          |       |           |            |
-------------------+----------+-------+-----------+------------+-------------
Total import time  |          |   165 |    27.6KB |      0.24s |
```

### 5.5 Verificar se Migração Funcionou

```bash
# Conectar ao PostgreSQL
sudo -u postgres psql -d $PG_DATABASE

# Listar tabelas
\dt

# Deve mostrar 27 tabelas (excluindo views)
```

### ⚠️ Se Der Erro?

Veja a seção [Solução de Problemas](#solução-de-problemas) abaixo.

---

## 👁️ Passo 6: Recriar Views

As views não são migradas automaticamente. Precisam ser recriadas.

### 6.1 Usar o Script SQL

```bash
# Conectar ao PostgreSQL e executar o script
sudo -u postgres psql -d $PG_DATABASE -f views_postgresql.sql
```

### 6.2 Verificar se Views Foram Criadas

```bash
# Conectar ao banco
sudo -u postgres psql -d $PG_DATABASE

# Listar views
\dv

# Deve mostrar:
//          Lista de relações
//  Schema  |       Nome        |   Tipo   |   Dono
// ----------+-------------------+----------+----------
//  public   | vw_areas          | view     | postgres
//  public   | vw_equipes        | view     | postgres
//  public   | vw_rh_colaborador | view     | postgres
```

### 6.3 Testar as Views

```bash
# Testar vw_Areas
sudo -u postgres psql -d $PG_DATABASE -c "SELECT * FROM vw_Areas LIMIT 5;"

# Testar vw_Equipes
sudo -u postgres psql -d $PG_DATABASE -c "SELECT * FROM vw_Equipes LIMIT 5;"

# Testar vw_RH_Colaborador_Atual
sudo -u postgres psql -d $PG_DATABASE -c "SELECT * FROM vw_RH_Colaborador_Atual LIMIT 5;"
```

---

## ✅ Passo 7: Validação

### 7.1 Usar o Script de Validação (Recomendado)

```bash
# Executar validação
./validate_migration.sh
```

**O que o script faz:**
1. Conta tabelas no MySQL
2. Conta tabelas no PostgreSQL
3. Compara contagem de registros por tabela
4. Mostra quais tabelas têm diferenças

### 7.2 Validação Manual

```bash
# Conectar ao PostgreSQL
sudo -u postgres psql -d $PG_DATABASE

# Contar tabelas
SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';
# Deve retornar: 27

# Verificar tamanho do banco
SELECT pg_size_pretty(pg_database_size('$PG_DATABASE'));

# Contar registros em algumas tabelas
SELECT 'areas' as tabela, COUNT(*) as total FROM areas
UNION ALL
SELECT 'empresas', COUNT(*) FROM empresas
UNION ALL
SELECT 'rh_colaboradores', COUNT(*) FROM rh_colaboradores;

# Sair do psql
\q
```

### 7.3 Comparar com MySQL

```bash
# Contar no MySQL
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PASSWORD -D $MYSQL_DATABASE -e "
SELECT 'areas' as tabela, COUNT(*) as total FROM areas
UNION ALL
SELECT 'empresas', COUNT(*) FROM empresas
UNION ALL
SELECT 'rh_colaboradores', COUNT(*) FROM rh_colaboradores;
"
```

### 7.4 Otimizar PostgreSQL

```bash
# Conectar ao PostgreSQL
sudo -u postgres psql -d $PG_DATABASE

# Analisar tabelas para otimizar queries
ANALYZE;

# Reclaim space e atualizar estatísticas
VACUUM ANALYZE;

# Sair
\q
```

---

## 🧪 Passo 8: Testes Finais

### 8.1 Testar Conexão via Aplicação

Se você tem uma aplicação que usa o banco:

```python
# Exemplo Python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="Unico_Database",
    user="postgres",
    password="sua_senha"
)

cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM areas")
print(cursor.fetchone())
```

```php
// Exemplo PHP
$conn = pg_connect("host=localhost dbname=Unico_Database user=postgres");
$result = pg_query($conn, "SELECT COUNT(*) FROM areas");
print_r(pg_fetch_assoc($result));
```

### 8.2 Testar Queries Comuns

```bash
# Conectar ao PostgreSQL
sudo -u postgres psql -d $PG_DATABASE

# Testar JOIN
SELECT e.EMPRESA_NOME, a.AREA_NOME, eq.NOME_EQUIPE
FROM Empresas e
JOIN Areas a ON e.ID = a.ID_EMPRESA
JOIN Equipes eq ON a.ID = eq.ID_AREA
LIMIT 10;

# Testar agregação
SELECT
    e.EMPRESA_NOME,
    COUNT(c.ID_COLABORADOR) as total_colaboradores
FROM Empresas e
LEFT JOIN RH_Colaboradores c ON e.ID = c.ID_EMPRESA
GROUP BY e.EMPRESA_NOME;

# Testar view
SELECT * FROM vw_RH_Colaborador_Atual WHERE STATUS = 'ATIVO';

# Sair
\q
```

### 8.3 Performance Test

```bash
# Medir tempo de query
time sudo -u postgres psql -d $PG_DATABASE -c "
SELECT COUNT(*) FROM RH_Colaboradores
WHERE ID_EMPRESA IN (SELECT ID FROM Empresas);
"
```

---

## 🔧 Solução de Problemas

### Problema 1: "command not found: pgloader"

**Solução:**
```bash
# Arch Linux
sudo pacman -S pgloader

# Ubuntu/Debian
sudo apt install pgloader

# Ou compilar do código fonte
# https://github.com/dimitri/pgloader#building-pgloader
```

### Problema 2: "connection refused" no PostgreSQL

**Solução:**
```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Iniciar se não estiver
sudo systemctl start postgresql

# Verificar se a porta está correta
sudo netstat -tlnp | grep 5432
```

### Problema 3: Erro de autenticação PostgreSQL

**Solução:**
```bash
# Editar pg_hba.conf
sudo nano /var/lib/postgres/data/pg_hba.conf  # Arch
# ou
sudo nano /etc/postgresql/15/main/pg_hba.conf  # Ubuntu

# Alterar:
# local   all             postgres                                peer
# Para:
# local   all             postgres                                trust

# Reiniciar PostgreSQL
sudo systemctl restart postgresql
```

### Problema 4: "database is being accessed by other users"

**Solução:**
```bash
# Matar todas as conexões do banco
sudo -u postgres psql -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'Unico_Database'
AND pid <> pg_backend_pid();
"
```

### Problema 5: Diferença na contagem de registros

**Solução:**
```bash
# Verificar qual tabela tem diferença
./validate_migration.sh

# Se a diferença for pequena, pode ser transação em andamento
# Verifique se não há inserts/updates durante a migração

# Migrar novamente a tabela específica
pgloader --verbose \
  --only-table 'nome_tabela' \
  mysql://$MYSQL_USER:$MYSQL_PASSWORD@$MYSQL_HOST/$MYSQL_DATABASE \
  postgresql://$PG_USER@$PG_HOST:$PG_PORT/$PG_DATABASE
```

### Problema 6: Tipo de dados não suportado

**Solução:**
```bash
# Verificar o relatório do pgloader
cat migration_log.txt | grep -i error

# Converter manualmente a tabela problemática
sudo -u postgres psql -d $PG_DATABASE

# Alterar tipo de dado
ALTER TABLE nome_tabela
ALTER COLUMN nome_coluna TYPE novo_tipo;
```

### Problema 7: Espaço insuficiente em disco

**Solução:**
```bash
# Verificar espaço disponível
df -h

# Limpar cache de pacotes (Arch)
sudo pacman -Sc

# Limpar logs antigos
sudo journalctl --vacuum-time=7d

# Ou migrar tabela por tabela
pgloader --with "on error stop" \
  --only-table 'tabela1' \
  mysql://$MYSQL_USER:$MYSQL_PASSWORD@$MYSQL_HOST/$MYSQL_DATABASE \
  postgresql://$PG_USER@$PG_HOST:$PG_PORT/$PG_DATABASE
```

---

## 📚 Comandos Úteis PostgreSQL

### Conectar ao Banco

```bash
# Conectar ao banco específico
sudo -u postgres psql -d Unico_Database

# Conectar com usuário específico
psql -U postgres -d Unico_Database -h localhost

# Conectar via string de conexão
psql "postgresql://postgres@localhost:5432/Unico_Database"
```

### Comandos Interativos

```sql
-- Listar tabelas
\dt

-- Listar views
\dv

-- Descrever tabela
\d nome_tabela

-- Listar todos os bancos
\l

-- Sair
\q

-- Ajuda
\?
```

### Queries Úteis

```sql
-- Tamanho das tabelas
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Encontrar tabelas sem índices
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
AND tablename NOT IN (SELECT DISTINCT tablename FROM pg_indexes WHERE schemaname = 'public');

-- Conexões ativas
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query_start,
    state_change
FROM pg_stat_activity
WHERE datname = 'Unico_Database';

-- Matar conexão
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'Unico_Database'
AND pid = 12345;  -- substituir pelo PID
```

---

## 🎯 Checklist Final

Antes de considerar a migração concluída:

### ✅ Migração Completa

- [ ] Backup do MySQL realizado e testado
- [ ] PostgreSQL instalado e rodando
- [ ] pgloader instalado
- [ ] Migração executada sem erros críticos
- [ ] Todas as 27 tabelas migradas
- [ ] Todas as 3 views recriadas
- [ ] Validação executada (0 divergências)
- [ ] ANALYZE e VACUUM executados

### ✅ Testes Realizados

- [ ] Queries simples funcionando
- [ ] Queries com JOIN funcionando
- [ ] Views funcionando
- [ ] Aplicação conectada (se aplicável)
- [ ] Performance aceitável

### ✅ Documentação

- [ ] Credenciais salvas em local seguro
- [ ] Novas credenciais PostgreSQL documentadas
- [ ] Strings de conexão da aplicação atualizadas
- [ ] Equipe notificada sobre a mudança

### ✅ Contingência

- [ ] Backup MySQL guardado por 30 dias
- [ ] MySQL mantido rodando em modo read-only por 7 dias
- [ ] Plano de rollback documentado
- [ ] Monitoramento configurado

---

## 📖 Referências

- [pgloader Documentation](http://pgloader.io/)
- [PostgreSQL Official Docs](https://www.postgresql.org/docs/)
- [MySQL to PostgreSQL Wiki](https://wiki.postgresql.org/wiki/Converting_from_other_Databases_to_PostgreSQL)

---

## 📞 Suporte

**Data da Análise:** 06/02/2026
**Repositório:** https://github.com/niamwite/migracao-chico
**Relatório Completo:** Veja `migration_report.md` para análise detalhada

---

## 🎉 Próximos Passos

Após a migração completa:

1. **Monitoramento:** Configure alertas de performance
2. **Otimização:** Crie índices adicionais se necessário
3. **Documentação:** Atualize documentação interna
4. **Treinamento:** Treine a equipe no PostgreSQL
5. **Limpeza:** Após 30 dias, pode desligar o MySQL

**Boa sorte com a migração! 🚀**
