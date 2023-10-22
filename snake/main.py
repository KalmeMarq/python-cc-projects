import pygame
import random
from enum import Enum

GRID_ROWS = 16
GRID_COLS = 20

SLOT_SIZE = 32
GAME_WIDTH = GRID_COLS * SLOT_SIZE
GAME_HEIGHT = GRID_ROWS * SLOT_SIZE

pygame.init()
screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Snake")
pygame.display.set_icon(pygame.image.load("icon.png"))
clock = pygame.time.Clock()
running = True

play_sound = pygame.mixer.Sound("play.mp3")
eat_sound = pygame.mixer.Sound("eat.mp3")

class Direction(Enum):
  UP = 1
  LEFT = 2
  RIGHT = 3
  DOWN = 4

class GameState(Enum):
  START = 1
  PLAYING = 2
  WON = 3
  LOST = 4

class Snake:
  SNAKE_PART_IMG = pygame.image.load("snakepart.png")

  def __init__(self):
    self.x = random.randrange(0, int(GAME_WIDTH / 2 / SLOT_SIZE))
    self.y = random.randrange(0, int(GAME_HEIGHT / 2 / SLOT_SIZE))
    self.direction = Direction.RIGHT
    self.tail = [(self.x, self.y)]

  def move(self):
    head = self.tail[-1]
    
    if self.direction == Direction.UP:
      new_head = (head[0], head[1] - 1)
    elif self.direction == Direction.DOWN:
      new_head = (head[0], head[1] + 1)
    elif self.direction == Direction.LEFT:
      new_head = (head[0] - 1, head[1])
    elif self.direction == Direction.RIGHT:
      new_head = (head[0] + 1, head[1])

    if new_head[0] >= GAME_WIDTH / SLOT_SIZE:
      new_head = (0, new_head[1])

    if new_head[0] < 0:
      new_head = (GAME_WIDTH / SLOT_SIZE, new_head[1])

    if new_head[1] >= GAME_HEIGHT / SLOT_SIZE:
      new_head = (new_head[0], 0)

    if new_head[1] < 0:
      new_head = (new_head[0], GAME_HEIGHT / SLOT_SIZE)

    self.tail.pop(0)
    self.tail.append(new_head)

  def draw(self, screen):
    for i,part in enumerate(self.tail):
      if i + 1 < len(self.tail):
        screen.blit(Snake.SNAKE_PART_IMG, (part[0] * SLOT_SIZE, part[1] * SLOT_SIZE))
      else:
        color = (13, 220, 20) if i + 1 < len(self.tail) else (0, 255, 255)
        x = part[0] * SLOT_SIZE + 6
        y = part[1] * SLOT_SIZE + 6
        w = SLOT_SIZE - 12
        h = SLOT_SIZE - 12
        pygame.draw.rect(screen, color, pygame.Rect(x, y, w, h))


class Food:
  IMGS = [
    pygame.image.load('apple.png'),
    pygame.image.load('banana.png'),
    pygame.image.load('carrot.png')
  ]

  def __init__(self):
    self.relocate()
    self.type = 0

  def relocate(self):
    while True:
      self.x = random.randrange(0, int(GAME_WIDTH / SLOT_SIZE))
      self.y = random.randrange(0, int(GAME_HEIGHT / SLOT_SIZE))

      is_colliding_with_snake = False

      for part in snake.tail:
        if self.x == part[0] and self.y == part[1]:
          is_colliding_with_snake = True
          break

      if not is_colliding_with_snake:
        break

  def reset(self):
    self.relocate()
    self.type = random.randrange(0, len(Food.IMGS))

  def draw(self, screen):
    screen.blit(Food.IMGS[self.type], (self.x * SLOT_SIZE, self.y * SLOT_SIZE))

def draw_grid(screen):
  for col in range(int(GAME_WIDTH / SLOT_SIZE)):
    pygame.draw.line(screen, (50, 50, 50), (col * SLOT_SIZE, 0), (col * SLOT_SIZE, GAME_HEIGHT))
  
  for row in range(int(GAME_HEIGHT / SLOT_SIZE)):
    pygame.draw.line(screen, (50, 50, 50), (0, row * SLOT_SIZE), (GAME_WIDTH, row * SLOT_SIZE))

game_state = GameState.START
snake: Snake | None = None
food: Food | None = None

font = pygame.font.SysFont(None, 40)
start_text = font.render("Press Space to Start Game", True, (255, 255, 255))
won_text = font.render("You Won!", True, (255, 255, 255))
lost_text = font.render("You Lost!", True, (255, 255, 255))

def update():
  global running
  global snake
  global food
  global game_state
  
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    elif event.type == pygame.KEYDOWN:
      if game_state == GameState.PLAYING:
        if event.key == pygame.K_UP or event.key == pygame.K_w:
          snake.direction = Direction.UP
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
          snake.direction = Direction.DOWN
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
          snake.direction = Direction.LEFT
        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
          snake.direction = Direction.RIGHT 
        elif event.key == pygame.K_ESCAPE:
          game_state = GameState.START
      elif game_state == GameState.START or game_state == GameState.LOST or game_state == GameState.WON:
        if event.key == pygame.K_SPACE:
          pygame.mixer.Sound.play(play_sound)
          game_state = GameState.PLAYING
          snake = Snake()
          food = Food()

  if game_state == GameState.PLAYING:
    if len(snake.tail) == GRID_COLS * GRID_ROWS:
      game_state = GameState.WON
    else:
      snake.move()

      snake_head = snake.tail[-1]

      if snake_head[0] == food.x and snake_head[1] == food.y:
        snake.tail.append((food.x, food.y))
        food.reset()
        pygame.mixer.Sound.play(eat_sound)

      for i in range(len(snake.tail) - 2):
        if snake.tail[i][0] == snake_head[0] and snake.tail[i][1] == snake_head[1]:
          game_state = GameState.LOST
          break
    

def render(screen):
  screen.fill("black")

  if game_state == GameState.PLAYING:
    draw_grid(screen)
    food.draw(screen)
    snake.draw(screen)
  elif game_state == GameState.START:
    screen.blit(start_text, (GAME_WIDTH / 2 - start_text.get_width() / 2, GAME_HEIGHT / 2 - start_text.get_height() / 2))
  elif game_state == GameState.LOST:
    screen.blit(lost_text, (GAME_WIDTH / 2 - lost_text.get_width() / 2, GAME_HEIGHT / 2 - lost_text.get_height() / 2 - 80))
    screen.blit(start_text, (GAME_WIDTH / 2 - start_text.get_width() / 2, GAME_HEIGHT / 2 - start_text.get_height() / 2))
  elif game_state == GameState.WON:
    screen.blit(won_text, (GAME_WIDTH / 2 - lost_text.get_width() / 2, GAME_HEIGHT / 2 - lost_text.get_height() / 2 - 80))
    screen.blit(start_text, (GAME_WIDTH / 2 - start_text.get_width() / 2, GAME_HEIGHT / 2 - start_text.get_height() / 2))

while running:
  update()
  render(screen)
  pygame.display.flip()
  clock.tick(15)

pygame.quit()