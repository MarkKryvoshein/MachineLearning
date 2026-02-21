import random


class Hotel:
    def __init__(self, img_dict, positions):
        self.obj = img_dict["hotel"]
        self.hotel_rect = self.obj.get_rect()
        self.hotel_rect.x, self.hotel_rect.y = random.choice(positions)

    def draw(self, surface):
        surface.blit(self.obj, self.hotel_rect)
