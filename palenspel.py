import pygame
import numpy as np
from sys import exit
from typing import Self

class Game:
    def __init__(self, player_count) -> None:
        self.player_count = player_count
        self.players: list[Player]
        self.palen: list(Paal)

class Paal:
    def __init__(self, position: np.ndarray) -> None:
        self.position = position
        self.rect: pygame.Rect = None

    def is_occupied(self) -> bool:
        return len(self.rect.collidelistall([player.rect for player in players])) > 1

class Player:
    def __init__(self, position: np.ndarray, controller: pygame.joystick.JoystickType, color:str) -> None:
        self.position = np.array([position[0], position[1]], dtype=float)
        self.controller = controller
        self.color = color
        self.speed: int = 0
        self.energy: int = 100
        self.cooldown: int = 0
        self.score: int = 0
        self.boosting : bool = False
        self.paal: Paal = None
        self.rect: pygame.Rect = None
        self.previous_positions = []
        self.direction: np.ndarray = None

    def __lt__(self, other: Self) -> bool:
        return self.score < other.score

    def move(self):
        x, y = round(self.controller.get_axis(0)), round(self.controller.get_axis(1))
        self.direction = unify_vector(np.array([x, y], dtype=float))
        if x or y: self.speed = self.speed + 0.2 if self.speed < 4 else self.speed - 0.02
        if not x and not y: self.speed = 0
        self.position += self.direction * self.speed

    def keep_track(self):
        if len(self.previous_positions) > 3000: self.previous_positions.pop(0)
        self.previous_positions.append(self.position)

    def boost(self):
        self.boosting = False
        if self.energy < 3: return
        trying_to_boost = self.controller.get_button(5)
        if self.energy >= 3 and trying_to_boost:
            self.boosting = True
            self.speed = self.speed + 0.2 if self.speed < 10 else 10
            self.energy -= 3

    def move_to_closest_paal(self):
        distances = {paal: magnitude(self.position - (paal.position - np.array([12.5, 12.5], dtype=float))) for paal in palen}
        closest = min(distances, key=distances.get)
        if self.rect.colliderect(closest.rect):
            self.speed = 0
            return
        direction = unify_vector(closest.position - self.position)
        self.speed = self.speed + 0.2 if self.speed < 4 else self.speed - 0.02
        self.position += direction * self.speed
    
    def move_to_paal_in_direction(self):
        x, y = round(self.controller.get_axis(0)), round(self.controller.get_axis(1))
        self.direction = unify_vector(np.array([x, y], dtype=float))
        distances = {paal: magnitude(unify_vector(paal.position - self.position) - self.direction) for paal in palen}
        closest = min(distances, key=distances.get)
        if self.rect.colliderect(closest.rect):
            self.speed = 0
            return
        direction = unify_vector(closest.position - self.position)
        self.speed = self.speed + 0.2 if self.speed < 4 else self.speed - 0.02
        self.position += direction * self.speed

    def check_collisions(self, palen: list[Paal]):
        for player in players:
            if player.rect.colliderect(self.rect) and player != self:
                self.bounce_off_player(player)
        for paal in palen:
            if paal.rect.colliderect(self.rect):
                if self.paal == paal: return
                elif paal.is_occupied(): return
                elif self.paal != paal:
                    self.take_paal(paal)

    def take_paal(self, paal: Paal):
        for player in players:
            if player == self: continue
            if player.paal == paal:
                player.paal = None
            self.paal = paal
            self.energy += 100
            self.score += 100

    def bounce_off_player(self, other: Self):
        bouncer = self if self.speed >= other.speed else other
        bounced = self if bouncer != self else other
        if bounced.paal:
            if bounced.rect.colliderect(bounced.paal.rect): return
        direction = unify_vector(bounced.position - bouncer.position)
        bounced.position += (direction * bouncer.speed * 10)
        bounced.speed = 0

    def get_distance_from_paal(self) -> int:
        return magnitude(self.position - self.paal.position) if self.paal else 0
    
    def degrade_boost(self):
        if not self.paal: return
        if self.get_distance_from_paal() < 100:
            self.energy = self.energy - 0.3 if self.energy > 0 else 0

    def get_bonus_boost(self):
        if self.boosting: return
        if not self.paal: return
        if self.energy > 50: return
        if self.get_distance_from_paal() > 200:
            self.energy = self.energy + 0.5

