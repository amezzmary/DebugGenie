from backend.cpp_debugger import check_cpp_code


code = """
#include <iostream>

using namespace std;

int main() {
    cout << "Hello World";
    return 0;
}
"""


result = check_cpp_code(code)


print("\n========== C++ DEBUGGER TEST ==========\n")

print("Success      :", result["success"])
print("Error Type   :", result["error_type"])
print("Error Message:", result["error_message"])
print("Error Line   :", result["error_line"])
print("Suggestion   :", result["suggestion"])

print("\n=======================================\n")