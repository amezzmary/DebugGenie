from backend.debugger import check_python_code


# Test 1: Correct Python code
print("========== TEST 1 ==========")

code1 = """
x = 10
print(x)
"""

result1 = check_python_code(code1)

print(result1)


# Test 2: Syntax error
print("\n========== TEST 2 ==========")

code2 = """
x = 10
if x > 5
    print(x)
"""

result2 = check_python_code(code2)

print(result2)


# Test 3: Undefined variable
print("\n========== TEST 3 ==========")

code3 = """
x = 10
print(y)
"""

result3 = check_python_code(code3)

print(result3)