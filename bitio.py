class BitWriter:
    def __init__(self):
        self.buffer = bytearray()
        self.current_byte = 0
        self.bit_count = 0

    def write_bit(self, bit):
        self.current_byte = (self.current_byte << 1) | (bit & 1)
        self.bit_count += 1
        if self.bit_count == 8:
            self.buffer.append(self.current_byte)
            self.current_byte = 0
            self.bit_count = 0

    def write_bits(self, value, nbits):
        for i in range(nbits - 1, -1, -1):
            self.write_bit((value >> i) & 1)

    def flush(self):
        if self.bit_count > 0:
            self.current_byte <<= (8 - self.bit_count)
            self.buffer.append(self.current_byte)
            self.current_byte = 0
            self.bit_count = 0
        return bytes(self.buffer)


class BitReader:
    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.bit_pos = 0

    def read_bit(self):
        if self.pos >= len(self.data):
            raise EOFError("Reading past end of bit stream")
        bit = (self.data[self.pos] >> (7 - self.bit_pos)) & 1
        self.bit_pos += 1
        if self.bit_pos == 8:
            self.pos += 1
            self.bit_pos = 0
        return bit

    def read_bits(self, nbits):
        value = 0
        for _ in range(nbits):
            value = (value << 1) | self.read_bit()
        return value

    def byte_aligned(self):
        return self.bit_pos == 0