#!/usr/bin/env python3
import ast
import os
import re
import json
import argparse
from pathlib import Path
from typing import Any, Dict, Optional

ROUTES_BASE = os.path.join("src", "routes")

BASE_PY_TEMPLATE = '''from fastapi import APIRouter
from typing import Dict, Any
router = APIRouter()

@router.get("/")
async def default_response() -> Dict[str, str]:
    return {"message": "Default response for this route."}

__endpoints__: Dict[str, Any] = {}

'''

INIT_PY_TEMPLATE = '''# This file is auto-generated by bearpath.py. Do not edit directly.
from fastapi import APIRouter
from .base import router as base_router
from typing import Dict, Any

router = APIRouter()
router.include_router(base_router)

__endpoints__: Dict[str, Any] = {}
'''

ENDPOINT_REGEX = re.compile(r"""@router\.(get|post|put|delete|patch)\(\s*["']([^"']+)["']\s*\)""", re.IGNORECASE)
DECORATOR_REGEX = re.compile(r"@router\.(get|post|put|delete|patch)\(\s*['\"]([^'\"]+)['\"]\s*\)", re.IGNORECASE)

VERBOSE = False

def verbose_print(message: str) -> None:
    if VERBOSE:
        print(message)


def ensure_directory_structure(path: str) -> None:
    segments = [seg for seg in path.strip("/").split("/") if seg]
    current_dir = Path(ROUTES_BASE)
    for seg in segments:
        current_dir = current_dir / seg
        if not current_dir.exists():
            verbose_print(f"Creating directory: {current_dir}")
            current_dir.mkdir(parents=True, exist_ok=True)
        base_file = current_dir / "base.py"
        if not base_file.exists():
            verbose_print(f"Creating file: {base_file}")
            base_file.write_text(BASE_PY_TEMPLATE)
        init_file = current_dir / "__init__.py"
        if not init_file.exists():
            verbose_print(f"Creating file: {init_file}")
            init_file.write_text(INIT_PY_TEMPLATE)

def create_route(route_path: str) -> None:
    ensure_directory_structure(route_path)
    verbose_print(f"Route structure for '{route_path}' created under {ROUTES_BASE}")

def extract_full_function(content: str, method: str, endpoint: str) -> str:
    lines = content.splitlines()
    function_found = False
    extracted_lines = []
    indent_level = None

    for i, line in enumerate(lines):
        stripped_line = line.strip()
        match = DECORATOR_REGEX.match(stripped_line)
        if match:
            matched_method, route = match.groups()
            if function_found:
                break
            if matched_method.lower() == method.lower() and route == endpoint:
                function_found = True
                extracted_lines.append(line)
                continue

        if function_found:
            if stripped_line.startswith("def "):
                extracted_lines.append(line)
                indent_level = len(line) - len(line.lstrip())
                continue
            if indent_level is not None and ((len(line) - len(line.lstrip())) < indent_level or stripped_line.startswith("@router")):
                break
            extracted_lines.append(line)
    return "\n".join(extracted_lines) if extracted_lines else ""

