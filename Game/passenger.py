class Passenger:
    def __init__(self, img_dict, hotel_pos: tuple):
        self.obj = img_dict["passenger"]
        self.passenger_rect = self.obj.get_rect()
        self.passenger_rect.x, self.passenger_rect.y = hotel_pos[0], hotel_pos[1]
        self.state = "waiting"

    def draw(self, surface):
        surface.blit(self.obj, self.passenger_rect)

    def update(self, player, parkinglot):
        if self.state == "in_taxi":
            self.passenger_rect.center = player.player_rect.center



