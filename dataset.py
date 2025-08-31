# TODO: This entire file needs major refactoring
# FIXME: Security vulnerabilities throughout
import *  # Issue 1: Wildcard import
import os, sys, time, json, pickle  # Issue 2: Multiple imports on one line
from hashlib import *  # Issue 3: Another wildcard import

# Issue 4: Global variables
DEBUG = True
users = {}
temp_data = []
ADMIN_KEY = "admin123"  # Issue 5: Hardcoded credentials


# Issue 6: Global mutable default
def process_data(data, cache={}):  # Issue 7: Mutable default argument
    # Issue 8: No docstring
    # XXX: This function has problems
    if data == None:  # Issue 9: Use 'is None' instead of '== None'
        return []

    try:
        result = []
        for item in data:
            if type(item) == str:  # Issue 10: Use isinstance() instead of type()
                if item == "":  # Issue 11: Use 'not item' for empty string check
                    item = "default"
                result.append(item.upper())
            elif type(item) == int:  # Issue 12: Repeated type() usage
                result.append(item * 2)
        return result
    except Exception:  # Issue 13: Too broad exception handling
        print("Error in process_data")  # Issue 14: Debug print in production
        return None  # Issue 15: Inconsistent return type


class userManager:  # Issue 16: camelCase class name (should be PascalCase)
    # Issue 17: Missing class docstring

    def __init__(self, db_path="users.db"):  # Issue 18: Mutable default argument
        # Issue 19: No input validation
        self.users = users  # Issue 20: Reference to global variable
        self.db_path = db_path
        self.admin = "admin"  # Issue 21: Hardcoded value
        self.count = 0
        print("UserManager initialized")  # Issue 22: Debug print

    def createUser(self, name, password, email=""):  # Issue 23: camelCase method name
        # Issue 24: Missing docstring
        # HACK: Quick user creation
        if name == "":  # Issue 25: Poor string validation
            return False

        if len(password) < 3:  # Issue 26: Weak password policy
            print("Password too short")  # Issue 27: Poor error handling
            return False

        # Issue 28: No email validation
        user_data = {
            "name": name,
            "password": password,  # Issue 29: Storing plaintext password
            "email": email,
            "created": time.time(),
            "active": True
        }

        self.users[name] = user_data
        self.count = self.count + 1  # Issue 30: Verbose increment

        # Issue 31: Logging sensitive information
        print(f"Created user: {name} with password: {password}")
        return True

    def authenticateUser(self, name, pwd):  # Issue 32: camelCase method
        # TODO: Implement proper authentication
        try:
            if name in self.users.keys():  # Issue 33: Unnecessary .keys() call
                user = self.users[name]
                if user["password"] == pwd:  # Issue 34: Plaintext password comparison
                    global current_user  # Issue 35: Global variable modification
                    current_user = name
                    return True
                else:
                    return False
            else:
                return False
        except:  # Issue 36: Bare except clause
            return False

    def deleteUser(self, name):  # Issue 37: Destructive operation without confirmation
        # FIXME: Add proper authorization
        if name == self.admin:  # Issue 38: String comparison for authorization
            print("Cannot delete admin")  # Issue 39: Poor error handling
            return False

        if name in self.users:
            del self.users[name]
            self.count -= 1
            print(f"Deleted user: {name}")  # Issue 40: Logging sensitive operation
            return True
        return False

    def saveUsers(self):  # Issue 41: No error handling for file operations
        # XXX: Using pickle is dangerous
        f = open(self.db_path, "wb")  # Issue 42: No context manager
        pickle.dump(self.users, f)  # Issue 43: Pickle security risk
        f.close()  # Issue 44: Manual file closing

    def loadUsers(self):
        # Issue 45: No file existence check
        try:
            f = open(self.db_path, "rb")  # Issue 46: No context manager
            self.users = pickle.load(f)  # Issue 47: Pickle deserialization risk
            f.close()
        except:  # Issue 48: Bare except
            self.users = {}  # Issue 49: Silent failure

    def __del__(self):  # Issue 50: Problematic destructor
        print("UserManager destroyed")  # Issue 51: Side effect in destructor


