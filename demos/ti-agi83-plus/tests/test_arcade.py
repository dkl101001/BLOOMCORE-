# SPDX-License-Identifier: AGPL-3.0-only
import uuid
import pytest
from tiagi83.store import Store


def test_scores_restart_idempotency_and_work_isolation(tmp_path):
    path = tmp_path / 'work.sqlite'
    s = Store(path, 'numpy')
    s.run_audit(1)
    before = s.export()
    play = str(uuid.uuid4())
    result = s.record_game_score('snake', 20, play)
    assert result['games']['snake'] == {'best': 20, 'plays': 1}
    assert s.record_game_score('snake', 20, play) == result
    after = s.export()
    for key in ('sheets', 'geometry', 'incidents', 'audits'):
        assert after[key] == before[key]
    assert len(after['events']) == len(before['events']) + 1
    with pytest.raises(ValueError):
        s.record_game_score('snake', 30, play)
    s.close()
    s = Store(path, 'numpy')
    assert s.game_scores() == result
    assert s.verify()['integrity'] == 'PASS'
    s.close()


@pytest.mark.parametrize('game,score,play', [
    ('missing', 0, str(uuid.uuid4())), ('pong', True, str(uuid.uuid4())),
    ('snake', -1, str(uuid.uuid4())), ('blocks', 1.5, str(uuid.uuid4())),
    ('blocks', 1_000_000_001, str(uuid.uuid4())), ('snake', 0, 'broken'),
    ('snake', 0, None),
])
def test_invalid_scores(tmp_path, game, score, play):
    s = Store(tmp_path / 'work.sqlite', 'numpy')
    with pytest.raises((ValueError, TypeError)):
        s.record_game_score(game, score, play)
    assert s.export()['game_scores'] == []
    s.close()


def test_score_and_receipt_rollback_together(tmp_path):
    s = Store(tmp_path / 'work.sqlite', 'numpy')
    before = s.history()
    s.db.execute("CREATE TRIGGER stop_games BEFORE INSERT ON events WHEN NEW.type='game_complete' BEGIN SELECT RAISE(ABORT, 'test failure'); END;")
    with pytest.raises(Exception):
        s.record_game_score('pong', 5, str(uuid.uuid4()))
    assert s.export()['game_scores'] == []
    assert s.history() == before
    s.close()


def test_v02_database_additive_upgrade(tmp_path):
    path = tmp_path / 'work.sqlite'
    s = Store(path, 'numpy')
    s.run_audit(1)
    before = s.export()
    s.db.execute('DROP TABLE game_scores')
    s.db.commit()
    s.close()
    s = Store(path, 'numpy')
    assert s.export() == before
    assert s.game_scores()['games']['snake']['plays'] == 0
    s.close()
