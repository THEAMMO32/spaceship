import pygame
import random
import sys
from spaceship import SpaceShip, CrewMember, Mission, Role, MissionEvent

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

class Star:
    """Background star particle."""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.randint(1, 4)
        self.size = random.randint(1, 2)
    
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
    
    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size)

class Meteor:
    """Meteor obstacle."""
    def __init__(self):
        self.size = random.choice([20, 30, 40, 50])
        self.x = random.randint(0, WIDTH - self.size)
        self.y = -self.size
        self.speed = random.randint(2, 5)
        self.health = self.size // 10
    
    def update(self):
        self.y += self.speed
    
    def draw(self, screen):
        color = (100, 100, 100)
        pygame.draw.circle(screen, color, (int(self.x + self.size // 2), int(self.y + self.size // 2)), self.size // 2)
        pygame.draw.circle(screen, (80, 80, 80), (int(self.x + self.size // 2), int(self.y + self.size // 2)), self.size // 2, 2)
    
    def is_off_screen(self):
        return self.y > HEIGHT

class Rocket:
    """Player rocket projectile."""
    def __init__(self, x, y, offset=0):
        self.x = x + offset
        self.y = y
        self.speed = 10
        self.width = 4
        self.height = 15
    
    def update(self):
        self.y -= self.speed
    
    def draw(self, screen):
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height))
        pygame.draw.polygon(screen, RED, [(self.x, self.y), (self.x + self.width, self.y), (self.x + self.width // 2, self.y - 5)])
    
    def is_off_screen(self):
        return self.y < 0

class Powerup:
    """Power-up collectible."""
    def __init__(self, powerup_type):
        self.type = powerup_type  # 'fuel', 'health', 'oxygen'
        self.x = random.randint(20, WIDTH - 20)
        self.y = -20
        self.speed = 3
        self.size = 20
        
        if powerup_type == 'fuel':
            self.color = RED
        elif powerup_type == 'health':
            self.color = GREEN
        else:  # oxygen
            self.color = BLUE
    
    def update(self):
        self.y += self.speed
    
    def draw(self, screen):
        if self.type == 'fuel':
            # Red barrel
            pygame.draw.rect(screen, self.color, (self.x - 10, self.y - 10, 20, 20))
            pygame.draw.rect(screen, (150, 0, 0), (self.x - 10, self.y - 10, 20, 20), 2)
        elif self.type == 'health':
            # Green medkit
            pygame.draw.rect(screen, self.color, (self.x - 10, self.y - 10, 20, 20))
            pygame.draw.rect(screen, WHITE, (self.x - 8, self.y - 2, 16, 4))
            pygame.draw.rect(screen, WHITE, (self.x - 2, self.y - 8, 4, 16))
        else:  # oxygen
            # Blue tank
            pygame.draw.ellipse(screen, self.color, (self.x - 8, self.y - 12, 16, 24))
            pygame.draw.ellipse(screen, (0, 50, 200), (self.x - 8, self.y - 12, 16, 24), 2)
    
    def is_off_screen(self):
        return self.y > HEIGHT

class Game:
    """Main game class."""
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Spaceship Simulator")
        self.clock = pygame.time.Clock()
        self.reset_game()
    
    def reset_game(self):
        """Reset game state."""
        # Create spaceship and crew
        self.ship = SpaceShip("Explorer-1")
        self.ship.position = [WIDTH // 2, HEIGHT - 80]
        
        self.crew = [
            CrewMember("Alex", Role.PILOT, skills={'piloting': 90}),
            CrewMember("Sam", Role.ENGINEER, skills={'repair': 85}),
            CrewMember("Taylor", Role.MEDIC, skills={'medicine': 80})
        ]
        
        # Create mission
        self.mission = Mission(
            "Deep Space Exploration",
            ["Survive 5 minutes", "Collect resources", "Avoid asteroids"]
        )
        
        # Game objects
        self.stars = [Star() for _ in range(100)]
        self.meteors = []
        self.rockets = []
        self.powerups = []
        
        # Game state
        self.meteor_spawn_timer = 0
        self.powerup_spawn_timer = 0
        self.rocket_launcher_index = 0  # Alternate between launchers
        self.current_event = None
        self.event_timer = 0
        self.fuel_consumption_timer = 0
        self.oxygen_consumption_timer = 0
        
        # Font
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
    
    def handle_input(self):
        """Handle player input."""
        keys = pygame.key.get_pressed()
        
        # Movement
        if keys[pygame.K_LEFT] and self.ship.position[0] > 30:
            self.ship.position[0] -= 5
        if keys[pygame.K_RIGHT] and self.ship.position[0] < WIDTH - 30:
            self.ship.position[0] += 5
        if keys[pygame.K_UP] and self.ship.position[1] > 30:
            self.ship.position[1] -= 5
        if keys[pygame.K_DOWN] and self.ship.position[1] < HEIGHT - 30:
            self.ship.position[1] += 5
    
    def spawn_meteor(self):
        """Spawn a new meteor."""
        self.meteors.append(Meteor())
    
    def spawn_powerup(self):
        """Spawn a random powerup."""
        powerup_type = random.choice(['fuel', 'health', 'oxygen'])
        self.powerups.append(Powerup(powerup_type))
    
    def shoot_rocket(self):
        """Fire a rocket from alternating launchers."""
        # Alternate between left and right launchers
        offsets = [-15, 15]
        offset = offsets[self.rocket_launcher_index]
        self.rocket_launcher_index = (self.rocket_launcher_index + 1) % 2
        
        rocket = Rocket(self.ship.position[0], self.ship.position[1] - 20, offset)
        self.rockets.append(rocket)
    
    def check_collisions(self):
        """Check for collisions between objects."""
        ship_rect = pygame.Rect(self.ship.position[0] - 25, self.ship.position[1] - 15, 50, 30)
        
        # Rocket-meteor collisions
        for rocket in self.rockets[:]:
            rocket_rect = pygame.Rect(rocket.x, rocket.y, rocket.width, rocket.height)
            for meteor in self.meteors[:]:
                meteor_rect = pygame.Rect(meteor.x, meteor.y, meteor.size, meteor.size)
                if rocket_rect.colliderect(meteor_rect):
                    if rocket in self.rockets:
                        self.rockets.remove(rocket)
                    meteor.health -= 1
                    if meteor.health <= 0 and meteor in self.meteors:
                        self.meteors.remove(meteor)
                    break
        
        # Ship-meteor collisions
        for meteor in self.meteors[:]:
            meteor_rect = pygame.Rect(meteor.x, meteor.y, meteor.size, meteor.size)
            if ship_rect.colliderect(meteor_rect):
                damage = meteor.size // 5
                self.ship.take_damage(damage)
                if meteor in self.meteors:
                    self.meteors.remove(meteor)
        
        # Ship-powerup collisions
        for powerup in self.powerups[:]:
            powerup_rect = pygame.Rect(powerup.x - 10, powerup.y - 10, 20, 20)
            if ship_rect.colliderect(powerup_rect):
                if powerup.type == 'fuel':
                    self.ship.refuel(30)
                elif powerup.type == 'health':
                    self.ship.repair(25)
                else:  # oxygen
                    self.ship.refill_oxygen(30)
                self.powerups.remove(powerup)
    
    def update(self):
        """Update game state."""
        # Update stars
        for star in self.stars:
            star.update()
        
        # Update meteors
        for meteor in self.meteors[:]:
            meteor.update()
            if meteor.is_off_screen():
                self.meteors.remove(meteor)
        
        # Update rockets
        for rocket in self.rockets[:]:
            rocket.update()
            if rocket.is_off_screen():
                self.rockets.remove(rocket)
        
        # Update powerups
        for powerup in self.powerups[:]:
            powerup.update()
            if powerup.is_off_screen():
                self.powerups.remove(powerup)
        
        # Spawn meteors
        self.meteor_spawn_timer += 1
        if self.meteor_spawn_timer > random.randint(30, 60):
            self.spawn_meteor()
            self.meteor_spawn_timer = 0
        
        # Spawn powerups
        self.powerup_spawn_timer += 1
        if self.powerup_spawn_timer > random.randint(180, 300):
            self.spawn_powerup()
            self.powerup_spawn_timer = 0
        
        # Consume resources
        self.fuel_consumption_timer += 1
        if self.fuel_consumption_timer > 60:
            self.ship.consume_fuel(0.5)
            self.fuel_consumption_timer = 0
        
        self.oxygen_consumption_timer += 1
        if self.oxygen_consumption_timer > 90:
            self.ship.consume_oxygen(1)
            self.oxygen_consumption_timer = 0
        
        # Update mission and events
        self.event_timer += 1
        if self.event_timer > 300:
            event = self.mission.update()
            if event:
                self.current_event = event
            self.event_timer = 0
        
        # Check collisions
        self.check_collisions()
        
        # Check game over
        if self.ship.hull_integrity <= 0:
            return False
        
        return True
    
    def draw_ship(self):
        """Draw the spaceship."""
        x, y = self.ship.position
        
        # Ship body
        pygame.draw.polygon(self.screen, BLUE, 
                          [(x, y - 20), (x - 25, y + 10), (x + 25, y + 10)])
        
        # Cockpit
        pygame.draw.circle(self.screen, (100, 200, 255), (x, y - 5), 8)
        
        # Wings
        pygame.draw.polygon(self.screen, (0, 80, 200), 
                          [(x - 25, y + 10), (x - 40, y + 20), (x - 25, y + 15)])
        pygame.draw.polygon(self.screen, (0, 80, 200), 
                          [(x + 25, y + 10), (x + 40, y + 20), (x + 25, y + 15)])
        
        # Engines
        pygame.draw.rect(self.screen, RED, (x - 15, y + 10, 8, 8))
        pygame.draw.rect(self.screen, RED, (x + 7, y + 10, 8, 8))
        pygame.draw.rect(self.screen, ORANGE, (x - 15, y + 18, 8, 5))
        pygame.draw.rect(self.screen, ORANGE, (x + 7, y + 18, 8, 5))
    
    def draw_hud(self):
        """Draw HUD elements."""
        # Health bar
        health_text = self.small_font.render(f"Hull: {int(self.ship.hull_integrity)}%", True, WHITE)
        self.screen.blit(health_text, (10, 10))
        pygame.draw.rect(self.screen, RED, (10, 30, 200, 20), 2)
        pygame.draw.rect(self.screen, GREEN, (10, 30, int(200 * self.ship.hull_integrity / 100), 20))
        
        # Fuel bar
        fuel_text = self.small_font.render(f"Fuel: {int(self.ship.fuel)}%", True, WHITE)
        self.screen.blit(fuel_text, (10, 55))
        pygame.draw.rect(self.screen, RED, (10, 75, 200, 20), 2)
        pygame.draw.rect(self.screen, YELLOW, (10, 75, int(200 * self.ship.fuel / 100), 20))
        
        # Oxygen bar
        oxygen_text = self.small_font.render(f"Oxygen: {int(self.ship.oxygen)}%", True, WHITE)
        self.screen.blit(oxygen_text, (10, 100))
        pygame.draw.rect(self.screen, RED, (10, 120, 200, 20), 2)
        pygame.draw.rect(self.screen, BLUE, (10, 120, int(200 * self.ship.oxygen / 100), 20))
        
        # Current event
        if self.mission.active_events:
            event_text = self.small_font.render(f"Event: {self.mission.active_events[-1].value}", True, RED)
            self.screen.blit(event_text, (WIDTH - 250, 10))
        
        # Mission name
        mission_text = self.small_font.render(f"Mission: {self.mission.name}", True, WHITE)
        self.screen.blit(mission_text, (WIDTH - 300, HEIGHT - 30))
    
    def draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font.render("GAME OVER", True, RED)
        restart_text = self.small_font.render("Press R to Restart", True, WHITE)
        
        text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        
        self.screen.blit(game_over_text, text_rect)
        self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        """Main game loop."""
        running = True
        game_active = True
        space_pressed = False
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and game_active:
                        if not space_pressed:
                            self.shoot_rocket()
                            space_pressed = True
                    
                    if event.key == pygame.K_r and not game_active:
                        self.reset_game()
                        game_active = True
                
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        space_pressed = False
            
            if game_active:
                self.handle_input()
                game_active = self.update()
            
            # Draw everything
            self.screen.fill(BLACK)
            
            # Draw stars
            for star in self.stars:
                star.draw(self.screen)
            
            # Draw meteors
            for meteor in self.meteors:
                meteor.draw(self.screen)
            
            # Draw powerups
            for powerup in self.powerups:
                powerup.draw(self.screen)
            
            # Draw rockets
            for rocket in self.rockets:
                rocket.draw(self.screen)
            
            # Draw ship
            self.draw_ship()
            
            # Draw HUD
            self.draw_hud()
            
            if not game_active:
                self.draw_game_over()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
