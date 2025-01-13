class CardPositionManager:
    def __init__(self, players, board):
        self.players = players
        self.board = board

    def allign_shop_cards(self):
        shop_cards = self.board.shop_cards
        print(shop_cards)

        base_x = 500
        base_y = 100
        count = 0
        for i in range(3):
            for j in range(2):
                x = base_x + (120*j)
                y = base_y + (220*i)
                shop_cards[count].pos = (x, y)

                count += 1


