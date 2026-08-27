from rss.schema import from_jsonl
from rss.normalize import RSSConfig, normalize_base_metrics
from rss.metrics import compute_base_metrics
from rss.subscores import compute_subscores
from rss.composite import compute_rss

def test_metrics_pipeline_smoke():
    eps = []
    eps.extend(from_jsonl("examples/traces/minimal_single_agent.jsonl"))
    eps.extend(from_jsonl("examples/traces/minimal_replay_group.jsonl"))
    eps.extend(from_jsonl("examples/traces/minimal_multi_agent.jsonl"))

    cfg = RSSConfig()
    base = compute_base_metrics(eps, cfg)
    norm = normalize_base_metrics(base, cfg)

    applicability = {
        "multi_agent": any(k in base for k in ("AR","RRS","AC")),
        "counterfactual": any(k in base for k in ("RC","CSI","CT")),
    }
    subs = compute_subscores(norm, cfg, applicability)
    rss, w_eff = compute_rss(subs, cfg, applicability)

    assert 0.0 <= rss <= 1.0
    assert "S_T" in subs and "S_L" in subs and "S_A" in subs
