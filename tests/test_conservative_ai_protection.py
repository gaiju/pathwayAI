import ast
from concurrent.futures import ThreadPoolExecutor
import hashlib
import hmac
import ipaddress
import json
import math
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import urllib.request
import urllib.error
from ai_service_status import safe_ai_failure_message, AI_UNAVAILABLE_MESSAGE

APP=Path(__file__).resolve().parents[1]/'app.py'
SOURCE=APP.read_text();TREE=ast.parse(SOURCE)


def funcs(*names, **extra):
    nodes=[n for n in TREE.body if isinstance(n,ast.FunctionDef) and n.name in names]
    scope=dict(sqlite3=sqlite3,time=time,math=math,Path=Path,__file__=str(APP),
               AI_WINDOW_SECONDS=1800,AI_WINDOW_MAX_REQUESTS=3,
               AI_SERVER_WINDOW_SECONDS=3600,AI_SERVER_MAX_REQUESTS=4,
               hmac=hmac,hashlib=hashlib,ipaddress=ipaddress,OPENAI_API_KEY='fake-only',**extra)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(APP),'exec'),scope)
    return scope


class ConservativeProtectionTests(unittest.TestCase):
    def test_connection_policy_and_all_inline_photos_are_unchanged(self):
        baseline=ast.parse(subprocess.check_output(['git','show','aaecdc4:app.py'],cwd=APP.parent,text=True))
        old=next(n for n in baseline.body if isinstance(n,ast.FunctionDef) and n.name=='_ai_bucket')
        new=next(n for n in TREE.body if isinstance(n,ast.FunctionDef) and n.name=='_ai_bucket')
        self.assertEqual(ast.dump(old),ast.dump(new))
        def photos(tree):
            n=next(n for n in tree.body if isinstance(n,ast.Assign) and any(getattr(t,'id','')=='PATHWAY_PHOTOS116' for t in n.targets))
            return ast.literal_eval(n.value)
        self.assertEqual(photos(baseline),photos(TREE))
        a=SimpleNamespace(context=SimpleNamespace(ip_address=None),session_state={})
        b=SimpleNamespace(context=SimpleNamespace(ip_address=None),session_state={})
        self.assertEqual(funcs('_ai_bucket',st=a)['_ai_bucket'](),funcs('_ai_bucket',st=b)['_ai_bucket']())

    def test_connection_limit_server_limit_and_window_expiry(self):
        quota=funcs('_ai_quota')['_ai_quota']
        with tempfile.TemporaryDirectory() as directory:
            db=Path(directory)/'limits.sqlite'
            for _ in range(3):self.assertTrue(quota(db,'one',consume=True,now=1000)[0])
            self.assertFalse(quota(db,'one',consume=True,now=1001)[0])
            self.assertTrue(quota(db,'two',consume=True,now=1001)[0])
            self.assertFalse(quota(db,'three',consume=True,now=1002)[0])
            self.assertFalse(quota(db,'one',consume=True,now=2801)[0])
            self.assertTrue(quota(db,'one',consume=True,now=4602)[0])
            with sqlite3.connect(db) as conn:self.assertEqual(conn.execute('select count(*) from ai_requests').fetchone()[0],1)

    def test_atomic_server_ceiling_cannot_be_bypassed_by_many_buckets(self):
        quota=funcs('_ai_quota')['_ai_quota']
        with tempfile.TemporaryDirectory() as directory:
            db=Path(directory)/'limits.sqlite';quota(db,'init',now=1000)
            with ThreadPoolExecutor(max_workers=8) as pool:
                results=list(pool.map(lambda n:quota(db,str(n),consume=True,now=1000)[0],range(12)))
            self.assertEqual(sum(results),4)

    def test_blocked_session_and_service_limits_send_no_api_request(self):
        class LimitError(RuntimeError):pass
        state={'pathwayai_ai_calls':5}
        scope=funcs('_limited_ai_urlopen',st=SimpleNamespace(session_state=state),
                    MAX_AI_CALLS_PER_SESSION=5,AIRateLimitError=LimitError,
                    _ai_bucket=lambda:'bucket',_ai_quota=lambda *a,**kw:(False,'Service busy'),
                    urllib=urllib)
        with patch('urllib.request.urlopen') as opener:
            with self.assertRaises(LimitError):scope['_limited_ai_urlopen'](object())
            state['pathwayai_ai_calls']=0
            with self.assertRaises(LimitError):scope['_limited_ai_urlopen'](object())
            opener.assert_not_called()

    def test_safe_messages_across_existing_ai_routes(self):
        class LimitError(RuntimeError):pass
        def fail(*args,**kwargs):raise ValueError('SECRET_KEY PATIENT_NOTE')
        scope=funcs('_safe_ai_failure_message','_openai_text_request',
                    'extract_story_with_llm','agent_search_live_evidence',
                    AIRateLimitError=LimitError,safe_ai_failure_message=safe_ai_failure_message,
                    urllib=urllib,json=json,PATHWAYAI_LLM_MODEL='fake',_limited_ai_urlopen=fail)
        for name,args in [('_openai_text_request',('System','PATIENT_NOTE')),
                          ('extract_story_with_llm',('PATIENT_NOTE',)),
                          ('agent_search_live_evidence',('Public question',))]:
            with self.subTest(name=name):
                with self.assertLogs('pathwayai.ai_service',level='WARNING') as captured:
                    result=scope[name](*args)
                self.assertIn(AI_UNAVAILABLE_MESSAGE,str(result))
                for sentinel in ('SECRET_KEY','PATIENT_NOTE'):
                    self.assertNotIn(sentinel,str(result))
                    self.assertNotIn(sentinel,' '.join(captured.output))
