import Button
import Card
import Effect
import Enemy
import Event


class Schwerpunkt:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.belonging = None

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description

    def apply_effect(self, game_state, event=None):
        if event is None:
            self._apply_active(game_state)
        else:
            self._apply_passive(game_state, event)

    def _apply_active(self, game_state):
        pass

    def _apply_passive(self, game_state, event):
        pass

    def apply_end_turn_effect(self, game_state):
        pass

    def can_use(self, game_state):
        return False

class Zaubertranke(Schwerpunkt):
    def __init__(self):
        super().__init__("Zaubertränke", "Wenn du in deinem Zug mindestens jeweils 1 Verbündeten, Gegenstand und Spruch ausgespielt hast, bekommt ein Held deiner Wahl 1 Blitz und 1 Herz.")
        self.types_played = {"object": False, "ally": False, "spell": False}
        self.deactivate = False

    def _apply_passive(self, game_state, event):
        if self.deactivate:
            return
        if not isinstance(event, Event.CardPlayedEvent):
            return

        card = event.data["card"]
        card_type = card.data["type"]
        self.types_played[card_type] = True

        if all(self.types_played.values()):
            game_state.select_targets([game_state.current_player], 1, game_state.players, self, self, Effect.GiveBoltHealEffect(1), prio=False)
            self.deactivate = True

    def apply_end_turn_effect(self, game_state):
        self.types_played = {"object": False, "ally": False, "spell": False}
        self.deactivate = False


class GeschichteZauberei(Schwerpunkt):
    def __init__(self):
        super().__init__("Geschichte der Zauberei", "Jedes Mal, wenn du einen Spruch erwirbst, bekommt ein Held deiner Wahl 1 Münze.")

    def _apply_passive(self, game_state, event):
        if not isinstance(event, Event.BuyCardEvent):
            return

        card = event.data["card"]
        card_type = card.data["type"]
        if card_type == "spell":
            game_state.select_targets([game_state.current_player], 1, game_state.players, self, self,
                                      Effect.GiveCoinsEffect(1))


class Verteidigung(Schwerpunkt):
    def __init__(self):
        super().__init__("Verteidigung gegen die dunklen Künste", "Jedes Mal, wenn eine Dunkle-Künste-Karte oder ein Bösewicht dich dazu zwingt, eine Karte abzuwerfen, bekommst du 1 Blitz und 1 Herz.")

    def _apply_passive(self, game_state, event):
        if not isinstance(event, Event.CardDroppedEvent):
            return
        if event.data["is_death"]:
            return

        if isinstance(event.data["source"], Card.DarkArtsCard) or isinstance(event.data["source"], Enemy.Enemy):
            game_state.apply_effect(Effect.GiveBoltEffect(1), self, [self.belonging])
            game_state.apply_effect(Effect.HealEffect(1), self, [self.belonging])


class Arithmantik(Schwerpunkt):
    def __init__(self):
        super().__init__("Arithmantik", "Karten die dich einen Haus-Würfel werfen lassen kosten dich 1 Münze weniger. Jedes Mal, wenn du einen Würfel wirfst, darfst du dich entscheiden, ihn einmal erneut zu werfen.")


class Krauterkunde(Schwerpunkt):
    def __init__(self):
        super().__init__("Kräuterkunde", "Wenn ein Held 3 oder mehr Herzen während deines Zuges bekommt, darf dieser Held eine zusätzliche Karte ziehen.")
        self.heals_given = None
        self.deactivate = None

    def _apply_passive(self, game_state, event):
        if self.heals_given is None:
            self.heals_given = dict(zip(game_state.players, [0 for _ in range(len(game_state.players))]))
            self.deactivate = dict(zip(game_state.players, [False for _ in range(len(game_state.players))]))

        if not isinstance(event, Event.HealthGainedEvent):
            return

        amount = event.data["amount"]
        target = event.data["target"]

        if self.deactivate[target]:
            return

        if not target.health:
            return

        if target.health + amount >= 10:
            amount = 10 - target.health

        self.heals_given[target] += amount
        if self.heals_given[target] >= 3:
            self.deactivate[target] = True
            game_state.apply_effect(Effect.DrawCardEffect(1), self, [target])

    def apply_end_turn_effect(self, game_state):
        self.heals_given = dict(zip(game_state.players, [0 for _ in range(len(game_state.players))]))
        self.deactivate = dict(zip(game_state.players, [False for _ in range(len(game_state.players))]))