class UI:
    def __init__(self) -> None:
        pygame.init()
        pygame.joystick.init()
        pygame.font.init()
        self.screen_resolution = (1680, 1050)
        self.window = pygame.display.set_mode(self.screen_resolution, pygame.FULLSCREEN)
        self.font = pygame.font.SysFont('freesanbold.ttf', 40)

    def draw_game(self):
        self.window.fill((0, 0, 0))
        for paal in palen:
            paal.rect = pygame.draw.rect(
                self.window, (230, 190, 240), (int(paal.position[0]) - 25, int(paal.position[1]) - 25, 50, 50))
        players.sort(reverse=True)
        for index, player in enumerate(players):
            player.rect = pygame.draw.rect(
                self.window, player.color, (int(player.position[0] - 10), int(player.position[1] - 10), 20, 20))
            score_text = self.font.render(f'{player.score}', True, player.color)
            score_rect = score_text.get_rect()
            score_rect.center = score_positions[index]
            self.window.blit(score_text, score_rect)
            if not player.paal: continue
            pygame.draw.rect(self.window, player.color, (int(player.paal.position[0]) - 25, int(player.paal.position[1]) - 25, 20, 20))
        self.draw_boost(players)
        pygame.display.update()

    def draw_boost(self, players: list[Player]):
        for player in [player for player in players if player.boosting]:
            position = player.position - player.direction * 10
            trail = pygame.draw.rect(surface=self.window, color= 'yellow', rect=(int(position[0]) - 5, int(position[1]) - 5, 10, 10))

def magnitude(vector: np.ndarray) -> int:
    return np.sqrt(vector.dot(vector))

def unify_vector(vector: np.ndarray) -> np.ndarray:
    if not np.any(vector): return vector
    return vector / (vector**2).sum()**0.5

def run_game(players: list[Player]):
    run = True
    while run:
        if pygame.QUIT in [event.type for event in pygame.event.get()]: exit()
        pygame.time.delay(5)
        for player in players:
            # for button in range(player.controller.get_numbuttons()):
            #     print(button, player.controller.get_button(button))
            player.keep_track()
            if player.controller.get_button(3):
                player.move_to_closest_paal()
            elif player.controller.get_button(2):
                player.move_to_paal_in_direction()
            else:
                player.move()
            player.boost()
            player.check_collisions(palen)
            player.degrade_boost()
            player.get_bonus_boost()
            if player.controller.get_button(9): exit()
            # clock.tick()
            # print(int(clock.get_fps()))
            ui.draw_game()
    start_new_game()

def start_new_game():
    global palen
    global players
    global score_positions
    player_colors = ['blue', 'green', 'yellow', 'red', 'orange']
    start_positions = {2: [(100,100), (1480,900)], 3: [(800, 500), (850, 550), (750, 550)], 
                      4: [(800, 500), (850, 550), (750, 550), (900, 600)],
                      5: [(800, 500), (850, 550), (750, 550), (900, 600), (900, 500)]}
    paal_positions = {2:[(840, 50), (840, 908)], 3:[(840, 50), (840, 908)], 4: [(840,50), (80,50), (1600, 50)], 
                      5: [(80, 50), (1600, 50), (80, 1000), (1600, 1000)]}
    score_positions = [(1610, 50), (1610, 110), (1610, 170), (1610, 230), (1610, 290), (1610, 350), (1610, 410)]
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    player_positions = start_positions[len(joysticks)]
    paal_positions = paal_positions[len(joysticks)]
    players = []
    for count, controller in enumerate(joysticks):
        controller.init()
        player = Player(position=player_positions[count],controller=controller, color=player_colors[count])
        players.append(player)
    palen = []
    for position in paal_positions:
        paal = Paal(position=np.array(position, dtype=float))
        palen.append(paal)
    ui.draw_game()
    run_game(players)

def main():
    # global clock
    # clock = pygame.time.Clock()
    global ui
    ui = UI()
    start_new_game()

if __name__ == '__main__':
    main()