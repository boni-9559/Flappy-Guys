# video tutorial link: https://youtu.be/6gLeplbqtqg
import math
import os
import random
from os import listdir
from os.path import isfile, join
import pygame

pygame.init()

pygame.display.set_caption("Flappy guy (& tutorial from freecodecamp in youtube)")

def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles =[]

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image

WIDTH, HEIGHT = 800,800
FPS = 60 
PLAYER_VEL = 5
window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites):
    return[pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile (join(path,f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left" ] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 128, size, size)
    surface.blit(image, (0,0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite): 
    COLOR = (255, 0, 0)
    GRAVITY = 0
    SPRITES = load_sprite_sheets("MainCharacters", "PinkMan", 32, 32, True)
    ANIMATION_DELAY = 8

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.health = 100
        self.tick = 57
        self.tickresetter = 288

    def jump(self):
        self.y_vel = -self.GRAVITY * 4
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count >= 1:
            self.fall_count = 0

    def make_hit(self):
        self.hit = True

    def move(self, dx,dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self,vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self,vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0  

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / 200) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1
    
    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count >= 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"
        elif self.y_vel != 0:
            sprite_sheet = "idle"

        if sprite_sheet == "hit":
            self.tick -= 1
            self.tickresetter -= 1
            
        if self.tick == 0:
            self.health -= 20
            self.tick += 57
            print("Health = " + str(self.health))

        if self.tickresetter == 0:
            self.tick == 57
            self.tickresetter += 288

        if self.health <= 0:
            pygame.quit()
            pygame.init()

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x, offset_y):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x, offset_y):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))

  

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0,0))
        self.mask = pygame.mask.from_surface(self.image)

def draw(window, background, bg_image, player, objects, offset_x, offset_y):
    for tile in background:
        window.blit(bg_image, tile)
    
    for obj in objects:
        obj.draw(window, offset_x, offset_y)

    player.draw(window, offset_x, offset_y)

    pygame.display.update()

class Fire(Object):
    ANIMATION_DELAY = 9

    def __init__(self,x,y,width,height):
        super().__init__(x,y,width,height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width,height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player,obj):
            if dy > 0:
                player.health = 0
                print("You died!")
                player.rect.bottom = obj.rect.top
                player.landed() 
            elif dy < 0:
                player.health = 0
                print("You died!")
                player.rect.top = obj.rect.bottom
                player.hit_head()

        

            collided_objects.append(obj)

    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
    player.move(-dx, 0)
    player.update()
    return collided_object




