import pygame
import numpy as np
from sys import exit

class Paal:
    def __init__(self, position: np.ndarray) -> None:
        self.position = position
        self.zone: pygame.Rect = None

    def is_occupied(self) -> bool:
        return len(self.zone.collidelistall([player.rect for player in players])) > 1

class Player:
    def __init__(self, position: np.ndarray, controller: pygame.joystick.JoystickType, speed: int, color:str) -> None:
        self.position = np.array([position[0], position[1]], dtype=float)
        self.speed = speed
        self.controller = controller
        self.color = color
        self.energy: int = 100
        self.cooldown: int = 0
        self.score: int = 0
        self.paal: Paal = None
        self.rect: pygame.Rect

    def __lt__(self, other):
        return self.score < other.score

    def move(self):
        x, y = round(self.controller.get_axis(0)), round(self.controller.get_axis(1))
        self.position += unify_vector(np.array([x, y], dtype=float)) * self.speed

    def boost(self):
        is_boosting = self.controller.get_button(5)
        if self.energy < 2 or not is_boosting:
            self.speed = self.speed - 0.4 if self.speed > 4 else 4
        elif self.energy >= 2 and is_boosting:
            self.speed = self.speed + 0.4 if self.speed < 10 else 10
            self.energy -= 2

    def check_collisions(self, palen: list[Paal]):
        for paal in palen:
            if paal.zone.colliderect(self.rect):
                if self.paal == paal: return
                elif paal.is_occupied(): return
                elif self.paal != paal:
                    self.take_paal(paal)

    def take_paal(self, paal: Paal):
        for player in players:
            if player.paal == paal:
                player.paal = None
        self.paal = paal
        self.energy += 100
        self.score += 100

    def get_distance_from_paal(self) -> int:
        return magnitude(self.position - self.paal.position) if self.paal else 0
    
    def degrade_boost(self):
        if not self.paal: return
        if self.get_distance_from_paal() < 100:
            self.energy = self.energy - 1 if self.energy > 50 else 50

    def get_bonus_boost(self):
        if not self.paal: return
        if self.get_distance_from_paal() > 250 and not self.controller.get_button(5):
            self.energy = self.energy + 1 if self.energy > 1000 else 1000

def magnitude(vector: np.ndarray) -> int:
    return(vector[0] * vector[0] + vector[1] * vector[1])**0.5

def unify_vector(vector: np.ndarray) -> np.ndarray:
    if not np.any(vector):
        return vector
    return vector / (vector**2).sum()**0.5

score_positions = [(1610, 50), (1610, 110), (1610, 170), (1610, 230), (1610, 290), (1610, 350), (1610, 410)]
def draw_game():
    win.fill((0, 0, 0))
    for paal in palen:
        paal.zone = pygame.draw.rect(
            win, (230, 190, 240), (int(paal.position[0]), int(paal.position[1]), 50, 50))
    players.sort(reverse=True)
    for index, player in enumerate(players):
        player.rect = pygame.draw.rect(
            win, player.color, (int(player.position[0]), int(player.position[1]), 20, 20))

        score_text = font.render(f'{player.score}', True, player.color)
        score_rect = score_text.get_rect()
        score_rect.center = score_positions[index]

        win.blit(score_text, score_rect)
        if not player.paal: continue
        pygame.draw.rect(win, player.color, (int(player.paal.position[0]), int(player.paal.position[1]), 20, 20))
    pygame.display.update()

def run_game(players: list[Player]):
    run = True
    while run:
        if pygame.QUIT in [event.type for event in pygame.event.get()]: exit()
        pygame.time.delay(5)
        for player in players:
            # for button in range(player.controller.get_numbuttons()):
            #     print(button, player.controller.get_button(button))
            player.move()
            player.boost()
            player.check_collisions(palen)
            player.degrade_boost()
            player.get_bonus_boost()
            print(player.get_distance_from_paal())
            if player.controller.get_button(9): exit()
            draw_game()
    start_new_game()

def start_new_game():
    global palen
    global players
    player_colors = ['blue', 'green', 'yellow', 'red', 'orange']
    start_positions = {2: [(100,100), (1480,900)]}
    paal_positions = {2:[(840, 50), (840, 908)], 3:[(840, 50), (840, 908)]}
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    positions = start_positions[len(joysticks)]
    paal_positions = paal_positions[len(joysticks)]
    players = []
    for count, controller in enumerate(joysticks):
        controller.init()
        player = Player(position=positions[count],controller=controller, speed=4, color=player_colors[count])
        players.append(player)
    palen = []
    for position in paal_positions:
        paal = Paal(position=position)
        palen.append(paal)
    draw_game()
    run_game(players)

screen_resolution = (1680, 1050)
pygame.init()
win = pygame.display.set_mode(screen_resolution, pygame.FULLSCREEN)
pygame.display.set_caption('palenspel')
pygame.joystick.init()
pygame.font.init()
font = pygame.font.SysFont('freesanbold.ttf', 40)

start_new_game()