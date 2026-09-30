# SPDX-License-Identifier: AGPL-3.0-only
import copy
import json
import sqlite3
import numpy as np
import pytest
from tiagi83.audit import audit, parse_csv, export_csv
from tiagi83.store import Store, digest
from tiagi83 import geometry as g


def test_half_cent_is_decimal_half_up():
    r=audit('tax',[['Test','0.50','0.01','0.50']])
    assert r['findings'][0]['fix']=='0.51'
    assert audit('invoice',[['x','3','0.10','0.30']])['findings']==[]


@pytest.mark.parametrize('value',['','nan','inf','1e3','1,000','1.000000001','=1+1'])
def test_no_fabricated_input(value):
    r=audit('invoice',[['x',value,'8','12']])
    assert r['findings'] and all(f['fix'] is None for f in r['findings'])


@pytest.mark.parametrize('schema,row',[
    ('invoice',['x','-1','5','-5']),('invoice',['x','1.5','5','7.5']),
    ('invoice',['x','2','1.005','2.01']),('inventory',['x','2','3','-1']),
    ('inventory',['x','2.5','1','1.5']),('tax',['x','5','7','40']),
    ('tax',['x','5.001','.1','5.50']),])
def test_invalid_row_never_gets_an_arithmetic_repair(schema,row):
    r=audit(schema,[row]);assert r['findings'];assert not any(f['fix'] for f in r['findings'])


def test_exact_subcent_total_is_not_hidden():
    assert audit('invoice',[['x','1','1.00','1.001']])['findings'][0]['fix']=='1.00'


def test_csv_quotes_headers_and_formula_export():
    rows=parse_csv('Item,Qty,Unit price,Line total\r\n"A, B",2,4,8\r\n','invoice')
    assert rows[0][0]=='A, B'
    assert parse_csv(export_csv('invoice',rows),'invoice')==rows
    with pytest.raises(ValueError):parse_csv('Wrong,Qty,Unit price,Line total\nx,1,1,1','invoice')
    assert "'=cmd" in export_csv('invoice',[['=cmd','1','2','2']])


def test_audit_repair_undo_and_restart(tmp_path):
    p=tmp_path/'work.sqlite';s=Store(p,'numpy')
    a=s.run_audit(1);assert len(a['findings'])==1
    tick=s.state('invoice')['tick']
    assert s.run_audit(1)['duplicate_observation']
    assert s.state('invoice')['tick']==tick
    r=s.repair(1,a['audit_id'],a['signature']);assert r['sheet']['rows'][1][3]=='32.00'
    geometry_before=copy.deepcopy(s.state('invoice'))
    restored=s.undo(1,r['sheet']['signature']);assert restored['rows'][1][3]=='36.00'
    assert s.state('invoice')==geometry_before
    s.verify();s.close();s=Store(p,'numpy')
    assert s.state('invoice')==geometry_before
    assert s.sheet(1)['rows'][1][3]=='36.00';s.close()


def test_stale_repair_cannot_mutate(tmp_path):
    s=Store(tmp_path/'work.sqlite','numpy');a=s.run_audit(1);sheet=s.sheet(1)
    rows=copy.deepcopy(sheet['rows']);rows[1][1]='5';s.save(1,rows,sheet['signature'])
    before=s.export()
    with pytest.raises(ValueError,match='Fresh audit'):s.repair(1,a['audit_id'],a['signature'])
    assert s.export()==before;s.close()


def test_transaction_failure_rolls_back_all_surfaces(tmp_path):
    s=Store(tmp_path/'work.sqlite','numpy');before=s.export()
    s.db.execute("CREATE TRIGGER fail_event BEFORE INSERT ON events BEGIN SELECT RAISE(ABORT,'injected'); END;")
    with pytest.raises(sqlite3.IntegrityError):s.run_audit(1)
    assert s.export()==before;s.close()


