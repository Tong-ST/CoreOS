from data import data_store
from models import Task, Project, Goal, Habit, BadHabit, Badge
from datetime import datetime, date
from rich.console import Console
from rich.table import Table
import math

console = Console()

def generate_id(prefix, items):
    import re
    max_id = 0
    for item in items:
        # Extract the number from IDs like "task-005"
        match = re.search(r'-(\d+)$', item.id)
        if match:
            num = int(match.group(1))
            if num > max_id:
                max_id = num
    
    new_num = max_id + 1
    return f"{prefix}-{new_num:03}"

# --- Sync Logic ---
def sync_daily_tasks():
    today = date.today().isoformat()

    # Auto-delete overdue project tasks
    initial_task_count = len(data_store.tasks)
    tasks_to_keep = []
    for task in data_store.tasks:
        if task.project_id and task.status == "todo" and task.due_date:
            try:
                task_due_date = datetime.fromisoformat(task.due_date).date()
                if task_due_date < date.today():
                    console.print(f"[yellow]Overdue project task deleted: {task.title}[/yellow]")
                    continue # Skip adding this task to tasks_to_keep
            except ValueError: # Handle invalid date formats gracefully
                pass
        tasks_to_keep.append(task)
    data_store.tasks = tasks_to_keep
    if len(data_store.tasks) < initial_task_count:
        data_store.save()

    # Sync Projects
    for p in data_store.projects:
        if p.status == "active":
            daily_title = f"Project: {p.title}"
            # Check if today's task already exists
            exists = any(
                t.project_id == p.id and 
                t.title == daily_title and 
                t.due_date == today and # Check for today's specific task
                datetime.fromisoformat(t.created_at).date().isoformat() == today
                for t in data_store.tasks
            )
            if not exists:
                task_add(daily_title, project_id=p.id, due_date=today, priority=p.default_priority, estimated_minutes=p.default_task_minutes)

    # Goal tasks are no longer auto-created per user request. 
    # Users can link projects to goals instead.


# --- Economy Logic ---
def add_xp_credits(xp: int, credits: int):
    data_store.player.xp += xp
    data_store.player.credits += credits
    # Simple leveling: level = floor(sqrt(xp / 100)) + 1
    data_store.player.level = math.floor(math.sqrt(data_store.player.xp / 100)) + 1
    data_store.save()

# --- Goal Commands ---
def goal_add(title, description, badge_name, badge_description, due_date=None):
    new_id = generate_id("goal", data_store.goals)
    new_goal = Goal(id=new_id, title=title, description=description, badge_name=badge_name, badge_description=badge_description, due_date=due_date)
    data_store.goals.append(new_goal)
    data_store.save()
    console.print(f"[green]Goal added: {new_id} - {title}[/green]")

def goal_edit(goal_id, title=None, description=None, badge_name=None, badge_description=None, due_date=None):
    for g in data_store.goals:
        if g.id == goal_id:
            if title: g.title = title
            if description: g.description = description
            if badge_name: g.badge_name = badge_name
            if badge_description: g.badge_description = badge_description
            if due_date is not None: g.due_date = due_date
            data_store.save()
            console.print(f"[green]Goal updated: {goal_id}[/green]")
            return True
    console.print(f"[red]Goal {goal_id} not found.[/red]")
    return False

def goal_delete(goal_id):
    original_len = len(data_store.goals)
    data_store.goals = [g for g in data_store.goals if g.id != goal_id]
    if len(data_store.goals) < original_len:
        data_store.save()
        console.print(f"[green]Goal deleted: {goal_id}[/green]")
        return True
    console.print(f"[red]Goal {goal_id} not found.[/red]")
    return False

def goal_list():
    table = Table(title="Goals")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="magenta")
    table.add_column("Due", style="green")
    table.add_column("Status", style="yellow")
    for g in data_store.goals:
        table.add_row(g.id, g.title, g.due_date or "-", g.status)
    console.print(table)

def goal_done(goal_id):
    for g in data_store.goals:
        if g.id == goal_id and g.status != "done":
            g.status = "done"
            g.completed_at = datetime.now().isoformat()
            # Award Badge
            badge_id = generate_id("badge", data_store.badges)
            new_badge = Badge(id=badge_id, name=g.badge_name, description=g.badge_description, goal_id=g.id)
            data_store.badges.append(new_badge)
            # Award XP/Credits
            add_xp_credits(200, 100)
            data_store.save()
            console.print(f"[green]Goal completed! Badge earned: {g.badge_name}[/green]")
            return
    console.print(f"[red]Goal {goal_id} not found or already done.[/red]")

def goal_undo(goal_id):
    for g in data_store.goals:
        if g.id == goal_id and g.status == "done":
            g.status = "active"
            g.completed_at = None
            # Remove Badge
            data_store.badges = [b for b in data_store.badges if b.goal_id != g.id]
            # Deduct XP/Credits
            add_xp_credits(-200, -100)
            data_store.save()
            console.print(f"[yellow]Goal {goal_id} reverted to active. Rewards deducted.[/yellow]")
            return
    console.print(f"[red]Goal {goal_id} not found or not in 'done' status.[/red]")

