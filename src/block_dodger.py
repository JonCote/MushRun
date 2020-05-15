import os
import time
import random
import sqlite3
import pygame



CONN = sqlite3.connect('bbScoreBoard.db')
C = CONN.cursor()


def create_table():
    C.execute('CREATE TABLE IF NOT EXISTS scoreBoard(keyword TEXT, score INTEGER)')


def data_entry(name, score):
    C.execute("INSERT INTO scoreBoard (keyword, score) VALUES (?, ?)", (name, score))
    CONN.commit()


def top_five_score():
    score_list = []
    C.execute("SELECT * FROM scoreBoard ORDER BY score DESC")
    for i in C.fetchmany(5):
        score_list.append(i)
    return score_list


def close_db():
    C.close()
    CONN.close()


create_table()
pygame.init()       # initialize pygame

__loctation__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
IMAGES_PATH = __loctation__ + '/images'
SOUND_PATH = __loctation__ + '/Sound'
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 900


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BRIGHT_RED = (255, 0, 0)
BRIGHT_GREEN = (0, 255, 0)
GRASS_COLOR = (57, 88, 61)


GAME_DISPLAY = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption('Block Dodger')
GAME_DISPLAY.fill(WHITE)
CLOCK = pygame.time.Clock()
OBSTACLE_IMAGE = pygame.image.load(IMAGES_PATH + '/gasBomb-v2.png')
DECOR_TREE = pygame.image.load(IMAGES_PATH + '/deadTree.png')
DECOR_ROCK = pygame.image.load(IMAGES_PATH + '/rocks.png')
DECOR_BONES = pygame.image.load(IMAGES_PATH + '/bones.png')
DEATH_SCREEN = pygame.image.load(IMAGES_PATH + '/death.png')
YELLOW_BUTTON = pygame.image.load(IMAGES_PATH + '/PNG/yellow_button04.png')
RED_BUTTON = pygame.image.load(IMAGES_PATH + '/PNG/red_button01.png')
GREEN_BUTTON = pygame.image.load(IMAGES_PATH + '/PNG/green_button02.png')
BUTTON_SOUND_EFFECT = pygame.mixer.Sound(SOUND_PATH + '/SoundFX/click2.ogg')
BUTTON_SOUND_EFFECT.set_volume(1)

MENU_MUSIC_CONTROLLER = 0


class Obstacle:
    count = 0

    @staticmethod
    def count_reset():
        Obstacle.count = 0

    def __init__(self, image):
        self.obstacle_speed = 4
        self.obstacle_width = 65
        self.obstacle_height = 70
        self.obstacle_y_location = -(random.randrange(100, 1000))
        self.obstacle_x_location = random.randrange(0, (DISPLAY_WIDTH - self.obstacle_width))
        self.obstacle_color = BLACK
        self.obstacle_draw = image

    def obstacle_generator(self):
        GAME_DISPLAY.blit(self.obstacle_draw, (self.obstacle_x_location, self.obstacle_y_location))

    def obstacle_mover(self):
        self.obstacle_y_location += self.obstacle_speed

    def obstacle_off_screen(self):
        if self.obstacle_y_location > DISPLAY_HEIGHT:
            self.obstacle_y_location = 0 - self.obstacle_height
            self.obstacle_x_location = random.randrange(0, (DISPLAY_WIDTH - self.obstacle_width))
            Obstacle.count += 0.2


class Player:

    def __init__(self):
        self.player_width = 40
        self.player_height = 40
        self.player_x = (DISPLAY_WIDTH * 0.45)
        self.player_y = (DISPLAY_HEIGHT * 0.8)
        self.player_image = pygame.image.load(IMAGES_PATH + '/char_base.png')

    def player_generator(self):
        GAME_DISPLAY.blit(self.player_image, (self.player_x, self.player_y))

    def player_move(self, x_change):
        if self.player_x < 0:
            self.player_x += 1
            self.player_image = pygame.image.load(IMAGES_PATH + '/char_moving_right.png')
        elif self.player_x > DISPLAY_WIDTH - self.player_width:
            self.player_x += -1
            self.player_image = pygame.image.load(IMAGES_PATH + '/char_moving_left.png')
        else:
            if x_change < 0:
                self.player_image = pygame.image.load(IMAGES_PATH + '/char_moving_left.png')
            elif x_change > 0:
                self.player_image = pygame.image.load(IMAGES_PATH + '/char_moving_right.png')
            else:
                self.player_image = pygame.image.load(IMAGES_PATH + '/char_base.png')

            self.player_x += x_change


