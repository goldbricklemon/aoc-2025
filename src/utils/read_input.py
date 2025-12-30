

def read_test_input(s:str) -> list[str]:
    # Remove first empyt line due to python str literal formatting
    return s.splitlines(keepends=False)[1:]

def read_input(input_path:str) -> list[str]:
    with open(input_path, "r") as f:
        lines = f.readlines()
    return [l.strip("\n").strip("\r") for l in lines]
