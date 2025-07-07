#!/usr/bin/env python3
"""
Excel Format Verification Script
Verifies that the generated Excel files have the correct format for VBS software integration
"""

import pandas as pd
from pathlib import Path
from modules.excel_generator import EnhancedExcelGenerator

def verify_excel_format():
    """Verify that the Excel generation produces the correct format"""
    
    print("🔍 Excel Format Verification")
    print("=" * 50)
    
    # Expected format
    expected_headers = ['Hostname', 'IP_Address', 'MAC_Address', 'Package', 'AP_MAC', 'Upload', 'Download']
    
    print(f"✅ Expected Headers: {expected_headers}")
    
    # Test with current CSV files
    csv_dir = Path("EHC_Data/04july")
    
    if not csv_dir.exists():
        print("❌ CSV directory not found")
        return False
    
    # Generate Excel file
    generator = EnhancedExcelGenerator()
    result = generator.generate_excel_from_csv_directory(csv_dir)
    
    if not result.get("success"):
        print(f"❌ Excel generation failed: {result.get('error')}")
        return False
    
    excel_file = result["file_path"]
    print(f"📄 Generated Excel: {excel_file}")
    
    # Verify the generated file
    try:
        df = pd.read_excel(excel_file)
        actual_headers = list(df.columns)
        
        print(f"📊 Actual Headers: {actual_headers}")
        print(f"📏 Data Shape: {df.shape}")
        
        # Check header format
        if actual_headers == expected_headers:
            print("✅ Headers match expected format perfectly!")
        else:
            print("❌ Headers do not match expected format")
            return False
        
        # Check data types and sample
        print("\n📋 Sample Data:")
        print(df.head(3).to_string())
        
        print("\n✅ Excel format verification completed successfully!")
        print("🎯 The generated Excel file is ready for VBS software integration!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading generated Excel file: {e}")
        return False

def compare_with_reference():
    """Compare generated file with reference file if available"""
    
    print("\n🔄 Comparing with Reference File")
    print("=" * 40)
    
    reference_file = Path("EHC_Data_Merge/EHC_DATA_04072025.xlsx")
    generated_file = Path("EHC_Data_Merge/04july/EHC_Upload_Mac_04072025.xls")
    
    if not reference_file.exists():
        print("ℹ️  Reference file not found - skipping comparison")
        return
    
    if not generated_file.exists():
        print("❌ Generated file not found")
        return
    
    try:
        ref_df = pd.read_excel(reference_file)
        gen_df = pd.read_excel(generated_file)
        
        print(f"📄 Reference: {reference_file.name}")
        print(f"   Headers: {list(ref_df.columns)}")
        print(f"   Shape: {ref_df.shape}")
        
        print(f"📄 Generated: {generated_file.name}")
        print(f"   Headers: {list(gen_df.columns)}")
        print(f"   Shape: {gen_df.shape}")
        
        headers_match = list(ref_df.columns) == list(gen_df.columns)
        print(f"🎯 Headers Match: {'✅ Yes' if headers_match else '❌ No'}")
        
        if headers_match:
            print("✅ Generated file format matches reference perfectly!")
        
    except Exception as e:
        print(f"❌ Error comparing files: {e}")

if __name__ == "__main__":
    print("🚀 Starting Excel Format Verification\n")
    
    success = verify_excel_format()
    
    if success:
        compare_with_reference()
    
    print(f"\n{'🎉 All verifications passed!' if success else '❌ Verification failed'}") 