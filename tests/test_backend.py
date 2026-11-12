"""Assigned owner: KWOK Chun Ting. Regression and integration evidence."""
import io
import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from core import answer, retrieve, summarize, validate
from server import Handler, Store, ThreadingHTTPServer


def reading(rate=78, offset=0):
    return {'device_id': 'website-synthetic-demo', 'timestamp': (datetime.now(timezone.utc)+timedelta(seconds=offset)).isoformat(), 'heart_rate': rate, 'synthetic': True}


class CoreTests(unittest.TestCase):
    def test_timezone_normalization(self):
        row=reading();row['timestamp']='2026-10-08T10:00:00+08:00'
        self.assertEqual(validate(row)['timestamp'], '2026-10-08T02:00:00+00:00')

    def test_reject_invalid_readings(self):
        for value in [True, float('nan'),float('inf'),19,251,'78']:
            with self.subTest(value=value), self.assertRaises(ValueError):validate(reading(value))
        for changes in [{'synthetic':False},{'timestamp':'2026-01-01'},{'device_id':'../x'},{'timestamp':(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat()}]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):validate({**reading(),**changes})

    def test_rule_edges_and_gaps(self):
        self.assertTrue(summarize([reading(101,-120),reading(110,-60),reading(120)])['triggered'])
        self.assertFalse(summarize([reading(101,-120),reading(100,-60),reading(120)])['triggered'])
        self.assertFalse(summarize([reading(101,-1000),reading(110,-60),reading(120)])['triggered'])
        self.assertFalse(summarize([reading(110)])['triggered'])
        self.assertFalse(summarize([])['triggered'])

    def test_retrieval_and_unsupported_question(self):
        self.assertEqual(retrieve('AWS 系統流程')[0]['id'], 'system')
        self.assertEqual(retrieve('quantum pineapple'), [])
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY':''}):
            result=answer('量測規則', [reading()])
            self.assertFalse(result['ai_connected'])
            self.assertTrue(result['sources'])

    def test_deepseek_adapter_and_safe_failure(self):
        captured=[]
        def fake(req,timeout):
            captured.append(json.loads(req.data))
            return io.BytesIO(json.dumps({'choices':[{'message':{'content':'合成資料摘要 [rule]'}}]}).encode())
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY':'unit-test-placeholder'}):
            good=answer('心率規則',[reading()],opener=fake)
            self.assertEqual(good['mode'],'deepseek')
            self.assertNotIn('device_id',json.dumps(captured))
            self.assertIn('synthetic_summary',captured[0]['messages'][1]['content'])
            def fail(*a,**kw):raise RuntimeError('private upstream detail')
            bad=answer('心率規則',[reading()],opener=fail)
            self.assertEqual(bad['mode'],'retrieval')
            self.assertNotIn('private upstream detail',json.dumps(bad))


class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        Handler.store=Store(str(Path(cls.temp.name)/'test.db'))
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.base='http://127.0.0.1:'+str(cls.server.server_port)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join();cls.temp.cleanup()

    def request(self,path,body=None,headers=None):
        req=urllib.request.Request(self.base+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json',**(headers or {})})
        try:
            with urllib.request.urlopen(req) as res:return res.status,json.load(res)
        except urllib.error.HTTPError as e:return e.code,json.load(e)

    def test_persist_duplicate_conflict_and_query(self):
        row=reading()
        self.assertEqual(self.request('/api/readings',row)[0],201)
        self.assertEqual(self.request('/api/readings',row)[0],200)
        self.assertEqual(self.request('/api/readings',{**row,'heart_rate':79})[0],400)
        code,data=self.request('/api/demo')
        self.assertEqual(code,200);self.assertEqual(data['readings'][-1]['heart_rate'],78)
        reopened=Store(Handler.store.path)
        self.assertEqual(reopened.latest()[-1]['timestamp'],validate(row)['timestamp'])

    def test_cross_origin_and_invalid_input(self):
        self.assertEqual(self.request('/api/readings',reading(),{'Origin':'https://untrusted.example'})[0],403)
        self.assertEqual(self.request('/api/readings',{**reading(),'synthetic':False})[0],400)
        self.assertEqual(self.request('/api/readings',{**reading(),'device_id':'another-person'})[0],400)
        self.assertEqual(self.request('/api/no-such-route')[0],404)

    def test_assistant_and_empty_question(self):
        with patch.dict(os.environ,{'DEEPSEEK_API_KEY':''}):
            code,data=self.request('/api/analyze',{'question':'AWS 系統流程'})
            self.assertEqual(code,200);self.assertEqual(data['mode'],'retrieval')
            self.assertEqual(self.request('/api/analyze',{'question':''})[0],400)


if __name__=='__main__':unittest.main(verbosity=2)
