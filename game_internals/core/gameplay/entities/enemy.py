from game_internals.core.gameplay.entities.entity import Entity 

class Enemy(Entity):
    def __init__(
        self,
        name: str,
        hp: int | float,
        attack: int | float,
        speed: int | float,
        coins_loot: int = 0
    ):
        super().__init__(name=name, hp=hp, attack=attack, speed=speed)
        # for this class
        self.current_hp = self.base_hp  
        self.current_attack = self.base_attack
        self.current_speed = self.base_speed

        self.coins_loot = coins_loot


    def die(self) -> int:
        """
        can't pass player as argument and add coins - severe SoC violation
        """
        return self.coins_loot