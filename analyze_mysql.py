#!/usr/bin/env python3
"""
Script para analisar banco de dados MySQL e planejar migração para PostgreSQL
"""

import sys
from typing import List, Dict, Any

# Tentar importar biblioteca MySQL
try:
    import pymysql
    print("✓ Usando pymysql")
except ImportError:
    try:
        import mysql.connector as pymysql
        print("✓ Usando mysql.connector")
        # Criar wrapper compatível
        class MySQLCursor:
            def __init__(self, conn):
                self._cursor = conn.cursor()
            def execute(self, query, params=None):
                return self._cursor.execute(query, params or ())
            def fetchall(self):
                return self._cursor.fetchall()
            def fetchone(self):
                return self._cursor.fetchone()
            def description(self):
                return self._cursor.description

        class PyMySQLWrapper:
            def connect(self, **kwargs):
                conn = pymysql.connect(**kwargs)
                return conn

        pymysql = PyMySQLWrapper()
    except ImportError:
        print("✗ Biblioteca MySQL não encontrada")
        print("\nInstale com:")
        print("  pip install pymysql")
        print("  ou")
        print("  pip install mysql-connector-python")
        sys.exit(1)


# Configurações de conexão
MYSQL_CONFIG = {
    'host': '46.62.152.123',
    'user': 'willkoga',
    'password': 'Sucesso2026',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor if 'pymysql' in sys.modules else None
}

# Mapeamento de tipos MySQL para PostgreSQL
TYPE_MAPPINGS = {
    # Inteiros
    'tinyint': 'smallint',
    'smallint': 'smallint',
    'mediumint': 'integer',
    'int': 'integer',
    'integer': 'integer',
    'bigint': 'bigint',

    # Decimais
    'decimal': 'numeric',
    'numeric': 'numeric',
    'float': 'real',
    'double': 'double precision',

    # Strings
    'char': 'char',
    'varchar': 'varchar',
    'tinytext': 'text',
    'text': 'text',
    'mediumtext': 'text',
    'longtext': 'text',

    # Binários
    'binary': 'bytea',
    'varbinary': 'bytea',
    'tinyblob': 'bytea',
    'blob': 'bytea',
    'mediumblob': 'bytea',
    'longblob': 'bytea',

    # Data/Hora
    'date': 'date',
    'datetime': 'timestamp',
    'timestamp': 'timestamp',
    'time': 'time',
    'year': 'integer',

    # Boolean
    'bool': 'boolean',
    'boolean': 'boolean',

    # JSON
    'json': 'jsonb',
}

# Tipos que requerem atenção especial
PROBLEMATIC_TYPES = {
    'enum': 'ENUM não existe nativamente no PostgreSQL - usar VARCHAR com CHECK ou tipo ENUM customizado',
    'set': 'SET não existe no PostgreSQL - usar array ou VARCHAR',
    'year': 'YEAR não existe no PostgreSQL - usar INTEGER',
}


def connect_to_mysql():
    """Estabelece conexão com o MySQL"""
    try:
        if 'pymysql' in sys.modules:
            connection = pymysql.connect(**MYSQL_CONFIG)
        else:
            import mysql.connector
            connection = mysql.connector.connect(
                host=MYSQL_CONFIG['host'],
                user=MYSQL_CONFIG['user'],
                password=MYSQL_CONFIG['password'],
                charset=MYSQL_CONFIG['charset']
            )
        print(f"✓ Conectado ao MySQL em {MYSQL_CONFIG['host']}")
        return connection
    except Exception as e:
        print(f"✗ Erro ao conectar: {e}")
        sys.exit(1)


def get_databases(connection) -> List[str]:
    """Lista todos os bancos de dados"""
    cursor = connection.cursor()
    cursor.execute("SHOW DATABASES")
    databases = [row['Database'] if isinstance(row, dict) else row[0]
                 for row in cursor.fetchall()]

    # Filtrar bancos do sistema
    system_dbs = ['information_schema', 'performance_schema', 'mysql', 'sys']
    databases = [d for d in databases if d not in system_dbs]

    return databases


def analyze_database(connection, database: str) -> Dict[str, Any]:
    """Analisa um banco de dados específico"""
    cursor = connection.cursor()
    cursor.execute(f"USE `{database}`")

    analysis = {
        'name': database,
        'tables': {},
        'total_tables': 0,
        'issues': [],
        'warnings': []
    }

    # Obter tabelas
    cursor.execute("SHOW TABLES")
    tables_result = cursor.fetchall()
    tables = [row[list(row.keys())[0]] if isinstance(row, dict) else row[0]
              for row in tables_result]

    analysis['total_tables'] = len(tables)

    # Analisar cada tabela
    for table in tables:
        table_analysis = analyze_table(connection, database, table)
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


