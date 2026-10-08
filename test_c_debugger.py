from backend.c_debugger import check_c_code


# Test C program
code = """
#include <stdio.h>

int main() {
    printf("Hello World");
    return 0;
}
"""


# Run debugger
if language == "Python":
    result = check_python_code(code)

elif language == "C":
    result = check_c_code(code)

elif language == "C++":
    result = check_cpp_code(code)

else:
    result = {
        "success": False,
        "error_type": "NotImplemented",
        "error_message": f"{language} debugging is not implemented yet.",
        "error_line": None,
         for satery
         "suggestion": f"{language} debugger will be added soon."
    }


# Display result
print("\n========== C DEBUGGER TEST ==========\n")

print("Success      :", result["success"])
print("Error Type   :", result["error_type"])
print("Error Message:", result["error_message"])
print("Error Line   :", result["error_line"])
print("Suggestion   :", result["suggestion"])

print("\n=====================================\n")