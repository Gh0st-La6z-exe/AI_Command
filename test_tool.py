from command_center.tools.repository import inspect_repository, RepositoryResult


tool = inspect_repository

print("FUNCTION OBJECT:")
print(tool)

print("\nCALLING FUNCTION:")

result = tool("C:\\Dev\\AI_Command")

assert isinstance(result, RepositoryResult)
assert result.path == "C:\\Dev\\AI_Command"
assert result.count == len(result.entries)

print(f"Repository: {result.path}")
print(f"Entries found: {result.count}")

for item in result.entries:
    print(item)