def analyze_table(connection, database: str, table: str) -> Dict[str, Any]:
    """Analisa uma tabela específica"""
    cursor = connection.cursor()

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
    cursor.execute(f"DESCRIBE `{database}`.`{table}`")
    columns = cursor.fetchall()

    for col in columns:
        if isinstance(col, dict):
            col_name = col['Field']
            col_type = col['Type']
            nullable = col['Null'] == 'YES'
            default = col['Default']
            extra = col['Extra']
        else:
            col_name = col[0]
            col_type = col[1]
            nullable = col[2] == 'YES'
            default = col[4]
            extra = col[5]

        # Extrair tipo base e parâmetros
        base_type, params = extract_type_info(col_type)

        # Verificar problemas
        if base_type.lower() in PROBLEMATIC_TYPES:
            table_info['issues'].append(
                f"Coluna '{col_name}': {PROBLEMATIC_TYPES[base_type.lower()]}"
            )

        # Converter tipo para PostgreSQL
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
    cursor.execute(f"SHOW INDEX FROM `{database}`.`{table}`")
    indexes = cursor.fetchall()

    index_map = {}
    for idx in indexes:
        if isinstance(idx, dict):
            key_name = idx['Key_name']
            column = idx['Column_name']
            non_unique = idx['Non_unique'] == 1
        else:
            key_name = idx[2]
            column = idx[4]
            non_unique = idx[1] == 1

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

    # Obter foreign keys
    try:
        cursor.execute(f"""
            SELECT
                CONSTRAINT_NAME,
                COLUMN_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = %s
            AND TABLE_NAME = %s
            AND REFERENCED_TABLE_NAME IS NOT NULL
        """, (database, table))

        fks = cursor.fetchall()
        for fk in fks:
            if isinstance(fk, dict):
                table_info['foreign_keys'].append({
                    'name': fk['CONSTRAINT_NAME'],
                    'column': fk['COLUMN_NAME'],
                    'referenced_table': fk['REFERENCED_TABLE_NAME'],
                    'referenced_column': fk['REFERENCED_COLUMN_NAME']
                })
            else:
                table_info['foreign_keys'].append({
                    'name': fk[0],
                    'column': fk[1],
                    'referenced_table': fk[2],
                    'referenced_column': fk[3]
                })
    except Exception as e:
        table_info['warnings'].append(f"Não foi possível obter foreign keys: {e}")

    return table_info


def extract_type_info(type_str: str) -> tuple:
    """Extrai tipo base e parâmetros de uma string de tipo"""
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

    return mysql_type.upper()  # Fallback


def generate_migration_plan(analysis: Dict) -> str:
    """Gera plano de migração em Markdown"""
    report = []
    report.append("# Plano de Migração: MySQL → PostgreSQL\n")

    for db_analysis in analysis:
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
                    report.append(
                        f"  - {unique}`{idx['name']` ({', '.join(idx['columns'])})"
                    )

            # Foreign Keys
            if table_info['foreign_keys']:
                report.append("\n**Foreign Keys:**")
                for fk in table_info['foreign_keys']:
                    report.append(
                        f"  - `{fk['column']}` → `{fk['referenced_table']}`."
                        f"`{fk['referenced_column']}`"
                    )

    # Resumo e recomendações
    report.append("\n\n## 📋 Resumo e Recomendações\n")

    total_issues = sum(len(db['issues']) for db in analysis)
    total_warnings = sum(len(db['warnings']) for db in analysis)

    if total_issues == 0:
        report.append("✅ **Nenhum problema crítico encontrado!**")
    else:
        report.append(f"⚠️ **{total_issues} problema(s) crítico(s) encontrado(s)**")

    report.append(f"\n⚠️ **{total_warnings} aviso(s) encontrado(s)**")

    report.append("\n### Estratégia de Migração Recomendada:\n")
    report.append("1. **Backup completo do MySQL**")
    report.append("2. **Instalar PostgreSQL** e criar bancos correspondentes")
    report.append("3. **Usar ferramenta de migração** (pgloader, ora2pg, ou script customizado)")
    report.append("4. **Migrar esquema** (CREATE TABLE, indexes, constraints)")
    report.append("5. **Migrar dados** (INSERT/COPY)")
    report.append("6. **Recriar views, stored procedures, triggers**")
    report.append("7. **Validar dados** e **testar aplicação**")
    report.append("8. **Performance tuning** (ANALYZE, VACUUM, índices)")

    report.append("\n### Ferramentas Recomendadas:\n")
    report.append("- **pgloader** - Migração automática MySQL → PostgreSQL")
    report.append("- **py-mysql2postgresql** - Script Python de conversão")
    report.append("- **mysql2pgsql** - Outra ferramenta de conversão")

    return "\n".join(report)


def main():
    print("=" * 60)
    print("🔍 Análise de Banco MySQL para Migração para PostgreSQL")
    print("=" * 60)

    # Conectar
    connection = connect_to_mysql()

    # Listar bancos
    print("\n📊 Buscando bancos de dados...")
    databases = get_databases(connection)

    if not databases:
        print("⚠️ Nenhum banco de dados encontrado (apenas bancos do sistema)")
        sys.exit(0)

    print(f"✓ Encontrados {len(databases)} banco(s) de dados:")
    for db in databases:
        print(f"  - {db}")

    # Analisar cada banco
    print("\n🔬 Analisando estrutura dos bancos...")
    all_analysis = []
    for database in databases:
        print(f"  ⏳ Analisando '{database}'...")
        db_analysis = analyze_database(connection, database)
        all_analysis.append(db_analysis)

        # Resumo rápido
        print(f"    ✓ {db_analysis['total_tables']} tabela(s)")
        if db_analysis['issues']:
            print(f"    ⚠️ {len(db_analysis['issues'])} problema(s)")
        if db_analysis['warnings']:
            print(f"    ⚠️ {len(db_analysis['warnings'])} aviso(s)")

    # Fechar conexão
    connection.close()

    # Gerar relatório
    print("\n📝 Gerando relatório de migração...")
    report = generate_migration_plan(all_analysis)

    # Salvar relatório
    report_file = "migration_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"✅ Relatório salvo em: {report_file}")
    print("\n" + "=" * 60)

    return report


if __name__ == "__main__":
    main()
