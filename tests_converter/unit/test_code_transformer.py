"""
Unit tests for Code Transformer (REQ-3)

Tests cover:
- Creating modular structure (data loading, processing, visualization)
- Converting notebook cells into functions
- Generating configuration files
- Maintaining cell execution order
- Generating requirements.txt
"""

import pytest
from pathlib import Path


class TestCodeTransformer:
    """Test suite for CodeTransformer class - REQ-3: Structure Reorganization"""

    def test_transform_notebook_to_modules(self):
        """Test conversion of notebook to modular Python structure"""
        from src.notebook_converter.transformer.code_transformer import CodeTransformer

        transformer = CodeTransformer()
        parsed_notebook = {
            "cells": [
                {"type": "code", "source": "import pandas as pd"},
                {"type": "code", "source": "df = pd.read_csv('data.csv')"},
                {"type": "code", "source": "result = df.mean()"}
            ]
        }

        # ACT: Transform to modules
        modules = transformer.transform_to_modules(parsed_notebook)

        # ASSERT: Verify modular structure
        assert "data_loading" in modules
        assert "data_processing" in modules
        assert "visualization" in modules
        pytest.fail("Implementation not complete - TDD red phase")

    def test_create_data_loading_module(self):
        """Test creation of data loading module from notebook cells"""
        from src.notebook_converter.transformer.code_transformer import CodeTransformer

        transformer = CodeTransformer()
        code_cells = [
            "import pandas as pd",
            "df = pd.read_csv('sales.csv')",
            "df_clean = df.dropna()"
        ]

        # ACT: Create data loading module
        module_code = transformer.create_data_loading_module(code_cells)

        # ASSERT: Verify module structure
        assert module_code is not None
        assert "def load_data" in module_code
        assert "import pandas" in module_code
        assert "return" in module_code
        pytest.fail("Implementation not complete - TDD red phase")

    def test_create_data_processing_module(self):
        """Test creation of data processing module"""
        from src.notebook_converter.transformer.code_transformer import CodeTransformer

        transformer = CodeTransformer()
        code_cells = [
            "filtered = df[df['value'] > threshold]",
            "grouped = filtered.groupby('category').mean()",
            "result = grouped.sort_values('value')"
        ]

        # ACT: Create processing module
        module_code = transformer.create_processing_module(code_cells)

        # ASSERT: Verify module structure
        assert module_code is not None
        assert "def process_data" in module_code
        assert "threshold" in module_code  # Parameter
        pytest.fail("Implementation not complete - TDD red phase")

    def test_create_visualization_module(self):
        """Test creation of visualization module"""
        from src.notebook_converter.transformer.code_transformer import CodeTransformer

        transformer = CodeTransformer()
        code_cells = [
            "import matplotlib.pyplot as plt",
            "plt.figure(figsize=(10, 6))",
            "plt.plot(df['x'], df['y'])",
            "plt.title('Analysis Results')",
            "plt.show()"
        ]

        # ACT: Create visualization module
        module_code = transformer.create_visualization_module(code_cells)

        # ASSERT: Verify module structure
        assert module_code is not None
        assert "def create_plot" in module_code
        assert "import matplotlib" in module_code
        pytest.fail("Implementation not complete - TDD red phase")

    def test_convert_cell_to_function(self):
        """Test conversion of individual notebook cell to function"""
        from src.notebook_converter.transformer.code_transformer import CodeTransformer

        transformer = CodeTransformer()
        cell_code = """
threshold = 0.5
filtered_df = df[df['value'] > threshold]
result = filtered_df.mean()
        """

        # ACT: Convert to function
        function_code = transformer.convert_to_function(
            cell_code,
            function_name="filter_data",
            parameters=["df", "threshold"]
        )

        # ASSERT: Verify function structure
        assert "def filter_data(df, threshold" in function_code
        assert "return" in function_code
        pytest.fail("Implementation not complete - TDD red phase")

    def test_maintain_execution_order(self):
        """Test that cell execution order is maintained in transformed code"""
        from src.notebook_converter.transformer.code_transformer import CodeTransformer

        transformer = CodeTransformer()
        cells = [
            {"order": 1, "code": "x = 10"},
            {"order": 2, "code": "y = x + 5"},
            {"order": 3, "code": "z = y * 2"}
        ]

        # ACT: Transform maintaining order
        result = transformer.transform_to_modules(cells)

        # ASSERT: Verify execution order is preserved
        # Dependencies should be respected: x before y before z
        pytest.fail("Implementation not complete - TDD red phase")

    def test_generate_parameter_config_file(self):
        """Test generation of parameter configuration file"""
        from src.notebook_converter.transformer.code_transformer import CodeTransformer

        transformer = CodeTransformer()
        parameters = [
            {"name": "threshold", "type": "float", "value": 0.5, "min": 0.0, "max": 1.0},
            {"name": "window_size", "type": "int", "value": 30, "min": 1, "max": 365},
            {"name": "method", "type": "categorical", "value": "linear", "options": ["linear", "exponential"]}
        ]

        # ACT: Generate config
        config = transformer.generate_parameter_config(parameters)

        # ASSERT: Verify config structure
        assert isinstance(config, dict)
        assert "threshold" in config
        assert config["threshold"]["type"] == "float"
        assert config["threshold"]["min"] == 0.0
        pytest.fail("Implementation not complete - TDD red phase")

    def test_generate_data_source_config_file(self):
        """Test generation of data source configuration file"""
        from src.notebook_converter.transformer.code_transformer import CodeTransformer

        transformer = CodeTransformer()
        data_sources = [
            {"path": "sales.csv", "type": "csv"},
            {"path": "inventory.xlsx", "type": "excel"},
            {"connection": "postgresql://localhost/db", "type": "database"}
        ]

        # ACT: Generate config
        config = transformer.generate_data_source_config(data_sources)

        # ASSERT: Verify config structure
        assert isinstance(config, dict)
        assert len(config) == 3
        pytest.fail("Implementation not complete - TDD red phase")

    def test_generate_requirements_txt(self):
        """Test generation of requirements.txt from imports"""
        from src.notebook_converter.transformer.code_transformer import CodeTransformer

        transformer = CodeTransformer()
        imports = [
            {"module": "pandas", "version": None},
            {"module": "numpy", "version": None},
            {"module": "matplotlib", "version": None},
            {"module": "seaborn", "version": None},
            {"module": "plotly", "version": None}
        ]

        # ACT: Generate requirements.txt
        requirements = transformer.generate_requirements(imports)

        # ASSERT: Verify requirements format
        assert isinstance(requirements, str)
        assert "pandas" in requirements
        assert "numpy" in requirements
        assert "matplotlib" in requirements
        pytest.fail("Implementation not complete - TDD red phase")

    def test_parameterize_hardcoded_values(self):
        """Test conversion of hardcoded values to parameters"""
        from src.notebook_converter.transformer.code_transformer import CodeTransformer

        transformer = CodeTransformer()
        code = """
df = pd.read_csv('data.csv')
threshold = 0.5
result = df[df['value'] > threshold]
        """
        parameters = [
            {"name": "data_file", "value": "data.csv"},
            {"name": "threshold", "value": 0.5}
        ]

        # ACT: Parameterize code
        parameterized_code = transformer.parameterize_code(code, parameters)

        # ASSERT: Verify parameterization
        assert "data_file" in parameterized_code or "config[" in parameterized_code
        pytest.fail("Implementation not complete - TDD red phase")

    def test_extract_dependencies_from_imports(self):
        """Test extraction of library dependencies from imports"""
        from src.notebook_converter.transformer.code_transformer import CodeTransformer

        transformer = CodeTransformer()
        code = """
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
        """

        # ACT: Extract dependencies
        dependencies = transformer.extract_dependencies(code)

        # ASSERT: Verify dependencies are extracted
        assert "pandas" in dependencies
        assert "numpy" in dependencies
        assert "scikit-learn" in dependencies  # sklearn maps to scikit-learn
        assert "matplotlib" in dependencies
        pytest.fail("Implementation not complete - TDD red phase")

    def test_handle_cell_dependencies(self):
        """Test handling of dependencies between cells"""
        from src.notebook_converter.transformer.code_transformer import CodeTransformer

        transformer = CodeTransformer()
        cells = [
            {"id": 1, "code": "x = load_data()"},
            {"id": 2, "code": "y = process(x)"},
            {"id": 3, "code": "plot(y)"}
        ]

        # ACT: Analyze dependencies
        deps = transformer.analyze_cell_dependencies(cells)

        # ASSERT: Verify dependencies are identified
        assert deps[2]["depends_on"] == [1]  # Cell 2 depends on cell 1
        assert deps[3]["depends_on"] == [2]  # Cell 3 depends on cell 2
        pytest.fail("Implementation not complete - TDD red phase")

    def test_generate_init_files(self):
        """Test generation of __init__.py files for modules"""
        from src.notebook_converter.transformer.code_transformer import CodeTransformer

        transformer = CodeTransformer()
        modules = ["data_loading", "data_processing", "visualization", "export"]

        # ACT: Generate __init__ files
        init_files = transformer.generate_init_files(modules)

        # ASSERT: Verify __init__ files are created
        assert len(init_files) == 4
        assert "data_loading/__init__.py" in init_files
        pytest.fail("Implementation not complete - TDD red phase")

    def test_preserve_markdown_as_comments(self):
        """Test preservation of markdown cells as docstrings or comments"""
        from src.notebook_converter.transformer.code_transformer import CodeTransformer

        transformer = CodeTransformer()
        cells = [
            {"type": "markdown", "source": "# Data Loading\nThis section loads the data"},
            {"type": "code", "source": "df = pd.read_csv('data.csv')"}
        ]

        # ACT: Transform with markdown
        result = transformer.transform_to_modules(cells)

        # ASSERT: Verify markdown is preserved
        assert '"""' in result or "#" in result
        pytest.fail("Implementation not complete - TDD red phase")
