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
            json.load(f).get("highscore",0)
    else:
        return 0
def savehighscores(highscore):
    with open(highscorefil,'w',encoding='utf-8') as f:
        json.dump({"highscore":highscore},f,indent=2)

width = 850
height = 650
blocksize =40
pygame.init()
score = 0
snake_speed = 10
game_over = False
running = True
pygame.display.set_caption("Snake Game")
screen = pygame.display.set_mode((width,height))
Clock = pygame.time.Clock()
snakePosition = [300,200]

class Snake():
    def __init__(self):
        self.direction = 'RIGHT'
        self.body = [[300, 200], [280, 200], [260, 200]]
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

        self.directions = ['RIGHT', 'RIGHT', 'RIGHT']  # match body length

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
        return (
            head in self.body[1:] or
            head[0] < 0 or head[0] >= width or
            head[1] < 0 or head[1] >= height
        )

class Apple():
    def __init__(self):
        self.image = pygame.image.load('apple.png')
        self.image = pygame.transform.scale(self.image,(40,40))
        self.respawn()
    def respawn(self):
        self.position = [random.randint(0,(width//blocksize)-1)*blocksize,random.randint(0,(height//blocksize)-1)*blocksize]
    def draw(self,screen):
        screen.blit(self.image,self.position)

snake =Snake()
apple= Apple()
highscore = loadhighscore()
if highscore ==None:
    highscore =0
while running:
    screen.fill((20,20,20))
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
    snake.update(keys)
    snake.move()

    head_rect = pygame.Rect(snake.body[0][0], snake.body[0][1], blocksize, blocksize)
    apple_rect = pygame.Rect(apple.position[0], apple.position[1], blocksize, blocksize)
    if head_rect.colliderect(apple_rect):
        score += 1
        snake.growFlag = True
        apple.respawn()
        if score > highscore:
            highscore = score
            savehighscores(highscore)


        if snake.collisionChecker():
            print("Game over")
    apple.draw(screen)
    snake.draw(screen)
    pygame.display.flip()
    Clock.tick(10)
pygame.quit()
sys.exit()


