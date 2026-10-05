# Architecture

This document describes the implementation as it exists today. Planned capabilities such as model inference, verification, durable memory, and autonomous execution are not implemented yet.

## Components

- `CommandCenter` in `command_center/core.py` is the composition root and run coordinator. It constructs the event bus, planner, agent, and executor. `run()` creates a `Task` and `Context`, owns the full task lifecycle, coordinates repository inspection and follow-up planning, and returns the task on success.
- `Task` in `command_center/task.py` stores the prompt, identifier, lifecycle status, and accumulated tool results.
- `Context` in `command_center/context.py` carries the task, a goal string, and the repository path for planning and execution.
- `Planner`, `Plan`, and `PlanStep` in `command_center/planner/planner.py` translate a small set of keywords into follow-up operations using an already-inspected `RepositoryResult`. Planning does not resolve or invoke tools. A plan is an ordered list of steps; dependency identifiers exist in the data model but are not used by the executor.
- `Executor` in `command_center/execution/executor.py` checks that steps have an action and input, resolves actions through the registry, and runs individual steps or ordered plans. It does not finalize the overall task status.
- `Agent` in `command_center/agents/agent.py` runs the callable supplied by the executor, appends its result to the task, prints a summary, and emits per-step lifecycle events.
- `get_tool()` in `command_center/tools/registry.py` maps the action names `inspect_repository` and `read_file` to their implementations. The executor uses this registry to resolve planned actions.
- Repository and filesystem tools return structured `RepositoryResult` and `FileResult` objects derived from `ToolResult`.
- `EventBus` in `command_center/events/` dispatches events to subscribed handlers without coupling the agent to those handlers.

## Current data flow

1. `main.py` submits a prompt, goal, and repository path to `CommandCenter.run()`.
2. `CommandCenter` creates the task and context. The supplied repository path is passed into the context.
3. `CommandCenter` marks the task running and asks the executor to perform one `inspect_repository` step.
4. The agent runs the registered inspection tool, appends its structured result to the task once, prints a summary, and emits lifecycle events.
5. `CommandCenter` passes that observed `RepositoryResult` to the planner. The planner returns an ordered plan containing only matching follow-up reads; it performs no tool calls.
6. The executor runs the follow-up plan sequentially through the registry, and the agent records each result once.
7. `CommandCenter` marks the task completed after both phases succeed, or failed if inspection, planning, or a follow-up step raises. The caller receives the task on success.

## Current boundaries and limitations

- The registry is the available tool surface. It currently contains read-only repository inspection and file reading; there is no shell, write, network, package-installation, or commit capability.
- Planning is deterministic keyword matching, not model-assisted reasoning. It maps a small set of keywords to known filenames. Requests with no recognized target produce an inspection-only run; unsupported requests are not yet reported as a distinct planning error.
- Repository inspection is executed once by `CommandCenter` before planning. The resulting snapshot is passed into the pure planner, which can select existing files without hidden tool calls.
- `CommandCenter` owns task status across inspection and follow-up execution. `Executor.execute_plan()` only runs the plan it receives and does not mark the overall task completed.
- `PlanStep.depends_on` is currently descriptive only; execution follows list order and does not evaluate dependencies.
- Results are held in memory on the `Task`; they are not persisted across runs. The agent prints output directly, and there is no separate verifier or durable evidence store.
- The current test suite consists of top-level assertion scripts. See the repository README for commands.

## Intended evolution

The next engineering steps are to describe and validate registered capabilities and make plans explicitly grounded in available tool results. Execution evidence and deterministic verification should be established before adding model-generated plans or higher-risk capabilities. The model, when introduced, should propose plans through an interchangeable interface; the executor and registry remain responsible for validating and dispatching actions.