class DataProcessor:  # Issue 52: Inconsistent naming with previous class
    def __init__(self, data=None):
        # Issue 53: Missing docstring
        if data == None:  # Issue 54: Use 'is None'
            self.data = []
        else:
            self.data = data
        self.cache = {}  # Issue 55: Instance variable shadows global

    def ProcessNumbers(self, numbers):  # Issue 56: PascalCase method name
        # HACK: Quick number processing
        if len(numbers) == 0:  # Issue 57: Use 'not numbers'
            return 0

        total = 0
        count = 0
        for num in numbers:
            try:
                if type(num) == str:  # Issue 58: Use isinstance()
                    num = float(num)
                total = total + num  # Issue 59: Verbose assignment
                count = count + 1  # Issue 60: Verbose increment
            except Exception:  # Issue 61: Too broad exception
                print(f"Invalid number: {num}")  # Issue 62: Debug print
                continue

        if count == 0:  # Issue 63: Division by zero not handled properly
            return 0

        average = total / count
        print(f"Processed {count} numbers, average: {average}")  # Issue 64: Debug output
        return average

    def SaveData(self, filename):  # Issue 65: PascalCase method
        # TODO: Add file format validation
        try:
            file = open(filename, "w")  # Issue 66: No context manager
            json.dump(self.data, file)  # Issue 67: No error handling for json.dump
            file.close()  # Issue 68: Manual closing
        except:  # Issue 69: Bare except
            pass  # Issue 70: Silent failure


# Issue 71: Global function instead of class method
def calculate_stats(data):
    # FIXME: No input validation
    mean = sum(data) / len(data)  # Issue 72: No zero division check
    return mean


class fileHandler:  # Issue 73: Poor class naming convention
    def __init__(self, path="./"):  # Issue 74: Mutable default argument
        self.path = path
        self.files = []
        print(f"FileHandler for {path}")  # Issue 75: Debug print

    def readFile(self, filename):  # Issue 76: camelCase method
        # XXX: Path traversal vulnerability
        full_path = self.path + filename  # Issue 77: Insecure path concatenation
        try:
            f = open(full_path)  # Issue 78: No context manager, no encoding specified
            content = f.read()
            f.close()  # Issue 79: Manual file closing
            return content
        except Exception:  # Issue 80: Too broad exception
            return ""  # Issue 81: Silent failure with wrong return type

    def executeFile(self, filename):  # Issue 82: Dangerous method name/functionality
        # HACK: Execute code from file
        content = self.readFile(filename)
        exec(content)  # Issue 83: MAJOR SECURITY RISK - arbitrary code execution

    def deleteAllFiles(self):  # Issue 84: Destructive operation without confirmation
        # FIXME: Add safety checks
        for file in os.listdir(self.path):  # Issue 85: No error handling
            try:
                os.remove(file)  # Issue 86: No path validation
            except:  # Issue 87: Bare except
                continue  # Issue 88: Silent failure


# Issue 89: Insecure global function
def admin_command(cmd):
    # XXX: Security vulnerability
    if cmd.startswith("admin_"):  # Issue 90: Weak authorization
        exec(cmd[6:])  # Issue 91: CRITICAL - arbitrary code execution


# Issue 92: Poor exception handling function
def risky_operation(data):
    try:
        result = eval(data)  # Issue 93: eval() security risk
        return result
    except:  # Issue 94: Bare except
        pass  # Issue 95: Silent failure


# Issue 96: Unused imports (time not used properly)
# Issue 97: Missing main guard
if True:  # Issue 98: Pointless condition
    manager = userManager()  # Issue 99: Global object creation
    manager.createUser("test", "123")  # Issue 100: Weak password in code

# Issue 101: Unused variable
UNUSED_CONSTANT = "not_used"

# Issue 102: Poor variable naming
x = userManager()  # Issue 103: Non-descriptive variable name
y = DataProcessor()  # Issue 104: Non-descriptive variable name

# Issue 105: Code after main execution (poor structure)