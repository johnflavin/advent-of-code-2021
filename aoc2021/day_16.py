#!/usr/bin/env python
"""

"""

from collections.abc import Iterable
from itertools import islice


EXAMPLE = """\
9C0141080250320F1802104A08
"""
PART_ONE_EXAMPLE_RESULT = 20
PART_TWO_EXAMPLE_RESULT = 1
PART_ONE_RESULT = 929
PART_TWO_RESULT = 911945136934


LAST_THREE_BITS = 7
LAST_FIVE_BITS = 31


class Packet:
    version: int
    type_id: int
    value: int
    version_sum: int

    def __init__(
        self,
        version: int,
        type_id: int,
        value: int = 0,
        subpackets: Iterable["Packet"] | None = None,
    ):
        self.version = version
        self.type_id = type_id
        self.value = value

        version_sum = self.version
        subpacket_values = []
        if subpackets is not None:
            # print("INTERPRETING SUBPACKETS")
            for subpacket in subpackets:
                version_sum += subpacket.version_sum
                subpacket_values.append(subpacket.value)

        self.version_sum = version_sum

        if self.type_id == 0:
            # print("Sum packet")
            # print(subpacket_values)
            self.value = sum(subpacket_values)
        elif self.type_id == 1:
            # print("Product packet")
            # print(subpacket_values)
            prod = 1
            for value in subpacket_values:
                prod *= value
            self.value = prod
        elif self.type_id == 2:
            # print("Minimum packet")
            # print(subpacket_values)

            self.value = min(subpacket_values)
        elif self.type_id == 3:
            # print("Maximum packet")
            # print(subpacket_values)

            self.value = max(subpacket_values)
        elif self.type_id == 4:
            self.value = value
        elif self.type_id == 5:
            # print("Greater than packet")
            # print(subpacket_values)

            self.value = int(subpacket_values[0] > subpacket_values[1])
        elif self.type_id == 6:
            # print("Less than packet")
            # print(subpacket_values)

            self.value = int(subpacket_values[0] < subpacket_values[1])
        elif self.type_id == 7:
            # print("Equal to packet")
            # print(subpacket_values)

            self.value = int(subpacket_values[0] == subpacket_values[1])

    def __str__(self):
        return (
            f"{self.__class__.__name__}("
            f"version={self.version}, "
            f"type_id={self.type_id}, "
            f"value={self.value}, "
            f"version_sum={self.version_sum}"
            ")"
        )


class BitReader:
    message: int
    read_head: int

    def __init__(self, message: int, length: int):
        self.message = message
        self.read_head = 0
        self.length = length

    def read(self, num: int) -> int:
        """Read num bits of message from read head

        If num is None (default) read the rest of the message.
        """

        # cut off bits after the ones we want by shifting down
        unmasked = self.message >> (self.length - num - self.read_head)

        # Cut off bits before the ones we want by masking to the end
        mask = 2 ** num - 1

        # Update the read head so next time we get the next bits
        self.read_head += num

        return unmasked & mask

    def read_remaining(self) -> tuple[int, int]:

        # number of bits remaining
        num = self.length - self.read_head
        return self.read(num), num


def decode_packets(message: int, length: int) -> Iterable[Packet]:

    # print("BEGIN PACKET")

    reader = BitReader(message, length)

    # version is first three bits
    version = reader.read(3)
    # print(f"{version=:03b}={version}")

    # type id is next three bits
    type_id = reader.read(3)
    # print(f"{type_id=:03b}={type_id}")

    if type_id == 4:
        # literal value
        # print("READING VALUE")

        keep_reading = True
        value = 0
        value_bit_len = 0
        while keep_reading:

            # read five more bits off the message
            chunk = reader.read(5)
            # print(f"{chunk=:05b}")

            # first bit of the chunk is whether there are more chunks coming
            keep_reading = bool(chunk >> 4)
            # print(f"{keep_reading=:b}")

            # Remaining 4 bits of the chunk are the
            # next 4 bits of the value
            this_value = chunk & 15
            # print(f"{this_value=:04b}={this_value}")

            # Shift the value bits up by four and add this chunk
            value = (value << 4) + this_value
            value_bit_len += 4

        p = Packet(version, type_id, value)
        # print(p)
        yield p

        # If there is more left, parse that out too
        remaining, len_remaining = reader.read_remaining()
        if remaining and len_remaining:
            yield from decode_packets(remaining, len_remaining)

    else:
        # print("READING SUBPACKETS")
        # interpret subpackets
        # for now we don't do anything with the packets, just parse

        # one bit immediately after header is length type id
        length_type_id = reader.read(1)
        # print(f"{length_type_id=:b}")

        if length_type_id:
            # next 11 bits are number of subpackets
            num_subpackets = reader.read(11)
            # print(f"{num_subpackets=:011b}={num_subpackets}")

            # Interpret everything after this as subpackets
            subpacket_generator = decode_packets(*reader.read_remaining())

            p = Packet(
                version,
                type_id,
                subpackets=islice(subpacket_generator, num_subpackets),
            )
            # print(p)
            yield p

            # Everything after this isn't a subpacket, it's a sibling
            yield from subpacket_generator
        else:
            # next 15 bits are length of subpackets
            length_subpackets = reader.read(15)
            # print(f"{length_subpackets=:015b}={length_subpackets}")

            # We don't know how many are in there, but we know
            # the length we should interpret out of the rest
            subpacket_generator = decode_packets(
                reader.read(length_subpackets), length_subpackets
            )

            p = Packet(
                version,
                type_id,
                subpackets=subpacket_generator,
            )

            # print(p)
            yield p

            # If there is more left, parse that out too
            remaining, len_remaining = reader.read_remaining()
            if remaining and len_remaining:
                yield from decode_packets(remaining, len_remaining)


def packet_from_lines(lines: Iterable[str]) -> Packet:
    line = list(lines)[0].strip()  # only ever one line in this puzzle
    packets = list(decode_packets(int(line, base=16), 4 * len(line)))
    return packets[0]  # only one top-level packet


def part_one(lines: Iterable[str]) -> int:
    packet = packet_from_lines(lines)
    return packet.version_sum


def part_two(lines: Iterable[str]) -> int:
    packet = packet_from_lines(lines)

    return packet.value
