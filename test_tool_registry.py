from command_center.tools.registry import get_tool
from command_center.tools.repository import RepositoryResult
from command_center.tools.filesystem import FileResult


# The registry translates an action name into the actual callable tool.
# This verifies that the Executor can request tools indirectly instead of
# importing and selecting each tool implementation itself.
tool = get_tool("inspect_repository")

print("TOOL FROM REGISTRY:")
print(tool)

print("\nRUNNING TOOL:")

# Execute the function returned by the registry and validate its structured
# result. The registry itself does not perform the repository operation;
# it only resolves the correct callable.
result = tool(r"C:\Dev\AI_Command")

assert isinstance(result, RepositoryResult)
assert result.path == r"C:\Dev\AI_Command"
assert result.count == len(result.entries)

print(f"Repository: {result.path}")
print(f"Entries found: {result.count}")

for item in result.entries:
    print(item)


print("\nREADING FILE FROM REGISTRY:")

# Resolve a different tool through the same registry interface. This proves
# the registry can dispatch multiple tool types using their action names.
file_tool = get_tool("read_file")

file_result = file_tool(r"C:\Dev\AI_Command\main.py")

assert isinstance(file_result, FileResult)
assert file_result.path.endswith("main.py")
assert file_result.size == len(file_result.content)
assert "CommandCenter" in file_result.content

print(f"File: {file_result.path}")
print(f"Size: {file_result.size}")