import pygame
from pygame.locals import *
import random
import time
import sys
import json
import os

highscorefil = 'highscore.json'

def loadhighscore():
    if os.path.exists(highscorefil):
        with open(highscorefil,'r',encoding='utf-8') as f:
            return json.load(f).get("highscore",0)
    else:
        return 0

def savehighscores(highscore):
    with open(highscorefil,'w',encoding='utf-8') as f:
        json.dump({"highscore":highscore},f,indent=2)

width = 850
height = 650
blocksize = 40
pygame.init()
pygame.mixer.init()
score = 0
snake_speed = 7
game_over = False
running = True
game_state = "menu"
start_sound = pygame.mixer.Sound('strart_hiss.mp3')
apple_crunch = pygame.mixer.Sound('apple_crunch.wav')
game_over_sound = pygame.mixer.Sound('game_over.mp3')
pygame.display.set_caption("Snake Game")
screen = pygame.display.set_mode((width,height))
Clock = pygame.time.Clock()
snakePosition = [300,200]
font = pygame.font.Font(None, 32)
game_over_Font = pygame.font.Font(None, 72)
medium_font = pygame.font.Font(None, 40)

def write_text(text,x,y,fontO=font,color=(255,255,255)):
    textsurface = fontO.render(text,True,color)
    screen.blit(textsurface,(x,y))

