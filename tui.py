from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable, Button, Label, ProgressBar, Input, Select
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.screen import Screen, ModalScreen
from data import data_store
import commands
import math

# --- Modals ---

class TaskAddModal(ModalScreen):
    def __init__(self, task=None):
        super().__init__()
        self.task_item = task

    def compose(self) -> ComposeResult:
        title_val = self.task_item.title if self.task_item else ""
        due_val = self.task_item.due_date if self.task_item else ""
        priority_val = self.task_item.priority if self.task_item else "medium"
        duration_val = str(self.task_item.estimated_minutes) if self.task_item else "30"
        
        label_text = "Edit Task" if self.task_item else "Add New Task"
        yield Grid(
            Label(label_text, id="modal-title"),
            Input(placeholder="Title...", value=title_val, id="task-title"),
            Input(placeholder="Due Date (e.g. 2026-03-15)...", value=due_val, id="task-due"),
            Input(placeholder="Duration (minutes)...", value=duration_val, id="task-duration"),
            Label("Priority:"),
            Select(
                [("High", "high"), ("Medium", "medium"), ("Low", "low")],
                value=priority_val,
                id="task-priority"
            ),
            Horizontal(
                Button("Submit", variant="primary", id="submit"),
                Button("Cancel", variant="error", id="cancel"),
            ),
            id="task-modal-dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            title = self.query_one("#task-title", Input).value
            due = self.query_one("#task-due", Input).value
            duration = self.query_one("#task-duration", Input).value
            priority = self.query_one("#task-priority", Select).value
            if title:
                self.dismiss((title, due, priority, duration))
            else:
                self.dismiss()
        else:
            self.dismiss()

class GoalAddModal(ModalScreen):
    def __init__(self, goal=None):
        super().__init__()
        self.goal_item = goal

    def compose(self) -> ComposeResult:
        t = self.goal_item.title if self.goal_item else ""
        d = self.goal_item.description if self.goal_item else ""
        bn = self.goal_item.badge_name if self.goal_item else ""
        bd = self.goal_item.badge_description if self.goal_item else ""
        due = self.goal_item.due_date if self.goal_item else ""
        label_text = "Edit Goal" if self.goal_item else "Add New Goal"
        yield Grid(
            Label(label_text, id="modal-title"),
            Input(placeholder="Goal Title...", value=t, id="goal-title"),
            Input(placeholder="Description...", value=d, id="goal-desc"),
            Input(placeholder="Badge Name...", value=bn, id="goal-badge-name"),
            Input(placeholder="Badge Description...", value=bd, id="goal-badge-desc"),
            Input(placeholder="Due Date (Optional)...", value=due, id="goal-due"),
            Horizontal(
                Button("Submit", variant="primary", id="submit"),
                Button("Cancel", variant="error", id="cancel"),
            ),
            id="goal-modal-dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            title = self.query_one("#goal-title", Input).value
            desc = self.query_one("#goal-desc", Input).value
            bn = self.query_one("#goal-badge-name", Input).value
            bd = self.query_one("#goal-badge-desc", Input).value
            due = self.query_one("#goal-due", Input).value
            if title: self.dismiss((title, desc, bn, bd, due))
            else: self.dismiss()
        else:
            self.dismiss()

class ProjectAddModal(ModalScreen):
    def __init__(self, project=None):
        super().__init__()
        self.project_item = project

    def compose(self) -> ComposeResult:
        t = self.project_item.title if self.project_item else ""
        d = self.project_item.description if self.project_item else ""
        g = self.project_item.goal_id if self.project_item and self.project_item.goal_id else ""
        dur = str(self.project_item.default_task_minutes) if self.project_item else "30"
        due = self.project_item.due_date if self.project_item else ""
        label_text = "Edit Project" if self.project_item else "Add New Project"
        yield Grid(
            Label(label_text, id="modal-title"),
            Input(placeholder="Project Title...", value=t, id="proj-title"),
            Input(placeholder="Description...", value=d, id="proj-desc"),
            Input(placeholder="Goal ID (Optional, e.g. goal-001)...", value=g, id="proj-goal"),
            Input(placeholder="Daily Task Duration (mins)...", value=dur, id="proj-duration"),
            Input(placeholder="Due Date (Optional)...", value=due, id="proj-due"),
            Horizontal(
                Button("Submit", variant="primary", id="submit"),
                Button("Cancel", variant="error", id="cancel"),
            ),
            id="proj-modal-dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            title = self.query_one("#proj-title", Input).value
            desc = self.query_one("#proj-desc", Input).value
            goal = self.query_one("#proj-goal", Input).value
            dur = self.query_one("#proj-duration", Input).value
            due = self.query_one("#proj-due", Input).value
            if title: self.dismiss((title, desc, goal, dur, due))
            else: self.dismiss()
        else:
            self.dismiss()

class HabitAddModal(ModalScreen):
    def __init__(self, is_bad=False, habit=None):
        super().__init__()
        self.is_bad = is_bad
        self.habit_item = habit

    def compose(self) -> ComposeResult:
        t = self.habit_item.title if self.habit_item else ""
        if self.habit_item:
            v = str(self.habit_item.credit_cost if self.is_bad else self.habit_item.credit_reward)
        else:
            v = ""
        
        if self.habit_item:
            title_text = "Edit Bad Habit" if self.is_bad else "Edit Good Habit"
        else:
            title_text = "Add Bad Habit" if self.is_bad else "Add Good Habit"
            
        yield Grid(
            Label(title_text, id="modal-title"),
            Input(placeholder="Habit Title...", value=t, id="h-title"),
            Input(placeholder="Credit " + ("Cost" if self.is_bad else "Reward") + "...", value=v, id="h-value"),
            Horizontal(
                Button("Submit", variant="primary", id="submit"),
                Button("Cancel", variant="error", id="cancel"),
            ),
            id="habit-modal-dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            title = self.query_one("#h-title", Input).value
            val = self.query_one("#h-value", Input).value
            if title and val.isdigit():
                self.dismiss((title, int(val)))
            else:
                self.dismiss()
        else:
            self.dismiss()

# --- Screens ---

class Dashboard(Screen):
    def compose(self) -> ComposeResult:
        p = data_store.player
        yield Header()
        with Vertical(id="dashboard-container"):
            with Horizontal(id="stats-row"):
                yield Vertical(
                    Label(f"Level {p.level}", id="level-label"),
                    Label(f"XP: {p.xp}"),
                    ProgressBar(total=100, show_percentage=True, id="xp-bar"),
                    classes="stats-card"
                )
                yield Vertical(
                    Label("Credits", classes="card-title"),
                    Label(f"{p.credits} cr", id="credits-label"),
                    classes="stats-card"
                )
            yield Label("Active Tasks", classes="section-title")
            yield DataTable(id="dashboard-tasks")
            yield Label("Recent Badges", classes="section-title")
            yield DataTable(id="dashboard-badges")
        yield Footer()

    def on_mount(self) -> None:
        tasks_table = self.query_one("#dashboard-tasks", DataTable)
        tasks_table.add_columns("ID", "Title", "Due", "Duration", "Reward")
        badges_table = self.query_one("#dashboard-badges", DataTable)
        badges_table.add_columns("Name", "Earned At")
        self.refresh_data()

    def on_screen_resume(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        p = data_store.player
        try:
            self.query_one("#xp-bar", ProgressBar).progress = p.xp % 100
            self.query_one("#level-label", Label).update(f"Level {p.level}")
            self.query_one("#credits-label", Label).update(f"{p.credits} cr")
            
            tasks_table = self.query_one("#dashboard-tasks", DataTable)
            if tasks_table.columns:
                tasks_table.clear()
                for t in data_store.tasks:
                    if t.status == "todo":
                        xp = max(5, int(t.estimated_minutes / 3))
                        creds = max(2, int(t.estimated_minutes / 6))
                        tasks_table.add_row(t.id, t.title, t.due_date or "-", f"{t.estimated_minutes}m", f"{xp}xp/{creds}cr")
            
            badges_table = self.query_one("#dashboard-badges", DataTable)
            if badges_table.columns:
                badges_table.clear()
                for b in data_store.badges[-5:]:
                    badges_table.add_row(b.name, b.earned_at[:10])
        except Exception:
            pass # Screen might not be fully ready yet

class GoalsProjectsScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Goals & Projects (g/p: New, e: Edit, x: Delete, Enter/d: Done)", classes="section-title")
        with Horizontal():
            with Vertical(classes="column"):
                yield Label("Goals", classes="section-title")
                yield DataTable(id="goals-table")
            with Vertical(classes="column"):
                yield Label("Projects (Linked Goal shown)", classes="section-title")
                yield DataTable(id="projects-table")
        yield Footer()

    def on_mount(self) -> None:
        gt = self.query_one("#goals-table", DataTable)
        gt.add_columns("ID", "Title", "Due", "Status")
        gt.cursor_type = "row"
        
        pt = self.query_one("#projects-table", DataTable)
        pt.add_columns("ID", "Title", "Goal", "Due", "Status")
        pt.cursor_type = "row"
        
        self.refresh_data()

    def on_screen_resume(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        try:
            gt = self.query_one("#goals-table", DataTable)
            if gt.columns:
                gt.clear()
                for g in data_store.goals: gt.add_row(g.id, g.title, g.due_date or "-", g.status)
            
            pt = self.query_one("#projects-table", DataTable)
            if pt.columns:
                pt.clear()
                for p in data_store.projects: 
                    goal_slug = p.goal_id if p.goal_id else "-"
                    pt.add_row(p.id, p.title, goal_slug, p.due_date or "-", p.status)
        except Exception:
            pass

    def on_key(self, event) -> None:
        focused = self.app.focused
        if event.key == "g":
            self.app.push_screen(GoalAddModal(), self.add_goal_callback)
        elif event.key == "p":
            self.app.push_screen(ProjectAddModal(), self.add_project_callback)
        elif event.key == "d":
            if isinstance(focused, DataTable) and focused.row_count > 0:
                row_data = focused.get_row_at(focused.cursor_row)
                item_id = row_data[0]
                if focused.id == "goals-table":
                    commands.goal_done(item_id)
                else:
                    commands.project_done(item_id)
                self.refresh_data()
        elif event.key == "e":
            if isinstance(focused, DataTable) and focused.row_count > 0:
                row_data = focused.get_row_at(focused.cursor_row)
                item_id = row_data[0]
                if focused.id == "goals-table":
                    goal = next(g for g in data_store.goals if g.id == item_id)
                    self.app.push_screen(GoalAddModal(goal=goal), lambda res: self.edit_goal_callback(item_id, res))
                else:
                    proj = next(p for p in data_store.projects if p.id == item_id)
                    self.app.push_screen(ProjectAddModal(project=proj), lambda res: self.edit_project_callback(item_id, res))
        elif event.key == "x":
            if isinstance(focused, DataTable) and focused.row_count > 0:
                row_data = focused.get_row_at(focused.cursor_row)
                item_id = row_data[0]
                if focused.id == "goals-table":
                    commands.goal_delete(item_id)
                else:
                    commands.project_delete(item_id)
                self.refresh_data()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table_id = event.data_table.id
        item_id = event.data_table.get_row_at(event.cursor_row)[0]
        if table_id == "goals-table":
            commands.goal_done(item_id)
        else:
            commands.project_done(item_id)
        self.refresh_data()

    def add_goal_callback(self, res):
        if res:
            commands.goal_add(*res)
            self.refresh_data()

    def edit_goal_callback(self, goal_id, res):
        if res:
            commands.goal_edit(goal_id, *res)
            self.refresh_data()

    def add_project_callback(self, res):
        if res:
            commands.project_add(*res)
            self.refresh_data()

    def edit_project_callback(self, proj_id, res):
        if res:
            commands.project_edit(proj_id, *res)
            self.refresh_data()

class TasksScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("All Tasks (n: New, Enter/d: Done, e: Edit, x: Delete)", classes="section-title")
        yield DataTable(id="all-tasks-table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#all-tasks-table", DataTable)
        table.cursor_type = "row"
        table.add_columns("ID", "Title", "Due", "Duration", "Reward", "Status")
        self.refresh_data()

    def on_screen_resume(self) -> None:
        self.refresh_data()

    def on_key(self, event) -> None:
        if event.key == "n":
            self.app.push_screen(TaskAddModal(), self.add_task_callback)
            return

        table = self.query_one("#all-tasks-table", DataTable)
        if table.row_count > 0 and table.cursor_row is not None:
            row_data = table.get_row_at(table.cursor_row)
            task_id = row_data[0]
            if event.key == "d":
                commands.task_done(task_id)
                self.refresh_data()
            elif event.key == "e":
                task = next(t for t in data_store.tasks if t.id == task_id)
                self.app.push_screen(TaskAddModal(task=task), lambda res: self.edit_task_callback(task_id, res))
            elif event.key == "x":
                commands.task_delete(task_id)
                self.refresh_data()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        task_id = event.data_table.get_row_at(event.cursor_row)[0]
        commands.task_done(task_id)
        self.refresh_data()

    def add_task_callback(self, result: tuple):
        if result:
            title, due, priority, duration = result
            commands.task_add(title, due_date=due, priority=priority, estimated_minutes=duration)
            self.refresh_data()

    def edit_task_callback(self, task_id, res):
        if res:
            commands.task_edit(task_id, title=res[0], due_date=res[1], priority=res[2], estimated_minutes=res[3])
            self.refresh_data()

    def refresh_data(self):
        try:
            table = self.query_one("#all-tasks-table", DataTable)
            if table.columns:
                table.clear()
                for t in sorted(data_store.tasks, key=lambda x: (x.status == "done", x.priority != "high", x.priority != "medium")):
                    xp = max(5, int(t.estimated_minutes / 3))
                    creds = max(2, int(t.estimated_minutes / 6))
                    table.add_row(t.id, t.title, t.due_date or "-", f"{t.estimated_minutes}m", f"{xp}xp/{creds}cr", t.status)
        except Exception:
            pass

class EconomyScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Economy (h/b: New, e: Edit, x: Delete, Enter: Log/Spend)", classes="section-title")
        with Horizontal():
            with Vertical(classes="column"):
                yield Label("Good Habits", classes="section-title")
                yield DataTable(id="habits-table")
            with Vertical(classes="column"):
                yield Label("Bad Habits", classes="section-title")
                yield DataTable(id="bad-habits-table")
        yield Footer()

    def on_mount(self) -> None:
        h_table = self.query_one("#habits-table", DataTable)
        h_table.cursor_type = "row"
        h_table.add_columns("ID", "Title", "Reward", "Status")

        bh_table = self.query_one("#bad-habits-table", DataTable)
        bh_table.cursor_type = "row"
        bh_table.add_columns("ID", "Title", "Cost")
        self.refresh_data()

    def on_screen_resume(self) -> None:
        self.refresh_data()

    def refresh_data(self):
        try:
            from datetime import date, datetime
            today = date.today().isoformat()

            h_table = self.query_one("#habits-table", DataTable)
            if h_table.columns:
                h_table.clear()
                for h in data_store.habits:
                    last_done_date = None
                    if h.last_done:
                        last_done_date = datetime.fromisoformat(h.last_done).date().isoformat()

                    status = "[green]Done[/green]" if last_done_date == today else "[yellow]Pending[/yellow]"
                    h_table.add_row(h.id, h.title, f"{h.credit_reward} cr", status)

            bh_table = self.query_one("#bad-habits-table", DataTable)
            if bh_table.columns:
                bh_table.clear()
                for bh in data_store.bad_habits: bh_table.add_row(bh.id, bh.title, f"{bh.credit_cost} cr")
        except Exception:
            pass

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table_id = event.data_table.id
        row_data = event.data_table.get_row_at(event.cursor_row)
        item_id = row_data[0]
        
        if table_id == "habits-table":
            success = commands.habit_log(item_id)
            if success:
                self.app.notify("Good habit logged! XP and Credits awarded.")
            else:
                self.app.notify("Already logged today!", severity="warning")
        elif table_id == "bad-habits-table":
            success, msg = commands.badhabit_spend(item_id)
            if success:
                self.app.notify(msg)
            else:
                self.app.notify(msg, severity="error")
        
        self.refresh_data()

    def on_key(self, event) -> None:
        focused = self.app.focused
        if event.key == "h":
            self.app.push_screen(HabitAddModal(is_bad=False), self.add_habit_callback)
        elif event.key == "b":
            self.app.push_screen(HabitAddModal(is_bad=True), self.add_badhabit_callback)
        elif event.key == "e":
            if isinstance(focused, DataTable) and focused.row_count > 0:
                row_data = focused.get_row_at(focused.cursor_row)
                item_id = row_data[0]
                if focused.id == "habits-table":
                    habit = next(h for h in data_store.habits if h.id == item_id)
                    self.app.push_screen(HabitAddModal(is_bad=False, habit=habit), lambda res: self.edit_habit_callback(item_id, res))
                else:
                    bh = next(h for h in data_store.bad_habits if h.id == item_id)
                    self.app.push_screen(HabitAddModal(is_bad=True, habit=bh), lambda res: self.edit_badhabit_callback(item_id, res))
        elif event.key == "x":
            if isinstance(focused, DataTable) and focused.row_count > 0:
                row_data = focused.get_row_at(focused.cursor_row)
                item_id = row_data[0]
                if focused.id == "habits-table":
                    commands.habit_delete(item_id)
                else:
                    commands.badhabit_delete(item_id)
                self.refresh_data()

    def add_habit_callback(self, res):
        if res:
            commands.habit_add(*res)
            self.refresh_data()

    def edit_habit_callback(self, h_id, res):
        if res:
            commands.habit_edit(h_id, *res)
            self.refresh_data()

    def add_badhabit_callback(self, res):
        if res:
            commands.badhabit_add(*res)
            self.refresh_data()

    def edit_badhabit_callback(self, bh_id, res):
        if res:
            commands.badhabit_edit(bh_id, *res)
            self.refresh_data()

class CoreApp(App):
    CSS = """
    #dashboard-container { padding: 1; }
    #stats-row { height: 8; margin-bottom: 1; }
    .stats-card { width: 1fr; background: $surface; border: solid $primary; padding: 1; margin: 0 1; align: center middle; }
    #level-label { text-style: bold; color: $accent; }
    #credits-label { color: $success; text-style: bold; }
    .section-title { background: $primary; color: white; padding: 0 1; margin-top: 1; }
    .column { width: 1fr; padding: 1; }
    
    #task-modal-dialog, #goal-modal-dialog, #proj-modal-dialog, #habit-modal-dialog {
        grid-size: 1;
        padding: 1 2;
        background: $surface;
        border: thick $primary;
        width: 60;
        height: 40;
        align: center middle;
    }
    #modal-title { text-align: center; text-style: bold; margin-bottom: 1; }
    Input { margin-bottom: 1; }
    """
    BINDINGS = [
        ("f1", "switch_screen('dashboard')", "Dashboard"),
        ("f2", "switch_screen('goals')", "Goals/Proj"),
        ("f3", "switch_screen('tasks')", "Tasks"),
        ("f4", "switch_screen('economy')", "Economy"),
        ("f5", "refresh", "Sync"),
        ("q", "quit", "Quit"),
    ]
    SCREENS = {
        "dashboard": Dashboard,
        "goals": GoalsProjectsScreen,
        "tasks": TasksScreen,
        "economy": EconomyScreen,
    }

    def on_mount(self) -> None:
        self.push_screen("dashboard")

    def action_refresh(self) -> None:
        if hasattr(self.screen, "refresh_data"):
            self.screen.refresh_data()
            self.notify("Data synchronized.")

def launch():
    app = CoreApp()
    app.run()
