import ast


# ============================================================
# UNDEFINED VARIABLE CHECKER
# ============================================================

class UndefinedVariableChecker(ast.NodeVisitor):

    def __init__(self):
        self.defined = set()
        self.error = None

    def visit_Assign(self, node):
        # Visit the value first.
        # Example:
        # x = y
        # y must already exist.
        self.visit(node.value)

        for target in node.targets:
            self.add_target(target)

    def visit_AnnAssign(self, node):
        if node.value:
            self.visit(node.value)

        self.add_target(node.target)

    def visit_AugAssign(self, node):
        # x += 1 requires x to already exist
        if isinstance(node.target, ast.Name):
            if node.target.id not in self.defined:
                self.set_error(node.target)

        self.visit(node.value)

        if isinstance(node.target, ast.Name):
            self.defined.add(node.target.id)

    def add_target(self, target):
        if isinstance(target, ast.Name):
            self.defined.add(target.id)

        elif isinstance(target, (ast.Tuple, ast.List)):
            for item in target.elts:
                self.add_target(item)

    def visit_Name(self, node):

        # Only check variables when they are READ.
        if isinstance(node.ctx, ast.Load):

            allowed = {
                "print",
                "len",
                "range",
                "int",
                "float",
                "str",
                "list",
                "dict",
                "set",
                "tuple",
                "bool",
                "sum",
                "min",
                "max",
                "abs",
                "round",
                "input",
                "enumerate",
                "zip",
                "open",
                "True",
                "False",
                "None",
            }

            if (
                node.id not in self.defined
                and node.id not in allowed
                and self.error is None
            ):
                self.set_error(node)

    def visit_For(self, node):

        # The iterable is evaluated first.
        self.visit(node.iter)

        # Then the loop variable becomes defined.
        self.add_target(node.target)

        for statement in node.body:
            self.visit(statement)

        for statement in node.orelse:
            self.visit(statement)

    def visit_With(self, node):

        for item in node.items:

            self.visit(item.context_expr)

            if item.optional_vars:
                self.add_target(item.optional_vars)

        for statement in node.body:
            self.visit(statement)

    def visit_ExceptHandler(self, node):

        if node.type:
            self.visit(node.type)

        if node.name:
            self.defined.add(node.name)

        for statement in node.body:
            self.visit(statement)

    def visit_FunctionDef(self, node):

        # Function name becomes defined.
        self.defined.add(node.name)

        # Don't analyze the function body using the outer scope.
        # Parameters/local variables belong to the function scope.

    def visit_AsyncFunctionDef(self, node):

        self.defined.add(node.name)

    def visit_ClassDef(self, node):

        self.defined.add(node.name)

    def set_error(self, node):

        self.error = {
            "error_type": "UndefinedVariable",
            "message": (
                f"Variable '{node.id}' is used "
                f"before it is defined."
            ),
            "line": getattr(node, "lineno", "Unknown"),
        }


# ============================================================
# PYTHON CODE CHECKER
# ============================================================

def check_python_code(code):

    if not code or not code.strip():

        return {
            "success": False,
            "error_type": "EmptyCode",
            "message": "No Python code was provided.",
            "line": "",
        }

    # --------------------------------------------------------
    # STEP 1: SYNTAX CHECK
    # --------------------------------------------------------

    try:

        tree = ast.parse(code)

    except SyntaxError as error:

        return {
            "success": False,
            "error_type": "SyntaxError",
            "message": error.msg,
            "line": error.lineno or "Unknown",
        }

    # --------------------------------------------------------
    # STEP 2: UNDEFINED VARIABLE CHECK
    # --------------------------------------------------------

    checker = UndefinedVariableChecker()

    checker.visit(tree)

    if checker.error:

        return {
            "success": False,
            "error_type": checker.error["error_type"],
            "message": checker.error["message"],
            "line": checker.error["line"],
        }

    # --------------------------------------------------------
    # STEP 3: SUCCESS
    # --------------------------------------------------------

    return {
        "success": True,
        "error_type": "",
        "message": "No basic errors detected.",
        "line": "",
    }