# --- Project Commands ---
def project_add(title, description, goal_id=None, default_task_minutes=30, due_date=None, default_priority="medium"):
    new_id = generate_id("proj", data_store.projects)
    new_proj = Project(id=new_id, title=title, description=description, goal_id=goal_id, default_task_minutes=int(default_task_minutes), default_priority=default_priority, due_date=due_date)
    data_store.projects.append(new_proj)
    data_store.save()
    console.print(f"[green]Project added: {new_id} - {title}[/green]")
    
    # Create the first daily task immediately
    today = date.today().isoformat()
    daily_title = f"Project: {title}"
    task_add(daily_title, project_id=new_id, due_date=today, priority=default_priority, estimated_minutes=int(default_task_minutes))


def project_edit(project_id, title=None, description=None, goal_id=None, default_task_minutes=None, due_date=None, default_priority=None):
    for p in data_store.projects:
        if p.id == project_id:
            if title: p.title = title
            if description: p.description = description
            if goal_id is not None: p.goal_id = goal_id if goal_id != "" else None
            if default_task_minutes is not None: p.default_task_minutes = int(default_task_minutes)
            if due_date is not None: p.due_date = due_date
            if default_priority is not None: p.default_priority = default_priority
            data_store.save()
            console.print(f"[green]Project updated: {project_id}[/green]")
            return True
    console.print(f"[red]Project {project_id} not found.[/red]")
    return False

def project_delete(project_id):
    original_len = len(data_store.projects)
    data_store.projects = [p for p in data_store.projects if p.id != project_id]
    if len(data_store.projects) < original_len:
        data_store.save()
        console.print(f"[green]Project deleted: {project_id}[/green]")
        return True
    console.print(f"[red]Project {project_id} not found.[/red]")
    return False

def project_list():
    table = Table(title="Projects")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="magenta")
    table.add_column("Due", style="green")
    table.add_column("Status", style="yellow")
    for p in data_store.projects:
        table.add_row(p.id, p.title, p.due_date or "-", p.status)
    console.print(table)

def project_done(project_id):
    for p in data_store.projects:
        if p.id == project_id and p.status != "done":
            p.status = "done"
            add_xp_credits(50, 30)
            data_store.save()
            console.print(f"[green]Project completed! +50 XP, +30 Credits[/green]")
            return
    console.print(f"[red]Project {project_id} not found or already done.[/red]")

def project_undo(project_id):
    for p in data_store.projects:
        if p.id == project_id and p.status == "done":
            p.status = "active"
            add_xp_credits(-50, -30)
            data_store.save()
            console.print(f"[yellow]Project {project_id} reverted to active. Rewards deducted.[/yellow]")
            return
    console.print(f"[red]Project {project_id} not found or not in 'done' status.[/red]")

# --- Task Commands ---
def task_add(title, project_id=None, due_date=None, priority="medium", estimated_minutes=30):
    new_id = generate_id("task", data_store.tasks)
    new_task = Task(id=new_id, title=title, project_id=project_id, due_date=due_date, priority=priority, estimated_minutes=int(estimated_minutes))
    data_store.tasks.append(new_task)
    data_store.save()
    console.print(f"[green]Task added: {new_id} - {title} ({estimated_minutes} min)[/green]")

def task_edit(task_id, title=None, project_id=None, due_date=None, priority=None, estimated_minutes=None):
    for t in data_store.tasks:
        if t.id == task_id:
            if title: t.title = title
            if project_id is not None: t.project_id = project_id if project_id != "" else None
            if due_date: t.due_date = due_date
            if priority: t.priority = priority
            if estimated_minutes is not None: t.estimated_minutes = int(estimated_minutes)
            data_store.save()
            console.print(f"[green]Task updated: {task_id}[/green]")
            return True
    console.print(f"[red]Task {task_id} not found.[/red]")
    return False

def task_delete(task_id):
    original_len = len(data_store.tasks)
    data_store.tasks = [t for t in data_store.tasks if t.id != task_id]
    if len(data_store.tasks) < original_len:
        data_store.save()
        console.print(f"[green]Task deleted: {task_id}[/green]")
        return True
    console.print(f"[red]Task {task_id} not found.[/red]")
    return False

def task_list():
    table = Table(title="Tasks")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="magenta")
    table.add_column("Duration", style="green")
    table.add_column("Priority", style="yellow")
    table.add_column("Status", style="blue")
    for t in data_store.tasks:
        table.add_row(t.id, t.title, f"{t.estimated_minutes}m", t.priority, t.status)
    console.print(table)

def task_done(task_id):
    for t in data_store.tasks:
        if t.id == task_id and t.status != "done":
            t.status = "done"
            # XP/Credits based on duration: 60 mins = 20 XP / 10 Credits
            xp = max(5, int(t.estimated_minutes / 3))
            credits = max(2, int(t.estimated_minutes / 6))
            add_xp_credits(xp, credits)
            data_store.save()
            console.print(f"[green]Task done! +{xp} XP, +{credits} Credits (Duration: {t.estimated_minutes}m)[/green]")
            return
    console.print(f"[red]Task {task_id} not found or already done.[/red]")

