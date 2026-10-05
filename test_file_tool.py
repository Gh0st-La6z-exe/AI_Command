from command_center.tools.filesystem import read_file, FileResult


# Verify that the filesystem tool returns the expected structured result
# instead of exposing a raw string or some other unvalidated value.
result = read_file(r"C:\Dev\AI_Command\main.py")

assert isinstance(result, FileResult)

# Verify the result identifies the file that was actually read and preserves
# the content/metadata contract currently defined by FileResult.
assert result.path.endswith("main.py")
assert result.size == len(result.content)
assert "CommandCenter" in result.content


# Print the returned data so the test also provides immediate visibility
# into what the tool actually produced during development.
print(f"File: {result.path}")
print(f"Size: {result.size}")
print(result.content)