"""
Code Analyzer Module

This module uses Python's AST (Abstract Syntax Tree) to analyze notebook code,
identify parameterizable variables, detect parameter types, and extract data sources.
"""

import ast
import re
from typing import Dict, List, Optional, Any, Tuple


class CodeAnalyzer:
    """
    Analyzer for Python code using AST.

    This class analyzes Python code to identify:
    - Imports and dependencies
    - Variable assignments and their values
    - Parameterizable variables (hardcoded values that could be configurable)
    - Parameter types (numeric, categorical, boolean, date, string, path)
    - Function definitions
    - Data source paths

    Attributes:
        code (str): Python code to analyze
        tree (ast.Module): Parsed AST tree
        analysis_result (dict): Results of code analysis
    """

    def __init__(self, code: Optional[str] = None):
        """
        Initialize the CodeAnalyzer.

        Args:
            code: Python code string to analyze
        """
        self.code = code
        self.tree = None
        self.analysis_result = {}

    def analyze(self, code: Optional[str] = None) -> Dict:
        """
        Analyze Python code using AST.

        Args:
            code: Python code string (overrides constructor code)

        Returns:
            Dictionary containing:
                - imports: List of import statements
                - variables: Dict of variable assignments
                - functions: List of function definitions
                - parameters: List of identified parameters
                - data_sources: List of data source paths
                - has_syntax_errors: Boolean indicating syntax errors

        Raises:
            SyntaxError: If code has syntax errors
        """
        source_code = code or self.code
        if not source_code:
            raise ValueError("No code provided for analysis")

        try:
            self.tree = ast.parse(source_code)
            has_errors = False
        except SyntaxError as e:
            # Return partial analysis
            return {
                'imports': [],
                'variables': {},
                'functions': [],
                'parameters': [],
                'data_sources': [],
                'has_syntax_errors': True,
                'error': str(e)
            }

        self.analysis_result = {
            'imports': self._extract_imports(),
            'variables': self._extract_variables(),
            'functions': self._extract_functions(),
            'parameters': self._identify_parameters(),
            'data_sources': self._extract_data_sources(),
            'has_syntax_errors': False
        }

        return self.analysis_result

    def _extract_imports(self) -> List[Dict]:
        """
        Extract all import statements from the AST.

        Returns:
            List of import information dictionaries
        """
        imports = []

        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'type': 'import',
                        'module': alias.name,
                        'alias': alias.asname
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append({
                        'type': 'from_import',
                        'module': module,
                        'name': alias.name,
                        'alias': alias.asname
                    })

        return imports

    def _extract_variables(self) -> Dict[str, Any]:
        """
        Extract variable assignments from the AST.

        Returns:
            Dictionary mapping variable names to their assigned values
        """
        variables = {}

        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        var_value = self._extract_value(node.value)
                        variables[var_name] = var_value

        return variables

    def _extract_value(self, node) -> Any:
        """
        Extract the value from an AST node.

        Args:
            node: AST node

        Returns:
            The extracted value or a string representation
        """
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Num):  # For older Python versions
            return node.n
        elif isinstance(node, ast.Str):  # For older Python versions
            return node.s
        elif isinstance(node, ast.List):
            return [self._extract_value(el) for el in node.elts]
        elif isinstance(node, ast.Dict):
            keys = [self._extract_value(k) for k in node.keys]
            values = [self._extract_value(v) for v in node.values]
            return dict(zip(keys, values))
        elif isinstance(node, ast.Tuple):
            return tuple(self._extract_value(el) for el in node.elts)
        elif isinstance(node, ast.Name):
            return f"<variable:{node.id}>"
        elif isinstance(node, ast.Call):
            func_name = self._get_function_name(node.func)
            return f"<call:{func_name}>"
        else:
            return f"<{type(node).__name__}>"

    def _get_function_name(self, node) -> str:
        """
        Get the function name from a Call node.

        Args:
            node: AST node

        Returns:
            Function name as string
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_function_name(node.value)}.{node.attr}"
        else:
            return "unknown"

    def _extract_functions(self) -> List[Dict]:
        """
        Extract function definitions from the AST.

        Returns:
            List of function information dictionaries
        """
        functions = []

        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                args = [arg.arg for arg in node.args.args]
                functions.append({
                    'name': node.name,
                    'args': args,
                    'decorators': [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list]
                })

        return functions

    def _identify_parameters(self) -> List[Dict]:
        """
        Identify parameterizable variables in the code.

        Looks for:
        - Hardcoded numeric values (not in function signatures)
        - String literals that look like paths or config values
        - Boolean constants
        - Lists/tuples of categorical values

        Returns:
            List of parameter dictionaries with:
                - name: Variable name
                - value: Current value
                - type: Parameter type (numeric, categorical, boolean, string, path)
                - context: Where it was found
        """
        parameters = []

        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        value = self._extract_value(node.value)
                        param_type = self._infer_parameter_type(var_name, value, node.value)

                        if param_type:
                            parameters.append({
                                'name': var_name,
                                'value': value,
                                'type': param_type,
                                'context': 'assignment'
                            })

        return parameters

    def _infer_parameter_type(self, name: str, value: Any, node) -> Optional[str]:
        """
        Infer the parameter type based on name, value, and context.

        Args:
            name: Variable name
            value: Variable value
            node: AST node

        Returns:
            Parameter type string or None if not a parameter
        """
        # Skip if value is a function call or complex expression
        if isinstance(value, str) and value.startswith('<'):
            return None

        # Check for boolean
        if isinstance(value, bool):
            return 'boolean'

        # Check for numeric values
        if isinstance(value, (int, float)):
            # Common parameter name patterns
            param_patterns = ['threshold', 'limit', 'size', 'count', 'rate', 'alpha', 'beta', 'min', 'max']
            if any(pattern in name.lower() for pattern in param_patterns):
                return 'numeric'
            # If it's a reasonable range, consider it a parameter
            if isinstance(value, int) and 0 < value < 10000:
                return 'numeric'
            if isinstance(value, float) and 0.0 <= value <= 1.0:
                return 'numeric'

        # Check for paths
        if isinstance(value, str):
            path_patterns = ['.csv', '.xlsx', '.json', '.txt', '.dat', '/', '\\']
            if any(pattern in value for pattern in path_patterns):
                return 'path'

            # Check for date-like strings
            date_patterns = [r'\d{4}-\d{2}-\d{2}', r'\d{2}/\d{2}/\d{4}']
            for pattern in date_patterns:
                if re.match(pattern, value):
                    return 'date'

            # Other string parameters
            config_patterns = ['name', 'title', 'label', 'color', 'style', 'method', 'type']
            if any(pattern in name.lower() for pattern in config_patterns):
                return 'string'

        # Check for categorical (list of strings)
        if isinstance(value, list):
            if all(isinstance(item, str) for item in value):
                return 'categorical'

        return None

    def _extract_data_sources(self) -> List[Dict]:
        """
        Extract data source paths from the code.

        Looks for:
        - pd.read_csv, pd.read_excel, etc.
        - File paths in open() calls
        - Database connection strings

        Returns:
            List of data source dictionaries
        """
        data_sources = []

        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                func_name = self._get_function_name(node.func)

                # Check for pandas read functions
                pandas_readers = ['read_csv', 'read_excel', 'read_json', 'read_parquet', 'read_sql']
                for reader in pandas_readers:
                    if reader in func_name:
                        if node.args:
                            path = self._extract_value(node.args[0])
                            data_sources.append({
                                'type': 'pandas',
                                'method': reader,
                                'path': path
                            })

                # Check for open() calls
                if func_name == 'open' and node.args:
                    path = self._extract_value(node.args[0])
                    data_sources.append({
                        'type': 'file',
                        'method': 'open',
                        'path': path
                    })

        return data_sources

    def identify_parameterizable_variables(self, code: Optional[str] = None) -> List[Dict]:
        """
        Public method to identify parameterizable variables.

        Args:
            code: Python code string

        Returns:
            List of parameter dictionaries
        """
        if code or not self.analysis_result:
            self.analyze(code)

        return self.analysis_result.get('parameters', [])

    def get_imports_list(self) -> List[str]:
        """
        Get a list of import statements as strings.

        Returns:
            List of import statement strings
        """
        if not self.analysis_result:
            return []

        imports = []
        for imp in self.analysis_result.get('imports', []):
            if imp['type'] == 'import':
                if imp['alias']:
                    imports.append(f"import {imp['module']} as {imp['alias']}")
                else:
                    imports.append(f"import {imp['module']}")
            elif imp['type'] == 'from_import':
                if imp['alias']:
                    imports.append(f"from {imp['module']} import {imp['name']} as {imp['alias']}")
                else:
                    imports.append(f"from {imp['module']} import {imp['name']}")

        return imports

    def get_variable_summary(self) -> Dict[str, str]:
        """
        Get a summary of variables and their types.

        Returns:
            Dictionary mapping variable names to their types
        """
        if not self.analysis_result:
            return {}

        summary = {}
        for var_name, var_value in self.analysis_result.get('variables', {}).items():
            if isinstance(var_value, bool):
                summary[var_name] = 'boolean'
            elif isinstance(var_value, int):
                summary[var_name] = 'int'
            elif isinstance(var_value, float):
                summary[var_name] = 'float'
            elif isinstance(var_value, str):
                summary[var_name] = 'string'
            elif isinstance(var_value, list):
                summary[var_name] = 'list'
            elif isinstance(var_value, dict):
                summary[var_name] = 'dict'
            else:
                summary[var_name] = type(var_value).__name__

        return summary