def test_useful_related_incident_reaches_workflow(tmp_path):
    s=Store(tmp_path/'work.sqlite','numpy');a=s.run_audit(1);s.repair(1,a['audit_id'],a['signature'])
    sheet=s.import_sheet('invoice','Item,Qty,Unit price,Line total\nReplacement cable,5,8,44\n','another task')
    a=s.run_audit(sheet['id']);hit=a['findings'][0]['memory']['hits'][0]
    assert hit['repaired'] and '32.00' in hit['message']
    assert a['findings'][0]['fix']=='40.00' # history cannot overwrite current arithmetic
    assert a['findings'][0]['memory']['response_delta']>0
    assert hit['distance']!=hit['flat_distance'];s.close()


def test_geometry_is_independent_of_receipts(tmp_path):
    s=Store(tmp_path/'work.sqlite','numpy');s.run_audit(1)
    state=s.state('invoice');q=g.pattern({'kind':'arithmetic','col':3,'relative':.2,'delta':-1})
    response=g.response(state,q)
    # Test copy, not source: remove records and show substrate response survives.
    s.db.execute('DELETE FROM incidents');s.db.execute('DELETE FROM audits');s.db.execute('DELETE FROM events');s.db.commit()
    assert np.array_equal(response,g.response(s.state('invoice'),q))
    assert not s.candidates('invoice');s.close()


def test_history_fixed_geometry_ablation_changes_retrieval():
    f={'kind':'arithmetic','col':3,'relative':.2,'delta':-1,'message':'a'}
    c={'id':1,'finding':{**f,'relative':.5},'at':'test','repaired':False}
    state=g.initial()
    for _ in range(12):state=g.encounter(state,g.pattern(f))
    before=copy.deepcopy(state);r=g.related(state,f,[c]);flat=g.related(g.initial(),f,[c])
    assert r['hits'][0]['distance']!=flat['hits'][0]['distance']
    assert r['response_delta']>0 and state==before


def test_quiet_geometry_and_zero_control():
    state=g.initial();u=g.pattern({'kind':'format','col':2,'delta':0,'relative':0})
    learned=g.encounter(state,u);quiet=g.encounter(learned,np.zeros((8,8)))
    assert learned['px']==quiet['px'] and learned['py']==quiet['py']
    assert g.response(learned,u,flat=True).tolist()==g.response(state,u).tolist()


def test_reference_equations_and_backend_parity():
    pytest.importorskip('jax')
    rng=np.random.default_rng(83);u=rng.uniform(-1,1,(8,8)).astype('float32');s=g.initial()
    px=np.asarray(s['px'],dtype='float32'); expected=px+.04*abs(u-np.roll(u,-1,axis=0))*(2-px)
    n=g.encounter(s,u,'numpy');j=g.encounter(s,u,'jax')
    assert np.array_equal(np.asarray(n['px']),expected)
    assert np.allclose(n['px'],j['px'],atol=3e-6,rtol=3e-5)
    assert np.allclose(g.response(n,u,'numpy'),g.response(n,u,'jax'),atol=3e-6,rtol=3e-5)


def test_geometry_corruption_is_detected(tmp_path):
    p=tmp_path/'work.sqlite';s=Store(p,'numpy');s.run_audit(1)
    s.db.execute("UPDATE geometry SET hash='bad'");s.db.commit();s.close()
    with pytest.raises(ValueError,match='integrity'):Store(p,'numpy')


def test_receipt_corruption_is_detected(tmp_path):
    p=tmp_path/'work.sqlite';s=Store(p,'numpy');s.run_audit(1)
    s.db.execute("UPDATE events SET payload='{}' WHERE id=2");s.db.commit();s.close()
    with pytest.raises(ValueError,match='integrity'):Store(p,'numpy')


def test_scopes_do_not_cross(tmp_path):
    s=Store(tmp_path/'work.sqlite','numpy');s.run_audit(1)
    assert s.state('invoice')['tick']==1 and s.state('inventory')['tick']==0
    assert not s.candidates('inventory');s.close()
