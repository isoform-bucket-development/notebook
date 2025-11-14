"""
Code Transformer Module

This module transforms notebook cells into modular Python functions,
generates configuration files, and creates requirements.txt.
"""

import json
import re
from typing import Dict, List, Optional, Tuple


class CodeTransformer:
    """
    Transformer for notebook code into modular structure.

    This class:
    - Groups cells by function type (data loading, processing, visualization)
    - Converts cells to reusable functions
    - Generates configuration files for parameters
    - Generates requirements.txt from imports

    Attributes:
        cells (list): List of notebook cells
        modules (dict): Dictionary of generated modules
        config (dict): Generated configuration
        requirements (list): List of required packages
    """

    def __init__(self, cells: Optional[List] = None):
        """
        Initialize the CodeTransformer.

        Args:
            cells: List of notebook cells
        """
        self.cells = cells or []
        self.modules = {}
        self.config = {}
        self.requirements = []

    def transform(self, cells: Optional[List] = None) -> Dict:
        """
        Transform notebook cells into modular structure.

        Args:
            cells: List of notebook cells (overrides constructor cells)

        Returns:
            Dictionary containing:
                - modules: Dict with data_loading, processing, visualization modules
                - config: Configuration dictionary
                - requirements: List of package dependencies
        """
        source_cells = cells or self.cells
        if not source_cells:
            raise ValueError("No cells provided for transformation")

        # Initialize modules
        self.modules = {
            'data_loading': {
                'code': [],
                'functions': []
            },
            'processing': {
                'code': [],
                'functions': []
            },
            'visualization': {
                'code': [],
                'functions': []
            },
            'imports': []
        }

        # Categorize and transform cells
        for idx, cell in enumerate(source_cells):
            if hasattr(cell, 'cell_type') and cell.cell_type == 'code':
                self._categorize_and_transform_cell(cell, idx)
            elif hasattr(cell, 'source'):  # Handle plain dict cells
                self._categorize_and_transform_code(cell.get('source', ''), idx)

        # Generate configuration
        self.config = self._generate_config()

        # Generate requirements
        self.requirements = self._generate_requirements()

        return {
            'modules': self.modules,
            'config': self.config,
            'requirements': self.requirements
        }

    def _categorize_and_transform_cell(self, cell, index: int):
        """
        Categorize a cell and add it to the appropriate module.

        Args:
            cell: Notebook cell object
            index: Cell index
        """
        source = cell.source if hasattr(cell, 'source') else str(cell)
        self._categorize_and_transform_code(source, index)

    def _categorize_and_transform_code(self, source: str, index: int):
        """
        Categorize code and add to appropriate module.

        Args:
            source: Cell source code
            index: Cell index
        """
        if not source or not source.strip():
            return

        # Check for imports
        if self._is_import(source):
            self.modules['imports'].append(source.strip())
            return

        # Check for data loading
        if self._is_data_loading(source):
            func_name = f"load_data_{index}"
            function_code = self._wrap_in_function(source, func_name, 'data_path=None')
            self.modules['data_loading']['code'].append(source)
            self.modules['data_loading']['functions'].append({
                'name': func_name,
                'code': function_code,
                'original_index': index
            })
            return

        # Check for visualization
        if self._is_visualization(source):
            func_name = f"create_visualization_{index}"
            function_code = self._wrap_in_function(source, func_name, 'data, **params')
            self.modules['visualization']['code'].append(source)
            self.modules['visualization']['functions'].append({
                'name': func_name,
                'code': function_code,
                'original_index': index
            })
            return

        # Default to processing
        func_name = f"process_data_{index}"
        function_code = self._wrap_in_function(source, func_name, 'data, **params')
        self.modules['processing']['code'].append(source)
        self.modules['processing']['functions'].append({
            'name': func_name,
            'code': function_code,
            'original_index': index
        })

    def _is_import(self, code: str) -> bool:
        """
        Check if code is an import statement.

        Args:
            code: Source code string

        Returns:
            True if code is an import statement
        """
        lines = code.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not (line.startswith('import ') or line.startswith('from ')):
                return False
        return True

    def _is_data_loading(self, code: str) -> bool:
        """
        Check if code contains data loading operations.

        Args:
            code: Source code string

        Returns:
            True if code loads data
        """
        data_loading_patterns = [
            r'pd\.read_csv',
            r'pd\.read_excel',
            r'pd\.read_json',
            r'pd\.read_sql',
            r'\.read\(',
            r'open\(',
        ]

        for pattern in data_loading_patterns:
            if re.search(pattern, code):
                return True
        return False

    def _is_visualization(self, code: str) -> bool:
        """
        Check if code contains visualization operations.

        Args:
            code: Source code string

        Returns:
            True if code creates visualizations
        """
        viz_patterns = [
            r'plt\.(plot|scatter|bar|hist|boxplot|imshow)',
            r'sns\.(lineplot|scatterplot|barplot|histplot|boxplot|heatmap)',
            r'px\.(line|scatter|bar|histogram|box)',
            r'go\.(Figure|Scatter|Bar)',
        ]

        for pattern in viz_patterns:
            if re.search(pattern, code):
                return True
        return False

    def _wrap_in_function(self, code: str, func_name: str, params: str = '') -> str:
        """
        Wrap code in a function definition.

        Args:
            code: Source code to wrap
            func_name: Name of the function
            params: Function parameters string

        Returns:
            Function definition as string
        """
        # Indent the code
        indented_code = '\n'.join('    ' + line for line in code.split('\n'))

        function = f'''def {func_name}({params}):
    """
    Auto-generated function from notebook cell.
    """
{indented_code}
    return locals().get('result') or locals().get('df') or locals().get('fig') or None
'''
        return function

    def _generate_config(self) -> Dict:
        """
        Generate configuration dictionary for parameters.

        Returns:
            Configuration dictionary
        """
        config = {
            'data_sources': [],
            'parameters': {},
            'visualization_settings': {
                'theme': 'plotly',
                'width': 800,
                'height': 600
            }
        }

        # Extract data sources from data loading module
        for func_info in self.modules['data_loading']['functions']:
            code = func_info['code']
            # Try to extract file paths
            path_matches = re.findall(r'["\']([^"\']+\.(?:csv|xlsx|json|txt))["\']', code)
            for path in path_matches:
                config['data_sources'].append({
                    'name': f"data_source_{len(config['data_sources'])}",
                    'path': path,
                    'type': path.split('.')[-1]
                })

        return config

    def _generate_requirements(self) -> List[str]:
        """
        Generate list of required packages from imports.

        Returns:
            List of package names
        """
        requirements_set = set()

        # Package mapping from import name to pip package name
        package_mapping = {
            'pandas': 'pandas',
            'numpy': 'numpy',
            'matplotlib': 'matplotlib',
            'seaborn': 'seaborn',
            'plotly': 'plotly',
            'sklearn': 'scikit-learn',
            'scipy': 'scipy',
            'requests': 'requests',
            'bs4': 'beautifulsoup4',
            'PIL': 'Pillow',
            'cv2': 'opencv-python',
            'streamlit': 'streamlit',
            'nbformat': 'nbformat',
        }

        for import_line in self.modules['imports']:
            # Extract package name from import
            if import_line.startswith('import '):
                package = import_line.replace('import ', '').split()[0].split('.')[0]
            elif import_line.startswith('from '):
                package = import_line.replace('from ', '').split()[0].split('.')[0]
            else:
                continue

            # Map to pip package name
            pip_package = package_mapping.get(package, package)
            requirements_set.add(pip_package)

        # Add essential packages
        requirements_set.add('streamlit')
        requirements_set.add('pandas')
        requirements_set.add('plotly')
        requirements_set.add('nbformat')

        return sorted(list(requirements_set))

    def generate_requirements_file(self) -> str:
        """
        Generate requirements.txt content.

        Returns:
            String content for requirements.txt
        """
        if not self.requirements:
            self._generate_requirements()

        return '\n'.join(self.requirements) + '\n'

    def generate_config_file(self, format: str = 'json') -> str:
        """
        Generate configuration file content.

        Args:
            format: Output format ('json' or 'yaml')

        Returns:
            String content for config file
        """
        if not self.config:
            self._generate_config()

        if format == 'json':
            return json.dumps(self.config, indent=2)
        elif format == 'yaml':
            # Simple YAML generation without external dependency
            lines = []
            for key, value in self.config.items():
                if isinstance(value, dict):
                    lines.append(f"{key}:")
                    for k, v in value.items():
                        lines.append(f"  {k}: {v}")
                elif isinstance(value, list):
                    lines.append(f"{key}:")
                    for item in value:
                        if isinstance(item, dict):
                            lines.append(f"  -")
                            for k, v in item.items():
                                lines.append(f"    {k}: {v}")
                        else:
                            lines.append(f"  - {item}")
                else:
                    lines.append(f"{key}: {value}")
            return '\n'.join(lines)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def get_module_code(self, module_name: str) -> str:
        """
        Get the complete code for a specific module.

        Args:
            module_name: Name of the module (data_loading, processing, visualization)

        Returns:
            Complete Python code for the module
        """
        if module_name not in self.modules:
            raise ValueError(f"Module not found: {module_name}")

        module = self.modules[module_name]
        code_parts = []

        # Add imports
        if self.modules['imports']:
            code_parts.append('\n'.join(self.modules['imports']))
            code_parts.append('\n')

        # Add functions
        for func_info in module.get('functions', []):
            code_parts.append(func_info['code'])
            code_parts.append('\n')

        return '\n'.join(code_parts)

    def get_all_functions(self) -> List[Dict]:
        """
        Get all generated functions across all modules.

        Returns:
            List of function dictionaries
        """
        all_functions = []

        for module_name in ['data_loading', 'processing', 'visualization']:
            if module_name in self.modules:
                module = self.modules[module_name]
                for func_info in module.get('functions', []):
                    func_info['module'] = module_name
                    all_functions.append(func_info)

        return all_functions
