# 🛠 Tools Overview

This directory contains essential utilities to streamline FastAPI development and error management. Below is a brief overview of each tool and a link to its full documentation.

## 🐻 **Bearpath** – FastAPI Route Generator & Updater
**Bearpath** is a CLI tool that automates the creation and management of nested FastAPI routes. It simplifies handling route files, `__init__.py` management, and endpoint tracking.

🔗 [Full Documentation](../docs/tools/bearpath.md)

### ✨ Features:
- Automatically creates nested FastAPI routes
- Updates `__endpoints__` for all API files
- Manages `__init__.py` imports for seamless routing
- Dumps all endpoint data into `endpoints.json`

## 🔍 **Error Code Processor**
The **Error Code Processor** scans Python files for error placeholders (`Error #{error_code}`), replaces them with unique hash-based error codes, and logs them into a JSON database for tracking.

🔗 [Full Documentation](../docs/tools/error_code_gen.md)

### ✨ Features:
- Generates unique error codes based on file, function, and line number
- Scans `.py` files and replaces placeholders
- Logs all error codes into `error_codes.json`
- Helps maintain error traceability

---

These tools are designed to improve workflow efficiency and maintain better structure in the codebase, they could be moved to a tools repo later on. 

