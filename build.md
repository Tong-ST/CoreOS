Project: Personal Self-Development CLI — a terminal-based productivity and life management system for personal use only. Clean and functional, not production-grade.
Tech stack:

Python 3
JSON flat file (data.json) for all storage — human-readable, pretty-printed
rich for any plain output formatting
Textual for the interactive TUI mode


Data model:

Goal — id, title, description, status (active/done), badge_name, badge_description, created_at, completed_at
Project — id, goal_id (optional), title, description, status (active/done), created_at
Task — id, project_id (optional), title, due_date (optional), priority (high/medium/low), status (todo/done), created_at
Habit — id, title, credit_reward, last_done
BadHabit — id, title, credit_cost
Badge — id, name, description, goal_id, earned_at
Player — single object: xp, credits, level


Economy rules:

Completing a task gives XP + Credits based on priority:

High: 30 XP / 20 Credits
Medium: 20 XP / 10 Credits
Low: 10 XP / 5 Credits


Completing a Project gives bonus 50 XP / 30 Credits
Completing a Goal gives 200 XP / 100 Credits + auto-awards its Badge
Logging a good habit gives flat Credits (user-defined per habit, e.g. 15cr)
Credits never decay — they accumulate freely
XP is permanent and only used for leveling — never spent
Bad habits have a Credit cost set by the user — spending Credits logs the usage with timestamp


CLI commands (entry point: python main.py <command>):

goal add / goal list / goal done <id>
project add / project list / project done <id>
task add / task list / task done <id>
habit add / habit log <id> — log a good habit, earn credits
badhabit add / badhabit spend <id> — spend credits to unlock a bad habit
badge list — show earned badges
balance — show XP, Credits, Level, and earned Badges


TUI mode (launched by python main.py with no arguments, built with Textual):

Dashboard screen — Player level, XP bar, Credit balance, today's tasks, overdue tasks, recent badges
Goals & Projects screen — browse goals, see linked projects and their progress
Tasks screen — list tasks sorted by priority, overdue highlighted, mark done inline
Economy screen — log good habits, spend credits on bad habits, view balance
Keyboard navigation throughout — tab between screens, shortcuts for common actions (n = new, d = done, q = quit)


General notes:

IDs are short readable slugs like task-001, not UUIDs
If data.json doesn't exist, create it automatically on first run
Split code into modules — don't put everything in main.py. Suggested: data.py, models.py, commands.py, tui.py
CLI commands and TUI share the exact same data and logic layer


Build order — do it in this sequence:

Scaffold project structure and modules
Data read/write layer (data.py)
CLI commands — Goals and Tasks first
Economy system — XP, Credits, Badges
TUI screens with Textual, starting with Dashboard
