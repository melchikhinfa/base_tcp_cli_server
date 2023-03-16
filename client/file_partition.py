def read_part(conn, bytes_to_read):
    data = bytearray()
    while len(data) < bytes_to_read:
        part = conn.recv(bytes_to_read - len(data))
        if not part:
            raise IOError("Connection closed")
        data += part
    return bytes(data)

def read_full_message(conn):
    max_size = 4096
    data = bytearray()
    while True:
        part_len = int.from_bytes(read_part(conn, max_size), "big")
        if part_len == 0:
            break
        data += read_part(conn, part_len)
    return bytes(data)