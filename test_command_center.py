from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from command_center.agents.agent import Agent
from command_center.context import Context
from command_center.core import CommandCenter
from command_center.events.bus import EventBus
from command_center.execution.executor import Executor
from command_center.planner.planner import Plan, Planner, PlanStep
from command_center.task import Task, TaskStatus
from command_center.tools.registry import get_tool
from command_center.tools.repository import RepositoryResult


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
planner = Planner()

repository_result = get_tool("inspect_repository")(context.repository_path)
plan = planner.plan(context, repository_result)

assert isinstance(plan, Plan)
assert len(plan.steps) == 1

assert isinstance(plan.steps[0], PlanStep)
assert plan.steps[0].action == "read_file"
assert plan.steps[0].input == (
    r"C:\Dev\AI_Command\command_center\core.py"
)

assert Path(plan.steps[0].input).name == "core.py"


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

# Executor runs its supplied steps but does not own the overall Task lifecycle.
assert len(results) == 1
assert task.status == TaskStatus.PENDING
assert len(task.results) == 1


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
file_result = task.results[0]

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

filesystem_repository = get_tool("inspect_repository")(
    filesystem_context.repository_path
)
filesystem_plan = planner.plan(filesystem_context, filesystem_repository)

assert isinstance(filesystem_plan, Plan)
assert len(filesystem_plan.steps) == 1

assert isinstance(filesystem_plan.steps[0], PlanStep)
assert filesystem_plan.steps[0].action == "read_file"
assert Path(filesystem_plan.steps[0].input).name == "filesystem.py"


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

    center = CommandCenter()
    tool_calls = []

    def counting_registry(action):
        tool = get_tool(action)

        def counted_tool(value):
            tool_calls.append(action)
            return tool(value)

        return counted_tool

    center.executor.tool_registry = counting_registry
    command_task = center.run(
        "Analyze core",
        "Verify the supplied repository path.",
        temporary_repository,
    )

    assert command_task.status == TaskStatus.COMPLETED
    assert tool_calls == ["inspect_repository", "read_file"]
    assert len(command_task.results) == 2
    assert isinstance(command_task.results[0], RepositoryResult)
    assert Path(command_task.results[0].path).resolve() == repository_root.resolve()
    assert Path(command_task.results[1].path).resolve() == core_path.resolve()


# A failed discovery is part of the overall task and must set its status.
failed_inspection_task = Task("Analyze core")
with patch("command_center.core.Task", return_value=failed_inspection_task):
    failing_center = CommandCenter()

    def failing_inspection(action):
        def fail(_value):
            raise RuntimeError("inspection failed")

        return fail

    failing_center.executor.tool_registry = failing_inspection

    try:
        failing_center.run("Analyze core", "Fail inspection.", "unused")
        raise AssertionError("CommandCenter ignored an inspection failure.")
    except RuntimeError as error:
        assert str(error) == "inspection failed"

assert failed_inspection_task.status == TaskStatus.FAILED


# A failed follow-up read must also fail the overall task after inspection.
failed_read_task = Task("Analyze core")
with TemporaryDirectory() as temporary_repository:
    package_path = Path(temporary_repository) / "command_center"
    package_path.mkdir()
    (package_path / "core.py").write_text("source", encoding="utf-8")

    with patch("command_center.core.Task", return_value=failed_read_task):
        failing_center = CommandCenter()

        def failing_read(action):
            if action == "inspect_repository":
                return get_tool(action)

            def fail(_value):
                raise RuntimeError("read failed")

            return fail

        failing_center.executor.tool_registry = failing_read

        try:
            failing_center.run(
                "Analyze core",
                "Fail follow-up read.",
                temporary_repository,
            )
            raise AssertionError("CommandCenter ignored a read failure.")
        except RuntimeError as error:
            assert str(error) == "read failed"

assert failed_read_task.status == TaskStatus.FAILED


# A request with no recognized target still completes after one inspection.
with TemporaryDirectory() as temporary_repository:
    center = CommandCenter()
    tool_calls = []

    def inspection_only_registry(action):
        tool = get_tool(action)

        def counted_tool(value):
            tool_calls.append(action)
            return tool(value)

        return counted_tool

    center.executor.tool_registry = inspection_only_registry
    inspection_only_task = center.run(
        "Summarize this project",
        "No file target is selected.",
        temporary_repository,
    )

    assert inspection_only_task.status == TaskStatus.COMPLETED
    assert tool_calls == ["inspect_repository"]
    assert len(inspection_only_task.results) == 1


print("TEST PASSED")