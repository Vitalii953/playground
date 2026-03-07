class Item:
    """This turns equipment into actual objects"""

    def __init__(
        self,
        name: str,
        slot: str,
        attack_multiply: int | float = 1,
        attack_add: int | float = 0,
        hp_multiply: int | float = 1,
        hp_add: int | float = 0,
        speed: int | float = 0,
    ):
        self.name = name
        self.slot = slot
        self.attack_multiply = attack_multiply
        self.attack_add = attack_add
        self.hp_multiply = hp_multiply
        self.hp_add = hp_add
        self.speed = speed

    def __repr__(self):
        """For debugging purposes"""
        return f"{self.name} at {self.slot} with:\nattack_multiply: {self.attack_multiply};\nattack_add: {self.attack_add};\nhp_multiply: {self.hp_multiply};\nhp_add: {self.hp_add};\nspeed: {self.speed}"
