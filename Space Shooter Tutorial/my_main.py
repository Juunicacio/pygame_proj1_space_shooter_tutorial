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

# Time for Collision and lasers. We need to shoot the lasers from the enemies or from the player. First thing 
# we need to do when we're going to be shooting lasers is create some kind of laser object
class Laser:
    # this is gonna represent just one laser object
    # the idea is that we're gonna have multiple lasers being shot from each player. So if I shoot a 
    # laser going upwards, I need to make sure that it keeps going in that same direction, not following the player's moving
    # so the laser is gonna have an x, y and a image (passed from the ship class). When we make a new laser object, the player 
    # will create the laser object add it to its laser list and then it will control how those lasers are moved
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        # we need to make a mask for this as well because this is what is gonna be colliding
        self.mask = pygame.mask.from_surface(self.img)

    # draw method, taking the window as parameter
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    
    # define move, which will be moving with the velocity. That goes upwards for the player and downwards for the enemies. 
    # If we wanna go down, we will give a positive value, if we wanna go up we will give a negative value for velocity
    def move(self, vel):
        self.y += vel
    
    # define off screen, tell us if these lasers are off the screen, based on the height of the screen
    def off_screen(self, height):
        return not (self.y <= height and self.y > -50)
    
    # method collision, which is gonna tell us if this collides with an object. Call the function 
    # called collide. Return the collide of object itself. See if the obj is colliding with myself (this specific laser)
    def collision(self, obj):
        # returning the value of the collide function 
        return collide(obj, self)

# Set up a character, we want it to move on the screen
# Abstract class, we're not gonna use it, we're gonna inherit from it later
# we have enemies ship and player ship
class Ship:
    # CLASS VARIABLE
    COOLDOWN = 30 # half a second

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

        # Draw the laser
        for laser in self.lasers:
            # we have a draw method on our lasers that just draws them here
            laser.draw(window)
    
    # define a new method, to move the lasers. The reason I've objs here is that, when I move these lasers, I wanna check 
    # for collision with all of these objects, to do that I need the objects that I wanna to check collision with which are objs
    # So we are gonna move the lasers by this velocity. ## Change objs to obj, check if each laser has hit the player.
    # This is gonna be used for the player and for the enemy, but inside the player what I'll actually do, cause this is the base
    # class (ship), I'll implement a new method called move_lasers, but rather than checking if we hit the player, we'll check 
    # if we hit any enemies. We need 2 separate move_lasers methods. Since there is only one player, we only need 1 obj here
    def move_lasers(self, vel, obj):
        # Increment the cooldown counter by calling it, so everytime we move the lasers we're gonna call this once a frame,
        # wich means that we'll increment the cooldown counter when we move the lasers, so we can check if we can send another
        # laser or not. Then we'll loop through all of the lasers, move by the velocity
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            # and if the laser is off the screen(Height), we'll delete the laser
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            # otherwise, if laser collides with an obj (Player)
            elif laser.collision(obj):
                # then we can reduce the health of that obj, wich will be our player
                obj.health -= 10
                # delete the laser
                self.lasers.remove(laser)


    # To not go off the screen with the ship
    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

    # handle counting the cooldown
    def cooldown(self):
        # if that is greater than half a second,
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        # if the cooldown is 0 we are not doing anything, but if it is grater than 0, and it's not past the 30 seconds,
        # increment it by 1
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
        
    # Now, we need to implement a few things inside of the enemy and player class, in terms of creating a laser, as well as 
    # creating a cool-down for the laser, so we can't shoot it too fast. First thing, implement a shoot method here inside 
    # of this base class ship, because both of our classes will be able to use this
    def shoot(self):
        # if we are not in the process of counting up to a specific cooldown or keeping track of how long until the next shot
        if self.cool_down_counter == 0:
            # then, create a new laser and add it to the laser list. We'll give it our xy value and our laser_img
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            # start the cooldown counter, so that it starts counting up
            self.cool_down_counter = 1

