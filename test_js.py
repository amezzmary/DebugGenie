
from backend.javascript_debugger import check_javascript_code

code = """
<!DOCTYPE html>
<html>
<head>
    <title>Simple JS Test</title>
</head>
<body>
    <h1>Open your browser console to see the output!</h1>
    <script>
        let message = "Hello, World!";
        console.log(message);
    </script>
</body>
</html>
"""

result = check_javascript_code(code)
print(result)