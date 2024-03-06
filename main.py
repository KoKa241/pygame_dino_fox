import pygame
import random
import json
import os

def main():
    pygame.init()
    resolution = (1200, 600)
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(resolution)
    pygame.display.set_caption("Test game for Logika") #by Vlad Klymenko
    FPS = 60
    player_images = [pygame.transform.scale(pygame.image.load(f'res/player_img/player-run-{i}.png'), (78,78)) for i in range(1, 7)]
    barier_images = [pygame.image.load('res/environment/big-crate.png'), pygame.image.load('res/environment/rock.png')]
    
    class Player(pygame.sprite.Sprite):
        def __init__(self) -> None:
              super().__init__()
              self.image = player_images[0]
              self.rect = self.image.get_rect()
              self.rect.center = (300, 400)
              self.animation_frame = 0
              self.img_change_counter = 0
              self.jump = False
              self.jump_count = 12
              self.original_y = self.rect.y
              self.jump_time_counter = 0
        
        def update(self):
            if self.img_change_counter == 4:
                if self.animation_frame == 5:
                    self.animation_frame = 0
                    self.image = player_images[self.animation_frame]
                else:
                    self.animation_frame += 1
                    self.image = player_images[self.animation_frame]
                self.img_change_counter = 0
            else:
                self.img_change_counter += 1
            if self.jump:
                if self.jump_time_counter == 2:
                    if self.jump_count >= -10:
                        neg = 1
                        if self.jump_count < 0:
                            neg = -1
                        self.rect.y -= (self.jump_count ** 2) * 0.3 * neg
                        self.jump_count -= 1
                    else:
                        self.jump = False
                        self.jump_count = 10
                        self.rect.y = self.original_y
                    self.jump_time_counter = 0
                else:
                    self.jump_time_counter += 1
    
    class Barier(pygame.sprite.Sprite):
        def __init__(self) -> None:
            super().__init__()
            size = random.randint(30, 60)
            self.image = random.choice(barier_images)
            self.image = pygame.transform.scale(self.image, (size, size))
            self.rect = self.image.get_rect()
            self.rect.center = (resolution[0] + 70, 435 - size/3)
        
        def update(self):
            self.rect.x -= 3
        
    def get_best_score(filename):
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                return data.get('best_score', 0)  # return best score from json file
        except FileNotFoundError:
            return 0  #return 0 if file not found

    def write_best_score(filename, best_score):
        data = {'best_score': best_score}
        with open(filename, 'w') as file:
            json.dump(data, file)


    logo = pygame.image.load("res/logo/logika.png")
    pygame.display.set_icon(logo)

    font = pygame.font.Font("res/fonts/Oswald-Regular.ttf", 30)
    text = font.render("Score: 0", True, (255, 255, 255))
    score_menu = font.render("0 points", True, (255, 255, 255))
    best_score_menu = font.render("Best score: 0 points", True, (38, 227, 255))
    play_again = font.render("Play again", True, (218, 247, 166))
    score_menu_rect = score_menu.get_rect()
    score_menu_rect.center = (resolution[0]//2, 100)
    best_score_menu_rect = best_score_menu.get_rect()
    best_score_menu_rect.center = (resolution[0]//2, 140)
    play_again_rect = play_again.get_rect()
    play_again_rect.center = (resolution[0]//2, 380)
    text_rect = text.get_rect()
    text_rect.center = (1100, 50)
    
    background = pygame.image.load("res/bg/forest_bg.jpg").convert() #background
    background = pygame.transform.scale(background, resolution)
    
    pygame.mixer.music.load("res/sound/bg_sound.mp3") #sound
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
    pygame.mixer.music.pause()
    lose = pygame.mixer.Sound("res/sound/lose.wav")
    
    bg_x = 0
    player = Player()
    player_group = pygame.sprite.GroupSingle()
    player_group.add(player)
    
    barier_group = pygame.sprite.Group()
    barier_group.add(Barier())
    
    best_score = get_best_score('best_score.json')
    score = 0
    spawn_clock = 0
    spawn_target = 120
    game = True
    menu = False
    
    while True:                                #main loop
        if game:                               #game loop
            player_group.update()
            barier_group.update()
            screen.blit(background, (bg_x, 0)) #animation background
            screen.blit(background, (bg_x + resolution[0], 0))
            screen.blit(text, text_rect)
            player_group.draw(screen)
            barier_group.draw(screen)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and player.jump == False:
                 player.jump = True
            pygame.mixer.music.unpause()
            bg_x -= 3
            if bg_x == -resolution[0]:
                bg_x = 0
            if score % 3 == 0:
                text = font.render(f"Score: {score}", True, (255, 255, 255))
            for barrier in barier_group.copy(): #barier delete if go out of screen
                if barrier.rect.right <= 0:  
                    barier_group.remove(barrier)

            pygame.display.update()
            clock.tick(FPS)
            
            if spawn_clock == spawn_target:
                barier_group.add(Barier())
                spawn_clock = 0
                spawn_target = random.randint(2, 3) * FPS
            else:
                spawn_clock += 1
            score += 1
            if pygame.sprite.spritecollide(player, barier_group, False):
                 if score > best_score:
                     best_score = score
                 barier_group.empty()
                 pygame.mixer.music.pause()
                 lose.play()
                 game = False
        else:
              if menu == False:
                  pygame.image.save(screen, "res/menu.png")
                  menu_img = pygame.image.load("res/menu.png").convert()
                  menu_img = pygame.transform.smoothscale(menu_img, (resolution[0]//3, resolution[1]//3)) #menu bg blur
                  menu_img = pygame.transform.smoothscale(menu_img, resolution)
                  score_menu = font.render(f"{score} points", True, (255, 255, 255))
                  best_score_menu = font.render(f"Best score: {best_score} points", True, (254, 108, 19))
                  screen.blit(menu_img, (0, 0))
                  menu = True
              screen.blit(score_menu, score_menu_rect)
              screen.blit(best_score_menu, best_score_menu_rect)
              screen.blit(play_again, play_again_rect)
              pygame.display.update()
              clock.tick(FPS//3)
        for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        write_best_score('best_score.json', best_score)
                        if os.path.exists("res/menu.png"):
                            os.remove("res/menu.png")
                        pygame.quit()
                        quit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if play_again_rect.collidepoint(event.pos):
                            game = True
                            menu = False
                            score = 0
    

if __name__ == "__main__":
    main()