def collision_detector(player, obj):
    if player.player_y < obj.obstacle_y_location + obj.obstacle_height \
            and player.player_y + player.player_height > obj.obstacle_y_location \
            and player.player_x < obj.obstacle_x_location + obj.obstacle_width \
            and player.player_x + player.player_width > obj.obstacle_x_location:
        music_player(3, 'death.wav')
        death_screen()


def score_counter(count):
    font = pygame.font.SysFont(None, 25)
    text = font.render("Score: "+str(count), True, BLACK)
    GAME_DISPLAY.blit(GREEN_BUTTON, (-75, -20))
    GAME_DISPLAY.blit(text, (0, 0))


def message_display(text, font, size, x_location, y_location, timer=None):
    text_attributes = pygame.font.Font(font, size)
    text_surf, text_rect = text_objects(text, text_attributes)
    text_rect.center = (x_location, y_location)
    GAME_DISPLAY.blit(text_surf, text_rect)

    pygame.display.update()

    if timer is not None:
        time.sleep(timer)


def text_objects(text, font):
    text_surface = font.render(text, True, BLACK)
    return text_surface, text_surface.get_rect()


def button(text, font,
           x_location, y_location,
           width, height,
           action=None, parm1=None, parm2=None):

    mouse_location = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if (x_location + width > mouse_location[0] > x_location and y_location + height > mouse_location[1] > y_location):
        GAME_DISPLAY.blit(YELLOW_BUTTON, (x_location, y_location))

        if click[0] == 1 and (parm2 and parm1) is not None:
            BUTTON_SOUND_EFFECT.play()
            action(parm1, parm2)
        elif click[0] == 1 and parm1 is not None:
            BUTTON_SOUND_EFFECT.play()
            action(parm1)
        elif click[0] == 1 and action is not None:
            BUTTON_SOUND_EFFECT.play()
            action()
    else:
        GAME_DISPLAY.blit(RED_BUTTON, (x_location, y_location))

    message_display(text, font, 20, (x_location + (width/2)), (y_location + (height/2)))


def object_list_maker(number_of_object, image):
    object_list = []
    i = 0
    while i < number_of_object:
        obj = Obstacle(image)
        object_list.append(obj)
        i += 1
    return object_list


def object_control_loop(obj_list, player, collision=False):
    for i in obj_list:
        i.obstacle_generator()
        i.obstacle_mover()
        i.obstacle_off_screen()
        if collision:
            collision_detector(player, i)


def data_verification(name, score):
    data_entry(name, score)
    game_intro()


def print_leader_board():
    top_score = top_five_score()
    p_count = 0
    message_display("Name", 'freesansbold.ttf', 25, 400, 100)
    message_display("Score", 'freesansbold.ttf', 25, 500, 100)
    for i in top_score:
        p_count += 1
        message_display(str(p_count)+")", 'freesansbold.ttf', 25, 300, (100 + p_count * 50))
        message_display(str(i[0]), 'freesansbold.ttf', 25, 400, (100 + p_count * 50))
        message_display(str(i[1]), 'freesansbold.ttf', 25, 500, (100 + p_count * 50))


def submit_score_screen():
    GAME_DISPLAY.fill(GRASS_COLOR)
    score = int(Obstacle.count)
    font = pygame.font.Font(None, 32)
    input_box = pygame.Rect(350, 500, 140, 32)
    text = ''
    message_display("Score: " + str(score), 'freesansbold.ttf', 25, 400, 450)
    message_display("Name: ", 'freesansbold.ttf', 25, 300, 518)
    print_leader_board()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    data_verification(text, score)
                    text = ''
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif event.key == pygame.K_ESCAPE:
                    text = ''
                    game_intro()
                else:
                    if len(text) < 3:
                        text += event.unicode

        pygame.draw.rect(GAME_DISPLAY, WHITE, input_box)

        txt_surface = font.render(text, True, BLACK)

        GAME_DISPLAY.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(GAME_DISPLAY, BLACK, input_box, 2)

        button("Submit Score", 'freesansbold.ttf', 200, 600, 150, 50, data_verification, text, score)
        button("Main Menu", 'freesansbold.ttf', 400, 600, 150, 50, game_intro)

        pygame.display.update()
        CLOCK.tick(20)


