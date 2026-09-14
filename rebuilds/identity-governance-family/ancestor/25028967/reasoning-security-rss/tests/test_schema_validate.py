from rss.schema import from_jsonl
from rss.validate import validate_episodes

def test_validate_examples():
    eps = []
    for f in [
        "examples/traces/minimal_single_agent.jsonl",
        "examples/traces/minimal_replay_group.jsonl",
        "examples/traces/minimal_multi_agent.jsonl",
    ]:
        eps.extend(from_jsonl(f))
    errs = validate_episodes(eps)
    assert errs == []
