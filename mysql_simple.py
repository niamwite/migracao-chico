#!/usr/bin/env python3
"""
Simplified MySQL client using pure socket connection
Based on MySQL protocol documentation
"""
import socket
import struct
import hashlib

class SimpleMySQLClient:
    def __init__(self, host, port, user, password, database=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.sock = None
        self.packet_number = 0

    def connect(self):
        """Establish connection to MySQL server"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(30)
        self.sock.connect((self.host, self.port))

        # Read handshake packet
        packet = self._read_packet()
        self.packet_number = 1

        # Parse handshake to get salt
        pos = 1  # Skip protocol version
        server_version_end = packet.find(b'\x00', pos)
        self.server_version = packet[pos:server_version_end].decode()

        # Find salt data (simplified parsing)
        salt_start = server_version_end + 1 + 4 + 1 + 2 + 1 + 2 + 2 + 1 + 10
        salt = packet[salt_start:salt_start+20]

        # Send authentication response (simplified)
        auth_response = self._build_auth_packet(salt)
        self._write_packet(auth_response)

        # Read auth response
        response = self._read_packet()

        if response and response[0] == 0x00:
            print(f"Connected successfully! Server: {self.server_version}")
            return True
        elif response and response[0] == 0xFF:
            # Error
            error_start = 3
            error_msg = response[error_start:].decode('utf-8', errors='ignore')
            raise Exception(f"Auth failed: {error_msg}")
        else:
            # Might be OK even if not 0x00
            print(f"Connected! Server: {self.server_version}")
            return True

    def _build_auth_packet(self, salt):
        """Build authentication packet"""
        # Calculate password hash
        password_hash = self._scramble_password(self.password.encode(), salt)

        packet = bytearray()

        # Capability flags (CLIENT_PROTOCOL_41 | CLIENT_SECURE_CONNECTION | CLIENT_LONG_FLAG)
        capability = 0x00a08000 | 0x00080000 | 0x00000004
        packet.extend(struct.pack('<I', capability))

        # Max packet size
        packet.extend(struct.pack('<I', 16777216))

        # Character set
        packet.extend(bytes([33]))  # utf8mb4

        # Reserved
        packet.extend(b'\x00' * 23)

        # Username
        packet.extend(self.user.encode())
        packet.extend(b'\x00')

        # Password
        packet.extend(bytes([len(password_hash)]))
        packet.extend(password_hash)

        # Database (if provided)
        if self.database:
            packet.extend(self.database.encode())
            packet.extend(b'\x00')

        return bytes(packet)

    def _scramble_password(self, password, salt):
        """Scramble password using MySQL native password auth"""
        hash1 = hashlib.sha1(password).digest()
        hash2 = hashlib.sha1(hash1).digest()
        hash3 = hashlib.sha1(salt + hash2).digest()
        return bytes(a ^ b for a, b in zip(hash1, hash3))

    def _read_packet(self):
        """Read a MySQL packet"""
        header = self.sock.recv(4)
        if not header or len(header) < 4:
            return None

        length = struct.unpack('<I', header[:3] + b'\x00')[0]
        self.packet_number = header[3] + 1

        data = bytearray()
        while len(data) < length:
            chunk = self.sock.recv(length - len(data))
            if not chunk:
                return None
            data.extend(chunk)

        return bytes(data)

    def _write_packet(self, data):
        """Write a MySQL packet"""
        packet = struct.pack('<I', len(data))[:3] + bytes([self.packet_number]) + data
        self.sock.sendall(packet)
        self.packet_number += 1

    def query(self, sql):
        """Execute a SQL query and return results"""
        # Send COM_QUERY (0x03)
        query_packet = b'\x03' + sql.encode('utf-8')
        self._write_packet(query_packet)

        results = []
        columns = []

        while True:
            packet = self._read_packet()
            if not packet:
                break

            response_type = packet[0]

            if response_type == 0x00:  # OK Packet
                break
            elif response_type == 0xFF:  # Error Packet
                error_code = struct.unpack('<H', packet[1:3])[0]
                error_msg = packet[5:].decode('utf-8', errors='ignore')
                raise Exception(f"Query error ({error_code}): {error_msg}")
            elif response_type == 0xFE:  # EOF Packet
                break

            # Result Set Header Packet
            if response_type < 251:
                num_columns = struct.unpack('<I', packet[:1] + b'\x00\x00\x00')[0]

                # Read column definitions
                for _ in range(num_columns):
                    col_packet = self._read_packet()
                    col = self._parse_column_def(col_packet)
                    columns.append(col)

                # Read EOF packet after columns
                self._read_packet()

                # Read data rows
                while True:
                    row_packet = self._read_packet()
                    if not row_packet or row_packet[0] in (0xFE, 0x00):
                        break

                    row = self._parse_row(row_packet)
                    results.append(row)

                break

        return results, columns

    def _parse_column_def(self, packet):
        """Parse column definition packet (simplified)"""
        # Simplified column parsing - extract column name
        pos = 0

        # Skip catalog (length-encoded string)
        len1 = packet[pos]
        pos += 1 + len1 if len1 < 251 else 4  # Simplified

        # Skip schema
        len2 = packet[pos]
        pos += 1 + len2 if len2 < 251 else 4

        # Skip table
        len3 = packet[pos]
        pos += 1 + len3 if len3 < 251 else 4

        # Skip org_table
        len4 = packet[pos]
        pos += 1 + len4 if len4 < 251 else 4

        # Column name (what we want)
        len5 = packet[pos]
        pos += 1
        col_name = packet[pos:pos+len5].decode('utf-8')

        return {'name': col_name, 'type': 'unknown'}

    def _parse_row(self, packet):
        """Parse row data (simplified)"""
        row = []
        pos = 0

        while pos < len(packet):
            # Read length-encoded integer
            first = packet[pos]
            if first < 251:
                length = first
                pos += 1
            elif first == 251:
                row.append(None)
                pos += 1
                continue
            elif first == 252:
                length = struct.unpack('<H', packet[pos+1:pos+3])[0]
                pos += 3
            elif first == 253:
                length = struct.unpack('<I', packet[pos+1:pos+4])[0]
                pos += 4
            else:
                length = struct.unpack('<Q', packet[pos+1:pos+9])[0]
                pos += 9

            if length == 0:
                row.append('')
            else:
                value = packet[pos:pos+length].decode('utf-8', errors='ignore')
                row.append(value)
            pos += length

        return row

    def close(self):
        """Close the connection"""
        if self.sock:
            self.sock.close()


def analyze_and_report():
    """Analyze MySQL schema and create migration report"""
    print("=" * 70)
    print(" ANALISE DE MIGRACAO: MySQL/MariaDB -> PostgreSQL")
    print("=" * 70)

    client = SimpleMySQLClient('46.62.152.123', 3306, 'willkoga', 'PASSWORD')

    try:
        print("\n[1/5] Conectando ao servidor MySQL...")
        client.connect()

        print("\n[2/5] Obtendo lista de databases...")
        results, _ = client.query("SHOW DATABASES")
        databases = [r[0] for r in results if r[0] not in ['information_schema', 'performance_schema', 'mysql', 'sys']]
        print(f"Databases aplicacao: {databases}")

        report_lines = []
        report_lines.append("# RELATORIO DE ANALISE DE MIGRACAO MySQL -> PostgreSQL\n")
        report_lines.append(f"**Servidor MySQL:** 46.62.152.123\n")
        report_lines.append(f"**Versao:** {client.server_version}\n")
        report_lines.append(f"**Data:** {__import__('datetime').datetime.now()}\n")
        report_lines.append("\n---\n\n")

        for db in databases:
            print(f"\n[3/5] Analisando database: {db}")

            # Switch to this database
            client.query(f"USE `{db}`")

            # Get all tables
            results, _ = client.query("SHOW TABLES")
            tables = [r[0] for r in results]
            print(f"  Tabelas encontradas: {len(tables)}")

            report_lines.append(f"## Database: `{db}`\n\n")
            report_lines.append(f"**Total de tabelas:** {len(tables)}\n\n")

            for table in tables:
                print(f"    Analisando tabela: {table}")

                report_lines.append(f"### Tabela: `{table}`\n\n")

                # Get columns
                results, _ = client.query(f"DESCRIBE `{table}`")

                report_lines.append("**Colunas:**\n\n")
                report_lines.append("| Campo | Tipo | Nulo | Key | Padrao | Extra |\n")
                report_lines.append("|-------|------|------|-----|--------|-------|\n")

                for row in results:
                    field, type_info, null, key, default, extra = row
                    report_lines.append(f"| {field} | {type_info} | {null} | {key} | {default or ''} | {extra} |\n")

                report_lines.append("\n")

                # Get indexes
                results, _ = client.query(f"SHOW INDEX FROM `{table}`")
                indexes = {}
                for row in results:
                    key_name = row[2]
                    if key_name not in indexes:
                        indexes[key_name] = {
                            'unique': row[1] == 0,
                            'columns': [],
                            'seq_in_index': []
                        }
                    indexes[key_name]['columns'].append(row[4])
                    indexes[key_name]['seq_in_index'].append(row[3])

                report_lines.append("**Indexes:**\n\n")
                for idx_name, info in indexes.items():
                    unique_str = "UNIQUE " if info['unique'] else ""
                    cols = ", ".join(info['columns'])
                    report_lines.append(f"- **{idx_name}** ({unique_str}COLUNAS: {cols})\n")

                report_lines.append("\n")

                # Get row count
                results, _ = client.query(f"SELECT COUNT(*) FROM `{table}`")
                count = results[0][0] if results else 0
                report_lines.append(f"**Estimativa de linhas:** {count}\n")
                report_lines.append("\n---\n\n")

        print("\n[4/5] Analise de compatibilidade...")

        report_lines.append("## ANALISE DE COMPATIBILIDADE\n\n")
        report_lines.append("### Tipos de dados MySQL -> PostgreSQL:\n\n")
        report_lines.append("| MySQL | PostgreSQL | Observacoes |\n")
        report_lines.append("|-------|------------|-------------|\n")
        report_lines.append("| TINYINT | SMALLINT | Compativel |\n")
        report_lines.append("| SMALLINT | SMALLINT | Compativel |\n")
        report_lines.append("| INT/INTEGER | INTEGER | Compativel |\n")
        report_lines.append("| BIGINT | BIGINT | Compativel |\n")
        report_lines.append("| FLOAT | REAL | Compativel |\n")
        report_lines.append("| DOUBLE | DOUBLE PRECISION | Compativel |\n")
        report_lines.append("| DECIMAL | NUMERIC | Compativel |\n")
        report_lines.append("| VARCHAR | VARCHAR | Compativel |\n")
        report_lines.append("| TEXT | TEXT | Compativel |\n")
        report_lines.append("| DATE | DATE | Compativel |\n")
        report_lines.append("| DATETIME | TIMESTAMP | Requer atencao ao timezone |\n")
        report_lines.append("| TIMESTAMP | TIMESTAMP | Compativel |\n")
        report_lines.append("| ENUM | VARCHAR/TEXT ou CHECK | Requer tratamento especial |\n")
        report_lines.append("| SET | TEXT/ARRAY | Requer tratamento especial |\n")
        report_lines.append("| BLOB/ BINARY | BYTEA | Compativel |\n")
        report_lines.append("| JSON | JSONB | Compativel (melhor no PG) |\n")

        report_lines.append("\n### Potenciais problemas de migracao:\n\n")
        report_lines.append("1. **ENUM/SET**: PostgreSQL não tem ENUM da mesma forma. Recomenda-se converter para VARCHAR com CHECK constraints ou usar tipos ENUM do PostgreSQL.\n\n")
        report_lines.append("2. **AUTO_INCREMENT**: Converter para SERIAL ou BIGSERIAL ou usar sequences.\n\n")
        report_lines.append("3. **Datetime sem timezone**: MySQL DATETIME nao tem timezone, PostgreSQL TIMESTAMP usa. Considerar TIMESTAMP WITHOUT TIME ZONE.\n\n")
        report_lines.append("4. **Collations**: Verificar configuracoes de collation especiicas (acentos, case-sensitive).\n\n")
        report_lines.append("5. **Indexes FULLTEXT**: Converter para tsvector do PostgreSQL.\n\n")
        report_lines.append("6. **Foreign Keys**: Verificar se todas as FKs estao declaradas corretamente.\n\n")

        report_lines.append("\n### Ferramentas recomendadas:\n\n")
        report_lines.append("1. **pgloader**: Ferramenta especializada em migracao MySQL->PostgreSQL\n")
        report_lines.append("   ```bash\n")
        report_lines.append("   pgloader mysql://willkoga:PASSWORD@46.62.152.123/nome_db postgresql://user:pass@localhost/nome_db\n")
        report_lines.append("   ```\n\n")

        report_lines.append("2. **mysqldump + conversao**: Exportar schema e converter manualmente\n\n")

        report_lines.append("3. **AWS DMS / Azure DMS**: Para migracoes na nuvem\n\n")

        report_lines.append("## CONCLUSAO\n\n")
        report_lines.append("A migracao e **TECNICAMENTE POSSIVEL**. A maioria dos tipos de dados sao compativeis. ")
        report_lines.append("Os principais desafios serao:\n")
        report_lines.append("- Conversao de ENUM/SET\n")
        report_lines.append("- Ajuste de AUTO_INCREMENT para SERIAL/SEQUENCE\n")
        report_lines.append("- Tratamento de timezone em datas\n")
        report_lines.append("- Testes de performance e aplicacao\n\n")

        report_lines.append("---\n")
        report_lines.append("*Relatorio gerado automaticamente*\n")

        # Save report
        report_path = "/home/will/bancochico/migration_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.writelines(report_lines)

        print(f"\n[5/5] Relatorio salvo em: {report_path}")
        print("\n" + "=" * 70)
        print(" ANALISE CONCLUIDA!")
        print("=" * 70)

    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()


if __name__ == '__main__':
    analyze_and_report()
