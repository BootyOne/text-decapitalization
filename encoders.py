from heapq import heappush, heappop
from collections import Counter
from typing import List
from math import log2


class DeltaEncoder:
    def encode(self, source: bytes) -> bytes:
        offset = 0
        byte_offset = 7
        result: List[int] = [0]
        total_bits = 0

        def decrement_byte_offset():
            nonlocal byte_offset, total_bits, offset
            byte_offset = (byte_offset + 7) % 8
            total_bits += 1
            if byte_offset != 7:
                return
            offset += 1
            result.append(0)

        for b in source:
            section = int(log2(b + 1))
            section_of_section = int(log2(section + 1))
            for i in range(section_of_section):
                decrement_byte_offset()
            for i in range(section_of_section, -1, -1):
                v = (1 << i) & (section + 1)
                result[offset] |= (1 << byte_offset) if v > 0 else 0
                decrement_byte_offset()
            for i in range(section - 1, -1, -1):
                v = (1 << i) & (b + 1)
                result[offset] |= (1 << byte_offset) if v > 0 else 0
                decrement_byte_offset()

        print(f'Delta encoder:{total_bits}')
        return bytes(result)


class ArithmeticEncoder:
    def __init__(self, window):
        self.encoding_window = window
        self.interval_expansion = (1 << (window - 1))
        self.max_value = (1 << window)

    def encode(self, source):
        total_bits = 0
        result = bytearray()
        result.append(0)
        offset = 0
        byte_offset = 7
        counter = [1] * 256
        l = 0
        h = self.max_value - 1

        def decrement_byte_offset():
            nonlocal byte_offset, total_bits, offset
            byte_offset = (byte_offset + 7) % 8
            total_bits += 1
            if byte_offset != 7:
                return
            offset += 1
            if offset >= len(result):
                result.append(0)

        def project(counter, element, l, h):
            c = sum(counter[:element])
            summary_count = sum(counter)
            alpha = c / summary_count
            beta = (c + counter[element]) / summary_count
            range_size = h - l + 1
            new_l = l + int(alpha * range_size)
            new_h = l + int(beta * range_size) - 1
            return new_l, new_h

        def get_bits(l, h):
            offset = self.encoding_window - 2
            counter = 0
            while offset >= 0:
                o = 1 << offset
                if (l & o) != (h & o):
                    counter += 1
                else:
                    break
                offset -= 1
            return counter

        for b in source:
            l, h = project(counter, b, l, h)
            off = 1 << (self.encoding_window - 1)
            while (l & off) == (h & off):
                first_bit = (1 << byte_offset) if (l & off) > 0 else 0
                result[offset] |= first_bit
                decrement_byte_offset()
                l <<= 1
                h = (h << 1) | 1

            bits = get_bits(l, h)
            for i in range(bits):
                l = (l << 1) & (self.max_value - 1)
                h = (h << 1) & (self.max_value - 1) | 1

            counter[b] += 1

        return bytes(result)


class HuffmanEncoder:
    def __init__(self):
        self.codes = {}
        self.total_bits = 0

    def build_tree(self, frequencies):
        heap = []
        index = 0

        for char, freq in frequencies.items():
            heappush(heap, (freq, index, char))
            index += 1

        while len(heap) > 1:
            freq1, _, char1 = heappop(heap)
            freq2, _, char2 = heappop(heap)
            for char, code in ((char1, '0'), (char2, '1')):
                if isinstance(char, tuple):
                    for c in char:
                        self.codes[c] = code + self.codes.get(c, '')
                else:
                    self.codes[char] = code + self.codes.get(char, '')
            heappush(heap, (freq1 + freq2, index, (char1, char2)))
            index += 1

    def encode(self, source: bytes) -> bytes:
        frequencies = Counter(source)
        self.build_tree(frequencies)

        encoded_output = []
        for byte in source:
            encoded_output.append(self.codes[byte])

        encoded_string = ''.join(encoded_output)
        self.total_bits = len(''.join(encoded_output))

        b = bytearray()
        for i in range(0, len(encoded_string), 8):
            byte = encoded_string[i:i + 8]
            if len(byte) < 8:
                byte = byte.ljust(8, '0')
            b.append(int(byte, 2))

        return bytes(b)
