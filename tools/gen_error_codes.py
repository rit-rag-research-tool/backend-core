import os
import re
import hashlib
import json

ERROR_DB = "error_codes.json" 

def generate_error_code(file: str, func: str, line: int) -> str:
    identifier = f"{file}:{func}:{line}"
    return hashlib.sha256(identifier.encode()).hexdigest()[:8]

def preprocess_errors(directory: str) -> None:
    error_map = {}
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    lines = f.readlines()

                new_lines = []
                for idx, line in enumerate(lines):
                    match = re.search(r'Error #\{error_code\}', line)
                    if match:
                        func_name = get_function_name(lines, idx)
                        error_code = generate_error_code(file, func_name, idx + 1)
                        error_map[error_code] = {"file": file, "function": func_name, "line": idx + 1}
                        line = line.replace("#{error_code}", error_code)
                    new_lines.append(line)

                with open(file_path, "w") as f:
                    f.writelines(new_lines)

    with open(ERROR_DB, "w") as db_file:
        json.dump(error_map, db_file, indent=4)

def get_function_name(lines: list[str], idx: int) -> str:
    """Find the nearest function definition above the error line."""
    for i in range(idx, -1, -1):
        if lines[i].strip().startswith("def "):
            return lines[i].split("(")[0].split()[1]
    return "global"

if __name__ == "__main__":
    preprocess_errors("./your_project") 
