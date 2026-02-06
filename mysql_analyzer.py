#!/usr/bin/env python3
"""
MySQL/MariaDB client in pure Python for schema analysis
"""
import socket
import struct
import hashlib
import ssl

class MySQLClient:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user.encode()
        self.password = password.encode()
        self.sock = None
        self.connection_id = 0

    def connect(self):
        """Connect to MySQL server"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(30)
        self.sock.connect((self.host, self.port))

        # Read handshake packet
        packet = self._read_packet()
        if not packet:
            raise Exception("No handshake received")

        # Parse handshake
        pos = 0
        protocol_version = packet[pos]
        pos += 1

        server_version_end = packet.find(b'\x00', pos)
        self.server_version = packet[pos:server_version_end].decode()
        pos = server_version_end + 1

        self.connection_id = struct.unpack('<I', packet[pos:pos+4])[0]
        pos += 4

        auth_data_1 = packet[pos:pos+8]
        pos += 8 + 1  # +1 for filler

        capability_flags_low = struct.unpack('<H', packet[pos:pos+2])[0]
        pos += 2

        character_set = packet[pos]
        pos += 1

        status_flags = struct.unpack('<H', packet[pos:pos+2])[0]
        pos += 2

        capability_flags_high = struct.unpack('<H', packet[pos:pos+2])[0]
        pos += 2

        auth_plugin_data_len = packet[pos] if capability_flags_high & 0x0080 else 0
        pos += 1

        pos += 10  # reserved

        auth_data_2 = b''
        if capability_flags_low & 0x0080:
            auth_data_2_len = max(13, auth_plugin_data_len - 8)
            auth_data_2 = packet[pos:pos+auth_data_2_len]
            pos += auth_data_2_len

        # Auth plugin name
        if capability_flags_high & 0x0008:
            auth_plugin_end = packet.find(b'\x00', pos)
            auth_plugin = packet[pos:auth_plugin_end]
            pos = auth_plugin_end + 1

        salt = auth_data_1 + auth_data_2

        # Build authentication packet
        capability = 0x00a08000 | (capability_flags_high << 16) | capability_flags_low
        max_packet_size = 16777216
        charset = 33  # utf8mb4

        auth_resp = self._scramble_password(salt[:20])

        auth_packet = bytearray()
        auth_packet.extend(struct.pack('<I', capability))
        auth_packet.extend(struct.pack('<I', max_packet_size))
        auth_packet.extend(charset.to_bytes(1, 'little'))
        auth_packet.extend(b'\x00' * 23)  # reserved
        auth_packet.extend(self.user)
        auth_packet.extend(b'\x00')
        auth_packet.extend(struct.pack('B', len(auth_resp)))
        auth_packet.extend(auth_resp)
        auth_packet.extend(b'mysql_native_password')
        auth_packet.extend(b'\x00')

        self._send_packet(auth_packet)

        # Read auth response
        response = self._read_packet()

        if response[0] == 0x00:  # OK packet
            return True
        elif response[0] == 0xFF:  # Error packet
            error_code = struct.unpack('<H', response[1:3])[0]
            error_msg = response[3:].decode(errors='ignore')
            raise Exception(f"Authentication failed: {error_msg}")
        else:
            return True

    def _scramble_password(self, salt):
        """Scramble password using MySQL native password algorithm"""
        hash1 = hashlib.sha1(self.password).digest()
        hash2 = hashlib.sha1(hash1).digest()
        hash3 = hashlib.sha1(salt + hash2).digest()
        scrambled = bytes(a ^ b for a, b in zip(hash1, hash3))
        return scrambled

    def _read_packet(self):
        """Read a MySQL packet"""
        header = self.sock.recv(4)
        if not header or len(header) < 4:
            return None

        length = struct.unpack('<I', header[:3] + b'\x00')[0]
        number = header[3]

        data = bytearray()
        while len(data) < length:
            chunk = self.sock.recv(length - len(data))
            if not chunk:
                return None
            data.extend(chunk)

        return bytes(data)

    def _send_packet(self, data):
        """Send a MySQL packet"""
        packet = struct.pack('<I', len(data))[:3] + b'\x00' + data
        self.sock.sendall(packet)

    def query(self, sql):
        """Execute a query"""
        sql_bytes = sql.encode('utf-8')
        packet = b'\x03' + sql_bytes  # 0x03 = COM_QUERY
        self._send_packet(packet)

        result = []
        while True:
            packet = self._read_packet()
            if not packet:
                break

            if packet[0] == 0x00:  # OK packet
                break
            elif packet[0] == 0xFF:  # Error packet
                error_code = struct.unpack('<H', packet[1:3])[0]
                error_msg = packet[3:].decode(errors='ignore')
                raise Exception(f"Query error: {error_msg}")
            elif packet[0] == 0xFE:  # EOF
                break
            else:
                # Result set
                num_columns = packet[0] if len(packet) == 1 else struct.unpack('<I', packet[:1] + b'\x00\x00\x00')[0]

                # Read column definitions
                columns = []
                for _ in range(num_columns):
                    col_packet = self._read_packet()
                    columns.append(self._parse_column(col_packet))

                # Read EOF
                self._read_packet()

                # Read rows
                while True:
                    row_packet = self._read_packet()
                    if not row_packet or row_packet[0] == 0xFE or row_packet[0] == 0x00:
                        break

                    row = self._parse_row(row_packet)
                    result.append(row)

                break

        return result, columns

    def _parse_column(self, packet):
        """Parse column definition packet"""
        pos = 0
        catalog = self._read_length_encoded_string(packet, pos)
        pos += catalog[1]
        schema = self._read_length_encoded_string(packet, pos)
        pos += schema[1]
        table = self._read_length_encoded_string(packet, pos)
        pos += table[1]
        org_table = self._read_length_encoded_string(packet, pos)
        pos += org_table[1]
        name = self._read_length_encoded_string(packet, pos)
        pos += name[1]
        org_name = self._read_length_encoded_string(packet, pos)
        pos += org_name[1]
        pos += 1  # length of fixed fields
        charset = struct.unpack('<H', packet[pos:pos+2])[0]
        pos += 2
        length = struct.unpack('<I', packet[pos:pos+4])[0]
        pos += 4
        col_type = packet[pos]
        pos += 1
        flags = struct.unpack('<H', packet[pos:pos+2])[0]
        pos += 2
        decimals = packet[pos]

        return {
            'name': name[0].decode(),
            'type': col_type,
            'schema': schema[0].decode(),
            'table': table[0].decode(),
        }

    def _parse_row(self, packet):
        """Parse row data"""
        row = []
        pos = 0
        while pos < len(packet):
            length = self._read_length_encoded_integer(packet, pos)
            pos += length[1]
            if length[0] is None:
                row.append(None)
            else:
                data = packet[pos:pos+length[0]]
                row.append(data.decode('utf-8', errors='ignore'))
                pos += length[0]
        return row

    def _read_length_encoded_string(self, packet, pos):
        """Read length-encoded string"""
        length_info = self._read_length_encoded_integer(packet, pos)
        length = length_info[0]
        bytes_read = length_info[1]

        if length is None:
            return (b'', bytes_read)

        value = packet[pos+bytes_read:pos+bytes_read+length]
        return (value, bytes_read + length)

    def _read_length_encoded_integer(self, packet, pos):
        """Read length-encoded integer"""
        if pos >= len(packet):
            return (None, 0)

        first = packet[pos]
        if first < 251:
            return (first, 1)
        elif first == 251:
            return (None, 1)
        elif first == 252:
            return (struct.unpack('<H', packet[pos+1:pos+3])[0], 3)
        elif first == 253:
            return (struct.unpack('<I', packet[pos+1:pos+4])[0], 4)
        else:
            return (struct.unpack('<Q', packet[pos+1:pos+9])[0], 9)

    def close(self):
        """Close connection"""
        if self.sock:
            self.sock.close()


def analyze_schema(host, port, user, password):
    """Analyze MySQL schema and generate migration report"""
    print("=" * 60)
    print("MYSQL/MariaDB PARA POSTGRESQL - ANALISE DE MIGRACAO")
    print("=" * 60)

    client = MySQLClient(host, port, user, password)

    try:
        print(f"\nConectando a {host}:{port}...")
        client.connect()
        print(f"Conectado! Versao: {client.server_version}")

        # Get all databases
        print("\nObtendo lista de databases...")
        result, _ = client.query("SHOW DATABASES")
        databases = [row[0] for row in result if row[0] not in ('information_schema', 'performance_schema', 'mysql', 'sys')]

        print(f"Databases encontrados: {databases}")

        # Analyze each database
        for db in databases:
            print("\n" + "=" * 60)
            print(f"DATABASE: {db}")
            print("=" * 60)

            client.query(f"USE `{db}`")

            # Get all tables
            result, _ = client.query("SHOW TABLES")
            tables = [row[0] for row in result]

            print(f"\nTabelas encontradas: {len(tables)}")

            for table in tables:
                print(f"\n--- Tabela: {table} ---")

                # Get table structure
                result, _ = client.query(f"DESCRIBE `{table}`")

                print("Colunas:")
                for row in result:
                    field, type_info, null, key, default, extra = row
                    print(f"  - {field}: {type_info} NULL={null} KEY={key} DEFAULT={default} EXTRA={extra}")

                # Get indexes
                result, _ = client.query(f"SHOW INDEX FROM `{table}`")
                indexes = {}
                for row in result:
                    key_name = row[2]
                    if key_name not in indexes:
                        indexes[key_name] = {'unique': row[1] == 0, 'columns': []}
                    indexes[key_name]['columns'].append(row[4])

                print("\nIndexes:")
                for idx_name, idx_info in indexes.items():
                    print(f"  - {idx_name}: {'UNIQUE' if idx_info['unique'] else 'NON-UNIQUE'} ({', '.join(idx_info['columns'])})")

        print("\n" + "=" * 60)
        print("ANALISE CONCLUIDA COM SUCESSO")
        print("=" * 60)

    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()


if __name__ == '__main__':
    analyze_schema('seu_host_aqui', 3306, 'seu_usuario_aqui', os.environ.get('MYSQL_PASSWORD'))
