import pygame
import random
import time
import os

# Initialize Pygame
pygame.init()

# Set up the display
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Stickman Platform Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (135, 206, 235)  # Sky blue
LIGHT_BLUE = (173, 216, 230)  # Light blue for clouds
GRAY = (128, 128, 128)  # For rocks
DARK_GRAY = (64, 64, 64)  # For rock shadows
GROUND_COLOR = (200, 200, 200)  # Light gray for ground
RED = (255, 0, 0)  # Added for game over text
GREEN = (0, 255, 0)  # Added for restart button
BUILDING_COLOR = (169, 169, 169)  # For buildings
WINDOW_COLOR = (255, 255, 224)  # For building windows

# Player properties
player_width = 64  # Adjusted for typical sprite size
player_height = 64
player_speed = 5
jump_speed = -15
gravity = 0.8

player_velocity_y = 0
is_jumping = False
facing_right = True
player_x = WINDOW_WIDTH // 2
player_y = WINDOW_HEIGHT - player_height

# Rock properties
rock_width = 50
rock_height = 40
rock_speed = 5

# Load background image with error handling
background_path = "images/sky_background.png"  # Add a sky background image to your images folder
try:
    background = pygame.image.load(background_path)
    background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))
except (pygame.error, FileNotFoundError) as e:
    print(f"Error loading background: {e}")
    background = None

# Load player sprite with error handling
sprite_path = "images/boy.png"  # Make sure the sprite is located in the 'images' directory relative to the script
if os.path.exists(sprite_path):
    try:
        player_sprite = pygame.image.load(sprite_path)
        player_sprite = pygame.transform.scale(player_sprite, (player_width, player_height))  # Resize to fit
    except pygame.error as e:
        print(f"Error loading sprite: {e}")
        player_sprite = None  # Use None if image loading fails
else:
    print(f"Sprite file not found at {sprite_path}")
    player_sprite = None  # Use None if the file doesn't exist

