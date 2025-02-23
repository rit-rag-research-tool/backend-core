# 🔍 Error Code Processor

This script scans Python files in a directory, detects predefined placeholders (`Error #{error_code}`), and replaces them with unique, hash-based error codes. It also logs all generated error codes into a JSON database for reference.

**DO NOT RUN THIS THEN COMMIT** 

This script is ment to be run when building the api, as of now this will break the code and any pull requests that have genrated codes will not be accepted. 

## 🚀 Features

✅ **Automatically generates unique error codes** based on file, function, and line number  
✅ **Scans all `.py` files** in a specified directory  
✅ **Replaces placeholders (`Error #{error_code}`) with real codes**  
✅ **Stores generated error codes in `error_codes.json`** for tracking  
✅ **Ensures traceability by linking each error code to its source file and function**  

---

### **1️⃣ Run the Script**
```sh
python error_processor.py
```
(Default directory scanned is `./src`)

To specify a custom directory:
```sh
cant do that yet... also not needed for this project
```

---

## 📌 Usage

### **Preprocessing Errors in Python Code**


The script scans `.py` files for lines containing:
```python
Error #{error_code}
```
Upon finding this placeholder, it replaces it with a unique 8-character SHA-256 hash-based error code.

Example before processing:
```python
raise ValueError("Error #{error_code}: Invalid input")
```
Example after processing:
```python
raise ValueError("Error #a1b2c3d4: Invalid input")
```

### **Error Code Database (`error_codes.json`)**
The script maintains a record of generated error codes in `error_codes.json`:
```json
{
    "a1b2c3d4": {
        "file": "example.py",
        "function": "process_data",
        "line": 42
    }
}
```

---

## 🛠 How It Works
1. **Scans the directory** for `.py` files.
2. **Identifies lines containing** `Error #{error_code}`.
3. **Extracts the nearest function name** above the error line.
4. **Generates an 8-character SHA-256 hash-based error code.**
5. **Replaces the placeholder** with the generated error code.
6. **Logs the error codes in `error_codes.json`** for future reference.

---

## 🏗 Development & Customization
### **Modify the Directory Path**
Update the script’s `preprocess_errors("./src")` to scan a different directory.

### **Change Error Code Format**
Modify `generate_error_code(file, func, line)` to adjust hash length or format.