def handle_move(player, objects):
    p = 0
    keys = pygame.key.get_pressed()
    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 0.2)
    collide_right = collide(player, objects, PLAYER_VEL * 0.2)

    if p <= 0 and not p > 0:
        if keys[pygame.K_p] and not p > 0 :
            player.GRAVITY = 1
            p += 1   
            player.SPRITES = load_sprite_sheets("MainCharacters", "PinkMan", 32, 32, True)    
            print("Game Started")
            
    if player.GRAVITY >= 1:
        player.move_right(PLAYER_VEL * 0.4)

            

    #if keys[pygame.K_LEFT] and not collide_left or keys[pygame.K_a] and not collide_left:
        #player.move_left(PLAYER_VEL)
        #if keys[pygame.K_LSHIFT]:
            #player.move_left(PLAYER_VEL * 2)
       
    #if keys[pygame.K_RIGHT] and not collide_right or keys[pygame.K_d] and not collide_right: 
        #player.move_right(PLAYER_VEL)
        #if keys[pygame.K_LSHIFT]:
            #player.move_right(PLAYER_VEL * 2) 
        
    
        

    if keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
        pygame.quit()
    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Pink.png")

    block_size = 96

    player = Player(100, 120, 50, 50)
    fire = Fire(100, HEIGHT - block_size - 64,16,32)
    fire.on()
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) 
             for i in range((-WIDTH * -0) // block_size, (WIDTH * 20) // block_size)
    ]
    
    objects = [*floor, 
                

               


                #Block(block_size * 3, HEIGHT - block_size * 7.5, block_size),

                   #fire
                   ]
    
    for i in range(-1, 90):
        objects.append(Block(block_size * i, HEIGHT - block_size * 15, block_size))
        objects.append(Block(block_size * i, HEIGHT - block_size * 1, block_size))

    for wa in range (1,15):
        objects.append(Block(block_size * -1, HEIGHT - block_size * wa, block_size))
        #objects.append(Block(block_size * 5, HEIGHT - block_size * ab, block_size))
    
    
    

    def pillar1a():
        for b in range(13,15): objects.append(Block(block_size * 10, HEIGHT- block_size * b, block_size))
        for ab in range(1,10): objects.append(Block(block_size * 10, HEIGHT- block_size * ab, block_size))
    def pillar1b():
        for gf in range(9,15): objects.append(Block(block_size * 10, HEIGHT- block_size * gf, block_size))
        for gh in range(1,6): objects.append(Block(block_size * 10, HEIGHT- block_size * gh, block_size))
    def choose_pillar():
        if random.choice([True, False]):
            pillar1a()
            print("Press P to start the game!")
            print("pillar1a")
            
        else:
            pillar1b()
            print("Press P to start the game!")
            print("pillar1b")
    

    def pillar2a():
        for bc in range(12,15): objects.append(Block(block_size * 14, HEIGHT- block_size * bc, block_size))
        for ae in range(1,9): objects.append(Block(block_size * 14, HEIGHT- block_size * ae, block_size))
    def pillar2b():
        for bce in range(7,15): objects.append(Block(block_size * 14, HEIGHT- block_size * bce, block_size))
        for aer in range(1,3): objects.append(Block(block_size * 14, HEIGHT- block_size * aer, block_size))  
    def choose_pillar2():
        if random.choice([True, False]):
            pillar2a()
            print("pillar2a")
        else:
            pillar2b()
            print("pillar2b")
        

    def pillar3a():
        for ba in range(6,15): objects.append(Block(block_size * 18, HEIGHT- block_size * ba, block_size))
        for ag in range(1,2): objects.append(Block(block_size * 18, HEIGHT- block_size * ag, block_size))
    def pillar3b():
        for bcf in range(14,15): objects.append(Block(block_size * 18, HEIGHT- block_size * bcf, block_size))
        for aev in range(1,10): objects.append(Block(block_size * 18, HEIGHT- block_size * aev, block_size))
    def choose_pillar3():
        if random.choice([True, False]):
            pillar3a()
            print("pillar3a")
        else:
            pillar3b()
            print("pillar3b")
      
    
    def pillar4a():
        for br in range(9,15): objects.append(Block(block_size * 22, HEIGHT- block_size * br, block_size))
        for ah in range(1,5): objects.append(Block(block_size * 22, HEIGHT- block_size * ah, block_size))
    def pillar4b():
        for gb in range(8,15): objects.append(Block(block_size * 22, HEIGHT- block_size * gb, block_size))
        for tj in range(1,4): objects.append(Block(block_size * 22, HEIGHT- block_size * tj, block_size))
    def choose_pillar4():
        if random.choice([True, False]):
            pillar4a()
            print("pillar4a")
        else:
            pillar4b()
            print("pillar4b")
      

    def pillar5a():
        for bf in range(7,15): objects.append(Block(block_size * 26, HEIGHT- block_size * bf, block_size))
        for ay in range(1,3):objects.append(Block(block_size * 26, HEIGHT- block_size * ay, block_size))
    def pillar5b():
        for bt in range(13,15): objects.append(Block(block_size * 26, HEIGHT- block_size * bt, block_size))
        for vc in range(1,10):objects.append(Block(block_size * 26, HEIGHT- block_size * vc, block_size))
    def choose_pillar5():
        if random.choice([True, False]):
            pillar5a()
            print("pillar5a")
        else:
            pillar5b()
            print("pillar5b")
      
    
    def pillar6a():
        for e in range(15,15):objects.append(Block(block_size * 30, HEIGHT- block_size * e, block_size))
        for c in range(1,11):objects.append(Block(block_size * 30, HEIGHT- block_size * c, block_size))
    def pillar6b():
        for eh in range(9,15):objects.append(Block(block_size * 30, HEIGHT- block_size * eh, block_size))
        for cp in range(1,6):objects.append(Block(block_size * 30, HEIGHT- block_size * cp, block_size))
    def choose_pillar6():
        if random.choice([True, False]):
            pillar6a()
            print("pillar6a")
        else:
            pillar6b()
            print("pillar6b")
      

    def pillar7a():
        for e in range(7,15):objects.append(Block(block_size * 34, HEIGHT- block_size * e, block_size))
        for c in range(1,3):objects.append(Block(block_size * 34, HEIGHT- block_size * c, block_size))
    def pillar7b():
        for by in range(13,15):objects.append(Block(block_size * 34, HEIGHT- block_size * by, block_size))
        for gi in range(1,9):objects.append(Block(block_size * 34, HEIGHT- block_size * gi, block_size))
    def choose_pillar7():
        if random.choice([True, False]):
            pillar7a()
            print("pillar7a")
        else:
            pillar7b()
            print("pillar7b")
      

    def pillar8a():
        for r in range(8,15): objects.append(Block(block_size * 38, HEIGHT- block_size * r, block_size))
        for t in range(1,4): objects.append(Block(block_size * 38, HEIGHT- block_size * t, block_size))
    def pillar8b():
        for hg in range(11,15): objects.append(Block(block_size * 38, HEIGHT- block_size * hg, block_size))
        for op in range(1,8): objects.append(Block(block_size * 38, HEIGHT- block_size * op, block_size))
    def choose_pillar8():
        if random.choice([True, False]):
            pillar8a()
            print("pillar8a")
        else:
            pillar8b()
            print("pillar8b")
      

    def pillar9a():
        for y in range(8,15): objects.append(Block(block_size * 42, HEIGHT- block_size * y, block_size))
        for u in range(1,4):objects.append(Block(block_size * 42, HEIGHT- block_size * u, block_size))
    def pillar9b():
        for yb in range(14,15): objects.append(Block(block_size * 42, HEIGHT- block_size * yb, block_size))
        for uh in range(1,10):objects.append(Block(block_size * 42, HEIGHT- block_size * uh, block_size))
    def choose_pillar9():
        if random.choice([True, False]):
            pillar9a()
            print("pillar9a")
        else:
            pillar9b()
            print("pillar9b")
      

    def pillar10a():
        for p in range(11,15): objects.append(Block(block_size * 46, HEIGHT- block_size * p, block_size))
        for o in range(1,7): objects.append(Block(block_size * 46, HEIGHT- block_size * o, block_size))
    def pillar10b():
        for gj in range(13,15): objects.append(Block(block_size * 46, HEIGHT- block_size *gj, block_size))
        for ko in range(1,9): objects.append(Block(block_size * 46, HEIGHT- block_size * ko, block_size))
    def choose_pillar10():
        if random.choice([True, False]):
            pillar10a()
            print("pillar10a")
        else:
            pillar10b()
            print("pillar10b")
      


    def pillar11a():
        for s in range(14,15): objects.append(Block(block_size * 50, HEIGHT- block_size * s, block_size))
        for d in range(1,10): objects.append(Block(block_size * 50, HEIGHT- block_size * d, block_size))
    def pillar11b():
        for sg in range(12,15): objects.append(Block(block_size * 50, HEIGHT- block_size * sg, block_size))
        for dh in range(1,8): objects.append(Block(block_size * 50, HEIGHT- block_size * dh, block_size))
    def choose_pillar11():
        if random.choice([True, False]):
            pillar11a()
            print("pillar11a")
        else:
            pillar11b()
            print("pillar11b")
    

    def pillar12a():
        for f in range(7,15): objects.append(Block(block_size * 54, HEIGHT- block_size * f, block_size))
        for g in range(1,3): objects.append(Block(block_size * 54, HEIGHT- block_size * g, block_size))
    def pillar12b():
        for fgh in range(10,15): objects.append(Block(block_size * 54, HEIGHT- block_size * fgh, block_size))
        for gyu in range(1,6): objects.append(Block(block_size * 54, HEIGHT- block_size * gyu, block_size))
    def choose_pillar12():
        if random.choice([True, False]):
            pillar12a()
            print("pillar12a")
        else:
            pillar12b()
            print("pillar12b")
    


    def pillar13a():
        for h in range(13,15): objects.append(Block(block_size * 58, HEIGHT- block_size * h, block_size))
        for j in range(1,9): objects.append(Block(block_size * 58, HEIGHT- block_size * j, block_size))
    def pillar13b():
        for h in range(7,15): objects.append(Block(block_size * 58, HEIGHT- block_size * h, block_size))
        for j in range(1,4): objects.append(Block(block_size * 58, HEIGHT- block_size * j, block_size))
    def choose_pillar13():
        if random.choice([True, False]):
            pillar13a()
            print("pillar13a")
        else:
            pillar13b()
            print("pillar13b")
    


    def pillar14a():
        for k in range(11,15): objects.append(Block(block_size * 62, HEIGHT- block_size * k, block_size))
        for l in range(1,8): objects.append(Block(block_size * 62, HEIGHT- block_size * l, block_size))
    def pillar14b():
        for ke in range(12,15): objects.append(Block(block_size * 62, HEIGHT- block_size * ke, block_size))
        for lb in range(1,8): objects.append(Block(block_size * 62, HEIGHT- block_size * lb, block_size))
    def choose_pillar14():
        if random.choice([True, False]):
            pillar14a()
            print("pillar14a")
        else:
            pillar14b()
            print("pillar14b")
    


    def pillar15a():
        for z in range(14,15):objects.append(Block(block_size * 66, HEIGHT- block_size * z, block_size))
        for x in range(1,10):objects.append(Block(block_size * 66, HEIGHT- block_size * x, block_size))
    def pillar15b():
        for z in range(6,15):objects.append(Block(block_size * 66, HEIGHT- block_size * z, block_size))
        for x in range(1,3):objects.append(Block(block_size * 66, HEIGHT- block_size * x, block_size))
    def choose_pillar15():
        if random.choice([True, False]):
            pillar15a()
            print("pillar15a")
        else:
            pillar15b()
            print("pillar15b")
    


    def pillar16a():
        for c in range(12,15): objects.append(Block(block_size * 70, HEIGHT- block_size * c, block_size))
        for v in range(1,9): objects.append(Block(block_size * 70, HEIGHT- block_size * v, block_size))
    def pillar16b():
        for cv in range(8,15): objects.append(Block(block_size * 70, HEIGHT- block_size * cv, block_size))
        for vr in range(1,5): objects.append(Block(block_size * 70, HEIGHT- block_size * vr, block_size))
    def choose_pillar16():
        if random.choice([True, False]):
            pillar16a()
            print("pillar16a")
        else:
            pillar16b()
            print("pillar16b")
    


    def pillar17a():
        for b in range(8,15): objects.append(Block(block_size * 74, HEIGHT- block_size * b, block_size))
        for n in range(1,5): objects.append(Block(block_size * 74, HEIGHT- block_size * n, block_size))
    def pillar17b():
        for bk in range(15,15): objects.append(Block(block_size * 74, HEIGHT- block_size * bk, block_size))
        for nh in range(1,12): objects.append(Block(block_size * 74, HEIGHT- block_size * nh, block_size))
    def choose_pillar17():
        if random.choice([True, False]):
            pillar17a()
            print("pillar17a")
        else:
            pillar17b()
            print("pillar17b")
    

    def pillar18a():
        for m in range(4,15): objects.append(Block(block_size * 78, HEIGHT- block_size * m, block_size))
        for qw in range(1,1): objects.append(Block(block_size * 78, HEIGHT- block_size * qw, block_size))
    def pillar18b():
        for mg in range(13,15): objects.append(Block(block_size * 78, HEIGHT- block_size * mg, block_size))
        for qh in range(1,9): objects.append(Block(block_size * 78, HEIGHT- block_size * qh, block_size))
    def choose_pillar18():
        if random.choice([True, False]):
            pillar18a()
            print("pillar18a")
        else:
            pillar18b()
            print("pillar18b")
    

    def pillar19a():
        for er in range(7,15): objects.append(Block(block_size * 82, HEIGHT- block_size * er, block_size))
        for ty in range(1,3): objects.append(Block(block_size * 82, HEIGHT- block_size * ty, block_size))
    def pillar19b():
        for eb in range(11,15): objects.append(Block(block_size * 82, HEIGHT- block_size * eb, block_size))
        for ti in range(1,7): objects.append(Block(block_size * 82, HEIGHT- block_size * ti, block_size))
    def choose_pillar19():
        if random.choice([True, False]):
            pillar19a()
            print("pillar19a")
        else:
            pillar19b()
            print("pillar19b")
    

    def pillar20a():
        for ui in range(8,15):objects.append(Block(block_size * 86, HEIGHT- block_size * ui, block_size))
        for op in range(1,6): objects.append(Block(block_size * 86, HEIGHT- block_size * op, block_size))
    def pillar20b():
        for uib in range(11,15):objects.append(Block(block_size * 86, HEIGHT- block_size * uib, block_size))
        for opn in range(1,9): objects.append(Block(block_size * 86, HEIGHT- block_size * opn, block_size))
    def choose_pillar20():
        if random.choice([True, False]):
            pillar20a()
            print("pillar20a")
        else:
            pillar20b()
            print("pillar20b")

    for _ in range(1):
        choose_pillar()
        choose_pillar2()
        choose_pillar3()             
        choose_pillar4()
        choose_pillar5()
        choose_pillar6()
        choose_pillar7()
        choose_pillar8()
        choose_pillar9()
        choose_pillar10()
        choose_pillar11()
        choose_pillar12()
        choose_pillar13()
        choose_pillar14()
        choose_pillar15()
        choose_pillar16()
        choose_pillar17()
        choose_pillar18()
        choose_pillar19()
        choose_pillar20()

    

    def pillarfin():
        for gg in range(1,15):objects.append(Block(block_size * 88, HEIGHT- block_size * gg, block_size))
    pillarfin()
    print("if you find a pillar that you can't go through, that means you win!")
    
    
   



    offset_x = 0
    offset_y = 0
    scroll_area_width = 2000 
    scroll_area_height = 384


    run = True
    while run:
        clock.tick(FPS)
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 100^1000000000000000000000000000000000000000000000000000000000000000000000000000000:
                    player.jump() 
                elif event.key == pygame.K_w and player.jump_count < 100^1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000:
                    player.jump()
                elif event.key == pygame.K_UP and player.jump_count < 100^100000000000000000000000000000000000000000000000000000000000000000000000000000000:
                    player.jump()
        
        player.loop(FPS)   
        fire.loop() 
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x, offset_y)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel >= 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += (player.x_vel * 1)

        if ((player.rect.top - offset_y >= WIDTH - scroll_area_height) and player.y_vel >= 0) or (
                (player.rect.bottom - offset_y <= scroll_area_height) and player.y_vel < 0):
            offset_y += player.y_vel

        

if __name__ == "__main__":
    main(window)

 