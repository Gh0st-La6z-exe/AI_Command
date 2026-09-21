from command_center.task import Task
from command_center.agents.agent import Agent
from command_center.events.bus import EventBus
from command_center.core import CommandCenter
from command_center.context import Context
from command_center.tools.registry import get_tool


center = CommandCenter()
bus = center.bus
agent = center.agent

def handle_agent_started(event):
    print("EVENT RECEIVED:", event.type)
    print("DATA:", event.data)

def handle_agent_completed(event):
    print("EVENT COMPLETED:", event.type)
    print("DATA:", event.data)

def handle_agent_failed(event):
    print("EVENT FAILED:", event.type)
    print("DATA:", event.data)

bus.subscribe("agent.started", handle_agent_started)
bus.subscribe("agent.completed", handle_agent_completed)
bus.subscribe("agent.failed", handle_agent_failed)

agent = Agent("Command Center", bus, get_tool)
task = center.run(
    "Analyze my Repo",
    "Understand the structure and functionality of the codebase.",
    r"C:\Dev\AI_Command"
)

print(task.status)
