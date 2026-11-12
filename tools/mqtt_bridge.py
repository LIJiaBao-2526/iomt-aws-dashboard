"""LI Jia Bao: MQTT 3.1.1 QoS-0 subscriber -> existing loopback HTTP API.
No pip packages required. Public broker is for synthetic demos only.
"""
import argparse
import json
import math
import socket
import struct
import time
import urllib.request
import uuid
from datetime import datetime, timezone

TOPIC = 'pulse-demo/7de953b4-7952-4b45-9fe8-895df7dd90fc/heart-rate'


def utf8(text):
    raw=text.encode('utf-8')
    return struct.pack('!H',len(raw))+raw


def frame(kind, body):
    length=len(body);encoded=b''
    while True:
        byte=length%128;length//=128
        encoded+=bytes([byte|128 if length else byte])
        if not length:break
    return bytes([kind])+encoded+body


def exact(sock, size):
    result=b''
    while len(result)<size:
        chunk=sock.recv(size-len(result))
        if not chunk:raise ConnectionError('Broker disconnected')
        result+=chunk
    return result


def packet(sock):
    kind=exact(sock,1)[0];length=0;multiplier=1
    for _ in range(4):
        byte=exact(sock,1)[0];length+=(byte&127)*multiplier
        if not byte&128:break
        multiplier*=128
    else:raise ValueError('Invalid MQTT frame length')
    if length>4096:raise ValueError('Oversized MQTT frame')
    return kind,exact(sock,length)


def convert(raw):
    if len(raw)>512:raise ValueError('Oversized reading')
    body=json.loads(raw)
    if not isinstance(body,dict) or set(body)!={'heart_rate','synthetic'} or body['synthetic'] is not True:
        raise ValueError('Synthetic BPM message required')
    value=body['heart_rate']
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not 50<=value<=150:
        raise ValueError('Invalid synthetic BPM')
    return {'device_id':'website-synthetic-demo','timestamp':datetime.now(timezone.utc).isoformat(),
            'heart_rate':value,'synthetic':True}


def forward(raw, base_url):
    item=convert(raw)
    req=urllib.request.Request(base_url+'/api/readings',data=json.dumps(item).encode(),
        headers={'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req,timeout=5) as res:
        if res.status not in (200,201):raise ValueError('Local API rejected reading')
    return item


def subscribe(sock):
    client='pulse-bridge-'+uuid.uuid4().hex[:12]
    sock.sendall(frame(0x10,utf8('MQTT')+b'\x04\x02\x00\x1e'+utf8(client)))
    kind,body=packet(sock)
    if kind!=0x20 or body!=b'\x00\x00':raise ConnectionError('MQTT connection refused')
    sock.sendall(frame(0x82,b'\x00\x01'+utf8(TOPIC)+b'\x00'))
    kind,body=packet(sock)
    if kind!=0x90 or body!=b'\x00\x01\x00':raise ConnectionError('MQTT subscription refused')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--base-url',default='http://127.0.0.1:8877')
    parser.add_argument('--max-messages',type=int,default=0)
    args=parser.parse_args()
    from urllib.parse import urlparse
    parsed=urlparse(args.base_url)
    if parsed.scheme!='http' or parsed.hostname not in ('127.0.0.1','localhost') or parsed.path not in ('','/'):
        parser.error('Only loopback HTTP destinations are allowed')
    print('Synthetic data only. Public MQTT relay -> local SQLite API.',flush=True)
    count=0;last=0
    while True:
        try:
            with socket.create_connection(('broker.hivemq.com',1883),timeout=10) as sock:
                subscribe(sock);print('MQTT subscribed; start Wokwi and turn the knob.',flush=True)
                sock.settimeout(10);last_ping=time.monotonic()
                while True:
                    if time.monotonic()-last_ping>=15:
                        sock.sendall(b'\xc0\x00');last_ping=time.monotonic()
                    try:kind,body=packet(sock)
                    except socket.timeout:
                        sock.sendall(b'\xc0\x00');last_ping=time.monotonic();continue
                    if kind>>4!=3:continue
                    # Accept only non-retained QoS-0 publishes on the exact topic.
                    if kind&7 or len(body)<2:continue
                    size=struct.unpack('!H',body[:2])[0]
                    if len(body)<2+size or body[2:2+size]!=TOPIC.encode():continue
                    if time.monotonic()-last<1:continue
                    last=time.monotonic()
                    try:
                        item=forward(body[2+size:],args.base_url)
                        count+=1;print('STORED',item['heart_rate'],'bpm',item['timestamp'],flush=True)
                    except (ValueError,UnicodeError):
                        print('Ignored invalid synthetic message',flush=True);continue
                    if args.max_messages and count>=args.max_messages:return
        except KeyboardInterrupt:return
        except Exception as err:
            print('Connection or local API unavailable:',type(err).__name__,'retrying...',flush=True)
            time.sleep(3)


if __name__=='__main__':main()
