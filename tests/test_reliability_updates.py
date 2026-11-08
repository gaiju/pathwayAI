import ast
import base64
from concurrent.futures import ThreadPoolExecutor
import hashlib
import hmac
import ipaddress
import json
import math
import os
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import time
from types import SimpleNamespace
import unittest
import urllib.request
import urllib.error
from unittest.mock import patch
from PIL import Image
from ai_service_status import safe_ai_failure_message, AI_UNAVAILABLE_MESSAGE
from visual_assets import PHOTO_FILES, photo_data_uri, load_nys_boundaries

APP=Path(__file__).resolve().parents[1]/'app.py'
TREE=ast.parse(APP.read_text())

def functions(*names, **extra):
    nodes=[n for n in TREE.body if isinstance(n,ast.FunctionDef) and n.name in names]
    scope=dict(os=os,ipaddress=ipaddress,hmac=hmac,hashlib=hashlib,math=math,
               sqlite3=sqlite3,time=time,AI_WINDOW_SECONDS=1800,
               AI_WINDOW_MAX_REQUESTS=3,AI_SERVER_WINDOW_SECONDS=3600,
               AI_SERVER_MAX_REQUESTS=60,OPENAI_API_KEY='fake-only',**extra)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(APP),'exec'),scope)
    return scope

class ReliabilityUpdatesTests(unittest.TestCase):
    def test_unknown_connections_use_separate_stable_session_buckets(self):
        first=SimpleNamespace(context=SimpleNamespace(ip_address=None),session_state={})
        second=SimpleNamespace(context=SimpleNamespace(ip_address=None),session_state={})
        a=functions('_ai_bucket',st=first)['_ai_bucket']
        b=functions('_ai_bucket',st=second)['_ai_bucket']
        self.assertEqual(a(),a())
        self.assertNotEqual(a(),b())
        first.context.ip_address='invalid'
        self.assertEqual(a(),a())
        first.context.ip_address='192.0.2.1';second.context.ip_address='192.0.2.1'
        self.assertEqual(a(),b())
        self.assertNotIn('192.0.2.1',a())

    def test_bucket_and_server_windows_and_expiry_are_distinct(self):
        scope=functions('_ai_quota');scope['AI_SERVER_MAX_REQUESTS']=4
        check=scope['_ai_quota']
        with tempfile.TemporaryDirectory() as directory:
            db=Path(directory)/'quota.sqlite'
            for _ in range(3):self.assertTrue(check(db,'one',consume=True,now=1000)[0])
            self.assertFalse(check(db,'one',consume=True,now=1001)[0])
            self.assertTrue(check(db,'two',consume=True,now=1001)[0])
            self.assertFalse(check(db,'three',consume=True,now=1002)[0])
            # Bucket window expires, but server window does not yet expire.
            self.assertFalse(check(db,'one',consume=True,now=2801)[0])
            self.assertTrue(check(db,'one',consume=True,now=4602)[0])
            with sqlite3.connect(db) as conn:
                self.assertEqual(conn.execute('select count(*) from ai_requests').fetchone()[0],1)

    def test_atomic_shared_server_ceiling_across_sessions(self):
        scope=functions('_ai_quota');scope['AI_SERVER_MAX_REQUESTS']=4
        check=scope['_ai_quota']
        with tempfile.TemporaryDirectory() as directory:
            db=Path(directory)/'quota.sqlite'
            check(db,'init',now=1000)
            with ThreadPoolExecutor(max_workers=8) as pool:
                results=list(pool.map(lambda n:check(db,str(n),consume=True,now=1000)[0],range(12)))
            self.assertEqual(sum(results),4)

    def test_public_errors_and_logs_never_include_exception_text(self):
        for error in [ValueError('PATIENT_NOTE SECRET_KEY'),RuntimeError('PATIENT_NOTE SECRET_KEY')]:
            with self.assertLogs('pathwayai.ai_service',level='WARNING') as capture:
                message=safe_ai_failure_message(error)
            self.assertEqual(message,AI_UNAVAILABLE_MESSAGE)
            self.assertNotIn('PATIENT_NOTE',' '.join(capture.output))
            self.assertNotIn('SECRET_KEY',' '.join(capture.output))

    def test_assets_keep_alt_text_and_identical_map_geometry(self):
        original=subprocess.check_output(['git','show','aaecdc4:app.py'],cwd=APP.parent,text=True)
        tree=ast.parse(original)
        boundary=next(n for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='NYS_MAP_BOUNDARIES')
        self.assertEqual(load_nys_boundaries(),json.loads(ast.literal_eval(boundary.value.args[0])))
        self.assertIs(load_nys_boundaries(),load_nys_boundaries())
        for key,path in PHOTO_FILES.items():
            with Image.open(path) as image:self.assertLessEqual(image.width,1200)
            self.assertEqual(base64.b64decode(photo_data_uri(key).split(',',1)[1]),path.read_bytes())
        self.assertIsNone(photo_data_uri('../../secret'))
        self.assertNotIn('PATHWAY_PHOTOS116',APP.read_text())
        scope=functions('show_photo116',st=SimpleNamespace(markdown=lambda *a,**k:None))
        import html
        scope['html']=html
        calls=[];scope['st'].markdown=lambda value,**kwargs:calls.append(value)
        scope['show_photo116']('forest','Woodland <trail>')
        self.assertEqual(calls[0].count('<img '),1)
        self.assertIn('alt="Woodland &lt;trail&gt;"',calls[0])
        self.assertNotIn('--pathway-photo',calls[0])
        hero=next(n for n in TREE.body if isinstance(n,ast.FunctionDef) and n.name=='show_section_hero')
        self.assertIn("aria-hidden='true'",ast.get_source_segment(APP.read_text(),hero))

    def test_existing_ai_paths_use_safe_failure_messages(self):
        class LimitError(RuntimeError):pass
        def fail(*args,**kwargs):raise ValueError('SECRET_KEY PATIENT_NOTE')
        scope=functions('_safe_ai_failure_message','_openai_text_request',
                        'extract_story_with_llm','agent_search_live_evidence',
                        AIRateLimitError=LimitError,safe_ai_failure_message=safe_ai_failure_message,
                        urllib=urllib,json=json,PATHWAYAI_LLM_MODEL='fake',
                        _limited_ai_urlopen=fail)
        for name,args in [('_openai_text_request',('System','PATIENT_NOTE')),
                          ('extract_story_with_llm',('PATIENT_NOTE',)),
                          ('agent_search_live_evidence',('Public question',))]:
            with self.subTest(name=name):
                with self.assertLogs('pathwayai.ai_service',level='WARNING') as capture:
                    result=scope[name](*args)
                self.assertNotIn('SECRET_KEY',str(result))
                self.assertNotIn('PATIENT_NOTE',str(result))
                self.assertIn(AI_UNAVAILABLE_MESSAGE,str(result))
                self.assertNotIn('PATIENT_NOTE',' '.join(capture.output))
