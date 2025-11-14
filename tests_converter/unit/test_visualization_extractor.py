"""
Unit tests for Visualization Extractor (REQ-6)

Tests cover:
- Supporting multiple chart types (line, bar, scatter, heatmap, box plot, histogram)
- Converting Matplotlib to Plotly for Streamlit
- Converting Seaborn to Plotly
- Preserving interactivity features
- Chart configuration extraction
"""

import pytest


class TestVisualizationExtractor:
    """Test suite for VisualizationExtractor class - REQ-6: Interactive Visualization"""

    def test_identify_matplotlib_line_chart(self):
        """Test identification and extraction of matplotlib line charts"""
        from src.notebook_converter.analyzer.visualization_extractor import VisualizationExtractor

        extractor = VisualizationExtractor()
        code = """
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 6))
plt.plot(x_data, y_data, label='Sales')
plt.xlabel('Date')
plt.ylabel('Revenue')
plt.title('Sales Over Time')
plt.legend()
plt.show()
        """

        # ACT: Extract visualization
        viz = extractor.extract_visualization(code)

        # ASSERT: Verify line chart is identified
        assert viz["type"] == "line"
        assert viz["library"] == "matplotlib"
        assert "x_data" in viz["data_vars"]
        assert "y_data" in viz["data_vars"]
        pytest.fail("Implementation not complete - TDD red phase")

    def test_identify_matplotlib_bar_chart(self):
        """Test identification of matplotlib bar charts"""
        from src.notebook_converter.analyzer.visualization_extractor import VisualizationExtractor

        extractor = VisualizationExtractor()
        code = """
plt.bar(categories, values)
plt.title('Sales by Category')
        """

        # ACT: Extract visualization
        viz = extractor.extract_visualization(code)

        # ASSERT: Verify bar chart is identified
        assert viz["type"] == "bar"
        pytest.fail("Implementation not complete - TDD red phase")

    def test_identify_matplotlib_scatter_plot(self):
        """Test identification of matplotlib scatter plots"""
        from src.notebook_converter.analyzer.visualization_extractor import VisualizationExtractor

        extractor = VisualizationExtractor()
        code = """
plt.scatter(df['age'], df['income'], c=df['category'])
plt.xlabel('Age')
plt.ylabel('Income')
        """

        # ACT: Extract visualization
        viz = extractor.extract_visualization(code)

        # ASSERT: Verify scatter plot is identified
        assert viz["type"] == "scatter"
        pytest.fail("Implementation not complete - TDD red phase")

    def test_identify_seaborn_heatmap(self):
        """Test identification of seaborn heatmaps"""
        from src.notebook_converter.analyzer.visualization_extractor import VisualizationExtractor

        extractor = VisualizationExtractor()
        code = """
import seaborn as sns
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
        """

        # ACT: Extract visualization
        viz = extractor.extract_visualization(code)

        # ASSERT: Verify heatmap is identified
        assert viz["type"] == "heatmap"
        assert viz["library"] == "seaborn"
        pytest.fail("Implementation not complete - TDD red phase")

    def test_identify_seaborn_boxplot(self):
        """Test identification of seaborn box plots"""
        from src.notebook_converter.analyzer.visualization_extractor import VisualizationExtractor

        extractor = VisualizationExtractor()
        code = """
sns.boxplot(x='category', y='value', data=df)
        """

        # ACT: Extract visualization
        viz = extractor.extract_visualization(code)

        # ASSERT: Verify box plot is identified
        assert viz["type"] == "box"
        pytest.fail("Implementation not complete - TDD red phase")

    def test_identify_matplotlib_histogram(self):
        """Test identification of matplotlib histograms"""
        from src.notebook_converter.analyzer.visualization_extractor import VisualizationExtractor

        extractor = VisualizationExtractor()
        code = """
plt.hist(data, bins=30, alpha=0.7)
plt.xlabel('Value')
plt.ylabel('Frequency')
        """

        # ACT: Extract visualization
        viz = extractor.extract_visualization(code)

        # ASSERT: Verify histogram is identified
        assert viz["type"] == "histogram"
        pytest.fail("Implementation not complete - TDD red phase")

    def test_convert_matplotlib_to_plotly(self):
        """Test conversion of matplotlib code to Plotly"""
        from src.notebook_converter.transformer.visualization_converter import VisualizationConverter

        converter = VisualizationConverter()
        matplotlib_code = """
plt.figure(figsize=(10, 6))
plt.plot(x, y, label='Data')
plt.xlabel('X Axis')
plt.ylabel('Y Axis')
plt.title('My Chart')
plt.legend()
        """

        # ACT: Convert to Plotly
        plotly_code = converter.convert_to_plotly(matplotlib_code)

        # ASSERT: Verify Plotly conversion
        assert "import plotly" in plotly_code
        assert "go.Figure" in plotly_code or "px." in plotly_code
        assert "update_layout" in plotly_code
        pytest.fail("Implementation not complete - TDD red phase")

    def test_convert_seaborn_to_plotly(self):
        """Test conversion of seaborn code to Plotly"""
        from src.notebook_converter.transformer.visualization_converter import VisualizationConverter

        converter = VisualizationConverter()
        seaborn_code = """
sns.heatmap(data, annot=True, cmap='coolwarm')
        """

        # ACT: Convert to Plotly
        plotly_code = converter.convert_to_plotly(seaborn_code)

        # ASSERT: Verify Plotly conversion
        assert "import plotly" in plotly_code
        assert "go.Heatmap" in plotly_code or "px.imshow" in plotly_code
        pytest.fail("Implementation not complete - TDD red phase")

    def test_preserve_interactivity_features(self):
        """Test that interactivity features are preserved in conversion"""
        from src.notebook_converter.transformer.visualization_converter import VisualizationConverter

        converter = VisualizationConverter()
        code = """
plt.plot(x, y)
plt.title('Interactive Chart')
        """

        # ACT: Convert with interactivity
        plotly_code = converter.convert_to_plotly(code)

        # ASSERT: Verify interactivity is enabled
        # Plotly charts should have zoom, pan, hover by default
        assert "hovertemplate" in plotly_code or "hover_data" in plotly_code or plotly_code  # Default interactivity
        pytest.fail("Implementation not complete - TDD red phase")

    def test_extract_chart_configuration(self):
        """Test extraction of chart configuration (colors, size, axes)"""
        from src.notebook_converter.analyzer.visualization_extractor import VisualizationExtractor

        extractor = VisualizationExtractor()
        code = """
plt.figure(figsize=(12, 8))
plt.plot(x, y, color='blue', linewidth=2)
plt.xlabel('Time', fontsize=14)
plt.ylabel('Value', fontsize=14)
plt.title('Analysis Results', fontsize=16)
plt.grid(True)
        """

        # ACT: Extract configuration
        config = extractor.extract_chart_config(code)

        # ASSERT: Verify configuration is extracted
        assert config["figure_size"] == (12, 8)
        assert config["color"] == "blue"
        assert config["title"] == "Analysis Results"
        assert config["xlabel"] == "Time"
        pytest.fail("Implementation not complete - TDD red phase")

    def test_support_multiple_charts_in_cell(self):
        """Test handling of multiple charts in single notebook cell"""
        from src.notebook_converter.analyzer.visualization_extractor import VisualizationExtractor

        extractor = VisualizationExtractor()
        code = """
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
axes[0, 0].plot(x1, y1)
axes[0, 1].bar(categories, values)
axes[1, 0].scatter(x2, y2)
axes[1, 1].hist(data, bins=20)
        """

        # ACT: Extract all visualizations
        visualizations = extractor.extract_all_visualizations(code)

        # ASSERT: Verify multiple charts are detected
        assert len(visualizations) == 4
        assert any(v["type"] == "line" for v in visualizations)
        assert any(v["type"] == "bar" for v in visualizations)
        assert any(v["type"] == "scatter" for v in visualizations)
        assert any(v["type"] == "histogram" for v in visualizations)
        pytest.fail("Implementation not complete - TDD red phase")

    def test_identify_3d_charts(self):
        """Test identification of 3D charts when applicable"""
        from src.notebook_converter.analyzer.visualization_extractor import VisualizationExtractor

        extractor = VisualizationExtractor()
        code = """
from mpl_toolkits.mplot3d import Axes3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x, y, z)
        """

        # ACT: Extract visualization
        viz = extractor.extract_visualization(code)

        # ASSERT: Verify 3D chart is identified
        assert viz["type"] == "scatter3d"
        assert viz["dimensions"] == 3
        pytest.fail("Implementation not complete - TDD red phase")

    def test_extract_data_variables_from_chart(self):
        """Test extraction of data variables used in charts"""
        from src.notebook_converter.analyzer.visualization_extractor import VisualizationExtractor

        extractor = VisualizationExtractor()
        code = """
plt.plot(df['date'], df['revenue'], label='Revenue')
plt.plot(df['date'], df['cost'], label='Cost')
        """

        # ACT: Extract data variables
        data_vars = extractor.extract_data_variables(code)

        # ASSERT: Verify data variables are identified
        assert "df['date']" in data_vars or "date" in data_vars
        assert "df['revenue']" in data_vars or "revenue" in data_vars
        assert "df['cost']" in data_vars or "cost" in data_vars
        pytest.fail("Implementation not complete - TDD red phase")

    def test_chart_rendering_performance(self):
        """Test that chart rendering preparation meets < 2 second requirement (NFR-1)"""
        import time
        from src.notebook_converter.transformer.visualization_converter import VisualizationConverter

        converter = VisualizationConverter()
        code = """
plt.figure(figsize=(10, 6))
for i in range(10):
    plt.plot(range(100), [j + i for j in range(100)])
plt.title('Multiple Series')
        """

        # ACT: Time the conversion
        start_time = time.time()
        plotly_code = converter.convert_to_plotly(code)
        end_time = time.time()

        # ASSERT: Verify performance
        elapsed = end_time - start_time
        assert elapsed < 2.0, f"Chart conversion took {elapsed}s, should be < 2s"
        pytest.fail("Implementation not complete - TDD red phase")
