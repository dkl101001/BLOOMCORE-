# SPDX-License-Identifier: AGPL-3.0-only
from dataclasses import asdict, replace
import importlib
import importlib.resources
import json
import math
import pytest
from bloomcore_governance_weave.cli import sample_proposal
from bloomcore_governance_weave.execution import describe_invocation
from bloomcore_governance_weave.model import WeaveConfig
from bloomcore_governance_weave.receipts import ReceiptChain, canonical_json
from bloomcore_governance_weave.weave import evaluate


@pytest.mark.parametrize('changes', [
    {'hdot_window': ()}, {'risk': math.nan}, {'coherence': math.inf},
    {'compassion': -math.inf}, {'rgb_drift': (1e308, 1e308, 1e308)},
    {'value_previous': -1e308, 'value_current': 1e308},
])
def test_invalid_and_overflow_receipts_remain_strict_json(changes):
    proposal = replace(sample_proposal(), **changes)
    chain = ReceiptChain()
    result = evaluate(proposal, receipts=chain)
    assert result.status == 'SUPPRESS_EXPRESSION'
    assert result.numeric_residue
    assert result.veil_pressure is None
    json.dumps(asdict(result), allow_nan=False)
    restored = ReceiptChain(head=chain.head, receipts=json.loads(canonical_json(chain.receipts)))
    assert restored.verify()
    assert restored.receipts[0]['kind'] == 'GOVERNANCE_WEAVE.WITNESS.v2'
    second = ReceiptChain()
    evaluate(proposal, receipts=second)
    assert second.head == chain.head


def test_input_classification_survives_null_projection():
    chain = ReceiptChain()
    result = evaluate(replace(sample_proposal(), risk=math.nan), receipts=chain)
    assert result.numeric_residue['/proposal/risk'] == 'NaN'
    assert chain.receipts[0]['payload']['input_projection']['proposal']['risk'] is None


def test_invalid_configuration_is_not_clearance():
    result = evaluate(sample_proposal(), cfg=replace(WeaveConfig(), wisdom_threshold=math.inf))
    assert result.status == 'SUPPRESS_EXPRESSION'
    assert result.numeric_residue['/config/wisdom_threshold'] == '+Infinity'


def test_direct_nonfinite_receipt_is_rejected_without_mutation():
    chain = ReceiptChain()
    with pytest.raises(ValueError):
        chain.append('bad', {'value': math.nan})
    assert chain.receipts == []
    assert chain.head == '0' * 64


def test_receipt_snapshot_does_not_alias_caller_payload():
    chain = ReceiptChain()
    payload = {'nested': [1]}
    returned = chain.append('snapshot', payload)
    payload['nested'].append(2)
    returned['payload']['nested'].append(3)
    assert chain.verify()
    assert chain.receipts[0]['payload'] == {'nested': [1]}


def test_hybrid_reference_and_no_native_model_claim():
    root = importlib.resources.files('bloomcore_governance_weave')
    contract = json.loads(root.joinpath('hybrid_execution_object.json').read_text('utf-8'))
    assert contract['object_version'] == '0.2.0'
    assert contract['selected_reference']['sha256'] == '46f1592d80963c0129a92f134eff9e9136e4a04f6d300fa98494bbbad87e7f2b'
    assert contract['model_participation']['canonical_native_mode'] is None
    assert contract['model_participation']['native_model_zero_operation'] == 'NOT_IMPLEMENTED'
    assert not contract['native_state_mutation']
    axes = {'transition', 'recursion', 'exploration', 'scheduling', 'replay', 'persistence', 'mutation', 'authority'}
    for name in contract['profiles']:
        module, target = name.split(':')
        obj = importlib.import_module('bloomcore_governance_weave.' + module)
        for part in target.split('.'):
            obj = getattr(obj, part)
        assert callable(obj)
        witness = describe_invocation(name)
        assert axes <= witness['profile'].keys()
        assert {'budgets', 'failure', 'equality', 'unknown_influences'} <= witness['profile'].keys()
        assert all(len(value) == 64 for value in witness['code_sha256'].values())
        json.dumps(witness, allow_nan=False)


def test_finite_baseline_and_receipt_presence_do_not_change_decision():
    proposal = sample_proposal()
    assert asdict(evaluate(proposal)) == asdict(evaluate(proposal, receipts=ReceiptChain()))
    assert evaluate(proposal).numeric_residue == {}