def draw_menu():
    screen.fill((7,13,110))
    write_text("SNAKE GAME",width//2 - 180, height//2 - 200, game_over_Font, (36, 214, 13))
    write_text("Press SPACE to Start",width//2 - 140, height//2 - 80, medium_font, (255,255,255))
    write_text("Use Arrow Keys to Move",width//2 - 160, height//2 - 40, font, (200,200,200))
    write_text("Don't Hit Walls or Yourself!",width//2 - 180, height//2, font, (200,200,200))
    write_text(f"High Score: {highscore}",width//2 - 100, height//2 + 80, medium_font, (36, 214, 13))

def draw_game_over():
    screen.fill((7,13,110))
    write_text("GAME OVER",width//2 - 160, height//2 - 180, game_over_Font, (220, 50, 50))
    write_text(f"Your Score: {score}",width//2 - 100, height//2 - 80, medium_font, (255,255,255))
    write_text(f"High Score: {highscore}",width//2 - 110, height//2 - 40, medium_font, (36, 214, 13))
    
    if score == highscore and score > 0:
        write_text(" NEW HIGH SCORE",width//2 - 140, height//2 + 20, medium_font, (255, 215, 0))
    
    write_text("Press SPACE to Play Again",width//2 - 150, height//2 + 80, font, (200,200,200))
    write_text("Press ESC to Quit",width//2 - 90, height//2 + 120, font, (200,200,200))

def draw_inplay():
    write_text(f"Score: {score}",10,10, font, (255,255,255))
    write_text(f"High Score: {highscore}",10,40, font, (200,200,200))
    pygame.draw.line(screen,(128,128,128),(0,70),(width,70),2)

def generate_walls():
    walls = []
    for x in range(0, width, blocksize):
        walls.append([x, 80])
    
    for x in range(0, width, blocksize):
        walls.append([x, height - blocksize])
    
    for y in range(80 + blocksize, height - blocksize, blocksize):
        walls.append([0, y])
    
    for y in range(80 + blocksize, height - blocksize, blocksize):
        walls.append([width - blocksize, y])
    
    return walls

walls = generate_walls()

def draw_walls():
    for wall in walls:
        screen.blit(wallImage, wall)

class Snake():
    def __init__(self):
        self.direction = 'RIGHT'
        self.body = [[300, 160], [260, 160], [220, 160]]
        self.growFlag = False
        self.size = blocksize

        self.headI = pygame.image.load('head.png')
        self.headI = pygame.transform.scale(self.headI, (self.size, self.size))
        self.heads = {
            'UP': pygame.transform.rotate(self.headI, 180),
            'DOWN': self.headI,
            'LEFT': pygame.transform.rotate(self.headI, 270),
            'RIGHT': pygame.transform.rotate(self.headI, 90)
        }

        self.color1 = (100, 200, 100)
        self.color2 = (70, 160, 70)
        self.color3 = (50, 120, 50)

        self.body_raw = self.createbody()
        self.tail_raw = self.createtail()

        self.directions = ['RIGHT', 'RIGHT', 'RIGHT']

    def createbody(self):
        surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(surface, self.color1, (0, 0, self.size, self.size), border_radius=12)
        pygame.draw.rect(surface, self.color2, (0, self.size // 2, self.size, self.size // 2), border_radius=12)
        pygame.draw.line(surface, self.color3, (4, 4), (self.size - 4, 4), 2)
        return surface

    def createtail(self):
        surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.polygon(surface, self.color1, [(self.size // 4, 0), (3 * self.size // 4, 0), (self.size, self.size), (0, self.size)])
        pygame.draw.polygon(surface, self.color2, [(self.size // 4, self.size // 2), (3 * self.size // 4, self.size // 2), (self.size, self.size), (0, self.size)])
        return surface

    def update(self, keys):
        if keys[pygame.K_RIGHT] and self.direction != 'LEFT':
            self.direction = 'RIGHT'
        elif keys[pygame.K_LEFT] and self.direction != 'RIGHT':
            self.direction = 'LEFT'
        elif keys[pygame.K_UP] and self.direction != 'DOWN':
            self.direction = 'UP'
        elif keys[pygame.K_DOWN] and self.direction != 'UP':
            self.direction = 'DOWN'

    def move(self):
        x, y = self.body[0]
        if self.direction == 'RIGHT':
            x += self.size
        elif self.direction == 'LEFT':
            x -= self.size
        elif self.direction == 'UP':
            y -= self.size
        elif self.direction == 'DOWN':
            y += self.size

        if x >= width:
            x = 0
        elif x < 0:
            x = width - blocksize
        if y >= height:
            y = 80
        elif y < 80:
            y = height - blocksize
            
        new_head = [x, y]
        self.body.insert(0, new_head)
        self.directions.insert(0, self.direction)

        if not self.growFlag:
            self.body.pop()
            self.directions.pop()
        else:
            self.growFlag = False

    def draw(self, screen):
        for i, pos in enumerate(self.body):
            dir = self.directions[i]
            if i == 0:
                screen.blit(self.heads[dir], pos)
            elif i == len(self.body) - 1:
                tail_img = pygame.transform.rotate(self.tail_raw, self.get_rotation_angle(dir))
                screen.blit(tail_img, pos)
            else:
                body_img = pygame.transform.rotate(self.body_raw, self.get_rotation_angle(dir))
                screen.blit(body_img, pos)

    def get_rotation_angle(self, direction):
        return {
            'UP': 180,
            'DOWN': 0,
            'LEFT': 270,
            'RIGHT': 90
        }[direction]

    def collisionChecker(self):
        head = self.body[0]
        if head in self.body[1:]:
            return True
        
        return False

    def reset(self):
        self.body = [[300, 200], [280, 200], [260, 200]]
        self.direction = 'RIGHT'
        self.directions = ['RIGHT', 'RIGHT', 'RIGHT']
        self.growFlag = False

class Apple():
    def __init__(self):
        self.image = pygame.image.load('apple.png')
        self.image = pygame.transform.scale(self.image,(40,40))
        self.respawn()
    
    def respawn(self):
        while True:
            x = random.randint(1, (width//blocksize)-2) * blocksize
            y = random.randint(3, (height//blocksize)-2) * blocksize
            self.position = [x, y]
            if self.position not in walls and self.position not in snake.body:
                break
    
    def draw(self,screen):
        screen.blit(self.image,self.position)

snake = Snake()
apple = Apple()

def reset():
    global score, snake_speed
    score = 0
    snake_speed = 7
    snake.reset()
    apple.respawn()

highscore = loadhighscore()
if highscore == None:
    highscore = 0

while running:
    screen.fill((20,20,20))
    keys = pygame.key.get_pressed()
    
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                if game_state == "menu":
                    game_state = "playing"
                    reset()
                    start_sound.play()
                elif game_state == "game_over":
                    game_state = "playing"
                    reset()
                    start_sound.play()
            elif event.key == K_ESCAPE:
                if game_state == "playing":
                    game_state = "menu"
                elif game_state == "game_over":
                    running = False
    
    if game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        snake.update(keys)
        snake.move()

        if snake.collisionChecker():
            game_over_sound.play()
            game_state = "game_over"
        else:
            head_rect = pygame.Rect(snake.body[0][0], snake.body[0][1], blocksize, blocksize)
            apple_rect = pygame.Rect(apple.position[0], apple.position[1], blocksize, blocksize)
            if head_rect.colliderect(apple_rect):
                score += 1
                apple_crunch.play()
                snake.growFlag = True
                apple.respawn()
                if score > highscore:
                    highscore = score
                    savehighscores(highscore)
                if snake_speed < 15:
                    snake_speed += 0.1

        screen.fill((20,20,20))
        draw_inplay()
        apple.draw(screen)
        snake.draw(screen)
    
    elif game_state == "game_over":
        draw_game_over()
    
    pygame.display.flip()
    Clock.tick(int(snake_speed) if game_state == "playing" else 60)

pygame.quit()
sys.exit()