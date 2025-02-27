import json

import Button
import EffectModifiers
import Event
import Effect
import Card
import pygame
from Globals import GLOBAL_ENEMY_FONT_SIZE


class Enemy:
    def __init__(self, name, health, level, description, reward_text):
        self.name = name
        self.max_health = health
        self.health = health
        self.level = level
        self.stunned = False
        self.stun_count = 0
        self.is_dead = False
        self.description = description
        self.reward_text = reward_text
        self.pos = (0, 0)
        self.width = 500
        self.height = 250
        self.color = (0,0,0)
        self.back_color = (255, 255, 255)

        self.font_size = GLOBAL_ENEMY_FONT_SIZE
        self.font = pygame.font.SysFont('Arial', self.font_size)
        self.lines = [self.name]

    def __repr__(self):
        return self.name + f" {self.health}/{self.max_health}"

    def get_name(self):
        return self.name

    def render(self, screen, pos=None, width=None, height=None):
        altered = True
        if pos is None:
            pos = self.pos
            altered = False
        if width is None:
            width = self.width
            altered = False
        if height is None:
            height = self.height
            altered = False

        fill_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(fill_surface, (*self.back_color, 128), (0, 0, width, height))

        screen.blit(fill_surface, (pos[0], pos[1]))

        pygame.draw.rect(screen, self.color, (pos[0], pos[1], width, height), 2)

        if altered:
            lines = self.generate_lines()
        else:
            lines = self.lines
        y_offset = 0
        line_spacing = 5  # spacing between lines
        for line in lines:
            text_surface = self.font.render(line, True, self.color)
            text_rect = text_surface.get_rect(center=(pos[0] + width // 2,
                                                      pos[1] + height // 2 + y_offset - (len(lines) - 1) * (
                                                                  self.font_size + line_spacing) // 2))  # vertical align
            screen.blit(text_surface, text_rect)
            y_offset += self.font_size + line_spacing

        health_surface = self.font.render(str(self.health), True, self.color)
        health_width = health_surface.get_width()
        health_height = health_surface.get_height()

        # Calculate the center x-coordinate of the box
        center_x = pos[0] + width // 2

        # Calculate the x-coordinate for centering the health surface
        health_x = center_x - health_width // 2

        # Calculate the y-coordinate just above the bottom line of the box
        health_y = pos[1] + height - health_height - height // 16

        screen.blit(health_surface, (health_x, health_y))

        if self.stunned:
            self.render_stunned_overlay(screen)

    def generate_lines(self):
        text = self.name

        font_size = self.font_size
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
        lines.append(current_line)
        return lines

    def render_select_overlay(self, screen):
        green = (0, 255, 0)  # Green color
        thickness = 4  # Outline thickness

        # Create a rectangle for the outline
        outline_rect = pygame.Rect(self.pos[0] - thickness, self.pos[1] - thickness,
                                   self.width + 2 * thickness, self.height + 2 * thickness)

        pygame.draw.rect(screen, green, outline_rect, thickness)

    def render_stunned_overlay(self, screen):
        yellow = (255, 255, 0)
        thickness = 4  # Outline thickness

        # Create a rectangle for the outline
        outline_rect = pygame.Rect(self.pos[0] - thickness, self.pos[1] - thickness,
                                   self.width + 2 * thickness, self.height + 2 * thickness)

        pygame.draw.rect(screen, yellow, outline_rect, thickness)

    def apply_damage_effect(self, amount, game_state, event):
        if self.is_dead:
            return

        source = event.data["source"]

        source.bolts -= 1

        self.damage()

        if self.health <= 0:
            self.is_dead = True
            self.stunned = False
            game_state.apply_effect(Effect.EnemyDeadEffect(), source, [self])

    def apply_heal_effect(self, amount, game_state):
        self.heal(amount)

        if self.health > self.max_health:
            self.health = self.max_health

    def damage(self):
        self.health -= 1

    def heal(self, amount):
        self.health += amount

    def stun(self, game_state):
        self.stunned = True
        self.stun_count = 0

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
            return

        if event is None:
            self._execute_active(game_state)
        else:
            self._execute_passive(event, game_state)

    def apply_end_turn_effect(self, game_state):
        if self.stunned:
            self.stun_count += 1
        if self.stun_count == 4:
            self.stunned = False
            self.stun_count = 0

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


class Basilisk(Enemy):
    def __init__(self):
        super().__init__("Basilisk", 8, 2,
                         "Die Helden dürfen keine zusätzlichen Karten ziehen.",
                         "ALLE Helden ziehen eine Karte. Entfernt 1 Totenkopf vom aktuellen Ort.")
        self.modifier = EffectModifiers.CantDrawCardsModifier()

    def apply_reward(self, game_state):
        permanent_modifiers = game_state.permanent_modifiers
        if self.modifier in permanent_modifiers:
            permanent_modifiers.remove(self.modifier)
        game_state.apply_effect(Effect.DrawCardEffect(1), self, game_state.players)
        game_state.apply_effect(Effect.RemoveSkullEffect(1), self, [None])

    def apply_end_turn_effect(self, game_state):
        stunned_pre = self.stunned
        super().apply_end_turn_effect(game_state)
        if stunned_pre and not self.stunned:
            game_state.permanent_modifiers.append(self.modifier)
    
    def stun(self, game_state):
        super().stun(game_state)
        if self.modifier in game_state.permanent_modifiers:
            game_state.permanent_modifiers.remove(self.modifier)


class Lucius(Enemy):
    def __init__(self):
        super().__init__('Lucius Malfoy', 7, 2,
                         "Jedes Mal, wenn Totenköpfe auf den Ort gelegt werden, wird 1 Blitz von allen Bösewichten entfernt.",
                         "ALLE Helden bekommen 1 Münze. Entfernt 1 Totenkopf vom aktuellen Ort.")

    def _execute_passive(self, event, game_state):
        if not isinstance(event, Event.SkullPlacedEvent):
            return

        game_state.apply_effect(Effect.HealEffect(1), self, game_state.board.open_enemies)

    def apply_reward(self, game_state):
        game_state.apply_effect(Effect.GiveCoinsEffect(1), self, game_state.players)
        game_state.apply_effect(Effect.RemoveSkullEffect(1), self, [None])


class Riddle(Enemy):
    def __init__(self):
        super().__init__('Tom Riddle', 6, 2,
                         "Als aktiver Held wählst du für jeden Verbündeten auf deiner Hand: Du verlierst 2 Herzen oder wirf eine Karte ab.",
                         "ALLE Helden wählen: Du bekommst 2 Herzen oder nimm einen Verbündeten aus deinem Ablagestapel.")
        self.cards_picked = []

    def _execute_active(self, game_state):
        current_player = game_state.current_player
        selectables = [card for card in current_player.hand if card.data["type"] == "ally" and card not in self.cards_picked]

        if not selectables:
            self.cards_picked = []
            return

        game_state.init_choice([game_state.current_player], 1, {"game_state": game_state}, self.ability_callback, selectables, "Wähle einen Verbündeten!", self)

    def ability_callback(self, game_state):
        selection = game_state.current_selection
        game_state.resolve_choice()

        if not selection.selections:
            return

        selected_ally = selection.selections[0]
        self.cards_picked.append(selected_ally)

        button1 = Button.EffectButton({"type": "drop_cards", "amount": 1, "target": "self"}, game_state)
        button2 = Button.EffectButton({"type": "damage", "amount": 2, "target": "self"}, game_state)
        
        selectables = [button1, button2]
        game_state.card_position_manager.align_buttons(selectables)
        button1.set_text()
        button2.set_text()

        game_state.init_choice([game_state.current_player], 1, {"game_state": game_state}, self.effect_callback, selectables, f"Wähle einen Effekt für die Karte {selected_ally}", self)

    def effect_callback(self, game_state):
        selection = game_state.current_selection
        game_state.resolve_choice()

        button = selection.selections[0]
        effect = button.effect

        if effect["type"] == "damage":
            game_state.apply_effect(Effect.DamageEffect(2), self, [game_state.current_player])
            self._execute_active(game_state)
        else:
            game_state.init_choice([game_state.current_player], 1, {"game_state": game_state}, self.drop_callback, game_state.current_player.hand, "Wähle eine Karte zum abwerfen!", self, is_drop=True)

    def drop_callback(self, game_state):
        selection = game_state.current_selection
        game_state.resolve_choice()

        card = selection.selections[0]
        game_state.apply_effect(Effect.DropCardEffect(card), self, [game_state.current_player])
        self._execute_active(game_state)

    def apply_reward(self, game_state):
        button1 = Button.EffectButton({"type": "heal", "amount": 2, "target": "self"}, game_state)
        button2 = Button.EffectButton({"type": "redraw_ally", "amount": 1, "target": "self"}, game_state)
        selectables = [button1, button2]
        game_state.card_position_manager.align_buttons(selectables)
        button1.set_text()
        button2.set_text()

        players = game_state.players[:]
        for player in players:
            selecs = selectables[:]
            if not [card for card in player.discard_pile if card.data["type"] == "ally"]:
                selecs.remove(button2)

            game_state.init_choice([player], 1, {"game_state": game_state}, self.reward_callback,
                                   selecs, "Wähle einen Effekt", self, False)

    def reward_callback(self, game_state):
        selection = game_state.current_selection
        game_state.resolve_choice()

        button = selection.selections[0]
        effect = button.effect
        if effect["type"] == "heal":
            game_state.apply_effect(Effect.HealEffect(2), self, [selection.selector])
        else:
            game_state.apply_effect(Effect.ReDrawEffect(1, "ally", "Wähle einen Verbündeten"), self, [selection.selector])


class Dementor(Enemy):
    def __init__(self):
        super().__init__('Dementor', 8, 3,
                         "Der aktive Held verliert 2 Herzen.",
                         "ALLE Helden bekommen 2 Herzen. Entfernt 1 Totenkopf vom aktuellen Ort.")

    def _execute_active(self, game_state):
        game_state.apply_effect(Effect.DamageEffect(2), self, [game_state.current_player])

    def apply_reward(self, game_state):
        game_state.apply_effect(Effect.HealEffect(2), self, game_state.players)
        game_state.apply_effect(Effect.RemoveSkullEffect(1), self, [None])


class Pettigrew(Enemy):
    def __init__(self):
        super().__init__('Peter Pettigrew', 7, 3,
                         "Der aktive Held muss die oberste Karte seines Nachziehstapels aufdecken. Ist der Wert dieser Karte 1 Münze oder mehr, dann muss er diese Karte abwerfen und 1 Totenkopf auf den aktuellen Ort legen.",
                         "ALLE Helden dürfen ihren Ablagestapel nach einem Spruch durchsuchen und diesen auf die Hand nehmen. Entfernt 1 Totenkopf vom aktuellen Ort.")

    def _execute_active(self, game_state):
        target = game_state.current_player

        if not target.deck:
            return

        if target.deck[-1].data["cost"] > 0:
            card = target.deck.pop()
            target.hand.append(card)
            game_state.event_handler.dispatch_event(Event.CardDroppedEvent(self, target, card))
            game_state.apply_effect(Effect.PlaceSkullEffect(1), self, [None])

    def apply_reward(self, game_state):
        game_state.apply_effect(Effect.RemoveSkullEffect(1), self, [None])
        players = game_state.players[:]
        players.reverse()
        game_state.apply_effect(Effect.ReDrawEffect(1, "spell", "Wähle einen Spruch"), self, players)


class Todesser(Enemy):
    def __init__(self):
        super().__init__('Todesser', 7, 4,
                         "Jedes Mal, wenn Morsmordre! oder ein neuer Bösewicht aufgedeckt wird, verlieren ALLE Helden 1 Herz.",
                         "ALLE Helden bekommen 1 Herz. Entfernt 1 Totenkopf vom aktuellen Ort.")

    def _execute_passive(self, event, game_state):
        game_state.apply_effect(Effect.DamageEffect(1), self, game_state.players)

    def apply_reward(self, game_state):
        game_state.apply_effect(Effect.HealEffect(1), self, game_state.players)
        game_state.apply_effect(Effect.RemoveSkullEffect(1), self, [None])


class Barty(Enemy):
    def __init__(self):
        super().__init__('Barty Crouch, Jr.', 7, 4,
                         "Helden können keine Totenköpfe vom aktuellen Ort entfernen.",
                         "Entfernt 2 Totenköpfe vom aktuellen Ort.")
        self.modifier = EffectModifiers.CantRemoveSkullModifier()

    def apply_reward(self, game_state):
        permanent_modifiers = game_state.permanent_modifiers
        if self.modifier in permanent_modifiers:
            permanent_modifiers.remove(self.modifier)
        game_state.apply_effect(Effect.RemoveSkullEffect(2), self, [None])

    def apply_end_turn_effect(self, game_state):
        stunned_pre = self.stunned
        super().apply_end_turn_effect(game_state)
        if stunned_pre and not self.stunned:
            game_state.permanent_modifiers.append(self.modifier)

    def stun(self, game_state):
        super().stun(game_state)
        if self.modifier in game_state.permanent_modifiers:
            game_state.permanent_modifiers.remove(self.modifier)


class Umbridge(Enemy):
    def __init__(self):
        super().__init__('Dolores Umbridge', 7, 5,
                         "Jedes Mal, wenn ein Held eine Karte mit einem Wert von 4 oder mehr Münzen erwirbt, verliert dieser Held 1 Herz.",
                         "ALLE Helden bekommen 1 Münze und 2 Herzen.")

    def _execute_passive(self, event, game_state):
        game_state.apply_effect(Effect.DamageEffect(1), self, [game_state.current_player])

    def apply_reward(self, game_state):
        game_state.apply_effect(Effect.HealEffect(1), self, game_state.players)
        game_state.apply_effect(Effect.GiveCoinsEffect(2), self, game_state.players)


class Greyback(Enemy):
    def __init__(self):
        super().__init__('Fenrir Greyback', 8, 6,
                         "Helden können keine Herzen bekommen.",
                         "ALLE Helden bekommen 3 Herzen. Entfernt 2 Totenköpfe vom aktuellen Ort.")
        self.modifier = EffectModifiers.CantHealModifier()


class Bellatrix(Enemy):
    def __init__(self):
        super().__init__('Bellatrix Lestrange', 9, 6,
                         "Deckt jeden Zug eine zusätzliche Dunkle-Künste-Karte auf.",
                         "ALLE Helden dürfen ihren Ablagestapel nach einem Gegenstand durchsuchen und diesen auf die Hand nehmen. Entfernt 2 Totenköpfe vom aktuellen Ort.")


class Voldemort(Enemy):
    def __init__(self, name, health, level, description):
        super().__init__(name, health, level, description, "Die Helden gewinnen")


class Voldemort1(Voldemort):
    def __init__(self):
        super().__init__('Lord Voldemort', 10, 5,
                         "Der aktive Held verliert 1 Herz und muss eine Karte abwerfen.")

    def _execute_active(self, game_state):
        game_state.apply_effect(Effect.DamageEffect(1), self, [game_state.current_player])
        game_state.select_drop_cards([game_state.current_player], None, 1, self, prio=False)


class Voldemort2(Voldemort):
    def __init__(self):
        super().__init__('Lord Voldemort', 15, 6,
                         "Würfelt mit dem Slytherin-Würfel. Blitz = ALLE Helden verlieren 1 Herz. Münze = Legt 1 Totenkopf auf den aktuellen Ort. Herz = Entfernt 1 Blitz von allen Bösewichten. Karte = ALLE Helden müssen eine Karte abwerfen.")


class Voldemort3(Voldemort):
    def __init__(self):
        super().__init__('Lord Voldemort', 20, 7,
                         "Legt 1 Totenkopf auf den aktuellen Ort. Jedes Mal, wenn Totenköpfe vom Ort entfernt werden, verlieren ALLE Helden 1 Herz.")


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
