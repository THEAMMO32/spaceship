import random
from enum import Enum

class Role(Enum):
    PILOT = "Pilot"
    ENGINEER = "Engineer"
    MEDIC = "Medic"
    SCIENTIST = "Scientist"
    NAVIGATOR = "Navigator"

class CrewMember:
    """Представляет члена экипажа со здоровьем, навыками и ролью."""
    
    def __init__(self, name, role, health=100, skills=None):
        self.name = name
        self.role = role
        self.health = health
        self.skills = skills if skills else {}
        self.max_health = 100
    
    def take_damage(self, damage):
        """Уменьшить здоровье члена экипажа."""
        self.health = max(0, self.health - damage)
        return self.health > 0
    
    def heal(self, amount):
        """Восстановить здоровье члена экипажа."""
        self.health = min(self.max_health, self.health + amount)
    
    def get_status(self):
        """Вернуть текущий статус члена экипажа."""
        status = "Здоров" if self.health > 70 else "Ранен" if self.health > 30 else "Критическое состояние"
        return f"{self.name} ({self.role.value}) - Здоровье: {self.health}% - {status}"

class SpaceShip:
    """Представляет космический корабль с управлением топливом, целостностью корпуса и скоростью."""
    
    def __init__(self, name, fuel=100, hull_integrity=100, speed=0):
        self.name = name
        self.fuel = fuel
        self.max_fuel = 100
        self.hull_integrity = hull_integrity
        self.max_hull = 100
        self.speed = speed
        self.max_speed = 100
        self.oxygen = 100
        self.max_oxygen = 100
        self.position = [400, 300]  # координаты x, y
    
    def consume_fuel(self, amount):
        """Расходовать топливо для движения."""
        if self.fuel >= amount:
            self.fuel -= amount
            return True
        return False
    
    def refuel(self, amount):
        """Добавить топливо в корабль."""
        self.fuel = min(self.max_fuel, self.fuel + amount)
    
    def take_damage(self, damage):
        """Уменьшить целостность корпуса."""
        self.hull_integrity = max(0, self.hull_integrity - damage)
        return self.hull_integrity > 0
    
    def repair(self, amount):
        """Починить повреждения корпуса."""
        self.hull_integrity = min(self.max_hull, self.hull_integrity + amount)
    
    def consume_oxygen(self, amount):
        """Расходовать кислород со временем."""
        self.oxygen = max(0, self.oxygen - amount)
    
    def refill_oxygen(self, amount):
        """Пополнить баки с кислородом."""
        self.oxygen = min(self.max_oxygen, self.oxygen + amount)
    
    def accelerate(self, delta):
        """Изменить скорость корабля."""
        self.speed = max(0, min(self.max_speed, self.speed + delta))
    
    def get_status(self):
        """Вернуть текущий статус корабля."""
        return {
            'fuel': self.fuel,
            'hull': self.hull_integrity,
            'oxygen': self.oxygen,
            'speed': self.speed
        }

class MissionEvent(Enum):
    ASTEROID_FIELD = "Астероидное поле"
    METEOR_SHOWER = "Метеоритный дождь"
    SOLAR_FLARE = "Солнечная вспышка"
    FUEL_SHORTAGE = "Нехватка топлива"
    OXYGEN_LEAK = "Утечка кислорода"
    SYSTEM_MALFUNCTION = "Сбой системы"
    FRIENDLY_ENCOUNTER = "Дружественная встреча"

class Mission:
    """Представляет миссию с целями, ресурсами и случайными событиями."""
    
    def __init__(self, name, objectives, resources=None):
        self.name = name
        self.objectives = objectives
        self.resources = resources if resources else {}
        self.completed_objectives = []
        self.active_events = []
        self.mission_time = 0
    
    def trigger_random_event(self):
        """Сгенерировать случайное событие миссии."""
        if random.random() < 0.3:  # 30% шанс
            event = random.choice(list(MissionEvent))
            self.active_events.append(event)
            return event
        return None
    
    def resolve_event(self, event):
        """Удалить событие из активных событий."""
        if event in self.active_events:
            self.active_events.remove(event)
    
    def complete_objective(self, objective):
        """Отметить цель как выполненную."""
        if objective in self.objectives and objective not in self.completed_objectives:
            self.completed_objectives.append(objective)
            return True
        return False
    
    def is_completed(self):
        """Проверить, все ли цели выполнены."""
        return len(self.completed_objectives) == len(self.objectives)
    
    def update(self):
        """Обновить состояние миссии."""
        self.mission_time += 1
        return self.trigger_random_event()