class Player(Ship):
    def __init__(self, x, y, health=100):
        # Call the Ship initialization method. That create for us all the properties from ship
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        # Creating a mask, allow us do pixel perfect collision
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
    
    # copied the move_lasers from ship, and change a little bit. Change it to objs
    def move_lasers(self, vel, objs):
        # Increment the cooldown counter by calling it, so everytime we move the lasers we're gonna call this once a frame,
        # wich means that we'll increment the cooldown counter when we move the lasers, so we can check if we can send another
        # laser or not. Then we'll loop through all of the lasers, move by the velocity
        self.cooldown()
        # for each laser that the player has
        for laser in self.lasers:
            # move the laser
            laser.move(vel)
            # and if the laser is off the screen(Height), we'll delete the laser
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            # otherwise, if laser collides with an obj (Enemies)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        # Since we're passing a list of all of the enemies, (if the player's lasers have hit any enemies)
                        # we're just gonna remove that enemy from the objs list
                        objs.remove(obj)
                        # delete the laser if it is in the list
                        if laser in self.lasers:
                            self.lasers.remove(laser)
    
    # To do the health bar, implement a function inside a player. And all we're gonna do is draw rectangles that are red 
    # and green, based on the health of my player. So, the 1st rectangle I'm gonna draw is gonna be red. It's gonna be 
    # the lenght of my player, and then I'm gonna draw a green rectangle that goes on top of that red rectangle, but will 
    # be only the lenght of the health. So if we have 50% health, so it show half green and half red. We need to draw 
    # the health bar, so its gonna take the window as parameter. Then we need to color, then we need the rectangle (we 
    # want the healthbar bellow the player, so for the height, we want the x value of the player and the y + the picture of 
    # the ship + 10, for the width, we want the x value as the same width of the ship, and for the height 10 pixels.
    # Now copy the rectangle and do the same in green, except the only thinga that's gonna change is the width and the color
    # we are gonna multiply the width by some fraction, that will tell us how much width we wanna put. Multiply by 
    # health/max_health
    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))
    
    # let's implement the healthbar into the draw method of the player ship, so let's define the draw again. And we are 
    # gonna call the super draw method, and then we will call the self.healthbar.
    # I'm just overriting the draw method of the ship class with drawing the healthbar
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

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
    
    # The bullets were be shooting slightly offset from the center of the enemies, so to fix that, you can just subtract the 
    # x-value of where you're gonna start shooting the bullet from, so in this case, we need to override the shoot method from 
    # ship (copy it) in enemy class, and offset where it is being created.
    def shoot(self):
        # if we are not in the process of counting up to a specific cooldown or keeping track of how long until the next shot
        if self.cool_down_counter == 0:
            # then, create a new laser and add it to the laser list. We'll give it our xy value and our laser_img
            laser = Laser(self.x-18, self.y, self.laser_img)
            self.lasers.append(laser)
            # start the cooldown counter, so that it starts counting up
            self.cool_down_counter = 1

