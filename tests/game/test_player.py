import pytest

from game_internals.core.gameplay.entities.player import Player

# ── helpers -----------------------------------------------------------------


def _attach_multiplier(item, attr: str, value: float) -> None:
    """Pydantic models normally forbid new attributes; bypass for tests."""
    object.__setattr__(item, attr, value)


# ── basic properties -------------------------------------------------------


def test_initial_totals_equal_base_stats(player: Player):
    assert player.total_hp == player.base_hp
    assert player.total_attack == player.base_attack
    assert player.total_speed == player.base_speed


def test_total_hp_additive_and_multiplicative(player: Player, gear_factory):
    base = player.base_hp
    g1 = gear_factory(slot="helmet", hp_add=10)
    g2 = gear_factory(slot="chestplate", hp_add=5)
    _attach_multiplier(g2, "hp_multiply", 2)  # not part of the schema
    player.equip(g1)
    player.equip(g2)
    # (base + 10 + 5) * 2
    assert player.total_hp == pytest.approx((base + 15) * 2)


def test_total_attack_and_speed_behave_similarly(player: Player, gear_factory):
    base_a = player.base_attack
    base_s = player.base_speed
    gear_a = gear_factory(slot="boots", speed_add=3)
    _attach_multiplier(gear_a, "speed_multiply", 4)
    player.equip(gear_a)

    assert player.total_speed == pytest.approx((base_s + 3) * 4)

    gear_atk = gear_factory(slot="leggings", hp_add=0)
    _attach_multiplier(gear_atk, "attack_multiply", 5)
    player.equip(gear_atk)
    assert player.total_attack == pytest.approx(base_a * 5)


# ── equipping logic --------------------------------------------------------


def test_equip_weapon_clears_other_weapon_slots(player: Player, weapon_factory):
    w1 = weapon_factory("one-handed", attack_add=5)
    w2 = weapon_factory("two-handed", attack_add=10)
    player.equip(w1)
    assert player.equipped["one-handed"] is w1
    player.equip(w2)
    assert player.equipped["one-handed"] is None
    assert player.equipped["two-handed"] is w2
    assert player.equipped["shield"] is None

    # equipping a shield also wipes the other weapon slots
    shield = weapon_factory("shield", hp_add=3)
    player.equip(w1)
    player.equip(shield)
    assert player.equipped["one-handed"] is None
    assert player.equipped["shield"] is shield


def test_equip_accessory_does_not_touch_weapons(
    player: Player, weapon_factory, accessory_factory
):
    w = weapon_factory("one-handed")
    ring = accessory_factory()
    player.equip(w)
    player.equip(ring)
    assert player.equipped["one-handed"] is w
    assert player.equipped["finger"] is ring


def test_replacing_same_slot_overwrites(player: Player, gear_factory):
    h1 = gear_factory(slot="helmet", hp_add=1)
    h2 = gear_factory(slot="helmet", hp_add=2)
    player.equip(h1)
    player.equip(h2)
    assert player.equipped["helmet"] is h2


def test_equip_returns_true(player: Player, gear_factory):
    assert player.equip(gear_factory()) is True


# ── miscellaneous helpers --------------------------------------------------


def test_mount_floor_and_add_coins(player: Player):
    assert player.mount_floor() == 1
    assert player.mount_floor(3) == 4
    assert player.add_coins(5) == 5
    assert player.add_coins(10) == 15


@pytest.mark.parametrize(
    "runs,expected",
    [
        ([120], 120),
        ([120, 130], 120),
        ([120, 100], 100),
        ([200, 150, 180], 150),
    ],
)
def test_eval_runtime_updates_best(runs, expected, player: Player):
    for r in runs:
        got = player.eval_runtime(r)
    assert got == expected
    assert player.best_run == expected


def test_is_alive_and_heal(player: Player):
    # down to zero or below => not alive
    player.current_hp = 0
    assert not player.is_alive()
    player.current_hp = -5
    assert not player.is_alive()

    # heal should not exceed base_hp and should change current_hp only
    player.current_hp = 10
    healed = player.heal_by(20)
    assert healed == 30  # 10 + 20, capped by base_hp which is 100
    assert player.current_hp == 30


def test_attack_reduces_target_hp(monkeypatch, player: Player):
    # use a simple dummy target with hp fields
    from game_internals.core.gameplay.entities.entity import Entity

    class Dummy(Entity):
        def is_alive(self):
            return True

        def heal_by(self):
            pass

        def attack_(self):
            pass

        def die(self):
            pass

    target = Dummy(name="t", hp=50, attack=0, speed=0)  # start with 50 hp

    # patch uniform to a predictable value (no crit)
    monkeypatch.setattr(
        "game_internals.core.gameplay.entities.player.uniform", lambda a, b: 1.0
    )
    dmg = player.attack_(target)
    assert dmg == pytest.approx(min(round(player.current_attack * 1.0, 2), 50))
    assert target.current_hp == 50 - dmg

    # patch for critical hit
    monkeypatch.setattr(
        "game_internals.core.gameplay.entities.player.uniform", lambda a, b: 1.3
    )
    target.current_hp = 50
    dmg2 = player.attack_(target)
    # crit adds 20% of base_attack
    expected2 = (
        min(round(player.current_attack * 1.3, 2), 50) + player.base_attack * 0.2
    )
    assert dmg2 == pytest.approx(expected2)


def test_die_resets_floor_and_records_run(player: Player):
    player.floor = 5
    result = player.die(123.4)
    # die returns nothing; effect is side‑effects
    assert player.floor == 0
    assert player.best_run == 123.4
