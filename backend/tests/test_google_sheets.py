"""
Simple test script to verify Google Sheets Service Account setup.
"""

import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from google_sheets import GoogleSheetsManager

def test_google_sheets():
    """Test all Google Sheets functionality"""
    print("=== Google Sheets Service Account Test ===\n")
    
    # Load environment variables
    load_dotenv("/Users/chansoon/Documents/first_volunteer_project/backend/api.env")
    
    print("1. Loading environment variables...")
    sheet_id = os.getenv('GOOGLE_SHEET_ID')
    service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
    
    if not sheet_id:
        print("GOOGLE_SHEET_ID not found in .env file")
        return False
        
    if not service_account_file:
        print("GOOGLE_SERVICE_ACCOUNT_FILE not found in .env file")
        return False
        
    print(f"Sheet ID: {sheet_id}")
    print(f"Service Account File: {service_account_file}")
    
    if not os.path.exists(service_account_file):
        print(f"Service account file doesn't exist: {service_account_file}")
        return False
        
    print("Service account file exists\n")
    
    print("2. Initializing GoogleSheetsManager...")
    try:
        sheets_manager = GoogleSheetsManager()
        print("GoogleSheetsManager initialized\n")
    except Exception as e:
        print(f"Failed to initialize GoogleSheetsManager: {e}")
        return False
    
    print("3. Testing connection...")
    if sheets_manager.test_connection():
        print("Connection test passed\n")
    else:
        print("Connection test failed\n")
        return False
    
    print("4. Setting up headers...")
    if sheets_manager.setup_sheet_headers():
        print("Headers setup successful\n")
    else:
        print("Headers setup failed\n")
        return False
    
    print("5. Testing data write...")
    # Test data
    test_session_data = {
        'session_id': 'test-session-12345',
        'status': 'test',
        'created_at': '2024-01-01T12:00:00',
        'user_email': 'test@example.com'
    }
    
    test_answers = {
        'age': '25',
        'physical_ability': 'Yes',
        'physical_ability_stand': 'Yes',
        'physical_ability_move': 'Yes',
        'availability': ['Saturday', 'Sunday'],
        'working_preference': 'Front-facing',
        'leadership_preference': 'No',
        'prior_experience': 'Yes',
        'game_knowledge': 'Intermediate',
        'required_skills': ['Basic computer literacy', 'Photo and video editing'],
        'experience': ['Technical inspection experience']
    }
    
    if sheets_manager.update_session(test_session_data, test_answers):
        print("Test data write successful")
    else:
        print("Test data write failed\n")
        return False
    
    print("=== All Tests Passed! ===")
    print("Google Sheets integration is working correctly.")
    
    return True

if __name__ == "__main__":
    success = test_google_sheets()
    if not success:
        print("\n=== Test Failed ===")
        print("Please check the error messages above and fix the issues.")
        print("\nCommon issues:")
        print("- Make sure your .env file has the correct variables")
        print("- Check that the service account JSON file path is correct")
        print("- Verify you've shared your Google Sheet with the service account email")
        print("- Ensure the Google Sheets API is enabled in your Google Cloud project")
    else:
        print("Tests successfully completed!")