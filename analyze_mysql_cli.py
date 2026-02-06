#!/usr/bin/env python3
"""
Script para analisar banco de dados MySQL e planejar migração para PostgreSQL
Versão que usa o cliente mysql via CLI (sem dependências Python externas)
"""

import subprocess
import json
import sys
from typing import List, Dict, Any

# Configurações de conexão
MYSQL_HOST = '46.62.152.123'
MYSQL_USER = 'willkoga'
MYSQL_PASSWORD = 'Sucesso2026'

# Mapeamento de tipos MySQL para PostgreSQL
TYPE_MAPPINGS = {
    'tinyint': 'smallint',
    'smallint': 'smallint',
    'mediumint': 'integer',
    'int': 'integer',
    'integer': 'integer',
    'bigint': 'bigint',
    'decimal': 'numeric',
    'numeric': 'numeric',
    'float': 'real',
    'double': 'double precision',
    'char': 'char',
    'varchar': 'varchar',
    'tinytext': 'text',
    'text': 'text',
    'mediumtext': 'text',
    'longtext': 'text',
    'binary': 'bytea',
    'varbinary': 'bytea',
    'tinyblob': 'bytea',
    'blob': 'bytea',
    'mediumblob': 'bytea',
    'longblob': 'bytea',
    'date': 'date',
    'datetime': 'timestamp',
    'timestamp': 'timestamp',
    'time': 'time',
    'year': 'integer',
    'bool': 'boolean',
    'boolean': 'boolean',
    'json': 'jsonb',
}

PROBLEMATIC_TYPES = {
    'enum': 'ENUM não existe nativamente no PostgreSQL - usar VARCHAR com CHECK ou tipo ENUM customizado',
    'set': 'SET não existe no PostgreSQL - usar array ou VARCHAR',
    'year': 'YEAR não existe no PostgreSQL - usar INTEGER',
}


def run_mysql_query(query: str, database: str = None) -> List[Dict]:
    """Executa query usando cliente mysql via CLI"""
    cmd = ['mysql', '-h', MYSQL_HOST, '-u', MYSQL_USER, f'-p{MYSQL_PASSWORD}']

    if database:
        cmd.extend(['-D', database])

    cmd.extend(['-e', query, '-B', '--skip-column-names'])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print(f"⚠️ Erro na query: {result.stderr}")
            return []

        # Parse output
        lines = result.stdout.strip().split('\n')
        if not lines or lines[0] == '':
            return []

        # Dividir linhas por tab
        data = []
        for line in lines:
            if line.strip():
                data.append(line.split('\t'))

        return data

    except FileNotFoundError:
        print("✗ Cliente mysql não encontrado!")
        print("\nInstale com:")
        print("  sudo pacman -S mysql-clients")
        print("  ou")
        print("  paru -S mysql-clients")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("✗ Timeout na conexão MySQL")
        sys.exit(1)


def get_databases() -> List[str]:
    """Lista todos os bancos de dados"""
    print("📊 Buscando bancos de dados...")
    result = run_mysql_query("SHOW DATABASES")

    if not result:
        return []

    databases = [row[0] for row in result]

    # Filtrar bancos do sistema
    system_dbs = ['information_schema', 'performance_schema', 'mysql', 'sys']
    databases = [d for d in databases if d not in system_dbs]

    return databases


def analyze_database(database: str) -> Dict[str, Any]:
    """Analisa um banco de dados específico"""
    analysis = {
        'name': database,
        'tables': {},
        'total_tables': 0,
        'issues': [],
        'warnings': []
    }

    # Obter tabelas
    tables_result = run_mysql_query("SHOW TABLES", database)
    if not tables_result:
        return analysis

    tables = [row[0] for row in tables_result]
    analysis['total_tables'] = len(tables)

    # Analisar cada tabela
    for table in tables:
        table_analysis = analyze_table(database, table)
        analysis['tables'][table] = table_analysis

        if table_analysis['issues']:
            analysis['issues'].extend([
                f"{table}: {issue}" for issue in table_analysis['issues']
            ])
        if table_analysis['warnings']:
            analysis['warnings'].extend([
                f"{table}: {warning}" for warning in table_analysis['warnings']
            ])

    return analysis