def task_undo(task_id):
    for t in data_store.tasks:
        if t.id == task_id and t.status == "done":
            t.status = "todo"
            xp = max(5, int(t.estimated_minutes / 3))
            credits = max(2, int(t.estimated_minutes / 6))
            add_xp_credits(-xp, -credits)
            data_store.save()
            console.print(f"[yellow]Task {task_id} reverted to todo. Rewards deducted.[/yellow]")
            return
    console.print(f"[red]Task {task_id} not found or not in 'done' status.[/red]")

# --- Habit Commands ---
def habit_add(title, credit_reward):
    new_id = generate_id("habit", data_store.habits)
    new_habit = Habit(id=new_id, title=title, credit_reward=int(credit_reward))
    data_store.habits.append(new_habit)
    data_store.save()
    console.print(f"[green]Habit added: {new_id} - {title}[/green]")

def habit_edit(habit_id, title=None, reward=None):
    for h in data_store.habits:
        if h.id == habit_id:
            if title: h.title = title
            if reward is not None: h.credit_reward = int(reward)
            data_store.save()
            console.print(f"[green]Habit updated: {habit_id}[/green]")
            return True
    console.print(f"[red]Habit {habit_id} not found.[/red]")
    return False

def habit_delete(habit_id):
    original_len = len(data_store.habits)
    data_store.habits = [h for h in data_store.habits if h.id != habit_id]
    if len(data_store.habits) < original_len:
        data_store.save()
        console.print(f"[green]Habit deleted: {habit_id}[/green]")
        return True
    console.print(f"[red]Habit {habit_id} not found.[/red]")
    return False

def habit_log(habit_id):
    today = date.today().isoformat()
    for h in data_store.habits:
        if h.id == habit_id:
            last_done_date = None
            if h.last_done:
                last_done_date = datetime.fromisoformat(h.last_done).date().isoformat()
            
            if last_done_date == today:
                console.print(f"[yellow]Habit '{h.title}' already logged today![/yellow]")
                return False
            
            h.last_done = datetime.now().isoformat()
            add_xp_credits(0, h.credit_reward)
            data_store.save()
            console.print(f"[green]Habit logged! +{h.credit_reward} Credits[/green]")
            return True
    console.print(f"[red]Habit {habit_id} not found.[/red]")
    return False

# --- Bad Habit Commands ---
def badhabit_add(title, credit_cost):
    new_id = generate_id("bad", data_store.bad_habits)
    new_bh = BadHabit(id=new_id, title=title, credit_cost=int(credit_cost))
    data_store.bad_habits.append(new_bh)
    data_store.save()
    console.print(f"[green]Bad Habit added: {new_id} - {title}[/green]")

def badhabit_edit(badhabit_id, title=None, cost=None):
    for bh in data_store.bad_habits:
        if bh.id == badhabit_id:
            if title: bh.title = title
            if cost is not None: bh.credit_cost = int(cost)
            data_store.save()
            console.print(f"[green]Bad habit updated: {badhabit_id}[/green]")
            return True
    console.print(f"[red]Bad habit {badhabit_id} not found.[/red]")
    return False

def badhabit_delete(badhabit_id):
    original_len = len(data_store.bad_habits)
    data_store.bad_habits = [bh for bh in data_store.bad_habits if bh.id != badhabit_id]
    if len(data_store.bad_habits) < original_len:
        data_store.save()
        console.print(f"[green]Bad habit deleted: {badhabit_id}[/green]")
        return True
    console.print(f"[red]Bad habit {badhabit_id} not found.[/red]")
    return False

def badhabit_spend(badhabit_id):
    for bh in data_store.bad_habits:
        if bh.id == badhabit_id:
            if data_store.player.credits >= bh.credit_cost:
                data_store.player.credits -= bh.credit_cost
                
                # Log usage
                log_entry = {
                    "type": "bad_habit_spend",
                    "id": bh.id,
                    "title": bh.title,
                    "cost": bh.credit_cost,
                    "timestamp": datetime.now().isoformat()
                }
                data_store.logs.append(log_entry)
                
                data_store.save()
                msg = f"Credits spent! Enjoy your {bh.title}. (-{bh.credit_cost} cr)"
                console.print(f"[green]{msg}[/green]")
                return True, msg
            else:
                msg = f"Not enough credits! Need {bh.credit_cost}, have {data_store.player.credits}."
                console.print(f"[red]{msg}[/red]")
                return False, msg
    return False, "Bad Habit not found."

# --- Badge & Balance ---
def badge_list():
    table = Table(title="Earned Badges")
    table.add_column("Name", style="magenta")
    table.add_column("Description", style="cyan")
    table.add_column("Earned At", style="yellow")
    for b in data_store.badges:
        table.add_row(b.name, b.description, b.earned_at)
    console.print(table)

def balance():
    p = data_store.player
    console.print(f"[bold green]Level {p.level}[/bold green]")
    console.print(f"[bold blue]XP: {p.xp}[/bold blue]")
    console.print(f"[bold yellow]Credits: {p.credits}[/bold yellow]")
    badge_list()
