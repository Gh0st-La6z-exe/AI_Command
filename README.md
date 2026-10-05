# AI Command Center

Local-first, model-agnostic AI command center built from scratch to explore
agentic systems, tool orchestration, deterministic execution, verification,
memory, and AI-assisted software engineering.

AI Command Center is an early local-first Python prototype for coordinating a task, creating a deterministic plan, dispatching registered tools, and collecting structured results. The current implementation is intentionally small: it has no model integration, persistent memory, verification subsystem, shell access, or network tools.

## Requirements

- Python 3.11 or newer
- No third-party packages are currently required

## Run

From the repository root:

```powershell
python main.py
```

The entry point creates a `CommandCenter`, submits a repository-analysis request, and prints agent lifecycle events and tool results.

## Tests

The current tests are executable assertion scripts rather than pytest-discoverable test functions. Run them from the repository root:

```powershell
python test_command_center.py
python test_file_tool.py
python test_tool_registry.py
python test_tool.py
```

These scripts exercise the planner/executor flow and the current read-only repository and file tools. `test_file_tool.py` prints the file contents it reads.

## Current capabilities

- Inspect source files while pruning `.git` and `__pycache__` directories
- Read UTF-8 text files
- Resolve tool actions through a registry with input/result contracts and risk metadata
- Track task status and structured tool results
- Emit agent started/completed/failed events

The planner currently maps a small set of prompt keywords to known source filenames. It is not a general natural-language planner; requests without a supported target return `TaskStatus.UNSUPPORTED` with an explanatory message. The `main.py` example demonstrates that outcome for its generic repository prompt. See [Architecture](docs/architecture.md) for component responsibilities, capability contracts, data flow, and limitations.
