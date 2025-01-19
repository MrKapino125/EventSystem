class CardPositionManager:
    def __init__(self, game_state):
        self.game_state = game_state
        self.board = game_state.board
        self.players = self.board.players
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

    def realign_board(self, new_pos, new_width, new_height):
        self.board_width, self.board_height = new_width, new_height
        self.board.width, self.board.height = new_width, new_height
        self.board_x, self.board_y = new_pos

        self.board.pos = new_pos

        self.enemy_width = self.board_width // 5
        self.enemy_height = self.enemy_height = self.board_height // 8

        self.card_width = (7 / 16) * self.enemy_width
        self.card_height = self.board_height // 4.5

        for enemy in self.board.open_enemies + self.board.enemy_stack + self.board.enemy_dump:
            enemy.width = self.enemy_width
            enemy.height = self.enemy_height

        for card in self.board.shop_cards:
            card.width = self.card_width
            card.height = self.card_height

        for card in [card for player in self.players for card in (player.hand + player.deck + player.discard_pile)]:
            card.width = self.card_width
            card.height = self.card_height

        player_width = self.game_state.screen_size[0] - self.board.width
        player_height = self.game_state.screen_size[1] // 4
        for player in self.players:
            player.width = player_width
            player.height = player_height

            player.deck.width = card.width
            player.deck.height = card.height
            player.discard_pile.width = card.width
            player.discard_pile.height = card.height

        self.update()

    def align_enemies(self):
        enemies = self.board.open_enemies

        base_offset = self.enemy_width/8
        base_x = self.board_x + base_offset
        base_y = self.board_y + (15/16) * self.board_height - self.enemy_height
        for i, enemy in enumerate(enemies):
            x = base_x + i * (enemy.width + base_offset)
            y = base_y
            enemy.pos = x, y

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

    def align_players(self):
        players = self.game_state.players

        for i, player in enumerate(players):
            player_x = self.board_x + self.board_width
            player_y = i * player.height

            player.pos = player_x, player_y

            deck_x = player_x + (player.width / 8 - self.card_width) // 2
            deck_y = player_y + player.height - self.card_height
            player.deck.pos = deck_x, deck_y

            discard_pile_x = player_x + 7 * player.width / 8 + (player.width / 8 - self.card_width) // 2
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
            for card in hand:
                card.width *= scale_factor
                card.height *= scale_factor
            total_card_width = available_width

        available_height = player.height
        height_spacing = 1/8 * available_height
        available_height -= height_spacing

        if available_height < self.card_height:
            scale_factor = available_height / self.card_height
            for card in hand:
                card.height *= scale_factor
                card.width *= scale_factor

        start_offset = min_edge_space + (available_length_for_cards_and_spacing - (
                    total_card_width + total_spacing)) / 2  # Center the hand with min edge space
        current_x = start_x + start_offset

        for card in hand:
            card.pos = (current_x, y_level)
            current_x += card.width + (max_length / 64)  # Add card width and spacing


