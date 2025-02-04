import pygame
from os.path import join
from random import randint, uniform

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
         super().__init__(groups)
         self.image = pygame.image.load(join('space shooter', 'images', 'player.png')).convert_alpha()
         self.rect = self.image.get_frect(center = (WINDOW_WIDTH / 2,WINDOW_HEIGHT / 2))
         self.direction = pygame.math.Vector2()
         self.speed = 300

         #cooldown
         self.can_shoot = True
         self.laser_shoot_time = 0
         self.cooldown_duration = 400

        #mask
         self.mask = pygame.mask.from_surface(self.image)

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True
    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction *self.speed*dt

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites,laser_sprites))
            laser_sound.play()
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()

        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
         super().__init__(groups)
         self.image = surf
         self.rect = self.image.get_frect(center = (randint(0,WINDOW_WIDTH), randint(0,WINDOW_HEIGHT)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom <= 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = surf
        self.image = self.original_surf
        self.rect = self.image.get_frect(center = pos)
        self.spawn_time = pygame.time.get_ticks()
        self.life_time = 3000
        self.direction = pygame.Vector2(uniform(-.5, 0.5),1)
        self.speed = randint(400,500)
        self.rotation_speed = randint(-360, 360)
        self.rotation = 0


    def update(self, dt):

        self.rect.center += self.direction*self.speed*dt
        if self.spawn_time + self.life_time <= pygame.time.get_ticks():
            self.kill()
        #rotation
        self.rotation += self.rotation_speed *dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.image = self.frames[0]
        self.rect = self.image.get_frect(center = pos)
        
        self.current_frame = 0
        explosion_sound.play()

    def update(self,dt):
        
        self.current_frame +=  10 * dt
 
        if int(self.current_frame) < len(self.frames)  :
            self.image = self.frames[int(self.current_frame)]
        else:
            self.kill() 
        
def collisions():
    global running

    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        running = False
    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            AnimatedExplosion(explosion_surfs, laser.rect.midtop, all_sprites)
            
            laser.kill()
            
def display_score():
    current_time = pygame.time.get_ticks()
    text_surf = font.render(str(current_time),True, (240,240,240))
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH/2,WINDOW_HEIGHT -50))
    display_surface.blit(text_surf, text_rect)

    pygame.draw.rect(display_surface, (240,240,240), text_rect.inflate(20,10).move(0,-8), 5, 10)

pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Space shooter')

running = True
clock = pygame.time.Clock()

#imports
star_surf = pygame.image.load(join('space shooter', 'images', 'star.png')).convert_alpha()
meteor_surf = pygame.image.load(join('space shooter', 'images', 'meteor.png')).convert_alpha()
laser_surf = pygame.image.load(join('space shooter', 'images', 'laser.png')).convert_alpha()
font = pygame.font.Font(join('space shooter','images','Oxanium-Bold.ttf'), 40)
explosion_surfs = [pygame.image.load(join('space shooter', 'images', 'explosion',f'{i}.png')).convert_alpha() for i in range(0,21)]

laser_sound = pygame.mixer.Sound(join('space shooter','audio','laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('space shooter','audio','explosion.wav'))
explosion_sound.set_volume(0.5)
damage_sound = pygame.mixer.Sound(join('space shooter','audio','damage.ogg'))
damage_sound.set_volume(0.5)
game_music = pygame.mixer.Sound(join('space shooter','audio','game_music.wav'))
game_music.set_volume(0.3)
game_music.play(loops = -1)

#sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

stars = [Star(all_sprites, star_surf) for i in range(0,20)]
player = Player(all_sprites)

#custom events
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event,500)

while running:

    dt = clock.tick() / 1000
    #event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == meteor_event:
            x , y = randint(0,WINDOW_WIDTH), 0
            Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))

    #input
    
    all_sprites.update(dt)
    collisions()
    
    #draw the game
    display_surface.fill('#3a2e3f')
    all_sprites.draw(display_surface)
    
    display_score()
    pygame.display.update()


pygame.quit()