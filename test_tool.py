from command_center.tools.repository import inspect_repository, RepositoryResult


# Keep a reference to the tool's function object. This demonstrates that
# Python functions can be passed around as values and called later.
tool = inspect_repository

print("FUNCTION OBJECT:")
print(tool)

print("\nCALLING FUNCTION:")

# Execute the tool through the function reference and capture its structured
# result for validation.
result = tool(r"C:\Dev\AI_Command")

# Verify that the repository tool returns the result type expected by the
# execution pipeline and that its metadata matches the discovered entries.
assert isinstance(result, RepositoryResult)
assert result.path == r"C:\Dev\AI_Command"
assert result.count == len(result.entries)

print(f"Repository: {result.path}")
print(f"Entries found: {result.count}")

# Display the discovered repository entries so we can inspect the actual
# filesystem snapshot produced by the tool during development.
for item in result.entries:
    print(item)