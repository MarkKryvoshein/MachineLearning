class ParkingLot:
    def __init__(self, img_dict, hotel_pos: tuple):
        self.obj = img_dict["parking"]
        self.parkinglot_rect = self.obj.get_rect()
        self.parkinglot_rect.x, self.parkinglot_rect.y = hotel_pos[0], hotel_pos[1]

    def draw(self, surface):
        surface.blit(self.obj, self.parkinglot_rect)
