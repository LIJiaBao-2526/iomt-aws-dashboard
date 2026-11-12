import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from mqtt_bridge import convert, frame, packet


class BytesSocket:
    def __init__(self,data):self.data=data
    def recv(self,size):
        size=min(size,2);chunk=self.data[:size];self.data=self.data[size:];return chunk


class MQTTTests(unittest.TestCase):
    def test_fragmented_multi_byte_frame(self):
        body=b'x'*300
        self.assertEqual(packet(BytesSocket(frame(0x30,body))),(0x30,body))

    def test_bad_or_oversized_frame(self):
        for raw in [b'\x30\xff\xff\xff\xff',frame(0x30,b'x'*4097),b'\x30\x03x']:
            with self.subTest(raw=raw[:5]),self.assertRaises((ValueError,ConnectionError)):packet(BytesSocket(raw))

    def test_synthetic_input_only(self):
        self.assertEqual(convert(b'{"heart_rate":120,"synthetic":true}')['heart_rate'],120)
        for body in [{'heart_rate':120,'synthetic':False},{'heart_rate':True,'synthetic':True},{'heart_rate':151,'synthetic':True},{'heart_rate':float('nan'),'synthetic':True}]:
            with self.subTest(body=body),self.assertRaises(ValueError):convert(json.dumps(body).encode())


if __name__=='__main__':unittest.main()
