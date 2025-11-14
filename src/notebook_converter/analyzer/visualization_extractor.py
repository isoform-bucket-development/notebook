"""
Visualization Extractor Module

This module identifies visualization code in notebooks and extracts
chart types, configurations, and library usage.
"""

import ast
import re
from typing import Dict, List, Optional, Tuple


class VisualizationExtractor:
    """
    Extractor for visualization code from notebooks.

    This class identifies and analyzes visualization code from:
    - Matplotlib
    - Seaborn
    - Plotly

    Attributes:
        code (str): Python code to analyze
        visualizations (list): List of identified visualizations
    """

    def __init__(self, code: Optional[str] = None):
        """
        Initialize the VisualizationExtractor.

        Args:
            code: Python code string containing visualization code
        """
        self.code = code
        self.visualizations = []

    def extract(self, code: Optional[str] = None) -> List[Dict]:
        """
        Extract visualization information from code.

        Args:
            code: Python code string (overrides constructor code)

        Returns:
            List of visualization dictionaries with:
                - library: Visualization library (matplotlib, seaborn, plotly)
                - chart_type: Type of chart (line, bar, scatter, etc.)
                - function_call: The function used
                - config: Extracted configuration (title, labels, etc.)
        """
        source_code = code or self.code
        if not source_code:
            return []

        self.visualizations = []

        # Identify matplotlib visualizations
        self._extract_matplotlib(source_code)

        # Identify seaborn visualizations
        self._extract_seaborn(source_code)

        # Identify plotly visualizations
        self._extract_plotly(source_code)

        return self.visualizations

    def _extract_matplotlib(self, code: str):
        """
        Extract matplotlib visualizations from code.

        Args:
            code: Python code string
        """
        matplotlib_patterns = {
            'line': [r'plt\.plot\(', r'ax\.plot\('],
            'scatter': [r'plt\.scatter\(', r'ax\.scatter\('],
            'bar': [r'plt\.bar\(', r'ax\.bar\(', r'plt\.barh\('],
            'histogram': [r'plt\.hist\(', r'ax\.hist\('],
            'boxplot': [r'plt\.boxplot\(', r'ax\.boxplot\('],
            'heatmap': [r'plt\.imshow\(', r'ax\.imshow\('],
            'pie': [r'plt\.pie\(', r'ax\.pie\('],
        }

        for chart_type, patterns in matplotlib_patterns.items():
            for pattern in patterns:
                if re.search(pattern, code):
                    viz = {
                        'library': 'matplotlib',
                        'chart_type': chart_type,
                        'function_call': pattern.replace(r'\(', '').replace('\\', ''),
                        'config': self._extract_matplotlib_config(code, pattern)
                    }
                    self.visualizations.append(viz)

    def _extract_matplotlib_config(self, code: str, pattern: str) -> Dict:
        """
        Extract configuration for matplotlib charts.

        Args:
            code: Python code string
            pattern: Pattern that matched

        Returns:
            Dictionary of configuration options
        """
        config = {}

        # Extract title
        title_match = re.search(r'plt\.title\(["\']([^"\']+)["\']\)', code)
        if title_match:
            config['title'] = title_match.group(1)

        # Extract xlabel
        xlabel_match = re.search(r'plt\.xlabel\(["\']([^"\']+)["\']\)', code)
        if xlabel_match:
            config['xlabel'] = xlabel_match.group(1)

        # Extract ylabel
        ylabel_match = re.search(r'plt\.ylabel\(["\']([^"\']+)["\']\)', code)
        if ylabel_match:
            config['ylabel'] = ylabel_match.group(1)

        # Extract legend
        if 'plt.legend(' in code or 'ax.legend(' in code:
            config['has_legend'] = True

        # Extract grid
        if 'plt.grid(' in code or 'ax.grid(' in code:
            config['has_grid'] = True

        return config

    def _extract_seaborn(self, code: str):
        """
        Extract seaborn visualizations from code.

        Args:
            code: Python code string
        """
        seaborn_patterns = {
            'line': [r'sns\.lineplot\('],
            'scatter': [r'sns\.scatterplot\('],
            'bar': [r'sns\.barplot\('],
            'histogram': [r'sns\.histplot\(', r'sns\.distplot\('],
            'boxplot': [r'sns\.boxplot\('],
            'violin': [r'sns\.violinplot\('],
            'heatmap': [r'sns\.heatmap\('],
            'pairplot': [r'sns\.pairplot\('],
        }

        for chart_type, patterns in seaborn_patterns.items():
            for pattern in patterns:
                if re.search(pattern, code):
                    viz = {
                        'library': 'seaborn',
                        'chart_type': chart_type,
                        'function_call': pattern.replace(r'\(', '').replace('\\', ''),
                        'config': self._extract_seaborn_config(code, pattern)
                    }
                    self.visualizations.append(viz)

    def _extract_seaborn_config(self, code: str, pattern: str) -> Dict:
        """
        Extract configuration for seaborn charts.

        Args:
            code: Python code string
            pattern: Pattern that matched

        Returns:
            Dictionary of configuration options
        """
        config = {}

        # Seaborn often uses matplotlib for titles/labels
        # Extract title
        title_match = re.search(r'plt\.title\(["\']([^"\']+)["\']\)', code)
        if title_match:
            config['title'] = title_match.group(1)

        # Try to extract data and variables from the function call
        func_call_pattern = pattern.replace('\\', '')
        match = re.search(f'{func_call_pattern}([^)]+)\)', code)
        if match:
            args_str = match.group(1)
            # Extract x, y parameters
            x_match = re.search(r'x=["\']?([^,"\'\)]+)["\']?', args_str)
            if x_match:
                config['x'] = x_match.group(1).strip()
            y_match = re.search(r'y=["\']?([^,"\'\)]+)["\']?', args_str)
            if y_match:
                config['y'] = y_match.group(1).strip()

        return config

    def _extract_plotly(self, code: str):
        """
        Extract plotly visualizations from code.

        Args:
            code: Python code string
        """
        plotly_patterns = {
            'line': [r'px\.line\(', r'go\.Scatter\(.*mode=["\']lines'],
            'scatter': [r'px\.scatter\(', r'go\.Scatter\(.*mode=["\']markers'],
            'bar': [r'px\.bar\(', r'go\.Bar\('],
            'histogram': [r'px\.histogram\(', r'go\.Histogram\('],
            'boxplot': [r'px\.box\(', r'go\.Box\('],
            'heatmap': [r'px\.density_heatmap\(', r'go\.Heatmap\('],
            'pie': [r'px\.pie\(', r'go\.Pie\('],
            '3d_scatter': [r'px\.scatter_3d\(', r'go\.Scatter3d\('],
        }

        for chart_type, patterns in plotly_patterns.items():
            for pattern in patterns:
                if re.search(pattern, code):
                    viz = {
                        'library': 'plotly',
                        'chart_type': chart_type,
                        'function_call': pattern.replace(r'\(', '').replace('\\', ''),
                        'config': self._extract_plotly_config(code, pattern)
                    }
                    self.visualizations.append(viz)

    def _extract_plotly_config(self, code: str, pattern: str) -> Dict:
        """
        Extract configuration for plotly charts.

        Args:
            code: Python code string
            pattern: Pattern that matched

        Returns:
            Dictionary of configuration options
        """
        config = {}

        # Try to extract arguments from the function call
        func_call_pattern = pattern.replace('\\', '').replace('["\']lines', '').replace('["\']markers', '')
        match = re.search(f'{func_call_pattern}([^)]+)\)', code)
        if match:
            args_str = match.group(1)

            # Extract x, y parameters
            x_match = re.search(r'x=["\']?([^,"\'\)]+)["\']?', args_str)
            if x_match:
                config['x'] = x_match.group(1).strip()
            y_match = re.search(r'y=["\']?([^,"\'\)]+)["\']?', args_str)
            if y_match:
                config['y'] = y_match.group(1).strip()

            # Extract title
            title_match = re.search(r'title=["\']([^"\']+)["\']', args_str)
            if title_match:
                config['title'] = title_match.group(1)

        return config

    def identify_chart_type(self, code: str) -> Optional[Dict]:
        """
        Identify the chart type from a code snippet.

        Args:
            code: Python code string

        Returns:
            Dictionary with library and chart_type, or None if not found
        """
        visualizations = self.extract(code)
        if visualizations:
            return {
                'library': visualizations[0]['library'],
                'chart_type': visualizations[0]['chart_type']
            }
        return None

    def convert_to_plotly_code(self, viz_dict: Dict, data_var: str = 'df') -> str:
        """
        Generate Plotly code from visualization dictionary.

        Args:
            viz_dict: Visualization dictionary from extract()
            data_var: Name of the dataframe variable

        Returns:
            Python code string for Plotly visualization
        """
        library = viz_dict['library']
        chart_type = viz_dict['chart_type']
        config = viz_dict.get('config', {})

        # If already plotly, return as is
        if library == 'plotly':
            return f"# Plotly chart - {chart_type}\n{viz_dict['function_call']}"

        # Convert matplotlib/seaborn to plotly
        code_lines = ["import plotly.express as px", ""]

        x_col = config.get('x', 'x')
        y_col = config.get('y', 'y')
        title = config.get('title', f'{chart_type.title()} Chart')

        chart_mapping = {
            'line': f"fig = px.line({data_var}, x='{x_col}', y='{y_col}', title='{title}')",
            'scatter': f"fig = px.scatter({data_var}, x='{x_col}', y='{y_col}', title='{title}')",
            'bar': f"fig = px.bar({data_var}, x='{x_col}', y='{y_col}', title='{title}')",
            'histogram': f"fig = px.histogram({data_var}, x='{x_col}', title='{title}')",
            'boxplot': f"fig = px.box({data_var}, x='{x_col}', y='{y_col}', title='{title}')",
            'heatmap': f"fig = px.density_heatmap({data_var}, x='{x_col}', y='{y_col}', title='{title}')",
        }

        plotly_code = chart_mapping.get(chart_type, f"# Unsupported chart type: {chart_type}")
        code_lines.append(plotly_code)
        code_lines.append("st.plotly_chart(fig, use_container_width=True)")

        return '\n'.join(code_lines)

    def get_visualization_summary(self) -> Dict:
        """
        Get a summary of visualizations found.

        Returns:
            Dictionary with counts by library and chart type
        """
        summary = {
            'total': len(self.visualizations),
            'by_library': {},
            'by_chart_type': {},
            'libraries_used': set()
        }

        for viz in self.visualizations:
            library = viz['library']
            chart_type = viz['chart_type']

            summary['by_library'][library] = summary['by_library'].get(library, 0) + 1
            summary['by_chart_type'][chart_type] = summary['by_chart_type'].get(chart_type, 0) + 1
            summary['libraries_used'].add(library)

        summary['libraries_used'] = list(summary['libraries_used'])

        return summary
