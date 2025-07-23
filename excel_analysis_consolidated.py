#!/usr/bin/env python3
"""
Consolidated Excel Analysis Tools
Contains the essential Excel reading capabilities for reference.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from typing import Dict, List, Any, Optional

class ExcelAnalyzer:
    """Consolidated Excel analysis for pro forma reference."""
    
    def __init__(self, excel_path: str):
        self.excel_path = Path(excel_path)
        self.workbook = None
        
    def read_excel_structure(self) -> Dict[str, Any]:
        """Read and analyze Excel file structure."""
        
        if not self.excel_path.exists():
            raise FileNotFoundError(f"Excel file not found: {self.excel_path}")
        
        try:
            # Read all sheets
            excel_data = pd.read_excel(self.excel_path, sheet_name=None, engine='openpyxl')
            
            structure = {
                'file_path': str(self.excel_path),
                'total_sheets': len(excel_data),
                'sheet_names': list(excel_data.keys()),
                'sheets': {}
            }
            
            for sheet_name, df in excel_data.items():
                structure['sheets'][sheet_name] = {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': list(df.columns),
                    'has_data': not df.empty,
                    'sample_data': df.head(3).to_dict('records') if not df.empty else []
                }
            
            return structure
            
        except Exception as e:
            return {'error': f"Failed to read Excel file: {str(e)}"}
    
    def extract_pro_forma_parameters(self) -> Dict[str, Any]:
        """Extract key pro forma parameters from Excel."""
        
        try:
            # Read the main pro forma sheet (assuming first sheet)
            df = pd.read_excel(self.excel_path, sheet_name=0, engine='openpyxl')
            
            # Look for key pro forma metrics in the data
            parameters = {
                'interest_rate': self._find_parameter(df, ['interest', 'rate', 'loan']),
                'vacancy_rate': self._find_parameter(df, ['vacancy', 'vacant']),
                'rent_growth': self._find_parameter(df, ['rent', 'growth', 'increase']),
                'cap_rate': self._find_parameter(df, ['cap', 'rate', 'capitalization']),
                'ltv': self._find_parameter(df, ['ltv', 'loan to value']),
                'closing_costs': self._find_parameter(df, ['closing', 'cost']),
                'property_growth': self._find_parameter(df, ['property', 'appreciation', 'growth']),
                'expense_growth': self._find_parameter(df, ['expense', 'operating', 'growth'])
            }
            
            return parameters
            
        except Exception as e:
            return {'error': f"Failed to extract parameters: {str(e)}"}
    
    def _find_parameter(self, df: pd.DataFrame, keywords: List[str]) -> Optional[float]:
        """Find parameter value by searching for keywords."""
        
        for col in df.columns:
            if any(keyword.lower() in str(col).lower() for keyword in keywords):
                # Look for numeric values in this column
                numeric_values = df[col].dropna()
                numeric_values = pd.to_numeric(numeric_values, errors='coerce').dropna()
                if not numeric_values.empty:
                    return float(numeric_values.iloc[0])
        
        # Search in all cells if not found in columns
        for col in df.columns:
            for idx, value in df[col].items():
                if isinstance(value, str) and any(keyword.lower() in value.lower() for keyword in keywords):
                    # Look for numbers in adjacent cells
                    for check_col in df.columns:
                        try:
                            adjacent_value = pd.to_numeric(df.loc[idx, check_col], errors='coerce')
                            if not pd.isna(adjacent_value):
                                return float(adjacent_value)
                        except:
                            continue
        
        return None

def analyze_reference_excel():
    """Analyze the reference Excel file."""
    
    excel_path = Path(__file__).parent / "Reference_ Docs" / "MultiFamily_RE_Pro_Forma.xlsx"
    
    if not excel_path.exists():
        print(f"Reference Excel file not found at: {excel_path}")
        return
    
    analyzer = ExcelAnalyzer(excel_path)
    
    print("EXCEL STRUCTURE ANALYSIS")
    print("=" * 50)
    
    structure = analyzer.read_excel_structure()
    if 'error' in structure:
        print(f"Error: {structure['error']}")
        return
    
    print(f"File: {structure['file_path']}")
    print(f"Sheets: {structure['total_sheets']}")
    print(f"Sheet Names: {', '.join(structure['sheet_names'])}")
    
    for sheet_name, sheet_info in structure['sheets'].items():
        print(f"\n{sheet_name}:")
        print(f"  Dimensions: {sheet_info['rows']} rows x {sheet_info['columns']} columns")
        print(f"  Has Data: {sheet_info['has_data']}")
    
    print("\nPRO FORMA PARAMETERS")
    print("=" * 50)
    
    parameters = analyzer.extract_pro_forma_parameters()
    if 'error' in parameters:
        print(f"Error: {parameters['error']}")
        return
    
    for param_name, value in parameters.items():
        status = f"{value}" if value is not None else "Not found"
        print(f"{param_name}: {status}")

if __name__ == "__main__":
    analyze_reference_excel()