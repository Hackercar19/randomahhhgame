import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
INITIAL_SCROLL_SPEED = 3  # Starting speed
MAX_SCROLL_SPEED = 8     # Maximum speed
SCROLL_SPEED_INCREMENT = 0.05  # Reduced from 0.1 to 0.05 for more gradual increase
INITIAL_HORSE_SPEED = 5  # Starting horse movement speed
MAX_HORSE_SPEED = 10     # Maximum horse movement speed

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
GREEN = (34, 139, 34)  # Forest green
DARK_GREEN = (0, 100, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Escape the Monster!")
clock = pygame.time.Clock()

def get_scroll_speed(score):
    # Gradually increase speed with score
    return min(INITIAL_SCROLL_SPEED + (score * SCROLL_SPEED_INCREMENT), MAX_SCROLL_SPEED)

class BackgroundTree:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60

    def draw(self, screen):
        # Draw trunk
        pygame.draw.rect(screen, BROWN, (self.x, self.y, self.width, self.height))
        # Draw leaves
        pygame.draw.circle(screen, GREEN, (self.x + self.width//2, self.y - 20), 30)

    def update(self, scroll_speed):
        self.x -= scroll_speed

    def is_off_screen(self):
        return self.x + self.width < 0

class Obstacle:
    def __init__(self, x, y, width, height, color, obstacle_type):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.type = obstacle_type  # 'rock' or 'crocodile'

    def draw(self, screen):
        if self.type == 'rock':
            pygame.draw.rect(screen, (128, 128, 128), (self.x, self.y, self.width, self.height))
        else:  # crocodile
            # Draw body (main rectangle)
            pygame.draw.rect(screen, (0, 150, 0), (self.x, self.y, self.width, self.height))
            
            # Draw head (triangle)
            head_points = [
                (self.x + self.width, self.y + self.height//2),
                (self.x + self.width + 20, self.y + self.height//2 - 10),
                (self.x + self.width + 20, self.y + self.height//2 + 10)
            ]
            pygame.draw.polygon(screen, (0, 150, 0), head_points)
            
            # Draw tail (triangle)
            tail_points = [
                (self.x, self.y + self.height//2),
                (self.x - 15, self.y + self.height//2 - 10),
                (self.x - 15, self.y + self.height//2 + 10)
            ]
            pygame.draw.polygon(screen, (0, 150, 0), tail_points)
            
            # Draw legs
            leg_positions = [
                (self.x + 10, self.y + self.height),
                (self.x + 30, self.y + self.height),
                (self.x + 40, self.y + self.height)
            ]
            for leg_x, leg_y in leg_positions:
                pygame.draw.line(screen, (0, 150, 0), (leg_x, leg_y), (leg_x, leg_y + 15), 5)
            
            # Draw eyes
            pygame.draw.circle(screen, BLACK, (self.x + self.width + 15, self.y + self.height//2 - 5), 3)
            pygame.draw.circle(screen, BLACK, (self.x + self.width + 15, self.y + self.height//2 + 5), 3)
            
            # Draw teeth
            for i in range(3):
                pygame.draw.line(screen, WHITE, 
                               (self.x + self.width + 10, self.y + self.height//2 - 5 + i*5),
                               (self.x + self.width + 15, self.y + self.height//2 - 5 + i*5), 2)

    def update(self, scroll_speed):
        self.x -= scroll_speed

    def is_off_screen(self):
        return self.x + self.width < 0

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Monster:
    def __init__(self):
        self.reset_position()
        self.width = 50
        self.height = 50
        self.speed = 4
        self.color = RED
        self.chase_speed = 2
        self.vertical_speed = 0
        self.acceleration = 0.2

    def reset_position(self):
        self.x = WINDOW_WIDTH + 100
        self.y = random.randint(0, WINDOW_HEIGHT - 50)

    def draw(self, screen):
        # Draw monster body
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Draw eyes
        pygame.draw.circle(screen, BLACK, (self.x + 15, self.y + 15), 5)
        pygame.draw.circle(screen, BLACK, (self.x + 35, self.y + 15), 5)
        # Draw angry eyebrows
        pygame.draw.line(screen, BLACK, (self.x + 10, self.y + 10), (self.x + 20, self.y + 5), 2)
        pygame.draw.line(screen, BLACK, (self.x + 30, self.y + 5), (self.x + 40, self.y + 10), 2)

    def update(self, player_y, scroll_speed):
        # Move with the background
        self.x -= scroll_speed
        
        # Chase the player vertically
        if self.y < player_y:
            self.vertical_speed += self.acceleration
        else:
            self.vertical_speed -= self.acceleration
        
        # Apply vertical movement
        self.y += self.vertical_speed
        
        # Keep monster within screen bounds
        self.y = max(0, min(self.y, WINDOW_HEIGHT - self.height))

    def is_off_screen(self):
        return self.x + self.width < 0

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Horse:
    def __init__(self):
        self.x = WINDOW_WIDTH // 4
        self.y = WINDOW_HEIGHT // 2
        self.width = 60
        self.height = 40
        self.base_speed = INITIAL_HORSE_SPEED
        self.speed = self.base_speed
        self.jumping = False
        self.jump_height = 0
        self.galloping = False
        self.animation_frame = 0
        self.direction = 1
        self.health = 3

    def update_speed(self, scroll_speed):
        # Increase horse speed proportionally with scroll speed
        speed_factor = (scroll_speed - INITIAL_SCROLL_SPEED) / (MAX_SCROLL_SPEED - INITIAL_SCROLL_SPEED)
        self.speed = self.base_speed + (MAX_HORSE_SPEED - self.base_speed) * speed_factor

    def draw(self, screen):
        # Draw horse body
        pygame.draw.rect(screen, BROWN, (self.x, self.y, self.width, self.height))
        # Draw horse head
        pygame.draw.rect(screen, BROWN, (self.x + self.width - 10, self.y + 10, 20, 15))
        # Draw legs
        leg_positions = [(self.x + 10, self.y + self.height),
                        (self.x + 30, self.y + self.height),
                        (self.x + 40, self.y + self.height),
                        (self.x + 50, self.y + self.height)]
        
        for leg_x, leg_y in leg_positions:
            if self.galloping:
                leg_offset = 10 if self.animation_frame % 2 == 0 else -10
                pygame.draw.line(screen, BROWN, (leg_x, leg_y), (leg_x, leg_y + 30 + leg_offset), 5)
            else:
                pygame.draw.line(screen, BROWN, (leg_x, leg_y), (leg_x, leg_y + 30), 5)

        # Draw health hearts
        for i in range(self.health):
            pygame.draw.circle(screen, RED, (self.x + 20 + i*20, self.y - 20), 8)

    def move(self, dy):
        if not self.jumping:
            self.y += dy * self.speed
            self.y = max(0, min(self.y, WINDOW_HEIGHT - self.height))

    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.jump_height = 0
            self.galloping = False

    def update(self):
        if self.jumping:
            self.jump_height += 1
            self.y -= 2
            if self.jump_height >= 50:
                self.jumping = False
                self.y += 50

        if self.galloping:
            self.animation_frame += 1

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

def create_background_trees():
    trees = []
    # Create initial trees
    for _ in range(20):  # More trees for background
        x = random.randint(0, WINDOW_WIDTH)
        y = random.randint(0, WINDOW_HEIGHT - 60)
        trees.append(BackgroundTree(x, y))
    return trees

def create_obstacles():
    obstacles = []
    # Create initial obstacles
    for _ in range(10):  # Fewer obstacles since trees are now background
        x = random.randint(0, WINDOW_WIDTH)
        y = random.randint(0, WINDOW_HEIGHT - 60)
        obstacle_type = random.choice(['rock', 'crocodile'])
        if obstacle_type == 'rock':
            obstacles.append(Obstacle(x, y, 30, 30, (128, 128, 128), obstacle_type))
        else:  # crocodile
            obstacles.append(Obstacle(x, y, 50, 20, (0, 150, 0), obstacle_type))
    return obstacles

def main():
    horse = Horse()
    monster = Monster()
    background_trees = create_background_trees()
    obstacles = create_obstacles()
    game_over = False
    running = True
    score = 0
    invincibility_frames = 0
    scroll_speed = INITIAL_SCROLL_SPEED

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    horse.jump()
                elif event.key == pygame.K_r and game_over:
                    # Reset game
                    horse = Horse()
                    monster = Monster()
                    background_trees = create_background_trees()
                    obstacles = create_obstacles()
                    game_over = False
                    score = 0
                    scroll_speed = INITIAL_SCROLL_SPEED

        if not game_over:
            # Get keyboard state
            keys = pygame.key.get_pressed()
            dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
            
            # Handle galloping
            horse.galloping = keys[pygame.K_LSHIFT] and dy != 0
            
            # Update scroll speed based on score
            scroll_speed = get_scroll_speed(score)
            
            # Update horse speed based on scroll speed
            horse.update_speed(scroll_speed)
            
            # Move horse
            horse.move(dy)
            
            # Update horse state
            horse.update()

            # Update background trees
            for tree in background_trees[:]:
                tree.update(scroll_speed)
                if tree.is_off_screen():
                    background_trees.remove(tree)
                    # Add new tree at the right edge
                    background_trees.append(BackgroundTree(WINDOW_WIDTH, random.randint(0, WINDOW_HEIGHT - 60)))

            # Update obstacles
            for obstacle in obstacles[:]:
                obstacle.update(scroll_speed)
                if obstacle.is_off_screen():
                    obstacles.remove(obstacle)
                    # Add new obstacle at the right edge
                    obstacle_type = random.choice(['rock', 'crocodile'])
                    if obstacle_type == 'rock':
                        obstacles.append(Obstacle(WINDOW_WIDTH, random.randint(0, WINDOW_HEIGHT - 30), 30, 30, (128, 128, 128), obstacle_type))
                    else:  # crocodile
                        obstacles.append(Obstacle(WINDOW_WIDTH, random.randint(0, WINDOW_HEIGHT - 20), 50, 20, (0, 150, 0), obstacle_type))
                    score += 1

            # Update monster
            monster.update(horse.y, scroll_speed)
            if monster.is_off_screen():
                monster.reset_position()

            # Check for collisions
            if invincibility_frames <= 0:
                # Check collision with monster
                if horse.get_rect().colliderect(monster.get_rect()):
                    horse.health -= 1
                    invincibility_frames = 60  # 1 second of invincibility
                    if horse.health <= 0:
                        game_over = True

                # Check collision with obstacles
                for obstacle in obstacles:
                    if horse.get_rect().colliderect(obstacle.get_rect()):
                        horse.health -= 1
                        invincibility_frames = 60
                        if horse.health <= 0:
                            game_over = True
                        break

            if invincibility_frames > 0:
                invincibility_frames -= 1

        # Draw everything
        screen.fill(DARK_GREEN)
        
        # Draw background trees
        for tree in background_trees:
            tree.draw(screen)
        
        # Draw obstacles
        for obstacle in obstacles:
            obstacle.draw(screen)
        
        # Draw monster
        monster.draw(screen)
        
        # Draw horse
        horse.draw(screen)

        # Draw score and speed
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {score}', True, WHITE)
        speed_text = font.render(f'Speed: {int(scroll_speed)}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(speed_text, (10, 50))

        # Draw game over message
        if game_over:
            font = pygame.font.Font(None, 74)
            text = font.render('Game Over! Press R to restart', True, WHITE)
            text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
            screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 