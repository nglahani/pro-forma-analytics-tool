"""
Web-Based Property Input Forms

Provides HTML form generation and Flask endpoints for web-based
property data collection. This is an optional component for
web interface development.
"""

from typing import Dict, List, Optional, Any
from datetime import date
import json

from core.property_inputs import PropertyInputData, PropertyType, PropertyClass
from user_input.input_validation import PropertyInputValidator, PropertyInputHelper
from user_input.property_collector import PropertyInputCollector


class PropertyWebFormGenerator:
    """Generates HTML forms for web-based property input."""
    
    def __init__(self):
        self.validator = PropertyInputValidator()
        self.helper = PropertyInputHelper()
    
    def generate_property_form_html(self) -> str:
        """Generate complete HTML form for property input."""
        
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Property Data Input - Pro Forma Analytics</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            background-color: #f5f5f5;
        }
        .form-container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .section {
            margin-bottom: 30px;
            padding: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
        }
        .section h3 {
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
            color: #555;
        }
        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
        }
        .form-row {
            display: flex;
            gap: 15px;
        }
        .form-row .form-group {
            flex: 1;
        }
        .required {
            color: #dc3545;
        }
        .help-text {
            font-size: 12px;
            color: #666;
            margin-top: 3px;
        }
        .submit-btn {
            background: #007bff;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            margin-top: 20px;
        }
        .submit-btn:hover {
            background: #0056b3;
        }
        .error {
            color: #dc3545;
            font-size: 12px;
            margin-top: 3px;
        }
        .unit-mix-container {
            border: 1px solid #e0e0e0;
            padding: 15px;
            margin-top: 10px;
            border-radius: 4px;
        }
        .unit-row {
            display: flex;
            gap: 10px;
            align-items: end;
            margin-bottom: 10px;
        }
        .add-unit-btn {
            background: #28a745;
            color: white;
            padding: 8px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        .remove-unit-btn {
            background: #dc3545;
            color: white;
            padding: 5px 10px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="form-container">
        <h1>🏢 Property Data Input</h1>
        <p>Please provide comprehensive information about your property for pro forma analysis.</p>
        
        <form id="propertyForm" action="/api/property" method="POST">
            
            <!-- Basic Information -->
            <div class="section">
                <h3>📋 Basic Information</h3>
                
                <div class="form-group">
                    <label for="property_name">Property Name <span class="required">*</span></label>
                    <input type="text" id="property_name" name="property_name" required 
                           placeholder="e.g., Sunset Apartments, Downtown Office Complex">
                    <div class="help-text">A descriptive name for this property</div>
                </div>
                
                <div class="form-group">
                    <label for="analysis_date">Analysis Date</label>
                    <input type="date" id="analysis_date" name="analysis_date" value="{current_date}">
                    <div class="help-text">Date for this analysis (defaults to today)</div>
                </div>
            </div>
            
            <!-- Physical Characteristics -->
            <div class="section">
                <h3>🏗️ Physical Characteristics</h3>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="property_type">Property Type <span class="required">*</span></label>
                        <select id="property_type" name="property_type" required>
                            {property_type_options}
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="property_class">Property Class <span class="required">*</span></label>
                        <select id="property_class" name="property_class" required>
                            {property_class_options}
                        </select>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="total_units">Total Units <span class="required">*</span></label>
                        <input type="number" id="total_units" name="total_units" required min="1">
                        <div class="help-text">Number of rentable units</div>
                    </div>
                    
                    <div class="form-group">
                        <label for="total_square_feet">Total Square Feet <span class="required">*</span></label>
                        <input type="number" id="total_square_feet" name="total_square_feet" required min="1000">
                        <div class="help-text">Total rentable square footage</div>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="year_built">Year Built <span class="required">*</span></label>
                        <input type="number" id="year_built" name="year_built" required min="1800" max="{current_year}">
                    </div>
                    
                    <div class="form-group">
                        <label for="year_renovated">Year Renovated</label>
                        <input type="number" id="year_renovated" name="year_renovated" min="1800" max="{current_year}">
                        <div class="help-text">Year of last major renovation (optional)</div>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="parking_spaces">Parking Spaces</label>
                        <input type="number" id="parking_spaces" name="parking_spaces" min="0">
                    </div>
                    
                    <div class="form-group">
                        <label for="stories">Stories</label>
                        <input type="number" id="stories" name="stories" min="1">
                    </div>
                </div>
            </div>
            
            <!-- Financial Information -->
            <div class="section">
                <h3>💰 Financial Information</h3>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="purchase_price">Purchase Price <span class="required">*</span></label>
                        <input type="number" id="purchase_price" name="purchase_price" required min="1" step="1000">
                        <div class="help-text">Total acquisition cost ($)</div>
                    </div>
                    
                    <div class="form-group">
                        <label for="down_payment_pct">Down Payment <span class="required">*</span></label>
                        <input type="number" id="down_payment_pct" name="down_payment_pct" required 
                               min="0" max="100" step="0.1">
                        <div class="help-text">Percentage (e.g., 25 for 25%)</div>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="current_noi">Current Annual NOI</label>
                        <input type="number" id="current_noi" name="current_noi" step="1000">
                        <div class="help-text">Net Operating Income ($)</div>
                    </div>
                    
                    <div class="form-group">
                        <label for="current_gross_rent">Current Annual Gross Rent</label>
                        <input type="number" id="current_gross_rent" name="current_gross_rent" step="1000">
                        <div class="help-text">Total rental income ($)</div>
                    </div>
                </div>
            </div>
            
            <!-- Location Information -->
            <div class="section">
                <h3>📍 Location Information</h3>
                
                <div class="form-group">
                    <label for="address">Street Address <span class="required">*</span></label>
                    <input type="text" id="address" name="address" required 
                           placeholder="123 Main Street">
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="city">City <span class="required">*</span></label>
                        <input type="text" id="city" name="city" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="state">State <span class="required">*</span></label>
                        <input type="text" id="state" name="state" required maxlength="2" 
                               placeholder="CA" style="text-transform: uppercase;">
                    </div>
                    
                    <div class="form-group">
                        <label for="zip_code">ZIP Code <span class="required">*</span></label>
                        <input type="text" id="zip_code" name="zip_code" required 
                               pattern="[0-9]{{5}}(-[0-9]{{4}})?" placeholder="90210">
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="msa_code">Metropolitan Area <span class="required">*</span></label>
                    <select id="msa_code" name="msa_code" required>
                        {msa_options}
                    </select>
                    <div class="help-text">Select the closest metropolitan statistical area</div>
                </div>
            </div>
            
            <!-- Operating Information -->
            <div class="section">
                <h3>⚙️ Operating Information</h3>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="management_fee_pct">Management Fee</label>
                        <input type="number" id="management_fee_pct" name="management_fee_pct" 
                               value="5" min="0" max="20" step="0.1">
                        <div class="help-text">Percentage (default: 5%)</div>
                    </div>
                    
                    <div class="form-group">
                        <label for="maintenance_reserve_pct">Maintenance Reserve</label>
                        <input type="number" id="maintenance_reserve_pct" name="maintenance_reserve_pct" 
                               value="2" min="0" max="10" step="0.1">
                        <div class="help-text">Percentage (default: 2%)</div>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="insurance_annual">Annual Insurance</label>
                        <input type="number" id="insurance_annual" name="insurance_annual" step="100">
                        <div class="help-text">Annual insurance cost ($)</div>
                    </div>
                    
                    <div class="form-group">
                        <label for="property_tax_annual">Annual Property Tax</label>
                        <input type="number" id="property_tax_annual" name="property_tax_annual" step="100">
                        <div class="help-text">Annual property tax ($)</div>
                    </div>
                </div>
            </div>
            
            <!-- Unit Mix (for Multifamily) -->
            <div class="section" id="unit_mix_section" style="display: none;">
                <h3>🏠 Unit Mix</h3>
                <p>Specify the unit types and rents for your multifamily property.</p>
                
                <div id="unit_mix_container">
                    <!-- Unit mix rows will be added dynamically -->
                </div>
                
                <button type="button" class="add-unit-btn" onclick="addUnitRow()">+ Add Unit Type</button>
            </div>
            
            <button type="submit" class="submit-btn">🚀 Analyze Property</button>
        </form>
    </div>
    
    <script>
        // Show/hide unit mix section based on property type
        document.getElementById('property_type').addEventListener('change', function() {{
            const unitMixSection = document.getElementById('unit_mix_section');
            if (this.value === 'multifamily') {{
                unitMixSection.style.display = 'block';
                if (document.querySelectorAll('.unit-row').length === 0) {{
                    addUnitRow();
                }}
            }} else {{
                unitMixSection.style.display = 'none';
            }}
        }});
        
        // Auto-format currency inputs
        ['purchase_price', 'current_noi', 'current_gross_rent', 'insurance_annual', 'property_tax_annual'].forEach(id => {{
            const input = document.getElementById(id);
            if (input) {{
                input.addEventListener('blur', function() {{
                    if (this.value) {{
                        this.value = parseInt(this.value).toLocaleString();
                    }}
                }});
                input.addEventListener('focus', function() {{
                    this.value = this.value.replace(/,/g, '');
                }});
            }}
        }});
        
        // Unit mix management
        let unitCounter = 0;
        
        function addUnitRow() {{
            unitCounter++;
            const container = document.getElementById('unit_mix_container');
            const row = document.createElement('div');
            row.className = 'unit-row';
            row.innerHTML = `
                <div class="form-group" style="flex: 2;">
                    <label>Unit Type</label>
                    <input type="text" name="unit_type_${{unitCounter}}" placeholder="e.g., 1BR/1BA" required>
                </div>
                <div class="form-group" style="flex: 1;">
                    <label>Count</label>
                    <input type="number" name="unit_count_${{unitCounter}}" min="1" required>
                </div>
                <div class="form-group" style="flex: 1;">
                    <label>Avg SF</label>
                    <input type="number" name="unit_sqft_${{unitCounter}}" min="200" required>
                </div>
                <div class="form-group" style="flex: 1;">
                    <label>Monthly Rent</label>
                    <input type="number" name="unit_rent_${{unitCounter}}" min="100" step="50" required>
                </div>
                <div class="form-group" style="flex: 0;">
                    <label>&nbsp;</label>
                    <button type="button" class="remove-unit-btn" onclick="removeUnitRow(this)">Remove</button>
                </div>
            `;
            container.appendChild(row);
        }}
        
        function removeUnitRow(button) {{
            button.closest('.unit-row').remove();
        }}
        
        // Form validation and submission
        document.getElementById('propertyForm').addEventListener('submit', function(e) {{
            e.preventDefault();
            
            // Collect form data
            const formData = new FormData(this);
            const data = {{}};
            
            // Convert FormData to object
            for (let [key, value] of formData.entries()) {{
                data[key] = value;
            }}
            
            // Collect unit mix data
            const unitMix = [];
            const unitRows = document.querySelectorAll('.unit-row');
            unitRows.forEach((row, index) => {{
                const inputs = row.querySelectorAll('input');
                if (inputs.length === 4 && inputs[0].value) {{
                    unitMix.push({{
                        unit_type: inputs[0].value,
                        count: parseInt(inputs[1].value) || 0,
                        avg_square_feet: parseInt(inputs[2].value) || 0,
                        current_rent: parseFloat(inputs[3].value) || 0
                    }});
                }}
            }});
            data.unit_mix = unitMix;
            
            // Submit to backend
            fetch('/api/property', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify(data)
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    alert('Property data saved successfully! Property ID: ' + data.property_id);
                    window.location.href = '/analysis/' + data.property_id;
                }} else {{
                    alert('Error: ' + data.error);
                }}
            }})
            .catch(error => {{
                console.error('Error:', error);
                alert('Error submitting form. Please try again.');
            }});
        }});
    </script>
