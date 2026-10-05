from pathlib import Path
from tempfile import TemporaryDirectory

from command_center.agents.agent import Agent
from command_center.context import Context
from command_center.core import CommandCenter
from command_center.events.bus import EventBus
from command_center.execution.executor import Executor
from command_center.planner.planner import Plan, Planner, PlanStep
from command_center.task import Task, TaskStatus
from command_center.tools.registry import get_tool


# --------------------------------------------------
# CORE TARGET TEST
# --------------------------------------------------

# Verify that Task and Context preserve the relationship between the
# original request, its goal, and the repository being analyzed.
task = Task("Analyze the core")

goal = "Verify task and context wiring."

context = Context(
    task,
    goal,
    r"C:\Dev\AI_Command"
)

assert context.task is task
assert context.goal == goal

# Verify that the Planner converts the request into the expected
# executable structure without actually executing the plan itself.
planner = Planner(get_tool)

plan = planner.plan(context)

assert isinstance(plan, Plan)
assert len(plan.steps) == 2

assert isinstance(plan.steps[0], PlanStep)
assert plan.steps[0].action == "inspect_repository"
assert plan.steps[0].input == r"C:\Dev\AI_Command"

assert isinstance(plan.steps[1], PlanStep)
assert plan.steps[1].action == "read_file"
assert plan.steps[1].input == (
    r"C:\Dev\AI_Command\command_center\core.py"
)

assert Path(plan.steps[1].input).name == "core.py"


# --------------------------------------------------
# EXECUTION TEST
# --------------------------------------------------

# Build the execution layer independently so the test can verify
# Executor and Agent behavior without relying on CommandCenter orchestration.
bus = EventBus()
agent = Agent("Test Agent", bus)

executor = Executor(
    agent,
    get_tool,
)

results = executor.execute_plan(plan, context)

# Verify that every planned step produced a result and that the Task
# reached the expected terminal state after successful execution.
assert len(results) == 2
assert task.status == TaskStatus.COMPLETED
assert len(task.results) == 2


# --------------------------------------------------
# EXECUTOR VALIDATION TEST
# --------------------------------------------------

# Executor must reject malformed steps before allowing them to reach
# the Agent or any tool.
invalid_step = PlanStep(
    action="",
    input=r"C:\Dev\AI_Command"
)

try:
    executor.execute_step(invalid_step, context)
    raise AssertionError("Executor accepted an invalid plan step.")
except ValueError as error:
    assert str(error) == "Plan step is missing an action."


# Verify that Executor rejects actions that are not registered as tools.
unknown_step = PlanStep(
    action="Does not exist.",
    input=r"C:\Dev\AI_Command"
)

try:
    executor.execute_step(unknown_step, context)
    raise AssertionError("Executor accepted an unknown action.")
except ValueError as error:
    assert str(error) == "Unknown action: Does not exist."


# --------------------------------------------------
# RESULT TEST
# --------------------------------------------------

# Results belong to the Task after execution. Verify that the repository
# inspection result and file result contain the expected structured data.
repository_result = task.results[0]
file_result = task.results[1]

core_file = repository_result.find_file("core.py")

assert core_file is not None
assert core_file.name == "core.py"
assert core_file == Path(
    r"C:\Dev\AI_Command\command_center\core.py"
)

missing_file = repository_result.find_file("does_not_exist.py")

assert missing_file is None

# Verify that the repository result accurately identifies the repository
# that was inspected and that its entry count matches the discovered files.
assert Path(repository_result.path).resolve() == Path(
    r"C:\Dev\AI_Command"
).resolve()

assert Path(file_result.path).resolve() == Path(
    r"C:\Dev\AI_Command\command_center\core.py"
).resolve()

assert isinstance(repository_result.entries, list)
assert repository_result.count == len(repository_result.entries)

# Verify the filesystem result contract: content is text, size reflects
# the current implementation's character count, and the expected source
# code was actually returned.
assert isinstance(file_result.content, str)
assert file_result.size == len(file_result.content)
assert "CommandCenter" in file_result.content


# --------------------------------------------------
# FILESYSTEM TARGET TEST
# --------------------------------------------------

# Verify that the Planner can identify a different target from the user's
# request and generate the corresponding read_file step.
filesystem_task = Task("Analyze the filesystem tool")

filesystem_context = Context(
    filesystem_task,
    "Understand the filesystem tool.",
    r"C:\Dev\AI_Command"
)

filesystem_plan = planner.plan(filesystem_context)

assert isinstance(filesystem_plan, Plan)
assert len(filesystem_plan.steps) == 2

assert isinstance(filesystem_plan.steps[0], PlanStep)
assert filesystem_plan.steps[0].action == "inspect_repository"

assert isinstance(filesystem_plan.steps[1], PlanStep)
assert filesystem_plan.steps[1].action == "read_file"
assert Path(filesystem_plan.steps[1].input).name == "filesystem.py"


# --------------------------------------------------
# COMMAND CENTER REPOSITORY PATH TEST
# --------------------------------------------------

# Verify that the public entry point passes its repository argument through
# Context, planning, and execution rather than using a placeholder path.
with TemporaryDirectory() as temporary_repository:
    repository_root = Path(temporary_repository)
    package_path = repository_root / "command_center"
    package_path.mkdir()
    core_path = package_path / "core.py"
    core_path.write_text("temporary core source", encoding="utf-8")

    command_task = CommandCenter().run(
        "Analyze core",
        "Verify the supplied repository path.",
        temporary_repository,
    )

    assert command_task.status == TaskStatus.COMPLETED
    assert Path(command_task.results[0].path).resolve() == repository_root.resolve()
    assert Path(command_task.results[1].path).resolve() == core_path.resolve()


print("TEST PASSED")