#!/usr/bin/env python3
"""
Test script to demonstrate template variable validation functionality
"""

import re
import pandas as pd
from io import StringIO

def extract_template_variables(template_body: str):
    """Extract all template variables from template body using regex."""
    # Pattern to match {VARIABLE_NAME} format
    pattern = r'\{([A-Z_][A-Z0-9_]*)\}'
    variables = re.findall(pattern, template_body)
    return set(variables)

def validate_template_variables(template_body: str, available_columns: list):
    """
    Validate template variables against available contact file columns.
    Returns validation result with missing and available variables.
    """
    template_variables = extract_template_variables(template_body)
    # Convert available columns to uppercase for comparison
    available_columns_upper = [col.upper() for col in available_columns]
    available_columns_set = set(available_columns_upper)
    
    missing_variables = template_variables - available_columns_set
    available_variables = template_variables & available_columns_set
    
    return {
        "template_variables": list(template_variables),
        "available_columns": available_columns,
        "missing_variables": list(missing_variables),
        "available_variables": list(available_variables),
        "is_valid": len(missing_variables) == 0,
        "missing_count": len(missing_variables),
        "available_count": len(available_variables)
    }

def test_validation():
    """Test the template validation with different scenarios."""
    
    # Red Roof Inn template with {CONTACT_NAME} and {COMPANY_NAME}
    red_roof_template = """Dear {CONTACT_NAME},

I trust this letter finds you well. I am writing to introduce the exclusive corporate rates available at Red Roof Inn, Moss Point, designed specifically for {COMPANY_NAME}'s contractors and workforce.

We look forward to establishing a lasting partnership with {COMPANY_NAME} and serving as your preferred accommodation provider.

Best regards,
Kathan Patel
General Manager
Red Roof Inn, Moss Point"""

    print("🧪 Testing Template Variable Validation")
    print("=" * 60)
    
    # Test Case 1: Valid contact file with all required variables
    print("\n📋 Test Case 1: Valid Contact File")
    print("-" * 40)
    
    valid_contacts_csv = """email,company_name,contact_name
sale.rrimp@gmail.com,Test Company 1,John Doe
sale.rrimp@gmail.com,Test Company 2,Jane Smith"""
    
    df_valid = pd.read_csv(StringIO(valid_contacts_csv))
    available_columns = [col.strip() for col in df_valid.columns.tolist()]
    
    print(f"Contact file columns: {available_columns}")
    
    validation_result = validate_template_variables(red_roof_template, available_columns)
    
    print(f"Template variables found: {validation_result['template_variables']}")
    print(f"Available variables: {validation_result['available_variables']}")
    print(f"Missing variables: {validation_result['missing_variables']}")
    print(f"Validation status: {'✅ Valid' if validation_result['is_valid'] else '❌ Invalid'}")
    
    # Test Case 2: Invalid contact file missing CONTACT_NAME
    print("\n📋 Test Case 2: Invalid Contact File (Missing CONTACT_NAME)")
    print("-" * 40)
    
    invalid_contacts_csv = """email,company_name
sale.rrimp@gmail.com,Test Company 1
sale.rrimp@gmail.com,Test Company 2"""
    
    df_invalid = pd.read_csv(StringIO(invalid_contacts_csv))
    available_columns_invalid = [col.strip() for col in df_invalid.columns.tolist()]
    
    print(f"Contact file columns: {available_columns_invalid}")
    
    validation_result_invalid = validate_template_variables(red_roof_template, available_columns_invalid)
    
    print(f"Template variables found: {validation_result_invalid['template_variables']}")
    print(f"Available variables: {validation_result_invalid['available_variables']}")
    print(f"Missing variables: {validation_result_invalid['missing_variables']}")
    print(f"Validation status: {'✅ Valid' if validation_result_invalid['is_valid'] else '❌ Invalid'}")
    
    if not validation_result_invalid['is_valid']:
        missing_vars = ", ".join(validation_result_invalid['missing_variables'])
        print(f"\n❌ Error: Missing variables in contact file: {missing_vars}")
        print("💡 Solution: Add these columns to your contact file or update your template")
    
    # Test Case 3: Show how the validation would work in the app
    print("\n📋 Test Case 3: Application Flow Example")
    print("-" * 40)
    
    print("1. User uploads contact file with columns: email, company_name")
    print("2. User selects Red Roof Inn template with variables: {CONTACT_NAME}, {COMPANY_NAME}")
    print("3. System validates template variables against contact file columns")
    print("4. System finds missing variable: CONTACT_NAME")
    print("5. System shows validation modal with error message")
    print("6. User must either:")
    print("   - Add 'contact_name' column to their contact file")
    print("   - Update template to use 'Dear Sir/Madam' instead of '{CONTACT_NAME}'")
    print("   - Remove {CONTACT_NAME} variable from template")
    
    print("\n✅ Template validation prevents campaigns from being sent with mismatched variables!")
    print("✅ This ensures all emails are properly personalized with available data.")

if __name__ == "__main__":
    test_validation() 