def display_fade():
    fade = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    fade.fill(GRASS_COLOR)
    for alpha in range(0, 255):
        fade.set_alpha(alpha)
        GAME_DISPLAY.blit(fade, (0, 0))
        pygame.display.update()
        pygame.time.delay(2)
    GAME_DISPLAY.fill(GRASS_COLOR)


def music_player(music_number, song_track):
    global MENU_MUSIC_CONTROLLER
    if(MENU_MUSIC_CONTROLLER == 0 and music_number == 0):
        pygame.mixer.music.load(SOUND_PATH + '/Music/' + song_track)
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.35)
        MENU_MUSIC_CONTROLLER = 1
    elif(music_number == 1):
        pygame.mixer.music.fadeout(500)
        pygame.mixer.music.load(SOUND_PATH + '/Music/' + song_track)
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.35)
    elif(music_number == 2):
        pygame.mixer.music.fadeout(500)
        pygame.mixer.music.load(SOUND_PATH + '/Music/' + song_track)
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.35)
    elif(music_number == 3):
        pygame.mixer.music.load(SOUND_PATH + '/SoundFx/' + song_track)
        pygame.mixer.music.play(0)
        pygame.mixer.music.set_volume(0.35)

        
def quit_game():
    close_db()
    pygame.quit()


def high_score_board():
    GAME_DISPLAY.fill(GRASS_COLOR)
    print_leader_board()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_intro()

        button("Main Menu", 'freesansbold.ttf', 300, 600, 150, 50, game_intro)


def death_screen():
    death = True
    score_counter(int(Obstacle.count))
    display_fade()
    global MENU_MUSIC_CONTROLLER
    MENU_MUSIC_CONTROLLER = 0
    music_player(2, 'gameOver.ogg')
    while death:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

        GAME_DISPLAY.blit(DEATH_SCREEN, (275,100))
        message_display('Game Over!', 'freesansbold.ttf', 115, (DISPLAY_WIDTH / 2), (DISPLAY_HEIGHT / 2))
        button("Replay", 'freesansbold.ttf', 100, 650, 100, 50, game_loop)
        button("Quit", 'freesansbold.ttf', 500, 650, 100, 50, quit_game)
        button("Submit Score", 'freesansbold.ttf', 300, 650, 150, 50, submit_score_screen)
        pygame.display.update()
        CLOCK.tick(20)


def game_intro():
    intro = True
    GAME_DISPLAY.fill(GRASS_COLOR)
    music_player(0, 'mainMenu.wav')
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

        message_display("Welcome", 'freesansbold.ttf', 80, (DISPLAY_WIDTH/2), (DISPLAY_HEIGHT/2))

        button("Start", 'freesansbold.ttf', 100, 650, 100, 50, game_loop)
        button("Quit", 'freesansbold.ttf', 500, 650, 100, 50, quit_game)
        button("Leader Boards", 'freesansbold.ttf', 300, 650, 150, 50, high_score_board)

        pygame.display.update()
        CLOCK.tick(60)


def game_loop():
    player = Player()
    Obstacle.count_reset()

    x_change = 0
    obstacle_list = object_list_maker(10, OBSTACLE_IMAGE)
    decor_tree_list = object_list_maker(10, DECOR_TREE)
    decor_rock_list = object_list_maker(10, DECOR_ROCK)
    decor_bones_list = object_list_maker(2, DECOR_BONES)
    game_exit = False
    music_player(1, 'level2.wav')

    while not game_exit:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x_change = -4
                elif event.key == pygame.K_RIGHT:
                    x_change = 4

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    x_change = 0

        player.player_move(x_change)
        GAME_DISPLAY.fill(GRASS_COLOR)

        object_control_loop(decor_tree_list, player)
        object_control_loop(decor_rock_list, player)
        object_control_loop(decor_bones_list, player)
        object_control_loop(obstacle_list, player, True)

        player.player_generator()
        score_counter(int(Obstacle.count))

        pygame.display.update()
        CLOCK.tick(120)


game_intro()
