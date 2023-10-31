import struct


def test_write_bin_data():
    print(struct.pack("i", 1,2,3))