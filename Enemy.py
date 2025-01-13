import json
import Event
import Effect
import Card


class Enemy:
    def __init__(self, name, health, level):
        self.name = name
        self.health = health
        self.level = level
        self.stunned = False
        self.description = None
        self.reward_text = None

    def render(self, screen):
        pass

    def apply_effect(self, event, game_state):
        if self.stunned:
            print(f"{self.name} is stunned")
            return

        if event is None:
            self._execute_active(event, game_state)
        else:
            self._execute_passive(event, game_state)

    def _execute_active(self, event, game_state):
        pass

    def _execute_passive(self, event, game_state):
        pass

    def apply_reward(self, event, game_state):
        pass


class Draco(Enemy):
    def __init__(self):
        super().__init__('Draco Malfoy', 6, 1)

    def _execute_passive(self, event, game_state):
        if not isinstance(event, Event.SkullPlacedEvent):
            return

        game_state.apply_effect(Effect.DamageEffect(2), self, game_state.current_player)

    def apply_reward(self, event, game_state):
        # TODO
        pass


class CrabbeGoyle(Enemy):
    def __init__(self):
        super().__init__("Crabbe & Goyle", 5, 1)

    def _execute_passive(self, event, game_state):
        if not isinstance(event, Event.CardDroppedEvent):
            return

        event_data = event.data
        source = event_data["source"]
        target = event_data["target"]

        if isinstance(source, Enemy) or isinstance(source, Card.DarkArtsCard):
            game_state.apply_effect(Effect.DamageEffect(1), self, target)

    def apply_reward(self, event, game_state):
        # TODO
        pass


class Quirrell(Enemy):
    def __init__(self):
        super().__init__("Quirinus Quirrell", 6, 1)

    def _execute_active(self, event, game_state):
        game_state.apply_effect(Effect.DamageEffect(1), self, game_state.current_player)

    def apply_reward(self, event, game_state):
        # TODO
        pass


def load_enemies(level):
    with open("enemies.json", "r", encoding="UTF-8") as f:
        enemies = []
        enemies_dict = json.load(f)
        for enemy in enemies_dict:
            if enemy["level"] <= level:
                enemy = load_enemy(enemy["name"])

                enemies.append(enemy)

        return enemies


def load_enemy(name):
    match name:
        case "Draco Malfoy":
            return Draco()
        case "Crabbe & Goyle":
            return CrabbeGoyle()
        case "Quirinus Quirrell":
            return Quirrell()
