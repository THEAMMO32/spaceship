import random
from enum import Enum

class Role(Enum):
    PILOT = "Pilot"
    ENGINEER = "Engineer"
    MEDIC = "Medic"
    SCIENTIST = "Scientist"
    NAVIGATOR = "Navigator"

class CrewMember:
    """Represents a crew member with health, skills, and role."""
    
    def __init__(self, name, role, health=100, skills=None):
        self.name = name
        self.role = role
        self.health = health
        self.skills = skills if skills else {}
        self.max_health = 100
    
    def take_damage(self, damage):
        """Reduce crew member's health."""
        self.health = max(0, self.health - damage)
        return self.health > 0
    
    def heal(self, amount):
        """Restore crew member's health."""
        self.health = min(self.max_health, self.health + amount)
    
    def get_status(self):
        """Return current status of crew member."""
        status = "Healthy" if self.health > 70 else "Injured" if self.health > 30 else "Critical"
        return f"{self.name} ({self.role.value}) - Health: {self.health}% - {status}"

class SpaceShip:
    """Represents a spaceship with fuel, hull integrity, and speed management."""
    
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
        self.position = [400, 300]  # x, y coordinates
    
    def consume_fuel(self, amount):
        """Consume fuel for movement."""
        if self.fuel >= amount:
            self.fuel -= amount
            return True
        return False
    
    def refuel(self, amount):
        """Add fuel to the ship."""
        self.fuel = min(self.max_fuel, self.fuel + amount)
    
    def take_damage(self, damage):
        """Reduce hull integrity."""
        self.hull_integrity = max(0, self.hull_integrity - damage)
        return self.hull_integrity > 0
    
    def repair(self, amount):
        """Repair hull damage."""
        self.hull_integrity = min(self.max_hull, self.hull_integrity + amount)
    
    def consume_oxygen(self, amount):
        """Consume oxygen over time."""
        self.oxygen = max(0, self.oxygen - amount)
    
    def refill_oxygen(self, amount):
        """Refill oxygen tanks."""
        self.oxygen = min(self.max_oxygen, self.oxygen + amount)
    
    def accelerate(self, delta):
        """Change ship speed."""
        self.speed = max(0, min(self.max_speed, self.speed + delta))
    
    def get_status(self):
        """Return ship's current status."""
        return {
            'fuel': self.fuel,
            'hull': self.hull_integrity,
            'oxygen': self.oxygen,
            'speed': self.speed
        }

class MissionEvent(Enum):
    ASTEROID_FIELD = "Asteroid Field"
    METEOR_SHOWER = "Meteor Shower"
    SOLAR_FLARE = "Solar Flare"
    FUEL_SHORTAGE = "Fuel Shortage"
    OXYGEN_LEAK = "Oxygen Leak"
    SYSTEM_MALFUNCTION = "System Malfunction"
    FRIENDLY_ENCOUNTER = "Friendly Encounter"

class Mission:
    """Represents a mission with objectives, resources, and random events."""
    
    def __init__(self, name, objectives, resources=None):
        self.name = name
        self.objectives = objectives
        self.resources = resources if resources else {}
        self.completed_objectives = []
        self.active_events = []
        self.mission_time = 0
    
    def trigger_random_event(self):
        """Generate a random mission event."""
        if random.random() < 0.3:  # 30% chance
            event = random.choice(list(MissionEvent))
            self.active_events.append(event)
            return event
        return None
    
    def resolve_event(self, event):
        """Remove an event from active events."""
        if event in self.active_events:
            self.active_events.remove(event)
    
    def complete_objective(self, objective):
        """Mark an objective as completed."""
        if objective in self.objectives and objective not in self.completed_objectives:
            self.completed_objectives.append(objective)
            return True
        return False
    
    def is_completed(self):
        """Check if all objectives are completed."""
        return len(self.completed_objectives) == len(self.objectives)
    
    def update(self):
        """Update mission state."""
        self.mission_time += 1
        return self.trigger_random_event()
