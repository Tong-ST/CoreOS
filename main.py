import sys
import argparse
import commands

def main():
    commands.sync_daily_tasks()
    if len(sys.argv) == 1:
        try:
            import tui
            tui.launch()
        except ImportError:
            print("TUI module not found. Please ensure 'textual' is installed and tui.py exists.")
        except Exception as e:
            print(f"Error launching TUI: {e}")
        return

    parser = argparse.ArgumentParser(description="CoreOS CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Goal
    goal_p = subparsers.add_parser("goal")
    goal_sub = goal_p.add_subparsers(dest="sub")
    goal_add = goal_sub.add_parser("add")
    goal_add.add_argument("title")
    goal_add.add_argument("description")
    goal_add.add_argument("badge_name")
    goal_add.add_argument("badge_description")
    goal_add.add_argument("--due", dest="due_date")
    goal_edit = goal_sub.add_parser("edit")
    goal_edit.add_argument("id")
    goal_edit.add_argument("--title")
    goal_edit.add_argument("--description")
    goal_edit.add_argument("--badge-name")
    goal_edit.add_argument("--badge-description")
    goal_edit.add_argument("--due", dest="due_date")
    goal_del = goal_sub.add_parser("delete")
    goal_del.add_argument("id")
    goal_sub.add_parser("list")
    goal_done = goal_sub.add_parser("done")
    goal_done.add_argument("id")
    goal_undo = goal_sub.add_parser("undo")
    goal_undo.add_argument("id")

    # Project
    proj_p = subparsers.add_parser("project")
    proj_sub = proj_p.add_subparsers(dest="sub")
    proj_add = proj_sub.add_parser("add")
    proj_add.add_argument("title")
    proj_add.add_argument("description")
    proj_add.add_argument("--goal", dest="goal_id")
    proj_add.add_argument("--duration", dest="duration", type=int, default=30)
    proj_add.add_argument("--due", dest="due_date")
    proj_add.add_argument("--priority", default="medium")
    proj_edit = proj_sub.add_parser("edit")
    proj_edit.add_argument("id")
    proj_edit.add_argument("--title")
    proj_edit.add_argument("--description")
    proj_edit.add_argument("--goal", dest="goal_id")
    proj_edit.add_argument("--duration", dest="duration", type=int)
    proj_edit.add_argument("--due", dest="due_date")
    proj_edit.add_argument("--priority")
    proj_del = proj_sub.add_parser("delete")
    proj_del.add_argument("id")
    proj_sub.add_parser("list")
    proj_done = proj_sub.add_parser("done")
    proj_done.add_argument("id")
    proj_undo = proj_sub.add_parser("undo")
    proj_undo.add_argument("id")

    # Task
    task_p = subparsers.add_parser("task")
    task_sub = task_p.add_subparsers(dest="sub")
    task_add = task_sub.add_parser("add")
    task_add.add_argument("title")
    task_add.add_argument("--project", dest="project_id")
    task_add.add_argument("--due", dest="due_date")
    task_add.add_argument("--priority", default="medium")
    task_add.add_argument("--duration", dest="duration", type=int, default=30)
    task_edit = task_sub.add_parser("edit")
    task_edit.add_argument("id")
    task_edit.add_argument("--title")
    task_edit.add_argument("--project", dest="project_id")
    task_edit.add_argument("--due", dest="due_date")
    task_edit.add_argument("--priority")
    task_edit.add_argument("--duration", dest="duration", type=int)
    task_del = task_sub.add_parser("delete")
    task_del.add_argument("id")
    task_sub.add_parser("list")
    task_done = task_sub.add_parser("done")
    task_done.add_argument("id")
    task_undo = task_sub.add_parser("undo")
    task_undo.add_argument("id")

    # Habit
    habit_p = subparsers.add_parser("habit")
    habit_sub = habit_p.add_subparsers(dest="sub")
    habit_add = habit_sub.add_parser("add")
    habit_add.add_argument("title")
    habit_add.add_argument("reward", type=int)
    habit_edit = habit_sub.add_parser("edit")
    habit_edit.add_argument("id")
    habit_edit.add_argument("--title")
    habit_edit.add_argument("--reward", type=int)
    habit_del = habit_sub.add_parser("delete")
    habit_del.add_argument("id")
    habit_log = habit_sub.add_parser("log")
    habit_log.add_argument("id")

    # Bad Habit
    bad_p = subparsers.add_parser("badhabit")
    bad_sub = bad_p.add_subparsers(dest="sub")
    bad_add = bad_sub.add_parser("add")
    bad_add.add_argument("title")
    bad_add.add_argument("cost", type=int)
    bad_edit = bad_sub.add_parser("edit")
    bad_edit.add_argument("id")
    bad_edit.add_argument("--title")
    bad_edit.add_argument("--cost", type=int)
    bad_del = bad_sub.add_parser("delete")
    bad_del.add_argument("id")
    bad_spend = bad_sub.add_parser("spend")
    bad_spend.add_argument("id")

    # Badge & Balance
    subparsers.add_parser("badge") # badge list
    subparsers.add_parser("balance")

    args = parser.parse_args()

    if args.command == "goal":
        if args.sub == "add": commands.goal_add(args.title, args.description, args.badge_name, args.badge_description, args.due_date)
        elif args.sub == "edit": commands.goal_edit(args.id, args.title, args.description, args.badge_name, args.badge_description, args.due_date)
        elif args.sub == "delete": commands.goal_delete(args.id)
        elif args.sub == "list": commands.goal_list()
        elif args.sub == "done": commands.goal_done(args.id)
        elif args.sub == "undo": commands.goal_undo(args.id)
    elif args.command == "project":
        if args.sub == "add": commands.project_add(args.title, args.description, args.goal_id, args.duration, args.due_date, args.priority)
        elif args.sub == "edit": commands.project_edit(args.id, args.title, args.description, args.goal_id, args.duration, args.due_date, args.priority)
        elif args.sub == "delete": commands.project_delete(args.id)
        elif args.sub == "list": commands.project_list()
        elif args.sub == "done": commands.project_done(args.id)
        elif args.sub == "undo": commands.project_undo(args.id)
    elif args.command == "task":
        if args.sub == "add": commands.task_add(args.title, args.project_id, args.due_date, args.priority, args.duration)
        elif args.sub == "edit": commands.task_edit(args.id, args.title, args.project_id, args.due_date, args.priority, args.duration)
        elif args.sub == "delete": commands.task_delete(args.id)
        elif args.sub == "list": commands.task_list()
        elif args.sub == "done": commands.task_done(args.id)
        elif args.sub == "undo": commands.task_undo(args.id)
    elif args.command == "habit":
        if args.sub == "add": commands.habit_add(args.title, args.reward)
        elif args.sub == "edit": commands.habit_edit(args.id, args.title, args.reward)
        elif args.sub == "delete": commands.habit_delete(args.id)
        elif args.sub == "log": commands.habit_log(args.id)
    elif args.command == "badhabit":
        if args.sub == "add": commands.badhabit_add(args.title, args.cost)
        elif args.sub == "edit": commands.badhabit_edit(args.id, args.title, args.cost)
        elif args.sub == "delete": commands.badhabit_delete(args.id)
        elif args.sub == "spend": commands.badhabit_spend(args.id)
    elif args.command == "badge":
        commands.badge_list()
    elif args.command == "balance":
        commands.balance()

if __name__ == "__main__":
    main()
