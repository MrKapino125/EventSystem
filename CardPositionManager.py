class CardPositionManager:
    def __init__(self, board):
        self.players = board.players
        self.board = board
        self.board_x, self.board_y = board.pos
        self.board_width, self.board_height = self.board.width, self.board.height

        self.enemy_width = self.board_width // 5
        self.enemy_height = self.board_height // 8
        self.card_width = (7/16) * self.enemy_width
        self.card_height = self.board_height // 4.5

    def update(self):
        self.align_shop_cards()
        self.align_enemies()

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

        base_offset = self.enemy_width / 8
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