def analyze_table(database: str, table: str) -> Dict[str, Any]:
    """Analisa uma tabela específica"""
    table_info = {
        'name': table,
        'columns': [],
        'primary_key': None,
        'foreign_keys': [],
        'indexes': [],
        'issues': [],
        'warnings': []
    }

    # Obter colunas
    columns_result = run_mysql_query(f"DESCRIBE `{table}`", database)

    for col in columns_result:
        col_name = col[0]
        col_type = col[1]
        nullable = col[2] == 'YES'
        default = col[4] if len(col) > 4 else None
        extra = col[5] if len(col) > 5 else None

        # Extrair tipo base
        base_type, params = extract_type_info(col_type)

        # Verificar problemas
        if base_type.lower() in PROBLEMATIC_TYPES:
            table_info['issues'].append(
                f"Coluna '{col_name}': {PROBLEMATIC_TYPES[base_type.lower()]}"
            )

        # Converter tipo
        pg_type = convert_mysql_to_postgres(base_type, params)

        column_info = {
            'name': col_name,
            'mysql_type': col_type,
            'postgres_type': pg_type,
            'nullable': nullable,
            'default': default,
            'extra': extra
        }

        table_info['columns'].append(column_info)

        # Verificar auto_increment
        if extra and 'auto_increment' in extra.lower():
            table_info['warnings'].append(
                f"Coluna '{col_name}': AUTO_INCREMENT requer SERIAL/BIGSERIAL em PostgreSQL"
            )

    # Obter índices
    indexes_result = run_mysql_query(f"SHOW INDEX FROM `{table}`", database)

    index_map = {}
    for idx in indexes_result:
        key_name = idx[2]
        column = idx[4]
        non_unique = idx[1] == '1'

        if key_name not in index_map:
            index_map[key_name] = {
                'name': key_name,
                'columns': [],
                'unique': not non_unique,
                'is_primary': key_name == 'PRIMARY'
            }
        index_map[key_name]['columns'].append(column)

        if key_name == 'PRIMARY':
            table_info['primary_key'] = column

    table_info['indexes'] = list(index_map.values())

    return table_info


def extract_type_info(type_str: str) -> tuple:
    """Extrai tipo base e parâmetros"""
    type_str = type_str.lower()
    for known_type in TYPE_MAPPINGS.keys():
        if type_str.startswith(known_type):
            params = None
            if '(' in type_str:
                try:
                    params = type_str[type_str.index('(') + 1:type_str.rindex(')')]
                except ValueError:
                    pass
            return known_type, params
    return type_str, None


def convert_mysql_to_postgres(mysql_type: str, params: str = None) -> str:
    """Converte tipo MySQL para PostgreSQL"""
    mysql_type = mysql_type.lower()

    if mysql_type in TYPE_MAPPINGS:
        pg_type = TYPE_MAPPINGS[mysql_type]
        if params and mysql_type in ['char', 'varchar', 'decimal', 'numeric']:
            return f"{pg_type}({params})"
        return pg_type

    return mysql_type.upper()


