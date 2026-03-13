"""
everything here is gonna be loaded in cache as soon as the app starts
then users will be refreshing them(hopefully)
"""

PHRASES = {
    "events": {
        "random_item": "You found a {item_name}!",
        "add_coins": "You found {amount} coins!",
        "floor_up": "You ascend to the next floor.",
        "floor_down": "You fell down a floor!",
        "summon_enemy": "An enemy stepped ouf of the dark: {enemy}",
        "poison": "You stepped on a trap and got poisoned! {HP} HP lost",
        "heal": "You found a healing fountain and restored {amount} HP!",
    },
}
