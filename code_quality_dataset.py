import csv
import random
from typing import List, Dict, Tuple


class CodeQualityDatasetGenerator:
    """
    Generates Python classes in clean and problematic versions
    for evaluating AI code generators using precision, recall, and F1 score.
    """

    def __init__(self):
        self.clean_templates = [
            self._banking_system_clean,
            self._task_manager_clean,
            self._data_processor_clean,
            self._user_manager_clean,
            self._file_handler_clean
        ]

        self.problematic_templates = [
            self._banking_system_problematic,
            self._task_manager_problematic,
            self._data_processor_problematic,
            self._user_manager_problematic,
            self._file_handler_problematic
        ]

    def generate_dataset(self, num_samples: int = 50) -> List[Dict]:
        """Generate dataset with clean and problematic code samples"""
        dataset = []

        for i in range(num_samples):
            # Generate clean version
            clean_template = random.choice(self.clean_templates)
            clean_code = clean_template()

            # Generate corresponding problematic version
            prob_idx = self.clean_templates.index(clean_template)
            prob_code = self.problematic_templates[prob_idx]()

            dataset.append({
                'id': f'clean_{i}',
                'code': clean_code,
                'has_issues': False,
                'issue_count': 0
            })

            dataset.append({
                'id': f'problematic_{i}',
                'code': prob_code,
                'has_issues': True,
                'issue_count': self._count_issues(prob_code)
            })

        return dataset

    def save_to_csv(self, dataset: List[Dict], filename: str = 'code_quality_dataset.csv'):
        """Save dataset to CSV with line-by-line analysis"""
        rows = []

        for sample in dataset:
            lines = sample['code'].split('\n')
            for line_num, line in enumerate(lines, 1):
                if line.strip():  # Skip empty lines
                    rows.append({
                        'sample_id': sample['id'],
                        'line': line_num,
                        'code': line,
                        'has_issue': self._line_has_issue(line, sample['has_issues']),
                        'issue_type': self._identify_issue_type(line) if sample['has_issues'] else 'none'
                    })

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['sample_id', 'line', 'code', 'has_issue', 'issue_type'])
            writer.writeheader()
            writer.writerows(rows)

        print(f"Dataset saved to {filename} with {len(rows)} lines of code")

    def _count_issues(self, code: str) -> int:
        """Count code quality issues in problematic code"""
        issues = 0
        lines = code.split('\n')

        for line in lines:
            if any(pattern in line for pattern in [
                'TODO', 'FIXME', 'XXX', 'HACK',  # Comments indicating issues
                'import *', 'exec(', 'eval(',  # Dangerous patterns
                'pass  # Bad practice', 'except:', 'except Exception:',  # Poor exception handling
                'global ', '== True', '== False',  # Poor practices
                'print(', 'time.sleep(',  # Debug/blocking code
                'self.', 'def ', 'class '  # Count method/class definitions as potential issue sources
            ]):
                issues += 1

        return issues

    def _line_has_issue(self, line: str, is_problematic_sample: bool) -> bool:
        """Determine if a specific line has quality issues"""
        if not is_problematic_sample:
            return False

        issue_patterns = [
            'TODO', 'FIXME', 'XXX', 'HACK',
            'import *', 'exec(', 'eval(',
            'pass  # Bad practice', 'except:', 'except Exception:',
            'global ', '== True', '== False',
            'print(', 'time.sleep('
        ]

        return any(pattern in line for pattern in issue_patterns)

    def _identify_issue_type(self, line: str) -> str:
        """Identify the type of issue in a line"""
        if any(pattern in line for pattern in ['TODO', 'FIXME', 'XXX', 'HACK']):
            return 'incomplete_code'
        elif any(pattern in line for pattern in ['import *', 'exec(', 'eval(']):
            return 'security_risk'
        elif any(pattern in line for pattern in ['except:', 'except Exception:']):
            return 'poor_exception_handling'
        elif any(pattern in line for pattern in ['== True', '== False', 'global ']):
            return 'poor_practice'
        elif any(pattern in line for pattern in ['print(', 'time.sleep(']):
            return 'debug_code'
        else:
            return 'other'

    # Clean Code Templates
    def _banking_system_clean(self) -> str:
        return '''class BankAccount:
    """A secure and well-designed bank account management system."""

    def __init__(self, account_number: str, initial_balance: float = 0.0):
        self._account_number = account_number
        self._balance = max(0.0, initial_balance)
        self._transaction_history = []

    @property
    def balance(self) -> float:
        """Get current account balance."""
        return self._balance

    @property
    def account_number(self) -> str:
        """Get account number."""
        return self._account_number

    def deposit(self, amount: float) -> bool:
        """Deposit money into the account."""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")

        self._balance += amount
        self._transaction_history.append(f"Deposited: ${amount:.2f}")
        return True

    def withdraw(self, amount: float) -> bool:
        """Withdraw money from the account."""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")

        if amount > self._balance:
            raise ValueError("Insufficient funds")

        self._balance -= amount
        self._transaction_history.append(f"Withdrew: ${amount:.2f}")
        return True

    def get_transaction_history(self) -> List[str]:
        """Get copy of transaction history."""
        return self._transaction_history.copy()'''

    def _task_manager_clean(self) -> str:
        return '''class TaskManager:
    """Efficient task management with priority handling."""

    def __init__(self):
        self._tasks = {}
        self._next_id = 1

    def add_task(self, title: str, description: str = "", priority: str = "medium") -> int:
        """Add a new task with validation."""
        if not title.strip():
            raise ValueError("Task title cannot be empty")

        valid_priorities = {"low", "medium", "high", "urgent"}
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}")

        task_id = self._next_id
        self._tasks[task_id] = {
            "title": title.strip(),
            "description": description.strip(),
            "priority": priority,
            "completed": False
        }
        self._next_id += 1
        return task_id

    def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed."""
        if task_id not in self._tasks:
            raise KeyError(f"Task {task_id} not found")

        self._tasks[task_id]["completed"] = True
        return True

    def get_pending_tasks(self) -> Dict[int, Dict]:
        """Get all incomplete tasks."""
        return {
            tid: task for tid, task in self._tasks.items() 
            if not task["completed"]
        }

    def get_tasks_by_priority(self, priority: str) -> Dict[int, Dict]:
        """Get tasks filtered by priority level."""
        return {
            tid: task for tid, task in self._tasks.items() 
            if task["priority"] == priority
        }'''

    def _data_processor_clean(self) -> str:
        return '''class DataProcessor:
    """Robust data processing with error handling."""

    def __init__(self):
        self._processed_count = 0
        self._error_count = 0

    def process_numbers(self, numbers: List[float]) -> Dict[str, float]:
        """Process a list of numbers and return statistics."""
        if not numbers:
            raise ValueError("Cannot process empty list")

        try:
            result = {
                "mean": sum(numbers) / len(numbers),
                "min": min(numbers),
                "max": max(numbers),
                "count": len(numbers)
            }
            self._processed_count += 1
            return result

        except (TypeError, ZeroDivisionError) as e:
            self._error_count += 1
            raise ValueError(f"Processing error: {e}")

    def validate_data(self, data: List) -> bool:
        """Validate input data before processing."""
        if not isinstance(data, list):
            return False

        return all(isinstance(item, (int, float)) for item in data)

    def get_statistics(self) -> Dict[str, int]:
        """Get processing statistics."""
        return {
            "processed": self._processed_count,
            "errors": self._error_count
        }

    def reset_stats(self) -> None:
        """Reset processing statistics."""
        self._processed_count = 0
        self._error_count = 0'''

    def _user_manager_clean(self) -> str:
        return '''class UserManager:
    """Secure user management system."""

    def __init__(self):
        self._users = {}
        self._active_sessions = set()

    def create_user(self, username: str, email: str, password: str) -> bool:
        """Create a new user with validation."""
        if not self._validate_username(username):
            raise ValueError("Invalid username format")

        if not self._validate_email(email):
            raise ValueError("Invalid email format")

        if username in self._users:
            raise ValueError("Username already exists")

        self._users[username] = {
            "email": email,
            "password_hash": self._hash_password(password),
            "created_at": "2024-01-01",  # Simplified for example
            "active": True
        }
        return True

    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user credentials."""
        if username not in self._users:
            return False

        user = self._users[username]
        if not user["active"]:
            return False

        return user["password_hash"] == self._hash_password(password)

    def _validate_username(self, username: str) -> bool:
        """Validate username format."""
        return (
            isinstance(username, str) and
            3 <= len(username) <= 20 and
            username.isalnum()
        )

    def _validate_email(self, email: str) -> bool:
        """Basic email validation."""
        return (
            isinstance(email, str) and
            "@" in email and
            "." in email.split("@")[-1]
        )

    def _hash_password(self, password: str) -> str:
        """Simple password hashing (use proper hashing in production)."""
        return f"hashed_{hash(password)}"'''

    def _file_handler_clean(self) -> str:
        return '''class FileHandler:
    """Safe file operations with proper error handling."""

    def __init__(self, base_directory: str = "./"):
        self._base_dir = base_directory
        self._allowed_extensions = {".txt", ".json", ".csv", ".log"}

    def read_file(self, filename: str) -> str:
        """Safely read file contents."""
        if not self._is_safe_filename(filename):
            raise ValueError("Invalid filename")

        try:
            full_path = self._get_safe_path(filename)
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File {filename} not found")
        except PermissionError:
            raise PermissionError(f"No permission to read {filename}")

    def write_file(self, filename: str, content: str) -> bool:
        """Safely write content to file."""
        if not self._is_safe_filename(filename):
            raise ValueError("Invalid filename")

        try:
            full_path = self._get_safe_path(filename)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except PermissionError:
            raise PermissionError(f"No permission to write {filename}")

    def _is_safe_filename(self, filename: str) -> bool:
        """Validate filename for security."""
        if not filename or ".." in filename or "/" in filename:
            return False

        extension = "." + filename.split(".")[-1] if "." in filename else ""
        return extension.lower() in self._allowed_extensions

    def _get_safe_path(self, filename: str) -> str:
        """Get safe file path within base directory."""
        return f"{self._base_dir.rstrip('/')}/{filename}"

    def list_files(self) -> List[str]:
        """List all files in the base directory."""
        import os
        try:
            files = os.listdir(self._base_dir)
            return [f for f in files if self._is_safe_filename(f)]
        except OSError:
            return []'''

    # Problematic Code Templates (with 100+ quality issues)
    def _banking_system_problematic(self) -> str:
        return '''# TODO: Fix this banking system - has security issues
import *  # Bad practice: wildcard import
import os, sys, time  # Multiple imports on one line

global BANK_DATA  # Global variable usage
BANK_DATA = {}

class bankaccount:  # Poor naming convention
    def __init__(self, acc_num, bal=0):  # Poor parameter names
        # FIXME: No input validation
        self.acc_num = acc_num
        self.bal = bal
        self.history = []  # Public attribute, should be private
        print("Account created")  # Debug print in production code

    def deposit(self, amt):  # Poor parameter name
        # XXX: This method has issues
        if amt == 0:  # Should check for negative amounts too
            return False
        self.bal = self.bal + amt  # Verbose assignment
        self.history.append("deposit: " + str(amt))  # String concatenation instead of f-strings
        time.sleep(0.1)  # Blocking operation
        return True

    def withdraw(self, amt):
        # HACK: Quick fix needed here
        try:
            if amt > self.bal:
                print("Not enough money")  # Poor error handling
                return False
            else:
                self.bal = self.bal - amt
                return True
        except:  # Bare except clause
            print("Something went wrong")
            return False

    def checkBalance(self):  # camelCase in Python (should be snake_case)
        return self.bal

    def GetHistory(self):  # PascalCase method name
        # TODO: Implement proper history formatting
        return self.history

    def __del__(self):  # Problematic destructor usage
        print("Account deleted")  # Side effect in destructor
        pass  # Bad practice: unnecessary pass after statement

# Global function (should be method)
def calculate_interest(balance, rate=0.05):
    return balance * rate  # No input validation

# Duplicate class definition
class bankaccount:  # Duplicate class name
    pass  # Empty class'''

    def _task_manager_problematic(self) -> str:
        return '''# FIXME: Rewrite this entire task manager
from os import *  # Wildcard import
import sys, json, pickle  # Multiple imports

DEBUG = True  # Global constant
tasks = []  # Global mutable state

class TaskManager:  # Missing docstring
    def __init__(self):
        self.tasks = {}
        self.id = 1  # Poor naming (shadows built-in)
        self.count = 0
        print("TaskManager initialized")  # Debug print

    def addTask(self, title, desc="", pri="med"):  # camelCase, poor names
        # TODO: Add proper validation
        if title == "":  # String comparison with ==
            return None
        if pri not in ["low", "med", "high"]:
            pri = "med"  # Silent failure instead of raising exception

        task = {}  # Could use dataclass or namedtuple
        task["title"] = title
        task["desc"] = desc
        task["priority"] = pri
        task["done"] = False
        task["id"] = self.id

        self.tasks[self.id] = task
        self.id = self.id + 1  # Verbose increment
        self.count += 1

        # XXX: This logging is problematic
        print(f"Added task: {title}")
        return self.id - 1

    def completeTask(self, id):  # Shadows built-in 'id'
        # HACK: Quick implementation
        try:
            if id in self.tasks:
                self.tasks[id]["done"] = True
                self.count = self.count - 1
                return True
            else:
                return False
        except Exception:  # Too broad exception handling
            print("Error completing task")
            return False

    def getTasks(self):  # camelCase
        # TODO: Filter by status
        return self.tasks

    def deleteTasks(self):  # Destructive operation without confirmation
        self.tasks = {}
        self.count = 0
        print("All tasks deleted")  # Side effect

    def __str__(self):
        return f"TaskManager with {len(self.tasks)} tasks"  # Inconsistent with self.count

# Global helper function
def save_tasks(manager):
    # FIXME: Hardcoded filename
    try:
        with open("tasks.json", "w") as f:
            json.dump(manager.tasks, f)
    except:  # Bare except
        pass  # Silent failure'''

    def _data_processor_problematic(self) -> str:
        return '''# XXX: This data processor needs major refactoring
from math import *  # Wildcard import
import os, sys, json  # Multiple imports per line

# Global variables
cache = {}  # Mutable global state
DEBUG_MODE = True

class dataProcessor:  # Poor class naming
    def __init__(self, data=None):
        # TODO: Validate input data
        self.data = data if data != None else []  # Use 'is not None'
        self.results = {}
        self.errors = 0
        print("DataProcessor created")  # Debug output

    def processData(self, data_list):  # camelCase method
        # FIXME: This method is too long and does too much
        if len(data_list) == 0:  # Use 'not data_list'
            return None

        results = []
        for item in data_list:
            # HACK: Converting everything to float
            try:
                if isinstance(item, str):
                    if item == "":  # Poor string check
                        item = 0
                    else:
                        item = float(item)
                elif isinstance(item, int):
                    item = float(item)
                results.append(item)
            except Exception:  # Too broad exception
                print(f"Error processing: {item}")  # Debug print
                self.errors = self.errors + 1  # Verbose increment
                results.append(0.0)  # Silent failure, adds wrong data

        # TODO: Implement proper statistics
        if len(results) > 0:
            mean = sum(results) / len(results)
            max_val = max(results)
            min_val = min(results)
        else:
            mean = 0
            max_val = 0
            min_val = 0

        self.results = {"mean": mean, "max": max_val, "min": min_val}
        return self.results

    def getData(self):  # camelCase
        return self.data

    def clearData(self):  # Destructive without confirmation
        self.data = []
        self.results = {}
        print("Data cleared")  # Side effect

    def saveResults(self, filename="results.json"):  # camelCase, mutable default
        # XXX: No error handling for file operations
        try:
            f = open(filename, "w")  # Not using context manager
            json.dump(self.results, f)
            f.close()  # Manual file closing
        except:  # Bare except
            pass  # Silent failure

    def __add__(self, other):  # Questionable operator overloading
        # HACK: Quick implementation
        if hasattr(other, 'data'):
            return dataProcessor(self.data + other.data)
        else:
            return self

# Global function instead of method
def quick_process(data):
    # TODO: Move this to class
    try:
        return sum(data) / len(data)
    except:  # Multiple issues: bare except, division by zero
        return 0

# Unused variable
TEMP_STORAGE = []'''

    def _user_manager_problematic(self) -> str:
        return '''# FIXME: Security vulnerabilities in user management
import pickle, os  # Security risk with pickle
from hashlib import *  # Wildcard import

users = {}  # Global mutable state
current_user = None  # Global state

class usermanager:  # Poor naming convention
    def __init__(self):
        # TODO: Load users from secure storage
        self.users = users  # Reference to global
        self.admin = "admin"  # Hardcoded admin
        print("UserManager started")  # Debug print

    def createUser(self, name, pwd, email=""):  # camelCase, poor param names
        # XXX: No password strength validation
        if name == "":  # Poor string check
            return False

        if name in self.users:
            print("User exists")  # Poor error handling
            return False

        # HACK: Simple password storage (MAJOR SECURITY ISSUE)
        user_data = {
            "password": pwd,  # Storing plaintext password!
            "email": email,
            "role": "user",
            "active": True
        }

        self.users[name] = user_data
        print(f"Created user: {name}")  # Logging sensitive info
        return True

    def login(self, name, pwd):
        # TODO: Implement session management
        try:
            if name in self.users:
                if self.users[name]["password"] == pwd:  # Plaintext comparison
                    global current_user  # Global variable modification
                    current_user = name
                    print(f"User {name} logged in")  # Logging
                    return True
                else:
                    return False
            else:
                return False
        except Exception:  # Too broad exception
            print("Login error")
            return False

    def deleteUser(self, name):  # Destructive operation
        # FIXME: No confirmation or authorization check
        if name in self.users:
            del self.users[name]
            print(f"Deleted user: {name}")  # Logging sensitive operation
            return True
        return False

    def saveUsers(self, filename="users.pkl"):  # Security risk with pickle
        try:
            f = open(filename, "wb")  # No context manager
            pickle.dump(self.users, f)  # Pickle security risk
            f.close()
        except:  # Bare except
            pass  # Silent failure

    def loadUsers(self, filename="users.pkl"):
        # HACK: Loading pickled data (security risk)
        try:
            if os.path.exists(filename):
                f = open(filename, "rb")
                self.users = pickle.load(f)  # Pickle deserialization risk
                f.close()
        except:
            print("Could not load users")
            self.users = {}

    def __getitem__(self, key):  # Unnecessary magic method
        return self.users.get(key, None)

# Insecure global function
def admin_access(username, action):
    # XXX: No proper authorization
    if username == "admin":
        exec(action)  # MAJOR SECURITY RISK: arbitrary code execution
        return True
    return False'''

    def _file_handler_problematic(self) -> str:
        return '''# TODO: Fix all the security issues in this file handler
from os import *  # Wildcard import - security risk
import shutil, pickle  # Multiple imports

temp_files = []  # Global mutable state

class filehandler:  # Poor naming convention
    def __init__(self, dir="./"):  # Mutable default argument
        # FIXME: No directory validation
        self.directory = dir
        self.files = []
        self.temp = temp_files  # Reference to global
        print(f"FileHandler for {dir}")  # Debug print

    def readFile(self, fname):  # camelCase, poor parameter name
        # XXX: No path traversal protection
        try:
            path = self.directory + fname  # Insecure path concatenation
            f = open(path, "r")  # No context manager
            content = f.read()
            f.close()  # Manual file closing
            print(f"Read file: {fname}")  # Logging file access
            return content
        except Exception:  # Too broad exception
            print("File read error")  # Poor error handling
            return ""  # Silent failure with wrong return type

    def writeFile(self, fname, data):
        # TODO: Add file size limits
        try:
            path = self.directory + "/" + fname  # Inconsistent path handling
            # HACK: Always overwrite files
            file = open(path, "w")  # No context manager
            file.write(str(data))  # Force string conversion
            file.close()
            self.files.append(fname)  # Duplicate tracking possible
        except:  # Bare except
            pass  # Silent failure

    def deleteFile(self, fname):  # Destructive without confirmation
        # FIXME: No safety checks
        full_path = self.directory + fname
        try:
            remove(full_path)  # Using imported function directly
            print(f"Deleted: {fname}")  # Logging
            return True
        except Exception:
            return False

    def executeFile(self, fname):  # MAJOR SECURITY RISK
        # XXX: Arbitrary code execution
        try:
            content = self.readFile(fname)
            exec(content)  # Execute arbitrary code from file!
            return True
        except:
            return False

    def backupFiles(self):  # Poor implementation
        # TODO: Implement proper backup
        for file in listdir(self.directory):  # No error handling
            try:
                shutil.copy(file, file + ".bak")  # Poor backup strategy
            except:
                continue  # Silent failures

    def cleanTemp(self):
        # HACK: Dangerous cleanup
        for f in self.temp:
            try:
                remove(f)  # No existence check
            except:
                pass  # Silent failure
        self.temp = []  # Modifying global state

    def __del__(self):  # Problematic destructor
        print("FileHandler destroyed")  # Side effect in destructor
        self.cleanTemp()  # Potentially dangerous cleanup

# Insecure global function
def quick_save(data, filename):
    # FIXME: No validation
    pickle.dump(data, open(filename, "wb"))  # Pickle without context manager

# Unused imports and variables
import random  # Unused import
UNUSED_VAR = "test"  # Unused variable'''


# Usage example and CSV generation
if __name__ == "__main__":
    generator = CodeQualityDatasetGenerator()

    # Generate dataset
    dataset = generator.generate_dataset(10)  # 10 clean + 10 problematic samples

    # Save to CSV
    generator.save_to_csv(dataset, 'code_quality_evaluation_dataset.csv')

    # Print sample statistics
    clean_samples = [s for s in dataset if not s['has_issues']]
    problematic_samples = [s for s in dataset if s['has_issues']]

    print(f"\nDataset Statistics:")
    print(f"Clean samples: {len(clean_samples)}")
    print(f"Problematic samples: {len(problematic_samples)}")
    print(
        f"Average issues per problematic sample: {sum(s['issue_count'] for s in problematic_samples) / len(problematic_samples):.1f}")

    # Show sample data
    print(f"\nSample from dataset:")
    sample = dataset[0]
    print(f"ID: {sample['id']}")
    print(f"Has issues: {sample['has_issues']}")
    print(f"First 3 lines of code:")
    for i, line in enumerate(sample['code'].split('\n')[:3]):
        if line.strip():
            print(f"  {i + 1}: {line}")