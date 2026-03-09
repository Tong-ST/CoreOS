from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime

@dataclass
class Task:
    id: str
    title: str
    project_id: Optional[str] = None
    due_date: Optional[str] = None
    priority: str = "medium"  # high, medium, low
    estimated_minutes: int = 30
    status: str = "todo"  # todo, done
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Project:
    id: str
    title: str
    description: str
    goal_id: Optional[str] = None
    status: str = "active"  # active, done
    default_task_minutes: int = 30
    due_date: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Goal:
    id: str
    title: str
    description: str
    badge_name: str
    badge_description: str
    status: str = "active"  # active, done
    due_date: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

@dataclass
class Habit:
    id: str
    title: str
    credit_reward: int
    last_done: Optional[str] = None

@dataclass
class BadHabit:
    id: str
    title: str
    credit_cost: int

@dataclass
class Badge:
    id: str
    name: str
    description: str
    goal_id: str
    earned_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Player:
    xp: int = 0
    credits: int = 0
    level: int = 1
