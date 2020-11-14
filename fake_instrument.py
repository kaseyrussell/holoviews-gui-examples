"""
fake_instrument.py --

A mock instrument that returns a random value when queried.
"""
import numpy as np


class FakeInstrument(object):
    def __init__(self, offset=0.0):
        self.offset = offset

    def set_offset(self, value):
        self.offset = value

    def read_data(self):
        return np.random.random() + self.offset
