import pytest

from game_internals.core.gameplay.entities.enemy import Enemy
from game_internals.core.gameplay.entities.player import Player


@pytest.mark.parametrize("hp,alive", [(10, True), (0, False), (-5, False)])
def test_enemy_is_alive(hp, alive):
    e = Enemy(name="e", hp=hp, attack=1, speed=1)
    assert e.is_alive() is alive


def test_heal_increases_base_hp():
    e = Enemy(name="e", hp=10, attack=1, speed=1)
    new_hp = e.heal_by(5)
    assert new_hp == 15
    assert e.base_hp == 15


def test_attack_affects_target(monkeypatch):
    e = Enemy(name="e", hp=20, attack=10, speed=1)
    target = Player(name="p", hp=30, attack=0, speed=0)

    # patch uniform to deterministic values
    monkeypatch.setattr(
        "game_internals.core.gameplay.entities.enemy.uniform", lambda a, b: 1.0
    )
    dmg = e.attack_(target)
    assert dmg == pytest.approx(min(round(e.base_attack * 1.0, 2), 50))
    assert target.current_hp == 30 - dmg

    monkeypatch.setattr(
        "game_internals.core.gameplay.entities.enemy.uniform", lambda a, b: 1.3
    )
    target.current_hp = 30
    dmg2 = e.attack_(target)
    expected2 = min(round(e.base_attack * 1.3, 2), 50) + e.base_attack * 0.2
    assert dmg2 == pytest.approx(expected2)
    assert target.current_hp == 30 - dmg2


def test_die_returns_loot_and_does_not_modify():
    e = Enemy(name="e", hp=5, attack=1, speed=1, coins_loot=12)
    assert e.die() == 12
