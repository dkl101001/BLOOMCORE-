# SPDX-License-Identifier: AGPL-3.0-only
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
import urllib.error
import pytest


@pytest.fixture
def endpoint(tmp_path):
    with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
    proc=subprocess.Popen([sys.executable,'-m','tiagi83','--state',str(tmp_path/'work.sqlite'),'--port',str(port),'--backend','numpy'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    base=f'http://127.0.0.1:{port}'
    for _ in range(80):
        try:
            with urllib.request.urlopen(base+'/api/bootstrap',timeout=.2) as r:b=json.load(r)
            break
        except OSError:time.sleep(.05)
    else:
        proc.terminate();raise RuntimeError('Server failed to start')
    yield base,b
    proc.terminate();proc.wait(timeout=5)


def test_http_workflow_and_session(endpoint):
    base,b=endpoint
    def post(path,data,token=b['token'],**headers):
        req=urllib.request.Request(base+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json','X-TI-Token':token,**headers})
        with urllib.request.urlopen(req) as r:return json.load(r)
    with pytest.raises(urllib.error.HTTPError) as e:post('/api/audit',{'id':1},token='wrong')
    assert e.value.code==403
    with pytest.raises(urllib.error.HTTPError) as e:post('/api/audit',{'id':1},Origin='https://elsewhere.example')
    assert e.value.code==403
    a=post('/api/audit',{'id':1});assert a['findings'][0]['fix']=='32.00'
    r=post('/api/repair',{'id':1,'audit_id':a['audit_id'],'signature':a['signature']})
    assert r['sheet']['rows'][1][3]=='32.00'
    with urllib.request.urlopen(base+'/api/export') as res:assert json.load(res)['receipt']['integrity']=='PASS'


def test_http_rejects_bad_host_and_schema(endpoint):
    base,b=endpoint
    req=urllib.request.Request(base+'/api/bootstrap',headers={'Host':'foreign.example'})
    with pytest.raises(urllib.error.HTTPError) as e:urllib.request.urlopen(req)
    assert e.value.code==403
    req=urllib.request.Request(base+'/api/import',data=json.dumps({'schema':'invoice','csv':'bad','name':'x'}).encode(),headers={'X-TI-Token':b['token']})
    with pytest.raises(urllib.error.HTTPError) as e:urllib.request.urlopen(req)
    assert e.value.code==400
