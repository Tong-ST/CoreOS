import json
import os
import inspect
from dataclasses import asdict
from typing import Dict, List, Any
from models import Task, Project, Goal, Habit, BadHabit, Badge, Player

DATA_FILE = "data.json"

class CoreData:
    def __init__(self):
        self.tasks: List[Task] = []
        self.projects: List[Project] = []
        self.goals: List[Goal] = []
        self.habits: List[Habit] = []
        self.bad_habits: List[BadHabit] = []
        self.badges: List[Badge] = []
        self.logs: List[Dict[str, Any]] = []
        self.player: Player = Player()
        self.load()

    def load(self):
        if not os.path.exists(DATA_FILE):
            self.save()
            return

        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            
            def safe_load(cls, items):
                import inspect
                valid_keys = inspect.signature(cls).parameters.keys()
                return [cls(**{k: v for k, v in item.items() if k in valid_keys}) for item in items]

            self.tasks = safe_load(Task, data.get("tasks", []))
            self.projects = safe_load(Project, data.get("projects", []))
            self.goals = safe_load(Goal, data.get("goals", []))
            self.habits = safe_load(Habit, data.get("habits", []))
            self.bad_habits = safe_load(BadHabit, data.get("bad_habits", []))
            self.badges = safe_load(Badge, data.get("badges", []))
            
            self.logs = data.get("logs", [])
            
            # Safe load for player
            player_data = data.get("player", {})
            valid_player_keys = inspect.signature(Player).parameters.keys()
            self.player = Player(**{k: v for k, v in player_data.items() if k in valid_player_keys})

    def save(self):
        data = {
            "tasks": [asdict(t) for t in self.tasks],
            "projects": [asdict(p) for p in self.projects],
            "goals": [asdict(g) for g in self.goals],
            "habits": [asdict(h) for h in self.habits],
            "bad_habits": [asdict(bh) for bh in self.bad_habits],
            "badges": [asdict(b) for b in self.badges],
            "logs": self.logs,
            "player": asdict(self.player)
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

# Global data instance
data_store = CoreData()