class Zauberkunst(Schwerpunkt):
    def __init__(self):
        super().__init__("Zauberkunst", "Einmal pro Zug darfst du 2 Sprüche abwerfen. Dadurch erhalten ALLE Helden 1 Münze und ziehen eine Karte.")
        self.deactivate = False

    def _apply_active(self, game_state):
        if self.deactivate:
            return

        game_state.inventory = False
        selectables = [card for card in self.belonging.hand if card.data["type"] == "spell"]
        game_state.init_choice([game_state.current_player], 2, {"game_state": game_state}, self.effect_callback,
                               selectables, "Wähle 2 Sprüche!", self, prio=False)
        self.deactivate = True

    def effect_callback(self, game_state):
        selection = game_state.current_selection
        game_state.resolve_choice()

        cards = selection.selections

        for card in cards:
            game_state.apply_effect(Effect.DropCardEffect(card), self, [self.belonging])

        game_state.apply_effect(Effect.GiveCoinsEffect(1), self, game_state.players)
        game_state.apply_effect(Effect.DrawCardEffect(1), self, game_state.players)

    def can_use(self, game_state):
        if self.deactivate:
            return False
        if game_state.current_player != self.belonging:
            return False
        count = 0
        for card in self.belonging.hand:
            if card.data["type"] == "spell":
                count += 1
            if count == 2:
                return True
        return False

    def apply_end_turn_effect(self, game_state):
        self.deactivate = False


class Besenflug(Schwerpunkt):
    def __init__(self):
        super().__init__("Besenflug", "Einmal pro Zug darfst du 5 Münzen abgeben, um 1 Totenkopf vom aktuellen Ort zu entfernen.")
        self.deactivate = False

    def _apply_active(self, game_state):
        if self.belonging.coins < 5 or self.deactivate:
            return

        game_state.inventory = False
        game_state.apply_effect(Effect.RemoveSkullEffect(1), self, [None])
        self.belonging.coins -= 5
        self.deactivate = True

    def can_use(self, game_state):
        if self.deactivate:
            return False
        if game_state.current_player != self.belonging:
            return False
        return self.belonging.coins >= 5 and game_state.board.active_place.skulls

    def apply_end_turn_effect(self, game_state):
        self.deactivate = False


class Wahrsagen(Schwerpunkt):
    def __init__(self):
        super().__init__("Wahrsagen", "Jedes Mal, wenn du einen Gegenstand ausspielst, darfst du die oberste Karte deines Nachziehstapels anschauen und dich entscheiden, ob du die Karte dort lassen oder abwerfen möchtest.")

    def _apply_passive(self, game_state, event):
        pass


class Verwandlung(Schwerpunkt):
    def __init__(self):
        super().__init__("Verwandlung", "Einmal pro Zug darfst du einen Gegenstand abwerfen, um deinen Nachziehstapel nach einer Karte mit einem Wert von 5 oder weniger Münzen zu durchsuchen und diese auf die Hand zu nehmen. Mische danach deinen Nachziehstapel.")
        self.deactivate = False

    def _apply_active(self, game_state):
        if self.deactivate:
            return

        game_state.inventory = False
        selectables = [card for card in self.belonging.hand if card.data["type"] == "object"]
        game_state.init_choice([game_state.current_player], 1, {"game_state": game_state}, self.effect_callback,
                               selectables, "Wähle einen Gegenstand!", self, prio=False)
        self.deactivate = True

    def effect_callback(self, game_state):
        selection = game_state.current_selection
        game_state.resolve_choice()
        if not selection.selections:
            return

        card = selection.selections[0]
        game_state.apply_effect(Effect.DropCardEffect(card), self, [self.belonging])

        buttons = []
        for card in self.belonging.deck:
            if card.data["cost"] > 5:
                continue
            button = Button.CardButton(card)
            buttons.append(button)
        game_state.card_position_manager.align_buttons(buttons)
        for button in buttons:
            button.set_text()

        game_state.init_choice([self.belonging], 1, {"game_state": game_state}, self.card_callback, buttons, "Nimm eine Karte auf die Hand!", self)

    def card_callback(self, game_state):
        selection = game_state.current_selection
        selections = selection.selections
        game_state.resolve_choice()
        if not selections:
            return

        card = selections[0].card
        selection.selector.deck.remove(card)
        selection.selector.hand.append(card)



    def can_use(self, game_state):
        if self.deactivate:
            return False
        if game_state.current_player != self.belonging:
            return False
        for card in self.belonging.hand:
            if card.data["type"] == "object":
                return True
        return False

    def apply_end_turn_effect(self, game_state):
        self.deactivate = False
