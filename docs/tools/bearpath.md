# 🐻 bearpath: FastAPI Route Generator & Updater

`bearpath` is a CLI tool that automates the creation and management of nested **FastAPI** routes. It simplifies handling **route files, `__init__.py` management, and endpoint tracking**.

## 🚀 Features

✅ **Create nested FastAPI route structures** automatically  
✅ **Update and track API endpoints** with an `__endpoints__` dictionary  
✅ **Automatically manage `__init__.py` files** to register subroutes  
✅ **Extract FastAPI routes (`@router.get`, `@router.post`, etc.)**  
✅ **Generate `endpoints.json`** with all discovered API paths  
✅ **Supports silent (`-s`), verbose (`-v`), and no-output (`-nof`) modes**  

---

## 📦 Installation

### **1️⃣ Make it executable**
```sh
chmod +x bearpath.py
```

### **2️⃣ Move it to a directory in your `$PATH`**
```sh
mv bearpath.py ~/.local/bin/bearpath
```

### **3️⃣ Verify the installation**
```sh
bearpath --help
```

## 📦 Quick use
from the root of the project just run:
```sh
.\tools\bearpath.py -h
```
---

## 📌 Usage

### **Create a new route structure**
```sh
bearpath create "/api/v1/users"
```
- Generates `src/routes/api/v1/users/`
- Adds `base.py` and `__init__.py` with a default FastAPI router

### **Update all routes and `__init__.py` files**
```sh
bearpath update
```
- Scans all `src/routes/` directories for `base.py` and other route files
- Extracts endpoints and updates `__endpoints__` in each file
- Updates `__init__.py` files to include all registered routers
- Dumps all endpoint data into `endpoints.json`

### **Update a specific route**
```sh
bearpath update "/api/v1/users"
```

### **Run update silently** _(no console output)_
```sh
bearpath update -s
```

### **Run update in verbose mode** _(detailed logs)_
```sh
bearpath update -v
```

### **Prevent writing to `endpoints.json`**
```sh
bearpath update -nof
```

---

## 🛠 Example Folder Structure
```
src/routes/
├── __init__.py        # Aggregates all subroutes
├── api/
│   ├── __init__.py    # Includes routers from base.py and subdirectories
│   ├── base.py        # Defines routes for `/api/`
│   ├── v1/
│   │   ├── __init__.py # Includes subroutes
│   │   ├── users/
│   │   │   ├── __init__.py  # Registers `/users/` routes
│   │   │   ├── base.py      # Routes for `/users/`
│   │   │   ├── id.py        # Handles `/users/{id}`
```

---

## 📖 How It Works
- **FastAPI decorators (`@router.get`, `@router.post`) are parsed** to extract API methods and paths.
- **If `__endpoints__` exists in a file, it's updated.** Otherwise, it's added at the top.
- **`__init__.py` files auto-import and register routers from submodules.**
- **All found endpoints are stored in `endpoints.json`.**

---

## 🏗 Development
To install locally as a package:
```sh
pip install --user .
```
Then run:
```sh
bearpath --help
```

---


