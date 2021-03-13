import pygame
import os
import time
import random
# Initialize fonts to it works
pygame.font.init()

# Setting our pygame window, width, heigth and name for our screen
WIDTH, HEIGHT = 850,850
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Space Shooter")

# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Player ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))

YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background
# to the background be in the correct side of the window, scale it with transform.scale method, 2nd arg the dimension
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

# Set up a character, we want it to move on the screen
# Abstract class, we're not gonna use it, we're gonna inherit from it later
# we have enemies ship and player ship
class Ship:
    # Properties of this ship we wanna store
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        
        # Allow us to draw the ship and the laser, when pick an image for the ship
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    # Define a few methods, draw taking the window as parameter to say where to we draw this
    def draw(self, window):
        # To draw a rectangle
        #pygame.draw.rect(window, (255,0,0), (self.x, self.y, 50, 50), 0) # where to draw, color, x/y position, rect (dimension) and fill it = 0

        # Drawing a proper ship
        window.blit(self.ship_img, (self.x, self.y))

    # To not go off the screen with the ship
    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self, x, y, health=100):
        # Call the Ship initialization method. That create for us all the properties from ship
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        # Creating a mask, allow us do pixel perfect collision
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

class Enemy(Ship):
    # Class variable for the colors, making a dict, when we pass the color as a string "red", and it gives me the right images
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, color, health=100):
        # Call the Ship initialization method. That create for us all the properties from ship
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        # Creating a mask, allow us do pixel perfect collision
        self.mask = pygame.mask.from_surface(self.ship_img)

    # Method that allow us to move the ship
    def move(self, vel):
        # The enemies ship will only be moving downwards, if we pass a velocity to this method we will move the ship downwards
        self.y += vel


# Main loop settings, handle all of our events, collisions, draws, char move, quit
def main():
    # define few variables for the game
    run = True
    FPS = 60
    clock = pygame.time.Clock()

    # After the background image, we need to draw some things on the screen
    # To draw text, create a font to be rendering, initialize it
    lives = 5
    level = 0
    main_font = pygame.font.SysFont("comicsans", 50)


    # Start move enemies, the list will store where all our enemies are
    enemies = []
    # We are gonna start with the enemies wave of 5 and increment that every time. Wave in random positions
    # Every time we get the next level, generate a whole new batch of enemies
    wave_length = 5
    enemy_vel = 1


    # Defining a velocity for the key pressed movement
    player_vel = 10

    # Using a Player. Draw it inside of the redraw_window
    player = Player(300, 650)

    # Create a function inside the main loop to redraw things, call it inside while, only can call inside of the main function
    # it allow us to call the variables created inside the main loop, rather then create its own funtion and pass parameters
    def redraw_window():
        # The first thing to do, since we are redrawing everything is draw the background image, cover anything draw behind
        # the blit function take one of the images passed and draw in the window
        WIN.blit(BG, (0,0))

        # Draw text, make a label and blit that label to the screen. The 1 is antialias wherever you are rendering some text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))        
        # blit the label to the screen with the position
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        # Draw the Enemies
        for enemy in enemies:
            enemy.draw(WIN)

        # Draw the Player
        player.draw(WIN)        


        pygame.display.update()


    while run:
        # Tick this clock based on FPS, makes it run at a consistent speed in any device
        clock.tick(FPS)

        # After the clock, immediately call redraw_window function
        redraw_window()
        
        # If we killed all the enemies, increase the game level
        if len(enemies) == 0:
            level += 1
            # let's increment the amount of enemies we are gonna have
            wave_length += 5
            # Spaw enemies and append to the enemies list. 
            # When spaw enemies, pick random positions for them, way above the screen, so them don't come down at the same time
            for i in range(wave_length):
                # For x and y, first the range for the x position, then the range for the y position 
                enemy = Enemy(
                    random.randrange(50, WIDTH-100), 
                    random.randrange(-1500*level/5, -100), # *level/5 for when the level is high
                    random.choice(["red", "green", "blue"])
                    )
                # add them to the enemies list. Then I can access my enemies list, to move them
                enemies.append(enemy)

        # To move the enemies. Everytime they're on the screen, if there's any enemies in our list,
        # then move them down by their velocity
        for enemy in enemies:
            enemy.move(enemy_vel)


        # Draw on screen and check for events
        # first check if the user has quit the window
        # every time we run this loop 60*sec loop through all events

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            # we could also check here if we get a keydown event, but we will use that in other loop, 
            # because it would only register one key at a time, if I pressed up and left, it wouln't move both ways

        """ 
        KEYS PRESSED AND POSITION ON THE SCREEN:
        To use keys at the same time. Return the dict of all keys pressed at the same time
        left, subtract from x value. -= 1 means 1 pixel to the left. define velocity to how fast move it
        right, add from x value
        up, subtract from y value
        down, add from y value

        If I add this player_vel to the current value of my x will I be of the screen? 
        If I'm not off the screen, let me move 

        The reason I can go far off to the right and to the bottom is because we're checking 
        the coordinates of the top left corner. Is the edge of this cube hit? add 50 (width of the cube)
        """

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player.x - player_vel > 0: 
            player.x -= player_vel
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player.x + player_vel + player.get_width() < WIDTH: 
            player.x += player_vel
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and player.y - player_vel > 0: 
            player.y -= player_vel
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player.y + player_vel + player.get_height() < HEIGHT: 
            player.y += player_vel        


# Call the main loop
main()