</body>
</html>
        """
        
        # Format the HTML with current data
        current_date = date.today().isoformat()
        current_year = date.today().year
        
        # Generate options
        property_type_options = self._generate_select_options(
            self.helper.get_property_type_options()
        )
        property_class_options = self._generate_select_options(
            self.helper.get_property_class_options()
        )
        msa_options = self._generate_select_options(
            self.helper.get_supported_msas()
        )
        
        return html.format(
            current_date=current_date,
            current_year=current_year,
            property_type_options=property_type_options,
            property_class_options=property_class_options,
            msa_options=msa_options
        )
    
    def _generate_select_options(self, options: List[tuple]) -> str:
        """Generate HTML option tags from list of (value, display) tuples."""
        option_html = '<option value="">Select...</option>\n'
        for value, display in options:
            option_html += f'<option value="{value}">{display}</option>\n'
        return option_html


class PropertyWebAPI:
    """Flask-compatible API endpoints for property data collection."""
    
    def __init__(self):
        self.collector = PropertyInputCollector()
        self.validator = PropertyInputValidator()
    
    def handle_property_submission(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle web form submission and create property data."""
        
        try:
            # Validate and convert form data
            property_data = self._convert_form_to_property_data(form_data)
            
            # Add to property manager
            from core.property_inputs import property_manager
            property_manager.add_property(property_data)
            
            return {
                'success': True,
                'property_id': property_data.property_id,
                'message': f'Property "{property_data.property_name}" saved successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _convert_form_to_property_data(self, form_data: Dict[str, Any]) -> PropertyInputData:
        """Convert web form data to PropertyInputData object."""
        
        # Generate property ID
        import uuid
        property_id = f"WEB_{uuid.uuid4().hex[:8].upper()}"
        
        # Basic info
        property_name = form_data.get('property_name', '').strip()
        if not property_name:
            raise ValueError("Property name is required")
        
        analysis_date_str = form_data.get('analysis_date')
        if analysis_date_str:
            analysis_date = date.fromisoformat(analysis_date_str)
        else:
            analysis_date = date.today()
        
        # Physical info
        from core.property_inputs import PropertyPhysicalInfo, PropertyType, PropertyClass
        
        physical_info = PropertyPhysicalInfo(
            property_type=PropertyType(form_data.get('property_type')),
            property_class=PropertyClass(form_data.get('property_class')),
            total_units=int(form_data.get('total_units', 0)),
            total_square_feet=int(form_data.get('total_square_feet', 0)),
            year_built=int(form_data.get('year_built', 0)),
            year_renovated=int(form_data.get('year_renovated')) if form_data.get('year_renovated') else None,
            parking_spaces=int(form_data.get('parking_spaces')) if form_data.get('parking_spaces') else None,
            stories=int(form_data.get('stories')) if form_data.get('stories') else None
        )
        
        # Financial info
        from core.property_inputs import PropertyFinancialInfo
        
        # Convert percentage from 0-100 to 0-1
        down_payment_pct = float(form_data.get('down_payment_pct', 0)) / 100
        
        financial_info = PropertyFinancialInfo(
            purchase_price=float(form_data.get('purchase_price', 0)),
            down_payment_pct=down_payment_pct,
            current_noi=float(form_data.get('current_noi')) if form_data.get('current_noi') else None,
            current_gross_rent=float(form_data.get('current_gross_rent')) if form_data.get('current_gross_rent') else None
        )
        
        # Location info
        from core.property_inputs import PropertyLocationInfo
        
        location_info = PropertyLocationInfo(
            address=form_data.get('address', '').strip(),
            city=form_data.get('city', '').strip(),
            state=form_data.get('state', '').strip().upper(),
            zip_code=form_data.get('zip_code', '').strip(),
            msa_code=form_data.get('msa_code', '').strip()
        )
        
        # Operating info
        from core.property_inputs import PropertyOperatingInfo, UnitMix
        
        # Convert percentages from 0-100 to 0-1
        mgmt_fee = float(form_data.get('management_fee_pct', 5)) / 100
        maint_reserve = float(form_data.get('maintenance_reserve_pct', 2)) / 100
        
        # Handle unit mix
        unit_mix = []
        if 'unit_mix' in form_data and form_data['unit_mix']:
            for unit_data in form_data['unit_mix']:
                if unit_data.get('unit_type'):
                    unit_mix.append(UnitMix(
                        unit_type=unit_data['unit_type'],
                        count=int(unit_data.get('count', 0)),
                        avg_square_feet=int(unit_data.get('avg_square_feet', 0)),
                        current_rent=float(unit_data.get('current_rent', 0))
                    ))
        
        operating_info = PropertyOperatingInfo(
            management_fee_pct=mgmt_fee,
            maintenance_reserve_pct=maint_reserve,
            insurance_annual=float(form_data.get('insurance_annual')) if form_data.get('insurance_annual') else None,
            property_tax_annual=float(form_data.get('property_tax_annual')) if form_data.get('property_tax_annual') else None,
            unit_mix=unit_mix
        )
        
        # Create property data
        return PropertyInputData(
            property_id=property_id,
            property_name=property_name,
            analysis_date=analysis_date,
            physical_info=physical_info,
            financial_info=financial_info,
            location_info=location_info,
            operating_info=operating_info
        )


# Flask integration example (optional)
def create_flask_app():
    """Create Flask app with property input endpoints."""
    try:
        from flask import Flask, render_template_string, request, jsonify
        
        app = Flask(__name__)
        form_generator = PropertyWebFormGenerator()
        web_api = PropertyWebAPI()
        
        @app.route('/')
        def index():
            """Serve the property input form."""
            return form_generator.generate_property_form_html()
        
        @app.route('/api/property', methods=['POST'])
        def submit_property():
            """Handle property form submission."""
            form_data = request.get_json()
            result = web_api.handle_property_submission(form_data)
            return jsonify(result)
        
        @app.route('/analysis/<property_id>')
        def analysis_results(property_id):
            """Show analysis results for a property."""
            # This would integrate with your Monte Carlo analysis
            return f"<h1>Analysis Results for Property {property_id}</h1><p>Monte Carlo analysis would be displayed here.</p>"
        
        return app
        
    except ImportError:
        print("Flask not installed. Web interface not available.")
        return None