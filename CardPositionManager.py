class CardPositionManager:
    def __init__(self, game_state):
        self.game_state = game_state
        self.board = game_state.board
        self.players = self.board.players

        self.enemy_stack = self.board.enemy_stack
        self.enemy_dump = self.board.enemy_dump
        self.dark_arts_stack = self.board.dark_arts_stack
        self.dark_arts_dump = self.board.dark_arts_dump
        self.hogwarts_stack = self.board.hogwarts_stack
        self.active_place = self.board.active_place

        self.board_x, self.board_y = self.board.pos
        self.board_width, self.board_height = self.board.width, self.board.height

        self.enemy_width = self.board_width // 5
        self.enemy_height = self.board_height // 8
        self.card_width = (7/16) * self.enemy_width
        self.card_height = self.board_height // 4.5

    def update(self):
        self.align_shop_cards()
        self.align_enemies()
        self.align_players()

    def realign_board(self, new_pos=None, new_width=None, new_height=None):
        if new_pos is None:
            new_pos = self.board_x, self.board_y
        if new_width is None:
            new_width = self.board_width
        if new_height is None:
            new_height = self.board_height

        self.board_width, self.board_height = new_width, new_height
        self.board.width, self.board.height = new_width, new_height
        self.board_x, self.board_y = new_pos

        self.board.pos = new_pos

        self.enemy_width = self.board_width // 5
        self.enemy_height = self.board_height // 7

        self.card_width = (7 / 16) * self.enemy_width
        self.card_height = self.board_height // 4.5

        self.enemy_stack.width = self.enemy_width
        self.enemy_stack.height = self.enemy_height

        for enemy in self.board.open_enemies + self.board.enemy_stack + self.board.enemy_dump:
            enemy.width = self.enemy_width
            enemy.height = self.enemy_height

        self.hogwarts_stack.width = self.card_width
        self.hogwarts_stack.height = self.card_height

        for card in self.board.shop_cards:
            card.width = self.card_width
            card.height = self.card_height

        for card in [card for player in self.players for card in (player.hand + player.deck + player.discard_pile)]:
            card.width = self.card_width
            card.height = self.card_height

        self.active_place.width = self.enemy_width
        self.active_place.height = self.enemy_height
        place_x = self.board_x + self.board_width // 16
        place_y = self.board_y + self.board_height // 16
        self.active_place.pos = (place_x, place_y)

        player_width = self.game_state.screen_size[0] - self.board.width
        player_height = self.game_state.screen_size[1] // 4

        available_deck_width = player_width // 8
        scale_factor = 1
        if available_deck_width < self.card_width:
            scale_factor = available_deck_width / self.card_width

        for player in self.players:
            player.width = player_width
            player.height = player_height

            player.deck.width = card.width * scale_factor
            player.deck.height = card.height * scale_factor
            player.discard_pile.width = card.width * scale_factor
            player.discard_pile.height = card.height * scale_factor

        left_point = self.active_place.pos[0] + self.active_place.width
        right_point = self.board_x + self.board_width - 2 * self.card_width - self.enemy_width // 8
        max_length = right_point - left_point

        self.dark_arts_stack.width = self.active_place.height
        self.dark_arts_stack.height = self.active_place.height
        self.dark_arts_dump.width = self.active_place.height
        self.dark_arts_dump.height = self.active_place.height

        dark_arts_stack_x = left_point + max_length // 3 - self.dark_arts_stack.width // 2
        dark_arts_dump_x = left_point + 2 * max_length // 3 - self.dark_arts_dump.width // 2

        self.dark_arts_stack.pos = dark_arts_stack_x, self.active_place.pos[1]
        self.dark_arts_dump.pos = dark_arts_dump_x, self.active_place.pos[1]

        self.update()

    def align_enemies(self):
        enemies = self.board.open_enemies
        enemy_stack = self.enemy_stack

        base_offset = self.enemy_width/8
        base_x = self.board_x + base_offset
        base_y = self.board_y + (15/16) * self.board_height - self.enemy_height
        for i, enemy in enumerate(enemies):
            x = base_x + i * (enemy.width + base_offset)
            y = base_y
            enemy.pos = x, y

        enemy_stack_x = base_x
        enemy_stack_y = base_y - (self.enemy_height + self.board_height/8)
        enemy_stack.pos = enemy_stack_x, enemy_stack_y

    def align_shop_cards(self):
        shop_cards = self.board.shop_cards

        base_offset = self.enemy_width // 8
        y_offset = 1/16 * self.card_height

        base_x = self.board_x + self.board_width - (base_offset + self.enemy_width)
        base_y = self.board_y + self.board_height - (3 * self.card_height + 3 * y_offset)
        count = 0
        for i in range(3):
            for j in range(2):
                card = shop_cards[count]

                x = base_x + j * (self.card_width + base_offset)
                y = base_y + i * (self.card_height + y_offset)
                card.pos = (x, y)

                count += 1

        hogwarts_stack_x = (base_x + (base_x + 2 * self.card_width + base_offset)) / 2 - self.card_width / 2
        hogwarts_stack_y = self.board.pos[1] + 1/16 * self.card_height

        self.hogwarts_stack.pos = hogwarts_stack_x, hogwarts_stack_y

    def align_players(self):
        players = self.game_state.players

        for i, player in enumerate(players):
            player_x = self.board_x + self.board_width
            player_y = i * player.height

            player.pos = player_x, player_y

            deck_x = player_x + (player.width / 8 - player.deck.width) // 2
            deck_y = player_y + player.height - player.deck.height
            if deck_y > player_y + player.height / 3:
                #print(deck_y, player_y + player.height / 2)
                deck_y = player_y + player.height / 3

            player.deck.pos = deck_x, deck_y

            discard_pile_x = player_x + 7 * player.width / 8 + (player.width / 8 - player.deck.width) // 2
            player.discard_pile.pos = discard_pile_x, deck_y

        self.align_hands()

    def align_hands(self):
        players = self.game_state.players
        current_player_idx = self.game_state.current_player_idx

        for i in range(4):
            player = players[(current_player_idx + i) % 4]

            self.align_hand(player)

        #print(self.players[0].hand[0].pos[0] - self.board_width, self.game_state.screen_size[0] - (self.players[0].hand[4].pos[0] + self.players[0].hand[4].width))
        #print((self.players[0].hand[0].pos[0] - self.board_width) / self.players[0].width)

    def align_hand(self, player):
        hand = player.hand
        deck = player.deck
        discard_pile = player.discard_pile

        num_cards = len(hand)
        if num_cards == 0:
            return

        start_x = player.pos[0] + player.width / 8
        max_length = 3 * player.width / 4
        y_level = player.pos[1] + (player.height - self.card_height) / 2

        min_edge_space = max_length / 32  # Minimum space on each edge
        available_length_for_cards_and_spacing = max_length - (2 * min_edge_space)

        total_card_width = sum(card.width for card in hand)
        total_spacing = (num_cards - 1) * (max_length / 64)  # 1/64th spacing between cards
        available_width = available_length_for_cards_and_spacing - total_spacing

        if available_width < total_card_width:
            # Handle if cards are wider than the available space
            scale_factor = available_width / total_card_width
            for card in hand + deck + discard_pile:
                card.width *= scale_factor
                card.height *= scale_factor

            total_card_width = available_width

        available_height = player.height
        height_spacing = 1/8 * available_height
        available_height -= height_spacing

        if available_height < self.card_height:
            scale_factor = available_height / self.card_height
            for card in hand + deck + discard_pile:
                card.height *= scale_factor
                card.width *= scale_factor

        start_offset = min_edge_space + (available_length_for_cards_and_spacing - (
                    total_card_width + total_spacing)) / 2  # Center the hand with min edge space
        current_x = start_x + start_offset

        for card in hand:
            card.pos = (current_x, y_level)
            current_x += card.width + (max_length / 64)  # Add card width and spacing


