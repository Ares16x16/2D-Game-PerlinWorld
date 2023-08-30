import pygame
import noise
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

BIOME_COLORS = {
    "green": {
        "color": (117, 181, 142),
        "probability": 0.8,
        "occurrence_probability": 0.4,
        "occurrence_colors": [(174, 211, 138), (139, 201, 116), (123, 189, 100)],
    },
    "brown": {
        "color": (160, 95, 85),
        "probability": 0.3,
        "occurrence_probability": 0.5,
        "occurrence_colors": [(198, 123, 102), (181, 94, 74), (157, 79, 61)],
    },
}


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, screen, camera_x, camera_y):
        pygame.draw.rect(
            screen,
            (0, 0, 0),
            (
                (self.x - camera_x) * TILE_SIZE,
                (self.y - camera_y) * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE,
            ),
        )


class World:
    def __init__(self, seed):
        self.tiles = {}
        self.seed = seed
        self.crosses = []

    def generate_world(self, camera_x, camera_y):
        for row in range(camera_y - GRID_HEIGHT, camera_y + 2 * GRID_HEIGHT):
            for col in range(camera_x - GRID_WIDTH, camera_x + 2 * GRID_WIDTH):
                if (col, row) not in self.tiles:
                    perlin_noise_value = noise.pnoise2(
                        col / 10,
                        row / 10,
                        octaves=6,
                        persistence=0.5,
                        lacunarity=2.0,
                        repeatx=1024,
                        repeaty=1024,
                        base=self.seed,
                    )

                    for biome_name, biome_data in BIOME_COLORS.items():
                        if random.random() <= biome_data["probability"]:
                            biome_color = biome_data["color"]

                            if random.random() < biome_data["occurrence_probability"]:
                                occurrence_colors = biome_data["occurrence_colors"]
                                biome_color = random.choice(occurrence_colors)

                            self.tiles[(col, row)] = (perlin_noise_value, biome_color)
                            break

    def draw(self, screen, camera_x, camera_y):
        for row in range(camera_y - GRID_HEIGHT, camera_y + 2 * GRID_HEIGHT):
            for col in range(camera_x - GRID_WIDTH, camera_x + 2 * GRID_WIDTH):
                noise_value, biome_color = self.tiles.get(
                    (col, row), (0, (255, 255, 255))
                )
                elevation = int((noise_value + 1) * 0.5 * 255)
                pygame.draw.rect(
                    screen,
                    biome_color,
                    (
                        (col - camera_x) * TILE_SIZE,
                        (row - camera_y) * TILE_SIZE,
                        TILE_SIZE,
                        TILE_SIZE,
                    ),
                )
        self.draw_crosses(screen, camera_x, camera_y)

    def add_cross(self, x, y):
        self.crosses.append((x, y))

    def draw_crosses(self, screen, camera_x, camera_y):
        for cross in self.crosses:
            cross_x, cross_y = cross
            cross_rect = pygame.Rect(
                (cross_x - camera_x) * TILE_SIZE,
                (cross_y - camera_y) * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE,
            )
            pygame.draw.line(
                screen, (255, 0, 0), cross_rect.topleft, cross_rect.bottomright
            )
            pygame.draw.line(
                screen, (255, 0, 0), cross_rect.topright, cross_rect.bottomleft
            )


class Game:
    def __init__(self, seed):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.is_running = False
        self.player = Player(2, 2)
        self.world = World(seed)
        self.camera_x = 0
        self.camera_y = 0

    def start(self):
        self.is_running = True
        self.world.generate_world(self.camera_x, self.camera_y)

        while self.is_running:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False

            self.handle_input()
            self.update()
            self.render()

        pygame.quit()

    def handle_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.player.y -= 1
        if keys[pygame.K_s]:
            self.player.y += 1
        if keys[pygame.K_a]:
            self.player.x -= 1
        if keys[pygame.K_d]:
            self.player.x += 1
        if keys[pygame.K_f]:
            cross_x = self.player.x
            cross_y = self.player.y
            self.world.add_cross(cross_x, cross_y)

    def update(self):
        self.camera_x = self.player.x - GRID_WIDTH // 2
        self.camera_y = self.player.y - GRID_HEIGHT // 2
        self.world.generate_world(self.camera_x, self.camera_y)

    def render(self):
        self.screen.fill((255, 255, 255))
        self.world.draw(self.screen, self.camera_x, self.camera_y)
        self.player.draw(self.screen, self.camera_x, self.camera_y)
        pygame.display.flip()


if __name__ == "__main__":
    seed = 1234
    game = Game(seed)
    game.start()
