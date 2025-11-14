"""
Notebook Converter Main Module

This module orchestrates the complete conversion pipeline from Jupyter Notebook
to interactive Streamlit web application.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

from .parser.notebook_parser import NotebookParser
from .analyzer.code_analyzer import CodeAnalyzer
from .analyzer.visualization_extractor import VisualizationExtractor
from .transformer.code_transformer import CodeTransformer
from .generator.web_app_generator import WebAppGenerator


class NotebookConverter:
    """
    Main orchestrator for notebook to web application conversion.

    This class coordinates the entire conversion pipeline:
    1. Parse notebook using NotebookParser
    2. Analyze code using CodeAnalyzer and VisualizationExtractor
    3. Transform code using CodeTransformer
    4. Generate web app using WebAppGenerator

    Attributes:
        notebook_path (str): Path to the input notebook
        output_dir (str): Directory for output files
        parser (NotebookParser): Parser instance
        analyzer (CodeAnalyzer): Analyzer instance
        viz_extractor (VisualizationExtractor): Visualization extractor instance
        transformer (CodeTransformer): Transformer instance
        generator (WebAppGenerator): Generator instance
        conversion_result (dict): Complete conversion result
    """

    def __init__(self, notebook_path: Optional[str] = None, output_dir: Optional[str] = None):
        """
        Initialize the NotebookConverter.

        Args:
            notebook_path: Path to the Jupyter Notebook file
            output_dir: Directory to save output files
        """
        self.notebook_path = notebook_path
        self.output_dir = output_dir or './converted_app'

        # Initialize components
        self.parser = NotebookParser(notebook_path)
        self.analyzer = CodeAnalyzer()
        self.viz_extractor = VisualizationExtractor()
        self.transformer = CodeTransformer()
        self.generator = WebAppGenerator()

        self.conversion_result = {}

    def convert(self, notebook_path: Optional[str] = None, output_dir: Optional[str] = None) -> Dict:
        """
        Convert a Jupyter Notebook to a Streamlit web application.

        This is the main entry point that executes the complete conversion pipeline.

        Args:
            notebook_path: Path to notebook file (overrides constructor path)
            output_dir: Output directory (overrides constructor output_dir)

        Returns:
            Dictionary containing:
                - app_code: Generated Streamlit application code
                - modules: Transformed code modules
                - config: Configuration dictionary
                - requirements: List of dependencies
                - parse_info: Parsing information
                - analysis_info: Code analysis results
                - viz_info: Visualization extraction results
                - success: Boolean indicating success
                - errors: List of errors if any

        Raises:
            FileNotFoundError: If notebook file doesn't exist
            ValueError: If conversion fails
        """
        path = notebook_path or self.notebook_path
        out_dir = output_dir or self.output_dir

        if not path:
            raise ValueError("No notebook path provided")

        try:
            # Stage 1: Parse Notebook
            print(f"📖 Parsing notebook: {path}")
            parse_result = self.parser.parse(path)
            print(f"✅ Parsed {parse_result['cell_count']} cells in {parse_result['parse_time']:.2f}s")

            # Stage 2: Analyze Code
            print("🔍 Analyzing code...")
            code_cells = parse_result['code_cells']
            all_parameters = []

            for idx, cell in enumerate(code_cells):
                source = cell.source if hasattr(cell, 'source') else str(cell)
                if source.strip():
                    analysis = self.analyzer.analyze(source)
                    parameters = analysis.get('parameters', [])
                    all_parameters.extend(parameters)

            print(f"✅ Identified {len(all_parameters)} parameters")

            # Stage 3: Extract Visualizations
            print("📊 Extracting visualizations...")
            all_visualizations = []

            for cell in code_cells:
                source = cell.source if hasattr(cell, 'source') else str(cell)
                if source.strip():
                    viz_list = self.viz_extractor.extract(source)
                    all_visualizations.extend(viz_list)

            print(f"✅ Found {len(all_visualizations)} visualizations")

            # Stage 4: Transform Code
            print("🔄 Transforming code to modules...")
            transform_result = self.transformer.transform(code_cells)
            modules = transform_result['modules']
            config = transform_result['config']
            requirements = transform_result['requirements']

            print(f"✅ Created {len(modules)} modules")

            # Stage 5: Generate Web Application
            print("🚀 Generating Streamlit application...")
            app_result = self.generator.generate(
                modules=modules,
                config=config,
                parameters=all_parameters
            )

            print(f"✅ Generated Streamlit app ({len(app_result['app_code'])} characters)")

            # Compile results
            self.conversion_result = {
                'app_code': app_result['app_code'],
                'modules': modules,
                'config': config,
                'requirements': requirements,
                'parse_info': {
                    'total_cells': parse_result['cell_count'],
                    'code_cells': len(code_cells),
                    'markdown_cells': len(parse_result['markdown_cells']),
                    'parse_time': parse_result['parse_time']
                },
                'analysis_info': {
                    'parameters_found': len(all_parameters),
                    'parameters': all_parameters
                },
                'viz_info': {
                    'visualizations_found': len(all_visualizations),
                    'visualizations': all_visualizations
                },
                'success': True,
                'errors': []
            }

            # Save files if output directory specified
            if out_dir:
                self._save_output(out_dir, app_result)
                print(f"💾 Saved application to: {out_dir}")

            print("✨ Conversion complete!")
            return self.conversion_result

        except Exception as e:
            error_msg = f"Conversion failed: {str(e)}"
            print(f"❌ {error_msg}")
            self.conversion_result = {
                'success': False,
                'errors': [error_msg],
                'app_code': None,
                'modules': None,
                'config': None,
                'requirements': None
            }
            return self.conversion_result

    def _save_output(self, output_dir: str, app_result: Dict):
        """
        Save generated files to output directory.

        Args:
            output_dir: Directory to save files
            app_result: Application generation result
        """
        os.makedirs(output_dir, exist_ok=True)

        # Save main app file
        app_path = os.path.join(output_dir, 'app.py')
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(app_result['app_code'])

        # Save requirements.txt
        if self.conversion_result.get('requirements'):
            req_path = os.path.join(output_dir, 'requirements.txt')
            with open(req_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.conversion_result['requirements']))
                # Add openpyxl for Excel export
                f.write('\nopenpyxl\n')

        # Save config.json
        if self.conversion_result.get('config'):
            import json
            config_path = os.path.join(output_dir, 'config.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.conversion_result['config'], f, indent=2)

        # Save README
        notebook_name = Path(self.notebook_path).stem if self.notebook_path else "notebook"
        readme_path = os.path.join(output_dir, 'README.md')
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(self.generator.generate_readme(notebook_name))

    def get_summary(self) -> Dict:
        """
        Get a summary of the conversion results.

        Returns:
            Dictionary with conversion summary
        """
        if not self.conversion_result:
            return {'status': 'not_converted'}

        if not self.conversion_result.get('success'):
            return {
                'status': 'failed',
                'errors': self.conversion_result.get('errors', [])
            }

        return {
            'status': 'success',
            'cells_processed': self.conversion_result['parse_info']['total_cells'],
            'code_cells': self.conversion_result['parse_info']['code_cells'],
            'parameters_found': self.conversion_result['analysis_info']['parameters_found'],
            'visualizations_found': self.conversion_result['viz_info']['visualizations_found'],
            'modules_created': len(self.conversion_result['modules']),
            'dependencies': len(self.conversion_result['requirements']),
            'parse_time': self.conversion_result['parse_info']['parse_time'],
            'app_code_size': len(self.conversion_result['app_code'])
        }

    def validate_notebook(self, notebook_path: Optional[str] = None) -> Dict:
        """
        Validate a notebook before conversion.

        Args:
            notebook_path: Path to notebook file

        Returns:
            Dictionary with validation results
        """
        path = notebook_path or self.notebook_path
        if not path:
            return {'valid': False, 'error': 'No notebook path provided'}

        path_obj = Path(path)
        if not path_obj.exists():
            return {'valid': False, 'error': 'Notebook file not found'}

        if not path_obj.suffix == '.ipynb':
            return {'valid': False, 'error': 'File is not a Jupyter Notebook (.ipynb)'}

        try:
            parse_result = self.parser.parse(path)
            return {
                'valid': True,
                'cells': parse_result['cell_count'],
                'code_cells': len(parse_result['code_cells']),
                'has_content': parse_result['cell_count'] > 0
            }
        except Exception as e:
            return {'valid': False, 'error': str(e)}

    def get_conversion_report(self) -> str:
        """
        Generate a detailed conversion report.

        Returns:
            Markdown-formatted report string
        """
        if not self.conversion_result or not self.conversion_result.get('success'):
            return "# Conversion Report\n\nConversion has not been completed or failed."

        summary = self.get_summary()

        report = f"""# Notebook Conversion Report