def parse_function_signature(func_source: str) -> dict[str, Any]:
    signature = {}
    try:
        tree = ast.parse(func_source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for arg in node.args.args:
                    arg_name = arg.arg
                    arg_type = "Any"
                    if arg.annotation:
                        arg_type = ast.dump(arg.annotation)
                    signature[arg_name] = arg_type
    except Exception as e:
        verbose_print(f"Error parsing function signature: {e}")
    return signature

def extract_endpoints_from_file(file_path: Path) -> dict[str, Any]:
    endpoints: dict[str, Any] = {}
    try:
        content = file_path.read_text()
    except Exception as e:
        verbose_print(f"Error reading {file_path}: {e}")
        return endpoints

    for match in ENDPOINT_REGEX.finditer(content):
        method, endpoint = match.groups()
        full_function_text = extract_full_function(content, method, endpoint)
        prameters = parse_function_signature(full_function_text)
        endpoints[endpoint] = {
            "method": method.upper(),
            "description": "None",
            "parameters": {k: {"type": v, "description": "None"} for k, v in prameters.items()},
            "response": "None",
        }
    verbose_print(f"Extracted {len(endpoints)} endpoints from {file_path}")
    return endpoints

def update_file_endpoints(file_path: Path, silent: bool) -> dict[str, Any]:
    endpoints = extract_endpoints_from_file(file_path)
    verbose_print(f"Extracted endpoints: {endpoints}")
    endpoints_block = f"__endpoints__: Dict[str, Any] = {json.dumps(endpoints, indent=4)}\n\n"
    try:
        content = file_path.read_text()
    except Exception as e:
        verbose_print(f"Error reading {file_path}: {e}")
        return endpoints
    
    endpoints_pattern = re.compile(
        r"(__endpoints__:\s*(Dict|dict)\[str,\s*Any\]\s*=\s*)\{[\s\S]*?\}\n\n",
        re.MULTILINE
    )

    if not silent:
        if endpoints_pattern.search(content):
            new_content = endpoints_pattern.sub(endpoints_block, content)
        else:
            lines = content.split("\n")
            insert_index = 0
            for i, line in enumerate(lines):
                if line.strip().startswith("from ") or line.strip().startswith("import "):
                    insert_index = i + 2
            lines.insert(insert_index, endpoints_block)
            new_content = "\n".join(lines)

        file_path.write_text(new_content)
        verbose_print(f"Updated endpoints in {file_path}")
        return endpoints
    else:
        if endpoints_pattern.search(content):
            new_content = endpoints_pattern.sub(" ", content)
        else:
            new_content = content
        file_path.write_text(new_content)
        return endpoints
    

def aggregate_directory_endpoints(dir_path: Path, silent: bool) -> Dict[str, Any]:
    aggregated: Dict[str, Any] = {}
    for file in sorted(dir_path.glob("*.py")):
        if file.name == "__init__.py":
            continue
        endpoints = update_file_endpoints(file, silent)
        key = "/" if file.stem == "base" else "/" + file.stem
        aggregated[key] = endpoints
    for subdir in sorted([d for d in dir_path.iterdir() if d.is_dir()]):
        init_file = subdir / "__init__.py"
        if init_file.exists():
            sub_aggregated = aggregate_directory_endpoints(subdir, silent)
            aggregated["/" + subdir.name] = sub_aggregated

    return aggregated

def update_init_imports(dir_path: Path) -> str:
    lines = []
    lines.append("# This file is auto-generated by bearpath.py. Do not edit directly.")
    lines.append("")
    lines.append("from fastapi import APIRouter")
    lines.append("from typing import Dict, Any")
    
    base_file = dir_path / "base.py"
    if base_file.exists():
        lines.append("from .base import router as base_router")
    
    for file in sorted(dir_path.glob("*.py")):
        if file.name in ["__init__.py", "base.py"]:
            continue
        module_name = file.stem  # e.g. "id"
        router_var = f"{module_name}_router"
        lines.append(f"from .{module_name} import router as {router_var}")
    
    for subdir in sorted([d for d in dir_path.iterdir() if d.is_dir()]):
        init_file = subdir / "__init__.py"
        if init_file.exists():
            router_var = f"{subdir.name}_router"
            lines.append(f"from .{subdir.name} import router as {router_var}")
    
    lines.append("")
    lines.append("router = APIRouter()")
    
    if base_file.exists():
        lines.append("router.include_router(base_router, prefix='')")
    
    for file in sorted(dir_path.glob("*.py")):
        if file.name in ["__init__.py", "base.py"]:
            continue
        module_name = file.stem
        router_var = f"{module_name}_router"
        lines.append(f"router.include_router({router_var}, prefix='/{module_name}')")
    
    for subdir in sorted([d for d in dir_path.iterdir() if d.is_dir()]):
        init_file = subdir / "__init__.py"
        if init_file.exists():
            router_var = f"{subdir.name}_router"
            lines.append(f"router.include_router({router_var}, prefix='/{subdir.name}')")
    
    lines.append("")
    return "\n".join(lines)

def update_init_file(dir_path: Path, aggregated: Dict[str, Any], silent: bool) -> None:
    init_file = dir_path / "__init__.py"
    free_line = "\n"
    
    router_section = update_init_imports(dir_path)
    
    if not silent:
        endpoints_block = f"__endpoints__: Dict[str, Any] = {json.dumps(aggregated, indent=4)}\n\n"
    else:
        endpoints_block = ""
        
    
    new_content = router_section + free_line + endpoints_block
    init_file.write_text(new_content)
    verbose_print(f"Updated init file endpoints in {init_file}")

def update_all_inits(dir_path: Path, silent: bool) -> Dict[str, Any]:
    aggregated = aggregate_directory_endpoints(dir_path, silent)
    update_init_file(dir_path, aggregated, silent)
    for subdir in [d for d in dir_path.iterdir() if d.is_dir()]:
        update_all_inits(subdir, silent)
    return aggregated


def update_endpoints_in_path(silent: bool, verose: bool, no_output: bool, route_path: Optional[str] = None) -> None:
    if verose:
        global VERBOSE
        VERBOSE = True

    aggregated_files = {}
    if route_path:
        base = Path(ROUTES_BASE) / route_path.strip("/")
    else:
        base = Path(ROUTES_BASE)

    for root, dirs, files in os.walk(base):
        for file in files:
            if file.endswith(".py") and file not in ("__init__.py",):
                file_path = Path(root) / file
                file_endpoints = update_file_endpoints(file_path, silent)
                rel_path = file_path.relative_to(ROUTES_BASE).with_suffix("")
                route_key = "/" + "/".join(rel_path.parts)
                aggregated_files[route_key] = file_endpoints

    aggregated_inits = update_all_inits(base, silent)

    verbose_print(f"Aggregated endpoints: {aggregated_inits}")
    if not no_output:
        overall = {"files": aggregated_files, "inits": aggregated_inits}
        with open("endpoints.json", "w") as f:
            json.dump(overall, f, indent=4)
        verbose_print(f"Aggregated endpoints dumped to endpoints.json")
    



def main() -> None:
    parser = argparse.ArgumentParser(description="bearpath: FastAPI route generator and updater")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Sub-command to run")

    create_parser = subparsers.add_parser("create", help="Create route directories and default files")
    create_parser.add_argument("path", type=str, help="Nested route path (e.g. '/apikey/v2')")

    update_parser = subparsers.add_parser("update", help="Update endpoint definitions in route files and init files")
    update_parser.add_argument("path", type=str, nargs="?", default=None,
                               help="Optional route path to update (e.g. '/apikey/v2'). If omitted, all routes are updated.")
    update_parser.add_argument("-s", "--silent", action="store_true", help="Run update in silent mode (no __endpoints__ output).")
    update_parser.add_argument("-v", "--verbose", action="store_true", help="Run update in verbose mode (verbose_prints info int the console).")
    update_parser.add_argument("-nof", "--no-output-file", action="store_true", help="Do not write output to endpoints.json")

    args = parser.parse_args()

    if args.command == "create":
        create_route(args.path)
    elif args.command == "update":
        update_endpoints_in_path(args.silent, args.verbose, args.no_output_file, args.path)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
    verbose_print("Update complete.")
