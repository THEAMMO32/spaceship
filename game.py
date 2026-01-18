import pygame
import random
import sys
from spaceship import SpaceShip, CrewMember, Mission, Role, MissionEvent

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GRAY = (100, 100, 100)

class Star:
    """Фоновая звездная частица."""
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
    """Метеорит - препятствие."""
    def __init__(self):
        self.size = random.choice([20, 30, 40, 50])
        self.x = random.randint(0, WIDTH - self.size)
        self.y = -self.size
        self.speed = random.randint(2, 5)
        # Уменьшенное здоровье - теперь маленькие метеориты уничтожаются за 1-2 попадания, большие за 2-5
        self.max_health = max(1, self.size // 20)
        self.health = self.max_health
        self.hit_flash = 0  # Визуальная обратная связь при попадании
    
    def update(self):
        self.y += self.speed
        if self.hit_flash > 0:
            self.hit_flash -= 1
    
    def draw(self, screen):
        # Вспышка белым при попадании
        if self.hit_flash > 0:
            color = (200, 200, 200)
        else:
            # Цвет в зависимости от здоровья - темнеет при повреждении
            health_ratio = self.health / self.max_health
            gray_value = int(100 * health_ratio)
            color = (gray_value, gray_value, gray_value)
        
        pygame.draw.circle(screen, color, (int(self.x + self.size // 2), int(self.y + self.size // 2)), self.size // 2)
        pygame.draw.circle(screen, (80, 80, 80), (int(self.x + self.size // 2), int(self.y + self.size // 2)), self.size // 2, 2)
        
        # Отрисовка полоски здоровья для больших метеоритов
        if self.max_health > 1:
            bar_width = self.size
            bar_height = 4
            health_width = int(bar_width * (self.health / self.max_health))
            # Фон
            pygame.draw.rect(screen, RED, (int(self.x), int(self.y - 8), bar_width, bar_height))
            # Здоровье
            pygame.draw.rect(screen, GREEN, (int(self.x), int(self.y - 8), health_width, bar_height))
    
    def take_damage(self, damage=1):
        """Нанести урон метеориту и вернуть True, если уничтожен."""
        self.health -= damage
        self.hit_flash = 5  # Вспышка на 5 кадров
        return self.health <= 0
    
    def is_off_screen(self):
        return self.y > HEIGHT

class Rocket:
    """Ракета игрока - снаряд."""
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
    """Собираемый бонус."""
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
            # Красная бочка
            pygame.draw.rect(screen, self.color, (self.x - 10, self.y - 10, 20, 20))
            pygame.draw.rect(screen, (150, 0, 0), (self.x - 10, self.y - 10, 20, 20), 2)
        elif self.type == 'health':
            # Зеленая аптечка
            pygame.draw.rect(screen, self.color, (self.x - 10, self.y - 10, 20, 20))
            pygame.draw.rect(screen, WHITE, (self.x - 8, self.y - 2, 16, 4))
            pygame.draw.rect(screen, WHITE, (self.x - 2, self.y - 8, 4, 16))
        else:  # oxygen
            # Синий баллон
            pygame.draw.ellipse(screen, self.color, (self.x - 8, self.y - 12, 16, 24))
            pygame.draw.ellipse(screen, (0, 50, 200), (self.x - 8, self.y - 12, 16, 24), 2)
    
    def is_off_screen(self):
        return self.y > HEIGHT

class Explosion:
    """Визуальный эффект взрыва при уничтожении метеорита."""
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.particles = []
        # Создание частиц
        for _ in range(int(size // 5)):
            angle = random.uniform(0, 2 * 3.14159)
            speed = random.uniform(1, 4)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': speed * (random.random() - 0.5) * 2,
                'vy': speed * (random.random() - 0.5) * 2,
                'life': 20,
                'size': random.randint(2, 4)
            })
    
    def update(self):
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
        self.particles = [p for p in self.particles if p['life'] > 0]
    
    def draw(self, screen):
        for particle in self.particles:
            alpha = particle['life'] / 20
            color_value = int(255 * alpha)
            color = (color_value, color_value // 2, 0)  # Оранжевый/желтый
            pygame.draw.circle(screen, color, (int(particle['x']), int(particle['y'])), particle['size'])
    
    def is_finished(self):
        return len(self.particles) == 0

class Game:
    """Главный игровой класс."""
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Spaceship Simulator")
        self.clock = pygame.time.Clock()
        self.reset_game()
    
    def reset_game(self):
        """Сброс состояния игры."""
        # Создание корабля и экипажа
        self.ship = SpaceShip("Explorer-1")
        self.ship.position = [WIDTH // 2, HEIGHT - 80]
        
        self.crew = [
            CrewMember("Alex", Role.PILOT, skills={'piloting': 90}),
            CrewMember("Sam", Role.ENGINEER, skills={'repair': 85}),
            CrewMember("Taylor", Role.MEDIC, skills={'medicine': 80})
        ]
        
        # Создание миссии
        self.mission = Mission(
            "Глубокий космос",
            ["Выжить 5 минут", "Собрать ресурсы", "Избежать астероидов"]
        )
        
        # Игровые объекты
        self.stars = [Star() for _ in range(100)]
        self.meteors = []
        self.rockets = []
        self.powerups = []
        self.explosions = []
        
        # Состояние игры
        self.meteor_spawn_timer = 0
        self.powerup_spawn_timer = 0
        self.rocket_launcher_index = 0  # Чередование пусковых установок
        self.current_event = None
        self.event_timer = 0
        self.fuel_consumption_timer = 0
        self.oxygen_consumption_timer = 0
        self.score = 0
        self.game_over_reason = ""  # Причина окончания игры
        
        # Шрифты
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
    
    def handle_input(self):
        """Обработка ввода игрока."""
        keys = pygame.key.get_pressed()
        
        # Движение
        if keys[pygame.K_LEFT] and self.ship.position[0] > 30:
            self.ship.position[0] -= 5
        if keys[pygame.K_RIGHT] and self.ship.position[0] < WIDTH - 30:
            self.ship.position[0] += 5
        if keys[pygame.K_UP] and self.ship.position[1] > 30:
            self.ship.position[1] -= 5
        if keys[pygame.K_DOWN] and self.ship.position[1] < HEIGHT - 30:
            self.ship.position[1] += 5
    
    def spawn_meteor(self):
        """Создать новый метеорит."""
        self.meteors.append(Meteor())
    
    def spawn_powerup(self):
        """Создать случайный бонус."""
        powerup_type = random.choice(['fuel', 'health', 'oxygen'])
        self.powerups.append(Powerup(powerup_type))
    
    def shoot_rocket(self):
        """Выстрелить ракетой из чередующихся установок."""
        # Чередование между левой и правой установками
        offsets = [-15, 15]
        offset = offsets[self.rocket_launcher_index]
        self.rocket_launcher_index = (self.rocket_launcher_index + 1) % 2
        
        rocket = Rocket(self.ship.position[0], self.ship.position[1] - 20, offset)
        self.rockets.append(rocket)
    
    def check_collisions(self):
        """Проверка столкновений между объектами."""
        ship_rect = pygame.Rect(self.ship.position[0] - 25, self.ship.position[1] - 15, 50, 30)
        
        # Столкновения ракет с метеоритами
        for rocket in self.rockets[:]:
            rocket_rect = pygame.Rect(rocket.x, rocket.y, rocket.width, rocket.height)
            for meteor in self.meteors[:]:
                meteor_rect = pygame.Rect(meteor.x, meteor.y, meteor.size, meteor.size)
                if rocket_rect.colliderect(meteor_rect):
                    # Удалить ракету
                    if rocket in self.rockets:
                        self.rockets.remove(rocket)
                    
                    # Нанести урон метеориту
                    if meteor.take_damage(1):
                        # Метеорит уничтожен
                        if meteor in self.meteors:
                            # Создать взрыв
                            self.explosions.append(Explosion(
                                meteor.x + meteor.size // 2,
                                meteor.y + meteor.size // 2,
                                meteor.size
                            ))
                            self.meteors.remove(meteor)
                            self.score += meteor.size  # Очки в зависимости от размера метеорита
                    break
        
        # Столкновения корабля с метеоритами
        for meteor in self.meteors[:]:
            meteor_rect = pygame.Rect(meteor.x, meteor.y, meteor.size, meteor.size)
            if ship_rect.colliderect(meteor_rect):
                damage = meteor.size // 5
                self.ship.take_damage(damage)
                if meteor in self.meteors:
                    self.meteors.remove(meteor)
        
        # Столкновения корабля с бонусами
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
        """Обновление состояния игры."""
        # Обновление звезд
        for star in self.stars:
            star.update()
        
        # Обновление метеоритов
        for meteor in self.meteors[:]:
            meteor.update()
            if meteor.is_off_screen():
                self.meteors.remove(meteor)
        
        # Обновление ракет
        for rocket in self.rockets[:]:
            rocket.update()
            if rocket.is_off_screen():
                self.rockets.remove(rocket)
        
        # Обновление бонусов
        for powerup in self.powerups[:]:
            powerup.update()
            if powerup.is_off_screen():
                self.powerups.remove(powerup)
        
        # Обновление взрывов
        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.is_finished():
                self.explosions.remove(explosion)
        
        # Появление метеоритов
        self.meteor_spawn_timer += 1
        if self.meteor_spawn_timer > random.randint(30, 60):
            self.spawn_meteor()
            self.meteor_spawn_timer = 0
        
        # Появление бонусов
        self.powerup_spawn_timer += 1
        if self.powerup_spawn_timer > random.randint(180, 300):
            self.spawn_powerup()
            self.powerup_spawn_timer = 0
        
        # Расход ресурсов
        self.fuel_consumption_timer += 1
        if self.fuel_consumption_timer > 60:
            self.ship.consume_fuel(0.5)
            self.fuel_consumption_timer = 0
        
        self.oxygen_consumption_timer += 1
        if self.oxygen_consumption_timer > 90:
            self.ship.consume_oxygen(1)
            self.oxygen_consumption_timer = 0
        
        # Обновление миссии и событий
        self.event_timer += 1
        if self.event_timer > 300:
            event = self.mission.update()
            if event:
                self.current_event = event
            self.event_timer = 0
        
        # Проверка столкновений
        self.check_collisions()
        
        # Проверка окончания игры
        if self.ship.hull_integrity <= 0:
            self.game_over_reason = "Корпус разрушен!"
            return False
        
        if self.ship.fuel <= 0:
            self.game_over_reason = "Топливо закончилось!"
            return False
        
        if self.ship.oxygen <= 0:
            self.game_over_reason = "Кислород закончился!"
            return False
        
        return True
    
    def draw_ship(self):
        """Отрисовка космического корабля."""
        x, y = self.ship.position
        
        # Корпус корабля
        pygame.draw.polygon(self.screen, BLUE, 
                          [(x, y - 20), (x - 25, y + 10), (x + 25, y + 10)])
        
        # Кабина
        pygame.draw.circle(self.screen, (100, 200, 255), (x, y - 5), 8)
        
        # Крылья
        pygame.draw.polygon(self.screen, (0, 80, 200), 
                          [(x - 25, y + 10), (x - 40, y + 20), (x - 25, y + 15)])
        pygame.draw.polygon(self.screen, (0, 80, 200), 
                          [(x + 25, y + 10), (x + 40, y + 20), (x + 25, y + 15)])
        
        # Двигатели
        pygame.draw.rect(self.screen, RED, (x - 15, y + 10, 8, 8))
        pygame.draw.rect(self.screen, RED, (x + 7, y + 10, 8, 8))
        pygame.draw.rect(self.screen, ORANGE, (x - 15, y + 18, 8, 5))
        pygame.draw.rect(self.screen, ORANGE, (x + 7, y + 18, 8, 5))
    
    def draw_hud(self):
        """Отрисовка элементов HUD."""
        # Полоса здоровья
        health_text = self.small_font.render(f"Корпус: {int(self.ship.hull_integrity)}%", True, WHITE)
        self.screen.blit(health_text, (10, 10))
        pygame.draw.rect(self.screen, RED, (10, 30, 200, 20), 2)
        pygame.draw.rect(self.screen, GREEN, (10, 30, int(200 * self.ship.hull_integrity / 100), 20))
        
        # Полоса топлива
        fuel_text = self.small_font.render(f"Топливо: {int(self.ship.fuel)}%", True, WHITE)
        self.screen.blit(fuel_text, (10, 55))
        pygame.draw.rect(self.screen, RED, (10, 75, 200, 20), 2)
        pygame.draw.rect(self.screen, YELLOW, (10, 75, int(200 * self.ship.fuel / 100), 20))
        
        # Полоса кислорода
        oxygen_text = self.small_font.render(f"Кислород: {int(self.ship.oxygen)}%", True, WHITE)
        self.screen.blit(oxygen_text, (10, 100))
        pygame.draw.rect(self.screen, RED, (10, 120, 200, 20), 2)
        pygame.draw.rect(self.screen, BLUE, (10, 120, int(200 * self.ship.oxygen / 100), 20))
        
        # Счет
        score_text = self.small_font.render(f"Счет: {self.score}", True, YELLOW)
        self.screen.blit(score_text, (10, 145))
        
        # Текущее событие
        if self.mission.active_events:
            event_text = self.small_font.render(f"Событие: {self.mission.active_events[-1].value}", True, RED)
            self.screen.blit(event_text, (WIDTH - 250, 10))
        
        # Название миссии
        mission_text = self.small_font.render(f"Миссия: {self.mission.name}", True, WHITE)
        self.screen.blit(mission_text, (WIDTH - 300, HEIGHT - 30))
    
    def draw_game_over(self):
        """Отрисовка экрана окончания игры."""
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font.render("ИГРА ОКОНЧЕНА", True, RED)
        reason_text = self.small_font.render(self.game_over_reason, True, ORANGE)
        score_text = self.small_font.render(f"Финальный счет: {self.score}", True, YELLOW)
        restart_text = self.small_font.render("Нажмите R для перезапуска", True, WHITE)
        
        text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
        reason_rect = reason_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        
        self.screen.blit(game_over_text, text_rect)
        self.screen.blit(reason_text, reason_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        """Главный игровой цикл."""
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
            
            # Отрисовка всего
            self.screen.fill(BLACK)
            
            # Отрисовка звезд
            for star in self.stars:
                star.draw(self.screen)
            
            # Отрисовка взрывов (позади метеоритов)
            for explosion in self.explosions:
                explosion.draw(self.screen)
            
            # Отрисовка метеоритов
            for meteor in self.meteors:
                meteor.draw(self.screen)
            
            # Отрисовка бонусов
            for powerup in self.powerups:
                powerup.draw(self.screen)
            
            # Отрисовка ракет
            for rocket in self.rockets:
                rocket.draw(self.screen)
            
            # Отрисовка корабля
            self.draw_ship()
            
            # Отрисовка HUD
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
