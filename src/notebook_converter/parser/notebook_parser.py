"""
Notebook Parser Module

This module provides functionality to parse Jupyter Notebook files using nbformat,
extract cell structures, identify data loading patterns, and detect visualization code.
"""

import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Union

try:
    import nbformat
except ImportError:
    nbformat = None


class NotebookParser:
    """
    Parser for Jupyter Notebook files.

    This class handles parsing of .ipynb files using nbformat library,
    extracts cells by type, identifies data loading patterns, and
    detects visualization code.

    Attributes:
        notebook_path (str): Path to the notebook file
        notebook (nbformat.NotebookNode): Parsed notebook object
        cells (list): List of all cells in the notebook
        parse_time (float): Time taken to parse the notebook in seconds
    """

    def __init__(self, notebook_path: Optional[str] = None):
        """
        Initialize the NotebookParser.

        Args:
            notebook_path: Path to the Jupyter Notebook file
        """
        self.notebook_path = notebook_path
        self.notebook = None
        self.cells = []
        self.parse_time = 0.0

    def parse(self, notebook_path: Optional[str] = None) -> Dict:
        """
        Parse a Jupyter Notebook file and extract its structure.

        Args:
            notebook_path: Path to the notebook file (overrides constructor path)

        Returns:
            Dictionary containing parsed notebook structure with keys:
                - cells: List of all cells
                - code_cells: List of code cells
                - markdown_cells: List of markdown cells
                - cell_count: Total number of cells
                - metadata: Notebook metadata
                - parse_time: Time taken to parse (seconds)

        Raises:
            FileNotFoundError: If notebook file doesn't exist
            ValueError: If nbformat is not installed or file is invalid
        """
        if nbformat is None:
            raise ValueError("nbformat is not installed. Please install it using: pip install nbformat")

        path = notebook_path or self.notebook_path
        if not path:
            raise ValueError("No notebook path provided")

        path_obj = Path(path)
        if not path_obj.exists():
            raise FileNotFoundError(f"Notebook file not found: {path}")

        start_time = time.time()

        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.notebook = nbformat.read(f, as_version=4)
        except Exception as e:
            raise ValueError(f"Failed to parse notebook: {str(e)}")

        self.cells = self.notebook.cells
        self.parse_time = time.time() - start_time

        return {
            'cells': self.cells,
            'code_cells': self.get_code_cells(),
            'markdown_cells': self.get_markdown_cells(),
            'cell_count': len(self.cells),
            'metadata': self.notebook.metadata,
            'parse_time': self.parse_time
        }

    def get_code_cells(self) -> List:
        """
        Extract all code cells from the notebook.

        Returns:
            List of code cell objects
        """
        if not self.cells:
            return []
        return [cell for cell in self.cells if cell.cell_type == 'code']

    def get_markdown_cells(self) -> List:
        """
        Extract all markdown cells from the notebook.

        Returns:
            List of markdown cell objects
        """
        if not self.cells:
            return []
        return [cell for cell in self.cells if cell.cell_type == 'markdown']

    def identify_data_loading_cells(self) -> List[Dict]:
        """
        Identify cells that contain data loading operations.

        Looks for patterns like:
        - pd.read_csv, pd.read_excel, pd.read_json, etc.
        - Database connections (sqlite3, psycopg2, pymysql)
        - API calls (requests.get, urllib)

        Returns:
            List of dictionaries containing:
                - cell_index: Index of the cell
                - cell: The cell object
                - patterns: List of data loading patterns found
                - sources: List of data source paths/URLs found
        """
        data_loading_cells = []
        code_cells = self.get_code_cells()

        # Patterns to identify data loading
        patterns = {
            'pandas_csv': r'pd\.read_csv\s*\(["\']([^"\']+)["\']',
            'pandas_excel': r'pd\.read_excel\s*\(["\']([^"\']+)["\']',
            'pandas_json': r'pd\.read_json\s*\(["\']([^"\']+)["\']',
            'pandas_sql': r'pd\.read_sql',
            'db_connection': r'(sqlite3\.connect|psycopg2\.connect|pymysql\.connect)',
            'api_call': r'requests\.(get|post)',
        }

        for idx, cell in enumerate(code_cells):
            source = cell.source
            found_patterns = []
            sources = []

            for pattern_name, pattern_regex in patterns.items():
                matches = re.findall(pattern_regex, source)
                if matches:
                    found_patterns.append(pattern_name)
                    # Extract file paths or URLs
                    if pattern_name in ['pandas_csv', 'pandas_excel', 'pandas_json']:
                        sources.extend([m if isinstance(m, str) else m[0] for m in matches])

            if found_patterns:
                data_loading_cells.append({
                    'cell_index': idx,
                    'cell': cell,
                    'patterns': found_patterns,
                    'sources': sources
                })

        return data_loading_cells

    def identify_visualization_cells(self) -> List[Dict]:
        """
        Identify cells that contain visualization code.

        Looks for patterns from:
        - Matplotlib (plt.plot, plt.scatter, etc.)
        - Seaborn (sns.lineplot, sns.barplot, etc.)
        - Plotly (px.line, px.scatter, go.Figure, etc.)

        Returns:
            List of dictionaries containing:
                - cell_index: Index of the cell
                - cell: The cell object
                - library: Visualization library used
                - chart_types: List of chart types detected
        """
        viz_cells = []
        code_cells = self.get_code_cells()

        # Patterns for different visualization libraries
        viz_patterns = {
            'matplotlib': [
                (r'plt\.plot\(', 'line'),
                (r'plt\.scatter\(', 'scatter'),
                (r'plt\.bar\(', 'bar'),
                (r'plt\.hist\(', 'histogram'),
                (r'plt\.boxplot\(', 'boxplot'),
                (r'plt\.imshow\(', 'heatmap'),
            ],
            'seaborn': [
                (r'sns\.lineplot\(', 'line'),
                (r'sns\.scatterplot\(', 'scatter'),
                (r'sns\.barplot\(', 'bar'),
                (r'sns\.histplot\(', 'histogram'),
                (r'sns\.boxplot\(', 'boxplot'),
                (r'sns\.heatmap\(', 'heatmap'),
            ],
            'plotly': [
                (r'px\.line\(', 'line'),
                (r'px\.scatter\(', 'scatter'),
                (r'px\.bar\(', 'bar'),
                (r'px\.histogram\(', 'histogram'),
                (r'px\.box\(', 'boxplot'),
                (r'go\.Figure\(', 'figure'),
            ]
        }

        for idx, cell in enumerate(code_cells):
            source = cell.source
            cell_viz_info = {
                'cell_index': idx,
                'cell': cell,
                'libraries': [],
                'chart_types': []
            }

            for library, patterns in viz_patterns.items():
                for pattern, chart_type in patterns:
                    if re.search(pattern, source):
                        if library not in cell_viz_info['libraries']:
                            cell_viz_info['libraries'].append(library)
                        if chart_type not in cell_viz_info['chart_types']:
                            cell_viz_info['chart_types'].append(chart_type)

            if cell_viz_info['libraries']:
                viz_cells.append(cell_viz_info)

        return viz_cells

    def extract_imports(self) -> List[str]:
        """
        Extract all import statements from the notebook.

        Returns:
            List of import statements as strings
        """
        imports = []
        code_cells = self.get_code_cells()

        import_patterns = [
            r'^import\s+[\w\.]+',
            r'^from\s+[\w\.]+\s+import\s+.+',
        ]

        for cell in code_cells:
            lines = cell.source.split('\n')
            for line in lines:
                line = line.strip()
                for pattern in import_patterns:
                    if re.match(pattern, line):
                        imports.append(line)
                        break

        return list(set(imports))  # Remove duplicates

    def get_execution_order(self) -> List[int]:
        """
        Get the execution order of code cells based on execution_count.

        Returns:
            List of cell indices in execution order
        """
        code_cells = self.get_code_cells()

        # Create list of (index, execution_count) tuples
        exec_info = []
        for idx, cell in enumerate(code_cells):
            exec_count = cell.get('execution_count')
            if exec_count is not None:
                exec_info.append((idx, exec_count))

        # Sort by execution_count
        exec_info.sort(key=lambda x: x[1])

        return [idx for idx, _ in exec_info]

    def get_notebook_summary(self) -> Dict:
        """
        Get a comprehensive summary of the notebook.

        Returns:
            Dictionary containing:
                - total_cells: Total number of cells
                - code_cells: Number of code cells
                - markdown_cells: Number of markdown cells
                - data_loading_cells: Number of data loading cells
                - visualization_cells: Number of visualization cells
                - imports: List of import statements
                - has_outputs: Whether cells have outputs
                - parse_time: Parse time in seconds
        """
        if not self.notebook:
            raise ValueError("No notebook parsed yet. Call parse() first.")

        code_cells = self.get_code_cells()
        markdown_cells = self.get_markdown_cells()
        data_loading = self.identify_data_loading_cells()
        viz_cells = self.identify_visualization_cells()
        imports = self.extract_imports()

        has_outputs = any(
            hasattr(cell, 'outputs') and len(cell.outputs) > 0
            for cell in code_cells
        )

        return {
            'total_cells': len(self.cells),
            'code_cells': len(code_cells),
            'markdown_cells': len(markdown_cells),
            'data_loading_cells': len(data_loading),
            'visualization_cells': len(viz_cells),
            'imports': imports,
            'has_outputs': has_outputs,
            'parse_time': self.parse_time
        }