## Summary

- **Status**: {summary['status'].upper()}
- **Total Cells**: {summary['cells_processed']}
- **Code Cells**: {summary['code_cells']}
- **Parse Time**: {summary['parse_time']:.2f}s

## Analysis Results

### Parameters
- **Parameters Identified**: {summary['parameters_found']}

"""

        # Add parameter details
        params = self.conversion_result['analysis_info']['parameters']
        if params:
            report += "| Parameter | Type | Value |\n|-----------|------|-------|\n"
            for param in params[:10]:  # Show first 10
                report += f"| {param['name']} | {param['type']} | {param['value']} |\n"
            if len(params) > 10:
                report += f"\n*... and {len(params) - 10} more parameters*\n"

        report += f"""
### Visualizations
- **Visualizations Found**: {summary['visualizations_found']}

"""

        # Add visualization details
        viz_list = self.conversion_result['viz_info']['visualizations']
        if viz_list:
            report += "| Library | Chart Type | Function |\n|---------|-----------|----------|\n"
            for viz in viz_list[:10]:  # Show first 10
                report += f"| {viz['library']} | {viz['chart_type']} | {viz['function_call']} |\n"
            if len(viz_list) > 10:
                report += f"\n*... and {len(viz_list) - 10} more visualizations*\n"

        report += f"""
## Generated Output

### Modules
- **Total Modules**: {summary['modules_created']}
- **Dependencies**: {summary['dependencies']}

### Application
- **App Code Size**: {summary['app_code_size']} characters
- **Framework**: Streamlit

## Dependencies

```
{chr(10).join(self.conversion_result['requirements'])}
```

## Next Steps

1. Navigate to the output directory
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `streamlit run app.py`
4. Access at http://localhost:8501

---
*Generated by Notebook Converter*
"""

        return report
