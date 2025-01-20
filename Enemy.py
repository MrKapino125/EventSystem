import json
import Event
import Effect
import Card
import pygame


class Enemy:
    def __init__(self, name, health, level, description, reward_text):
        self.name = name
        self.health = health
        self.level = level
        self.stunned = False
        self.is_dead = False
        self.description = description
        self.reward_text = reward_text
        self.pos = (0, 0)
        self.width = 500
        self.height = 250

    def render(self, screen):
        fill_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(fill_surface, (255, 255, 255, 128), (0, 0, self.width, self.height))

        screen.blit(fill_surface, (self.pos[0], self.pos[1]))

        pygame.draw.rect(screen, (255, 0, 0), (self.pos[0], self.pos[1], self.width, self.height), 2)

        text = self.name

        font_size = 20
        font = pygame.font.Font(None, font_size)
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            text_width, _ = font.size(test_line)
            if text_width <= self.width - 10:  # Add a small padding
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)  # Add the last line

        y_offset = 0
        line_spacing = 5  # spacing between lines
        for line in lines:
            text_surface = font.render(line, True, (255, 0, 0))
            text_rect = text_surface.get_rect(center=(self.pos[0] + self.width // 2,
                                                      self.pos[1] + self.height // 2 + y_offset - (len(lines) - 1) * (
                                                                  font_size + line_spacing) // 2))  # vertical align
            screen.blit(text_surface, text_rect)
            y_offset += font_size + line_spacing

        health_surface = font.render(str(self.health), True, (255, 0, 0))
        health_width = health_surface.get_width()
        health_height = health_surface.get_height()

        # Calculate the center x-coordinate of the box
        center_x = self.pos[0] + self.width // 2

        # Calculate the x-coordinate for centering the health surface
        health_x = center_x - health_width // 2

        # Calculate the y-coordinate just above the bottom line of the box
        health_y = self.pos[1] + self.height - health_height - self.height // 16

        screen.blit(health_surface, (health_x, health_y))



    def apply_damage_effect(self, amount, game_state):
        self.damage()

        if self.health <= 0:
            self.is_dead = True
            game_state.apply_effect(Effect.EnemyDeadEffect(), self, [None])

    def damage(self):
        self.health -= 1

    def is_hovering(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        rect_x, rect_y = self.pos
        rect_width, rect_height = self.width, self.height

        if (rect_x <= mouse_x <= rect_x + rect_width and
                rect_y <= mouse_y <= rect_y + rect_height):
            return True
        else:
            return False

    def apply_effect(self, event, game_state):
        if self.stunned:
            print(f"{self.name} is stunned")
            return

        if event is None:
            self._execute_active(game_state)
        else:
            self._execute_passive(event, game_state)

    def _execute_active(self, game_state):
        pass

    def _execute_passive(self, event, game_state):
        pass

    def apply_reward(self, game_state):
        pass


class Draco(Enemy):
    def __init__(self):
        super().__init__('Draco Malfoy', 6, 1,
                         "Jedes Mal, wenn Totenköpfe auf den Ort gelegt werden verliert der aktive Held 2 Herzen.",
                         "Entfernt 1 Totenkopf vom aktuellen Ort.")

    def _execute_passive(self, event, game_state):
        if not isinstance(event, Event.SkullPlacedEvent):
            return

        game_state.apply_effect(Effect.DamageEffect(2), self, [game_state.current_player])

    def apply_reward(self, game_state):
        game_state.apply_effect(Effect.RemoveSkullEffect(1), self, [None])


class CrabbeGoyle(Enemy):
    def __init__(self):
        super().__init__("Crabbe & Goyle", 5, 1,
                         "Jedes Mal, wenn ein Held durch eine Dunkle-Künste-Karte oder einen "
                         "Bösewicht eine Karte abwerfen muss, verliert dieser Held 1 Herz.",
                         "ALLE Helden ziehen eine Karte.")

    def _execute_passive(self, event, game_state):
        if not isinstance(event, Event.CardDroppedEvent):
            return

        event_data = event.data
        source = event_data["source"]
        target = event_data["target"]

        if isinstance(source, Enemy) or isinstance(source, Card.DarkArtsCard):
            game_state.apply_effect(Effect.DamageEffect(1), self, [target])

    def apply_reward(self, game_state):
        game_state.apply_effect(Effect.DrawCardEffect(1), self, game_state.players)


class Quirrell(Enemy):
    def __init__(self):
        super().__init__("Quirinus Quirrell", 6, 1,
                         "Der aktive Held verliert 1 Herz.",
                         "Alle Helden bekommen 1 Münze und 1 Herz.")

    def _execute_active(self, game_state):
        game_state.apply_effect(Effect.DamageEffect(1), self, [game_state.current_player])

    def apply_reward(self, game_state):
        game_state.apply_effect(Effect.GiveCoinsEffect(1), self, game_state.players)
        game_state.apply_effect(Effect.HealEffect(1), self, game_state.players)


class Bellatrix(Enemy):
    pass


class Todesser(Enemy):
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