# Cloud properties
class Cloud:
    def __init__(self, x):
        self.x = x
        self.y = random.randint(50, 200)
        self.width = random.randint(60, 120)
        self.height = random.randint(30, 50)
    
    def draw(self, screen):
        # Draw multiple circles for fluffy cloud appearance
        for i in range(3):
            offset_x = random.randint(-10, 10)
            offset_y = random.randint(-10, 10)
            pygame.draw.circle(screen, LIGHT_BLUE,
                             (self.x + offset_x + self.width//2, self.y + offset_y + self.height//2),
                             self.width//3)

# Building properties
class Building:
    def __init__(self, x, width, height):
        self.x = x
        self.width = width
        self.height = height
        self.window_rows = height // 40
        self.window_cols = width // 40
        
    def draw(self, screen):
        # Draw building body
        pygame.draw.rect(screen, BUILDING_COLOR, (self.x, WINDOW_HEIGHT - self.height, self.width, self.height))
        
        # Draw windows
        window_width = 20
        window_height = 30
        for row in range(self.window_rows):
            for col in range(self.window_cols):
                window_x = self.x + (col * 40) + 10
                window_y = WINDOW_HEIGHT - self.height + (row * 40) + 5
                pygame.draw.rect(screen, WINDOW_COLOR, (window_x, window_y, window_width, window_height))

# Generate buildings
buildings = []
x = 0
while x < WINDOW_WIDTH:
    width = random.randint(80, 150)
    height = random.randint(100, 400)
    buildings.append(Building(x, width, height))
    x += width + 20

# Generate clouds
clouds = []
x = -50  # Start slightly off-screen
while x < WINDOW_WIDTH + 100:  # Go slightly past screen width
    clouds.append(Cloud(x))
    x += random.randint(100, 200)  # Random spacing between clouds

# Rock class
class Rock:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = rock_width
        self.height = rock_height
    
    def move(self):
        self.x -= rock_speed  # Move the rock to the left
    
    def draw(self):
        # Draw main rock shape
        pygame.draw.polygon(screen, GRAY, [
            (self.x, self.y + self.height),
            (self.x + self.width//2, self.y),
            (self.x + self.width, self.y + self.height)
        ])
        # Add shadow detail
        pygame.draw.polygon(screen, DARK_GRAY, [
            (self.x + self.width//4, self.y + self.height//2),
            (self.x + self.width//2, self.y + self.height),
            (self.x + 3*self.width//4, self.y + self.height//2)
        ])
    
    def is_off_screen(self):
        return self.x + self.width < 0

    def check_collision(self, player_rect):
        rock_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return player_rect.colliderect(rock_rect)

# Game clock
clock = pygame.time.Clock()

# Function to draw a simple stickman
def draw_stickman(x, y, facing_right):
    # Head (circle)
    pygame.draw.circle(screen, BLACK, (x + player_width // 2, y + 10), 15)
    
    # Body (line)
    pygame.draw.line(screen, BLACK, (x + player_width // 2, y + 25), (x + player_width // 2, y + 50), 3)
    
    # Arms (lines)
    pygame.draw.line(screen, BLACK, (x + player_width // 2 - 20, y + 35), (x + player_width // 2 + 20, y + 35), 3)
    
    # Legs (lines)
    pygame.draw.line(screen, BLACK, (x + player_width // 2, y + 50), (x + player_width // 2 - 20, y + 70), 3)
    pygame.draw.line(screen, BLACK, (x + player_width // 2, y + 50), (x + player_width // 2 + 20, y + 70), 3)

    # Adjust stickman orientation (flip arms and legs based on direction)
    if not facing_right:
        pygame.draw.line(screen, BLACK, (x + player_width // 2 + 20, y + 35), (x + player_width // 2 - 20, y + 35), 3)  # Flip arms
        pygame.draw.line(screen, BLACK, (x + player_width // 2 + 20, y + 70), (x + player_width // 2 - 20, y + 70), 3)  # Flip legs

# Function to display "Game Over" and restart button
def display_game_over():
    # Create a semi-transparent overlay
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.fill(WHITE)
    overlay.set_alpha(128)  # 128 is semi-transparent
    screen.blit(overlay, (0, 0))
    
    font = pygame.font.Font(None, 72)
    game_over_text = font.render("GAME OVER", True, RED)
    screen.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, WINDOW_HEIGHT // 3))
    
    # Display the final score
    score_text = pygame.font.Font(None, 36).render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, WINDOW_HEIGHT // 2))

    # Draw restart instructions
    restart_text = pygame.font.Font(None, 36).render("Press R to Restart", True, BLACK)
    screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT // 2 + 50))

# Function to reset the game
def reset_game():
    global player_x, player_y, player_velocity_y, is_jumping, facing_right, score, rocks, game_over, final_time
    player_x = WINDOW_WIDTH // 2
    player_y = WINDOW_HEIGHT - player_height
    player_velocity_y = 0
    is_jumping = False
    facing_right = True
    score = 0
    rocks = [Rock(WINDOW_WIDTH + random.randint(100, 300), WINDOW_HEIGHT - rock_height)]
    game_over = False
    final_time = 0

# Game loop
running = True
rocks = [Rock(WINDOW_WIDTH + random.randint(100, 300), WINDOW_HEIGHT - rock_height)]
score = 0
game_over = False
final_time = 0

while running:
    # Get current time in seconds
    if not game_over:
        current_time = pygame.time.get_ticks() // 1000  # Time in seconds
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and not is_jumping and not game_over:
                player_velocity_y = jump_speed
                is_jumping = True
            if event.key == pygame.K_r and game_over:
                reset_game()

    # Only move the player and rocks if the game is not over
    if not game_over:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
            facing_right = False
        if keys[pygame.K_RIGHT] and player_x < WINDOW_WIDTH - player_width:
            player_x += player_speed
            facing_right = True

        # Apply gravity
        player_velocity_y += gravity
        player_y += player_velocity_y

        # Ground collision
        if player_y >= WINDOW_HEIGHT - player_height:
            player_y = WINDOW_HEIGHT - player_height
            player_velocity_y = 0
            is_jumping = False

        # Move rocks
        for rock in rocks:
            rock.move()

        # Remove rocks that go off-screen and add new ones
        if rocks[-1].x < WINDOW_WIDTH - 200:
            new_rock = Rock(WINDOW_WIDTH + random.randint(100, 300), WINDOW_HEIGHT - rock_height)
            rocks.append(new_rock)
        
        rocks = [rock for rock in rocks if not rock.is_off_screen()]  # Remove off-screen rocks

        # Collision detection with rocks
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        for rock in rocks:
            if rock.check_collision(player_rect):
                game_over = True  # End the game when the player hits a rock
                final_time = current_time  # Store the final time when game ends

        # Update score based on time passed
        score = current_time

    # Draw background
    if background:
        screen.blit(background, (0, 0))
    else:
        # Create a sky background if no image is available
        screen.fill(BLUE)  # Fill with sky blue color
        
        # Draw buildings
        for building in buildings:
            building.draw(screen)
            
        # Draw clouds
        for cloud in clouds:
            cloud.draw(screen)
        
        # Draw ground
        pygame.draw.rect(screen, GROUND_COLOR, (0, WINDOW_HEIGHT - 50, WINDOW_WIDTH, 50))

    # Draw player with appropriate sprite or stickman
    if player_sprite:
        current_sprite = pygame.transform.flip(player_sprite, not facing_right, False)
        screen.blit(current_sprite, (player_x, player_y))
    else:
        draw_stickman(player_x, player_y, facing_right)  # Draw stickman if no sprite is loaded

    # Draw rocks
    for rock in rocks:
        rock.draw()

    # Draw timer
    try:
        font = pygame.font.Font(None, 36)  # None uses the default system font
        display_time = final_time if game_over else current_time
        timer_text = font.render(f"Time: {display_time}s", True, BLACK)
        screen.blit(timer_text, (WINDOW_WIDTH - 150, 20))
    except pygame.error as e:
        print(f"Error drawing timer: {e}")

    # If game over, display the message and restart button
    if game_over:
        display_game_over()

    # Update display
    pygame.display.flip()
    clock.tick(60)  # Set the FPS to 60

pygame.quit()
