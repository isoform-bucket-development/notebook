"""
Unit tests for Code Analyzer (REQ-2, REQ-5)

Tests cover:
- Converting notebook code into modular Python functions
- Identifying parameterizable variables
- AST-based code analysis
- Parameter type detection (numeric, categorical, boolean, date)
- Parameter range validation
"""

import pytest
from pathlib import Path


class TestCodeAnalyzer:
    """Test suite for CodeAnalyzer class - REQ-2: Code Conversion and REQ-5: Parameter Extraction"""

    def test_analyze_code_with_ast(self):
        """Test AST-based analysis of Python code from notebooks"""
        from src.notebook_converter.analyzer.code_analyzer import CodeAnalyzer

        analyzer = CodeAnalyzer()
        code_sample = """
import pandas as pd
df = pd.read_csv('data.csv')
threshold = 0.5
filtered_df = df[df['value'] > threshold]
        """

        # ACT: Analyze code with AST
        result = analyzer.analyze_ast(code_sample)

        # ASSERT: Verify AST analysis results
        assert result is not None
        assert "imports" in result
        assert "variables" in result
        assert "functions" in result
        pytest.fail("Implementation not complete - TDD red phase")

    def test_identify_parameterizable_variables(self):
        """Test identification of hardcoded parameters that could be made configurable"""
        from src.notebook_converter.analyzer.code_analyzer import CodeAnalyzer

        analyzer = CodeAnalyzer()
        code_sample = """
threshold = 0.5  # Could be parameter
file_path = "data.csv"  # Could be parameter
debug_mode = True  # Could be parameter
max_iterations = 100  # Could be parameter
        """

        # ACT: Identify parameterizable variables
        params = analyzer.identify_parameters(code_sample)

        # ASSERT: Verify parameters are identified
        assert isinstance(params, list)
        assert len(params) == 4
        assert any(p["name"] == "threshold" for p in params)
        assert any(p["name"] == "file_path" for p in params)
        assert any(p["name"] == "debug_mode" for p in params)
        assert any(p["name"] == "max_iterations" for p in params)
        pytest.fail("Implementation not complete - TDD red phase")

    def test_detect_numeric_parameter_type(self):
        """Test detection of numeric parameter types"""
        from src.notebook_converter.analyzer.code_analyzer import CodeAnalyzer

        analyzer = CodeAnalyzer()
        code_sample = """
threshold = 0.5
count = 42
temperature = 98.6
        """

        # ACT: Detect parameter types
        params = analyzer.identify_parameters(code_sample)

        # ASSERT: Verify numeric types are detected
        threshold_param = next(p for p in params if p["name"] == "threshold")
        assert threshold_param["type"] == "float"
        assert threshold_param["value"] == 0.5

        count_param = next(p for p in params if p["name"] == "count")
        assert count_param["type"] == "int"
        assert count_param["value"] == 42
        pytest.fail("Implementation not complete - TDD red phase")

    def test_detect_categorical_parameter_type(self):
        """Test detection of categorical/string parameter types"""
        from src.notebook_converter.analyzer.code_analyzer import CodeAnalyzer

        analyzer = CodeAnalyzer()
        code_sample = """
analysis_method = "regression"  # Categorical choice
file_format = "csv"  # Categorical choice
color_scheme = "blue"
        """

        # ACT: Detect parameter types
        params = analyzer.identify_parameters(code_sample)

        # ASSERT: Verify categorical types are detected
        method_param = next(p for p in params if p["name"] == "analysis_method")
        assert method_param["type"] == "categorical"
        assert method_param["value"] == "regression"
        pytest.fail("Implementation not complete - TDD red phase")

    def test_detect_boolean_parameter_type(self):
        """Test detection of boolean parameter types"""
        from src.notebook_converter.analyzer.code_analyzer import CodeAnalyzer

        analyzer = CodeAnalyzer()
        code_sample = """
enable_logging = True
show_plots = False
verbose_mode = True
        """

        # ACT: Detect parameter types
        params = analyzer.identify_parameters(code_sample)

        # ASSERT: Verify boolean types are detected
        logging_param = next(p for p in params if p["name"] == "enable_logging")
        assert logging_param["type"] == "boolean"
        assert logging_param["value"] is True
        pytest.fail("Implementation not complete - TDD red phase")

    def test_detect_date_parameter_type(self):
        """Test detection of date parameter types"""
        from src.notebook_converter.analyzer.code_analyzer import CodeAnalyzer

        analyzer = CodeAnalyzer()
        code_sample = """
from datetime import datetime
start_date = datetime(2023, 1, 1)
end_date = "2023-12-31"
        """

        # ACT: Detect parameter types
        params = analyzer.identify_parameters(code_sample)

        # ASSERT: Verify date types are detected
        start_param = next(p for p in params if p["name"] == "start_date")
        assert start_param["type"] == "date"
        pytest.fail("Implementation not complete - TDD red phase")

    def test_extract_data_source_paths(self):
        """Test extraction of data source file paths as parameters"""
        from src.notebook_converter.analyzer.code_analyzer import CodeAnalyzer

        analyzer = CodeAnalyzer()
        code_sample = """
import pandas as pd
df1 = pd.read_csv('sales_data.csv')
df2 = pd.read_excel('/path/to/inventory.xlsx')
df3 = pd.read_json('config.json')
        """

        # ACT: Extract data source parameters
        data_sources = analyzer.extract_data_sources(code_sample)

        # ASSERT: Verify data sources are extracted
        assert isinstance(data_sources, list)
        assert len(data_sources) == 3
        assert any('sales_data.csv' in ds["path"] for ds in data_sources)
        assert any('inventory.xlsx' in ds["path"] for ds in data_sources)
        pytest.fail("Implementation not complete - TDD red phase")

    def test_extract_analysis_parameters(self):
        """Test extraction of analysis configuration parameters"""
        from src.notebook_converter.analyzer.code_analyzer import CodeAnalyzer

        analyzer = CodeAnalyzer()
        code_sample = """
# Analysis configuration
window_size = 30
confidence_level = 0.95
method = 'exponential'
include_outliers = False
        """

        # ACT: Extract analysis parameters
        params = analyzer.identify_parameters(code_sample)

        # ASSERT: Verify analysis parameters are extracted
        assert len(params) == 4
        window_param = next(p for p in params if p["name"] == "window_size")
        assert window_param["category"] == "analysis_config"
        pytest.fail("Implementation not complete - TDD red phase")

    def test_validate_parameter_ranges(self):
        """Test validation of parameter ranges and constraints"""
        from src.notebook_converter.analyzer.code_analyzer import CodeAnalyzer

        analyzer = CodeAnalyzer()
        code_sample = """
threshold = 0.5  # Valid range: 0.0 to 1.0
percentage = 75  # Valid range: 0 to 100
        """

        # ACT: Identify parameters with ranges
        params = analyzer.identify_parameters(code_sample)

        # ASSERT: Verify parameter ranges are inferred
        threshold_param = next(p for p in params if p["name"] == "threshold")
        assert "min" in threshold_param
        assert "max" in threshold_param
        assert threshold_param["min"] == 0.0
        assert threshold_param["max"] == 1.0
        pytest.fail("Implementation not complete - TDD red phase")

    def test_detect_parameter_dependencies(self):
        """Test detection of parameter dependencies"""
        from src.notebook_converter.analyzer.code_analyzer import CodeAnalyzer

        analyzer = CodeAnalyzer()
        code_sample = """
start_value = 10
end_value = start_value + 100  # Depends on start_value
range_size = end_value - start_value  # Depends on both
        """

        # ACT: Detect parameter dependencies
        params = analyzer.identify_parameters(code_sample)

        # ASSERT: Verify dependencies are detected
        end_param = next(p for p in params if p["name"] == "end_value")
        assert "depends_on" in end_param
        assert "start_value" in end_param["depends_on"]
        pytest.fail("Implementation not complete - TDD red phase")

    def test_extract_import_statements(self):
        """Test extraction and categorization of import statements"""
        from src.notebook_converter.analyzer.code_analyzer import CodeAnalyzer

        analyzer = CodeAnalyzer()
        code_sample = """
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression
import seaborn as sns
        """

        # ACT: Extract imports
        imports = analyzer.extract_imports(code_sample)

        # ASSERT: Verify imports are categorized
        assert isinstance(imports, list)
        assert len(imports) == 5
        assert any(imp["module"] == "pandas" for imp in imports)
        assert any(imp["module"] == "matplotlib" for imp in imports)
        pytest.fail("Implementation not complete - TDD red phase")

    def test_identify_function_calls(self):
        """Test identification of function calls in code"""
        from src.notebook_converter.analyzer.code_analyzer import CodeAnalyzer

        analyzer = CodeAnalyzer()
        code_sample = """
df = pd.read_csv('data.csv')
result = df.groupby('category').mean()
print(result)
        """

        # ACT: Identify function calls
        function_calls = analyzer.extract_function_calls(code_sample)

        # ASSERT: Verify function calls are identified
        assert isinstance(function_calls, list)
        assert any(fc["name"] == "read_csv" for fc in function_calls)
        assert any(fc["name"] == "groupby" for fc in function_calls)
        pytest.fail("Implementation not complete - TDD red phase")

    def test_parameter_identification_accuracy_threshold(self):
        """Test that parameter identification achieves > 85% accuracy (NFR-6)"""
        from src.notebook_converter.analyzer.code_analyzer import CodeAnalyzer

        analyzer = CodeAnalyzer()

        # Sample with known parameters
        code_sample = """
# Known parameters (should identify all 10)
threshold = 0.5
max_count = 100
file_path = "data.csv"
debug = True
method = "linear"
window_size = 30
alpha = 0.05
iterations = 1000
output_dir = "./results"
enable_cache = False
        """

        # ACT: Identify parameters
        params = analyzer.identify_parameters(code_sample)

        # ASSERT: Verify accuracy meets requirement
        expected_count = 10
        identified_count = len(params)
        accuracy = identified_count / expected_count
        assert accuracy >= 0.85, f"Parameter identification accuracy {accuracy:.1%} < 85%"
        pytest.fail("Implementation not complete - TDD red phase")

    def test_handle_complex_code_structures(self):
        """Test analysis of complex code with classes, functions, and nested structures"""
        from src.notebook_converter.analyzer.code_analyzer import CodeAnalyzer

        analyzer = CodeAnalyzer()
        code_sample = """
class DataProcessor:
    def __init__(self, threshold=0.5):
        self.threshold = threshold

    def process(self, data):
        return data[data > self.threshold]

def analyze_data(df, window=30):
    return df.rolling(window=window).mean()
        """

        # ACT: Analyze complex code
        result = analyzer.analyze_ast(code_sample)

        # ASSERT: Verify complex structures are handled
        assert "classes" in result
        assert "functions" in result
        assert len(result["classes"]) == 1
        assert len(result["functions"]) == 1
        pytest.fail("Implementation not complete - TDD red phase")
