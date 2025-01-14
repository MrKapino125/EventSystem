class CardPositionManager:
    def __init__(self, players, board):
        self.players = players
        self.board = board

    def update(self):
        self.align_shop_cards()
        self.align_enemies()

    def align_enemies(self):
        enemies = self.board.open_enemies

        base_x = 100
        base_y = 760
        for i, enemy in enumerate(enemies):
            x = base_x + i * (enemy.width + 20)
            y = base_y
            enemy.pos = x, y

    def align_shop_cards(self):
        shop_cards = self.board.shop_cards
        print(shop_cards)

        base_x = 1100
        base_y = 400
        count = 0
        for i in range(3):
            for j in range(2):
                x = base_x + (120*j)
                y = base_y + (220*i)
                shop_cards[count].pos = (x, y)

                count += 1


