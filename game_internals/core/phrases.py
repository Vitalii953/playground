"""
everything here is gonna be loaded in cache as soon as the app starts
then users will be refreshing them(hopefully)
"""

PHRASES = {
    "events": {
        "random_item": "You found a {item_name}!",
        "add_coins": "You found {amount} coins!",
        "floor_up": "There's nothing here. You ascend to the next floor, twice!",
        "floor_down": "You fell down a floor! But you recovered and found another way up!",
        "summon_enemy": "An enemy stepped ouf of the dark: {enemy}",
        "poison": "You stepped on a trap and got poisoned! {HP} HP lost",
        "heal": "You found a healing fountain and restored {amount} HP!",
    },
    "game_loop": {
        "player_dead": "You died! Better luck next time",
        "enemy_dead": "You survived! Enemy is dead",
        "hit_enemy": "You hit the enemy, they lost ",  # the phrase is naturally continued
        "hit_player": "The enemy hit you, you lost ",  # the phrase is naturally continued
        "pending_actions": {
            "equipped_successfully": "You equipped {item_name}!",
            "rejected_item": "You skipped {item_name}!",
        }
    },
}
