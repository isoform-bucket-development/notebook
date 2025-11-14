"""
Web Application Generator Module

This module generates Streamlit web applications from transformed notebook modules.
"""

from typing import Dict, List, Optional


class WebAppGenerator:
    """
    Generator for Streamlit web applications.

    This class:
    - Generates complete Streamlit app structure
    - Creates parameter widgets (sliders, selectboxes, etc.)
    - Generates data loading interface
    - Creates visualization displays
    - Adds export functionality

    Attributes:
        modules (dict): Dictionary of code modules
        config (dict): Configuration dictionary
        parameters (list): List of parameters
        app_code (str): Generated Streamlit app code
    """

    def __init__(self, modules: Optional[Dict] = None, config: Optional[Dict] = None):
        """
        Initialize the WebAppGenerator.

        Args:
            modules: Dictionary of code modules from CodeTransformer
            config: Configuration dictionary
        """
        self.modules = modules or {}
        self.config = config or {}
        self.parameters = []
        self.app_code = ""

    def generate(self, modules: Optional[Dict] = None, config: Optional[Dict] = None, parameters: Optional[List] = None) -> Dict:
        """
        Generate a complete Streamlit web application.

        Args:
            modules: Dictionary of code modules (overrides constructor modules)
            config: Configuration dictionary (overrides constructor config)
            parameters: List of parameter dictionaries

        Returns:
            Dictionary containing:
                - app_code: Complete Streamlit application code
                - components: Dictionary of individual components
                - file_structure: Suggested file structure
        """
        source_modules = modules or self.modules
        source_config = config or self.config
        self.parameters = parameters or []

        if not source_modules:
            raise ValueError("No modules provided for app generation")

        # Build the app components
        components = {
            'imports': self._generate_imports(),
            'title': self._generate_title(),
            'sidebar': self._generate_sidebar(),
            'data_upload': self._generate_data_upload(),
            'parameters': self._generate_parameter_widgets(),
            'data_preview': self._generate_data_preview(),
            'visualizations': self._generate_visualizations(),
            'export': self._generate_export_section(),
        }

        # Assemble the complete app
        self.app_code = self._assemble_app(components, source_modules)

        return {
            'app_code': self.app_code,
            'components': components,
            'file_structure': self._generate_file_structure()
        }

    def _generate_imports(self) -> str:
        """
        Generate import statements for the Streamlit app.

        Returns:
            Import statements as string
        """
        imports = [
            "import streamlit as st",
            "import pandas as pd",
            "import plotly.express as px",
            "import plotly.graph_objects as go",
            "from io import StringIO, BytesIO",
        ]

        # Add imports from modules
        if 'imports' in self.modules:
            for imp in self.modules['imports']:
                if imp not in imports and 'streamlit' not in imp:
                    imports.append(imp)

        return '\n'.join(imports)

    def _generate_title(self) -> str:
        """
        Generate the title section of the app.

        Returns:
            Title section code as string
        """
        return '''
# App Title and Configuration
st.set_page_config(page_title="Notebook Analysis", layout="wide")
st.title("📊 Interactive Data Analysis")
st.markdown("---")
'''

    def _generate_sidebar(self) -> str:
        """
        Generate the sidebar section.

        Returns:
            Sidebar code as string
        """
        return '''
# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown("Upload your data and configure analysis parameters.")
'''

    def _generate_data_upload(self) -> str:
        """
        Generate data upload interface.

        Returns:
            Data upload code as string
        """
        code = '''
    # Data Upload Section
    st.subheader("📁 Data Upload")
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload your data file to begin analysis"
    )

    # Data loading
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.success(f"✅ Loaded {len(df)} rows and {len(df.columns)} columns")
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            df = None
    else:
        st.info("Please upload a data file to begin")
        df = None
'''
        return code

    def _generate_parameter_widgets(self) -> str:
        """
        Generate parameter input widgets.

        Returns:
            Parameter widgets code as string
        """
        if not self.parameters:
            return "\n    # No parameters identified\n    st.markdown('No configurable parameters found.')\n"

        code = "\n    # Parameters Section\n    st.subheader('🎛️ Parameters')\n"

        for param in self.parameters:
            param_name = param.get('name', 'param')
            param_type = param.get('type', 'string')
            param_value = param.get('value', '')

            if param_type == 'numeric':
                if isinstance(param_value, float):
                    code += f"    {param_name} = st.slider('{param_name}', min_value=0.0, max_value=1.0, value={param_value}, step=0.01)\n"
                else:
                    code += f"    {param_name} = st.number_input('{param_name}', value={param_value})\n"

            elif param_type == 'boolean':
                code += f"    {param_name} = st.checkbox('{param_name}', value={param_value})\n"

            elif param_type == 'categorical':
                if isinstance(param_value, list):
                    options = param_value
                    code += f"    {param_name} = st.selectbox('{param_name}', options={options})\n"
                else:
                    code += f"    {param_name} = st.text_input('{param_name}', value='{param_value}')\n"

            elif param_type == 'date':
                code += f"    {param_name} = st.date_input('{param_name}')\n"

            else:  # string or path
                code += f"    {param_name} = st.text_input('{param_name}', value='{param_value}')\n"

        return code

    def _generate_data_preview(self) -> str:
        """
        Generate data preview section.

        Returns:
            Data preview code as string
        """
        return '''
# Main Content Area
if df is not None:
    # Data Preview Section
    st.header("📋 Data Preview")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows", len(df))
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        st.metric("Memory", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

    with st.expander("View Data Sample"):
        st.dataframe(df.head(20), use_container_width=True)

    with st.expander("Data Statistics"):
        st.dataframe(df.describe(), use_container_width=True)

    with st.expander("Column Info"):
        info_df = pd.DataFrame({
            'Column': df.columns,
            'Type': df.dtypes.values,
            'Non-Null': df.count().values,
            'Null': df.isnull().sum().values
        })
        st.dataframe(info_df, use_container_width=True)

    st.markdown("---")
'''

    def _generate_visualizations(self) -> str:
        """
        Generate visualization section.

        Returns:
            Visualization code as string
        """
        code = '''
    # Visualizations Section
    st.header("📊 Visualizations")

    # Get numeric and categorical columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    if len(numeric_cols) >= 2:
        # Line Chart
        st.subheader("Line Chart")
        col1, col2 = st.columns(2)
        with col1:
            x_col = st.selectbox("X-axis", df.columns, key='line_x')
        with col2:
            y_col = st.selectbox("Y-axis", numeric_cols, key='line_y')

        if x_col and y_col:
            fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} over {x_col}")
            st.plotly_chart(fig, use_container_width=True)

        # Scatter Plot
        st.subheader("Scatter Plot")
        col1, col2 = st.columns(2)
        with col1:
            scatter_x = st.selectbox("X-axis", numeric_cols, key='scatter_x')
        with col2:
            scatter_y = st.selectbox("Y-axis", numeric_cols, key='scatter_y', index=min(1, len(numeric_cols)-1))

        if scatter_x and scatter_y:
            fig = px.scatter(df, x=scatter_x, y=scatter_y, title=f"{scatter_y} vs {scatter_x}")
            st.plotly_chart(fig, use_container_width=True)

        # Bar Chart
        if categorical_cols and numeric_cols:
            st.subheader("Bar Chart")
            col1, col2 = st.columns(2)
            with col1:
                bar_x = st.selectbox("Category", categorical_cols, key='bar_x')
            with col2:
                bar_y = st.selectbox("Value", numeric_cols, key='bar_y')

            if bar_x and bar_y:
                # Aggregate data
                agg_df = df.groupby(bar_x)[bar_y].mean().reset_index()
                fig = px.bar(agg_df, x=bar_x, y=bar_y, title=f"Average {bar_y} by {bar_x}")
                st.plotly_chart(fig, use_container_width=True)

        # Histogram
        st.subheader("Histogram")
        hist_col = st.selectbox("Select column", numeric_cols, key='hist_col')
        if hist_col:
            fig = px.histogram(df, x=hist_col, title=f"Distribution of {hist_col}")
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Upload data with numeric columns to see visualizations")
'''
        return code

    def _generate_export_section(self) -> str:
        """
        Generate export functionality section.

        Returns:
            Export section code as string
        """
        return '''
    # Export Section
    st.markdown("---")
    st.header("💾 Export Data")

    col1, col2 = st.columns(2)

    with col1:
        # Export to CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="analysis_data.csv",
            mime="text/csv"
        )

    with col2:
        # Export to Excel
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)
        st.download_button(
            label="📥 Download Excel",
            data=buffer,
            file_name="analysis_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.info("👆 Please upload a data file in the sidebar to begin your analysis")
'''

    def _assemble_app(self, components: Dict, modules: Dict) -> str:
        """
        Assemble all components into a complete Streamlit app.

        Args:
            components: Dictionary of app components
            modules: Dictionary of code modules

        Returns:
            Complete app code as string
        """
        app_parts = [
            components['imports'],
            "",
            components['title'],
            components['sidebar'],
            components['data_upload'],
            components['parameters'],
            "",
            components['data_preview'],
            components['visualizations'],
            components['export'],
        ]

        return '\n'.join(app_parts)

    def _generate_file_structure(self) -> Dict:
        """
        Generate suggested file structure for the app.

        Returns:
            Dictionary describing file structure
        """
        return {
            'app.py': 'Main Streamlit application',
            'requirements.txt': 'Python dependencies',
            'config.json': 'Configuration file',
            'modules/': {
                'data_loading.py': 'Data loading functions',
                'processing.py': 'Data processing functions',
                'visualization.py': 'Visualization functions'
            },
            'README.md': 'Application documentation'
        }

    def generate_readme(self, notebook_name: str = "notebook") -> str:
        """
        Generate README.md content for the app.

        Args:
            notebook_name: Name of the original notebook

        Returns:
            README content as string
        """
        readme = f'''# Interactive Data Analysis App

This Streamlit application was automatically generated from the Jupyter notebook: `{notebook_name}.ipynb`

## Features

- 📁 Data upload (CSV/Excel)
- 📊 Interactive visualizations
- 🎛️ Configurable parameters
- 💾 Data export functionality

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

The app will open in your default web browser at `http://localhost:8501`

## Requirements

See `requirements.txt` for a list of dependencies.

## Data

Upload your data file using the sidebar. Supported formats:
- CSV (.csv)
- Excel (.xlsx, .xls)

## Visualizations

The app automatically generates:
- Line charts
- Scatter plots
- Bar charts
- Histograms

## Export

Export your processed data:
- CSV format
- Excel format

## About

This app was generated using the Jupyter Notebook to Web Application Converter.
'''
        return readme

    def save_app(self, output_dir: str, notebook_name: str = "notebook"):
        """
        Save the generated app to files.

        Args:
            output_dir: Directory to save the app files
            notebook_name: Name of the original notebook
        """
        import os

        os.makedirs(output_dir, exist_ok=True)

        # Save main app file
        with open(os.path.join(output_dir, 'app.py'), 'w') as f:
            f.write(self.app_code)

        # Save README
        with open(os.path.join(output_dir, 'README.md'), 'w') as f:
            f.write(self.generate_readme(notebook_name))

        # Save requirements.txt (if available)
        # This would be passed from CodeTransformer

        print(f"App saved to {output_dir}/")
