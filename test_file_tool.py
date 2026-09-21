from command_center.tools.filesystem import read_file, FileResult


result = read_file("C:\\Dev\\AI_Command\\main.py")

assert isinstance(result, FileResult)
assert result.path.endswith("main.py")
assert result.size == len(result.content)
assert "CommandCenter" in result.content

print(f"File: {result.path}")
print(f"Size: {result.size}")
print(result.content)