def generate_migration_plan(all_analysis: List[Dict]) -> str:
    """Gera plano de migração em Markdown"""
    report = []
    report.append("# Plano de Migração: MySQL → PostgreSQL\n")

    for db_analysis in all_analysis:
        db_name = db_analysis['name']
        report.append(f"\n## Banco de Dados: `{db_name}`")
        report.append(f"\n**Tabelas:** {db_analysis['total_tables']}")

        if db_analysis['issues']:
            report.append(f"\n### ⚠️ Problemas Críticos ({len(db_analysis['issues'])})")
            for issue in db_analysis['issues']:
                report.append(f"- ❌ {issue}")

        if db_analysis['warnings']:
            report.append(f"\n### ⚠️ Avisos ({len(db_analysis['warnings'])})")
            for warning in db_analysis['warnings']:
                report.append(f"- ⚠️ {warning}")

        # Detalhes das tabelas
        report.append(f"\n### Estrutura das Tabelas")
        for table_name, table_info in db_analysis['tables'].items():
            report.append(f"\n#### `{table_name}`")

            # Colunas
            report.append("\n**Colunas:**")
            for col in table_info['columns']:
                nullable_icon = "✓" if col['nullable'] else "✗"
                report.append(
                    f"  - `{col['name']}`: {col['mysql_type']} → "
                    f"`{col['postgres_type']}` [NULL: {nullable_icon}]"
                )

            # Primary Key
            if table_info['primary_key']:
                report.append(f"\n**Primary Key:** `{table_info['primary_key']}`")

            # Índices
            if table_info['indexes']:
                report.append("\n**Índices:**")
                for idx in table_info['indexes']:
                    if idx['is_primary']:
                        continue
                    unique = "UNIQUE " if idx['unique'] else ""
                    cols_str = ', '.join([f'`{c}`' for c in idx['columns']])
                    report.append(f"  - {unique}`{idx['name']}` ({cols_str})")

            # Foreign Keys
            if table_info['foreign_keys']:
                report.append("\n**Foreign Keys:**")
                for fk in table_info['foreign_keys']:
                    report.append(
                        f"  - `{fk['column']}` → `{fk['referenced_table']}`."
                        f"`{fk['referenced_column']}`"
                    )

    # Resumo
    report.append("\n\n## 📋 Resumo e Recomendações\n")

    total_issues = sum(len(db['issues']) for db in all_analysis)
    total_warnings = sum(len(db['warnings']) for db in all_analysis)
    total_tables = sum(db['total_tables'] for db in all_analysis)

    report.append(f"**Estatísticas:**")
    report.append(f"- Bancos de dados: {len(all_analysis)}")
    report.append(f"- Total de tabelas: {total_tables}")
    report.append(f"- Problemas críticos: {total_issues}")
    report.append(f"- Avisos: {total_warnings}")

    if total_issues == 0:
        report.append("\n✅ **Nenhum problema crítico encontrado!**")
    else:
        report.append(f"\n⚠️ **{total_issues} problema(s) crítico(s) encontrado(s)**")

    report.append(f"\n⚠️ **{total_warnings} aviso(s) encontrado(s)**")

    report.append("\n### 🛠️ Estratégia de Migração Recomendada:\n")
    report.append("1. **Backup completo do MySQL**")
    report.append("   ```bash")
    report.append("   mysqldump -h 46.62.152.123 -u willkoga -p --single-transaction --routines --triggers --all-databases > backup_mysql.sql")
    report.append("   ```")
    report.append("\n2. **Instalar PostgreSQL** e criar bancos correspondentes")
    report.append("\n3. **Usar ferramenta de migração**:")
    report.append("   - **pgloader** (recomendado - automático)")
    report.append("   - **mysql2pgsql**")
    report.append("   - Script customizado")
    report.append("\n4. **Exemplo com pgloader:**")
    report.append("   ```bash")
    report.append("   pgloader mysql://willkoga:Sucesso2026@46.62.152.123/nome_db postgresql://user@localhost/nome_db")
    report.append("   ```")
    report.append("\n5. **Migrar esquema** (CREATE TABLE, indexes, constraints)")
    report.append("\n6. **Migrar dados** (INSERT/COPY)")
    report.append("\n7. **Recriar views, stored procedures, triggers**")
    report.append("\n8. **Validar dados** e **testar aplicação**")
    report.append("\n9. **Performance tuning** (ANALYZE, VACUUM, índices)")

    report.append("\n### 📦 Instalação das Ferramentas:\n")
    report.append("```bash")
    report.append("# Cliente PostgreSQL")
    report.append("sudo pacman -S postgresql postgresql-clients")
    report.append("")
    report.append("# pgloader (ferramenta de migração)")
    report.append("sudo pacman -S pgloader")
    report.append("")
    report.append("# OU mysql2pgsql (Python)")
    report.append("pip install mysql2pgsql")
    report.append("```")

    return "\n".join(report)


def main():
    print("=" * 60)
    print("🔍 Análise de Banco MySQL para Migração para PostgreSQL")
    print("=" * 60)
    print(f"📍 Servidor: {MYSQL_HOST}")
    print(f"👤 Usuário: {MYSQL_USER}")
    print("=" * 60)

    # Listar bancos
    databases = get_databases()

    if not databases:
        print("\n⚠️ Nenhum banco de dados encontrado (apenas bancos do sistema)")
        sys.exit(0)

    print(f"✓ Encontrados {len(databases)} banco(s) de dados:")
    for db in databases:
        print(f"  - {db}")

    # Analisar cada banco
    print("\n🔬 Analisando estrutura dos bancos...")
    all_analysis = []
    for database in databases:
        print(f"  ⏳ Analisando '{database}'...")
        db_analysis = analyze_database(database)
        all_analysis.append(db_analysis)

        print(f"    ✓ {db_analysis['total_tables']} tabela(s)")
        if db_analysis['issues']:
            print(f"    ⚠️ {len(db_analysis['issues'])} problema(s)")
        if db_analysis['warnings']:
            print(f"    ⚠️ {len(db_analysis['warnings'])} aviso(s)")

    # Gerar relatório
    print("\n📝 Gerando relatório de migração...")
    report = generate_migration_plan(all_analysis)

    # Salvar relatório
    report_file = "/home/will/bancochico/migration_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"✅ Relatório salvo em: {report_file}")
    print("\n" + "=" * 60)
    print("\n📄 Visualizar relatório:")
    print(f"  cat {report_file}")
    print("  ou")
    print(f"  less {report_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
