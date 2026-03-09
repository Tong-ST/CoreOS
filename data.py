import json
import os
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
            self.tasks = [Task(**t) for t in data.get("tasks", [])]
            self.projects = [Project(**p) for p in data.get("projects", [])]
            self.goals = [Goal(**g) for g in data.get("goals", [])]
            self.habits = [Habit(**h) for h in data.get("habits", [])]
            self.bad_habits = [BadHabit(**bh) for bh in data.get("bad_habits", [])]
            self.badges = [Badge(**b) for b in data.get("badges", [])]
            self.logs = data.get("logs", [])
            self.player = Player(**data.get("player", {}))

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