# Creating a collide function, because we need to check if things are colliding when we're moving the laser. Essentially 
# what we're gonna do with the collide is use this masks to determine if 2 objects are overlapping, if the pixels between 
# them are overlapping and if they are, then we will say, yes, these 2 objects are colliding.
def collide(obj1, obj2):
    # use this mask property called overlap. an object has a width and a height. If there is pixels in the same area of both 
    # objs, overlapping both objs, we will say that this collided. To see if both mask of the objs are overlapping, we need 
    # to come up with something called offset (tell us the distance between the top left hand corner of both, and so the point
    # of intersection between them)
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    # is obj1 mask overlapping obj2 mask with the offset of offset_x, offset_y? (based on the offset we've given between the 
    # difference of their top left coordinates, then we will return true, otherwise we will return false (none), doesn't equal none)
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None 

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
    # lost font
    lost_font = pygame.font.SysFont("comicsans", 60)


    # Start move enemies, the list will store where all our enemies are
    enemies = []
    # We are gonna start with the enemies wave of 5 and increment that every time. Wave in random positions
    # Every time we get the next level, generate a whole new batch of enemies
    wave_length = 5
    enemy_vel = 1

    # Defining laser_velocity as variable
    laser_vel = 5

    # Defining a velocity for the key pressed movement
    player_vel = 10

    # Using a Player. Draw it inside of the redraw_window
    player = Player(300, 630)

    # Defining a lost variable
    lost = False
    # Increment a time for the lost message. How long to show the lost message before reset the game and also pause the game
    lost_count = 0


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

        # Draw lost
        if lost:
            lost_label = lost_font.render("Game Over!", 1, (255, 0, 0))
            # positioning label in the center of the screen. The center is width/2, but since we have the label width
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 425))           


        pygame.display.update()


    while run:
        # Tick this clock based on FPS, makes it run at a consistent speed in any device
        clock.tick(FPS)

        # After the clock, immediately call redraw_window function
        redraw_window()

        # implementing something to fix if we go negative lives, tell us that we lost
        if lives <= 0: #or player.health <= 0:
            lost = True
            # if lost = true, we're gonna increment a counter system, that show us a lost message
            # on the screen, for a certain amount of time, and then when done, we go back to main menu
            # that we are gonna create later
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                # If lost_count is greater than 3 seconds, pause the game
                run = False                
            else:
                # otherwise, continue, which means, don't do wherever is after continue, don't let us move, 
                # don't move anything, and go back to the beginning of this while loop and keep running. We will redraw 
                # the window, everytime, until that lost message hit 3 seconds.
                continue

        
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
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            # for each enemy ship, we need to move their lasers each loop, so for enemy in enemies we also need to call
            # move_lasers by its vel, and check if it's hit the player
            enemy.move_lasers(laser_vel, player)

            # let's make the enemy start shooting at us. What we need to do to have the enemies shooting is picking some 
            # probability that they're gonna shoot each frame. Random between 0 and some number is equal to 1, then have 
            # the enemy shoot. So what number do we pick? Let's say you want every second that your enemy to have a 
            # probability of 50% of shooting, so every second you want a 50% chance that your enemy is gonna shoot. So 
            # in theory every 2 seconds your enemy should shoot a bullet and that's gonna apply to every single enemy.
            # You need to take that probability which is 1/2, which would mean you just put 2 here and multiply it by sixty 
            # because you have 60 frames per second, so if you want 50% chance of shooting every second, then you make this number 
            # 120, because 2*60=120. If you want this easier, you can do 4*60 (240), so you can change this to have it equate 
            # to the amount of seconds before you want the enemy to shoot. You can hard code to have every 2 seconds the enemy to
            # shoot, but this way you can have a degree of randomness to make the game more difficult.
            if random.randrange(0, 2*FPS) == 1:
                enemy.shoot()
            
            # now, to do the collision between the player and all the enemies. Control it right after the enemy shoots
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
                
            if player.health <= 0:
                lives -= 1
                player.health = 100

            # now, everytime we move the enemies, make sure that they're not off the screen
            # and if they are, decrement the lives and remove them from the list 
            # (since we are removing then, we need to make a copy of the enemy list "in enemies[:]")
            # Put it as elif just to make sure that we're not gonna check if the enemy is off the screen if it's already 
            # collided with the player
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)            
            

        # Draw on screen and check for events
        # first check if the user has quit the window
        # every time we run this loop 60*sec loop through all events

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # if we say run = False, it will bring us back to main_menu. if we do quit(), we quit the entire python program
                quit()
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
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player.y + player_vel + player.get_height() + 10 < HEIGHT: # +10 for the healthbar
            player.y += player_vel

        # way to draw and to move our lasers, we are gonna call the shoot method that creates the laser from here, 
        # so, if we hit the space bar, we'll call shoot, which will create a new laser object
        if keys[pygame.K_SPACE]:
            # remember, it is only gonna create a new laser if the cooldown counter is equal to zero
            player.shoot()
        
        # move the player's lasers, move_lasers by its NEGATIVE vel, and check if it's hit any objects
        player.move_lasers(-laser_vel, enemies)

# Main Menu, what we wanna do is essentially have it, so its says like press any key to begin, and when you press that key, 
# you can begin. That way if you die, it'll bring you back to the main menu and you can choose when you wanna start playing 
# again. Let's implement a main menu
def main_menu():
    # creating a font
    title_font = pygame.font.SysFont("comicsans", 70)
    # I'm not moving anything around, so I don't need a clock here
    run = True
    while run:
        # put the background
        WIN.blit(BG, (0,0))
        # draw some text that says press space to begin. Rendering in the screen
        title_label = title_font.render("Press the mouse to start the game...", 1, (255,255,255))
        # let's put this in the middle of the screen
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # if we press the x button, run = false, we're gonna quit the game
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # if we press the mouse, enter in this main loop and start playing the game
                main()
    pygame.quit()



# Call the main_menu loop
main_menu()






