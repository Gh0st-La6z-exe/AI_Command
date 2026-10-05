from command_center.core import CommandCenter


# CommandCenter owns the system components, so the entry point only needs
# to create the top-level application object instead of constructing Agents,
# Executors, EventBuses, and tools independently.
center = CommandCenter()

bus = center.bus


def handle_agent_started(event):
    print("EVENT RECEIVED:", event.type)
    print("DATA:", event.data)


def handle_agent_completed(event):
    print("EVENT COMPLETED:", event.type)
    print("DATA:", event.data)


def handle_agent_failed(event):
    print("EVENT FAILED:", event.type)
    print("DATA:", event.data)


# Subscribe the entry point to lifecycle events so execution activity is
# visible without coupling Agent or Executor directly to the console.
bus.subscribe("agent.started", handle_agent_started)
bus.subscribe("agent.completed", handle_agent_completed)
bus.subscribe("agent.failed", handle_agent_failed)


# CommandCenter coordinates the request from Task creation through planning
# and execution. main.py only supplies the user's request and goal, then
# receives the completed Task back from the system.
task = center.run(
    "Analyze my Repo",
    "Understand the structure and functionality of the codebase.",
    r"C:\Dev\AI_Command"
)

print(task.status)