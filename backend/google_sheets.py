import os
import json
import requests
from datetime import datetime
from google.oauth2 import service_account
import google.auth.transport.requests
from dotenv import load_dotenv

load_dotenv("api.env")

class GoogleSheetsManager:
    """
    A manager class for interacting with Google Sheets API to store and update
    session data and user assessment answers.
    
    This class handles authentication, data formatting, and CRUD operations
    for a specific Google Sheet containing user assessment responses.

    ** The end point Google Sheet can be customized aesthetically however needed
    for easy readability as long as header names and column order remain the same.
    
    Usage:
        # Initialize the manager
        manager = GoogleSheetsManager()
        
        # Test connection (automatically sets up headers if needed)
        if manager.test_connection():
            print("Ready to use - headers automatically set up!")
            
            # Update session data - headers are handled automatically
            session_data = {'session_id': 'abc123', 'status': 'completed', ...}
            answers_dict = {'age': '25', 'physical_ability': 'YES', ...}
            manager.update_session(session_data, answers_dict)
            
    
    Environment Variables Required:
        - GOOGLE_SHEET_ID: The ID of the target Google Sheet
        - GOOGLE_SERVICE_ACCOUNT_FILE: Path to the service account JSON file
            - can be set up here: https://console.cloud.google.com/welcome/new
    """
    
    def __init__(self):
        """
        Initialize the GoogleSheetsManager with credentials and configuration.
        
        Sets up the sheet ID, service account file path, and question mapping
        for converting question IDs to column names.
        
        Usage:
            manager = GoogleSheetsManager()
        """
        self.sheet_id = os.getenv('GOOGLE_SHEET_ID')
        self.service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
        self.credentials = None
        self.base_url = "https://sheets.googleapis.com/v4/spreadsheets"
        
        # Initialize credentials without building service
        self._initialize_credentials()
        
        # Map question IDs to column names 
        self.question_mapping = {
            0: 'user_info',  
            1: 'age',
            2: 'physical_ability',
            3: 'physical_ability_stand',
            4: 'physical_ability_move',
            5: 'availability',
            6: 'working_preference',
            7: 'leadership_preference',
            8: 'prior_experience',
            9: 'game_knowledge',
            10: 'required_skills',
            11: 'experience'
        }

        # Define headers once to avoid mismatches
        self.headers = [
            'Session ID',
            'Status', 
            'Created At',
            'Updated At',
            'Answers Count',
            'Completion Rate (%)',
            'User Email',
            # User Information (after user email)
            'Full Name',
            'Email Address',
            'Zipcode',
            # Assessment Questions
            'Age',
            'Physical Activity Preference',
            'Can Stand Long Periods',
            'Can Move/Lift Long Periods',
            'Availability Days',
            'Working Preference (BTS/Front-facing)',
            'Leadership Preference',
            'Prior FIRST Experience',
            'Game Knowledge Level',
            'Required Skills',
            'Experience Areas'
        ]

    def _initialize_credentials(self):
        """
        Initialize Google Service Account credentials for Sheets API access.
        
        Loads credentials from the service account JSON file specified in
        environment variables and sets up proper scopes for Sheets access.
        
        Returns:
            - bool: True if credentials were initialized successfully, False otherwise.
            
        Usage:
            success = manager._initialize_credentials()
        """
        try:
            if not self.service_account_file:
                print("No service account file specified")
                return False
                
            if not os.path.exists(self.service_account_file):
                print(f"Service account file not found: {self.service_account_file}")
                return False
            
            # Load credentials from the service account file
            self.credentials = service_account.Credentials.from_service_account_file(
                self.service_account_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            print("Google Sheets credentials initialized successfully")
            return True
            
        except Exception as e:
            print(f"Failed to initialize credentials: {str(e)}")
            return False
    
    def _get_auth_headers(self):
        """
        Generate authorization headers for Google Sheets API requests.
        
        Refreshes credentials if needed and returns properly formatted
        headers including the Bearer token for API authentication.
        
        Returns:
            - dict: Dictionary containing Authorization and Content-Type headers,
                  or None if credentials are invalid.
                  
        Usage:
            headers = manager._get_auth_headers()
            if headers:
                # Use headers in API request
        """
        if not self.credentials:
            return None
            
        # Refresh credentials if needed
        if not self.credentials.valid:
            request = google.auth.transport.requests.Request()
            self.credentials.refresh(request)
        
        return {
            'Authorization': f'Bearer {self.credentials.token}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method, url, **kwargs):
        """
        Make authenticated HTTP requests to Google Sheets API with proper error handling.
        
        Handles authentication, SSL verification, timeouts, and error responses
        for all API interactions with Google Sheets.
        
        Args:
            - method (str): HTTP method ('GET', 'POST', 'PUT', etc.)
            - url (str): Target URL for the API request
            **kwargs: Additional arguments passed to requests (headers, json, params, etc.)
            
        Returns:
            - dict: Parsed JSON response from the API
            
        Raises:
            - Exception: If credentials are invalid or request fails
            
        Usage:
            response = manager._make_request('GET', 'https://sheets.googleapis.com/...')
            data = manager._make_request('POST', url, json={'values': [['data']]})
        """
        headers = self._get_auth_headers()
        if not headers:
            raise Exception("No valid credentials")
        
        # Merge headers
        if 'headers' in kwargs:
            kwargs['headers'].update(headers)
        else:
            kwargs['headers'] = headers
        
        # Configure SSL settings
        session = requests.Session()
        session.verify = True  # Verify SSL certificates
        
        # Make request with timeout
        kwargs['timeout'] = kwargs.get('timeout', 30)
        
        try:
            response = session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            print(f"Response content: {response.text}")
            raise e
    
    def _find_session_row(self, session_id):
        """
        Find the row number in Google Sheets for a specific session ID.
        
        Searches through the first column of the 'Responses' sheet to locate
        an existing session and return its row number for updates.
        
        Args:
            - session_id (str): The unique session identifier to search for
            
        Returns:
            - int: Row number (1-indexed) if session found, None if not found
            
        Usage:
            row_num = manager._find_session_row('session_abc123')
            if row_num:
                # Update existing row
            else:
                # Create new row
        """
        try:
            url = f"{self.base_url}/{self.sheet_id}/values/Responses!A:A"
            
            result = self._make_request('GET', url)
            values = result.get('values', [])
            
            # Skip header row (index 0) and search for session_id
            for i, row in enumerate(values[1:], start=2):  # start=2 because row 1 is header
                if row and len(row) > 0 and row[0] == session_id:
                    return i
                    
            return None  # Session not found
            
        except Exception as e:
            print(f"Error finding session row: {str(e)}")
            return None
    
    def _format_multiselect(self, options):
        """
        Format multiselect answer options for Google Sheets storage.
        
        Converts list or JSON string formats into comma-separated strings
        suitable for display in spreadsheet cells.
        
        Args:
            - options (list|str|any): The multiselect options to format.
                                   Can be a list, JSON string, or other format.
                                   
        Returns:
            - str: Comma-separated string of options, or empty string if no options
            
        Usage:
            formatted = manager._format_multiselect(['option1', 'option2'])
            # Returns: "option1, option2"
            
            formatted = manager._format_multiselect('["opt1", "opt2"]')
            # Returns: "opt1, opt2"
        """
        try:
            if isinstance(options, list):
                return ", ".join(str(opt) for opt in options) if options else ""
            if isinstance(options, str):
                try:
                    # Try to parse JSON string
                    parsed = json.loads(options)
                    if isinstance(parsed, list):
                        return ", ".join(str(opt) for opt in parsed)
                except:
                    pass
            return str(options) if options else ""
        except Exception as e:
            print(f"Error formatting multiselect: {e}")
            return str(options) if options else ""
    
    def _check_and_setup_headers(self):
        """
        Check if headers exist and set them up if they don't.
        
        This method checks if the first row has proper headers and creates them
        if the sheet is empty or doesn't have the expected header structure.
        
        Returns:
            - bool: True if headers are properly set up, False if setup failed
        """
        try:
            # Calculate the correct range based on number of headers
            end_column = chr(ord('A') + len(self.headers) - 1)  # A=0, B=1, etc.
            
            # Try to read the first row
            url = f"{self.base_url}/{self.sheet_id}/values/Responses!A1:{end_column}1"
            result = self._make_request('GET', url)
            values = result.get('values', [])
            
            # If no values or first row doesn't match expected headers, set up headers
            if not values or len(values[0]) < len(self.headers) or values[0][0] != 'Session ID':
                print("Headers not found or incomplete, setting up headers...")
                return self.setup_sheet_headers()
            else:
                print("Headers already exist and look correct")
                return True
                
        except Exception as e:
            print(f"Error checking headers, attempting to set them up: {str(e)}")
            return self.setup_sheet_headers()
    
    def _extract_user_info(self, answers_dict):
        """
        Extract individual user info fields from the user_info object.
        
        Parses the user_info answer which contains name, email, and zipcode
        and returns them as separate values for the spreadsheet columns.
        
        Args:
            - answers_dict (dict): Dictionary of user answers with question keys
            
        Returns:
            - tuple: (name, email, zipcode) as strings
            
        Usage:
            name, email, zipcode = manager._extract_user_info(answers_dict)
        """
        user_info = answers_dict.get('user_info', {})
        
        # Handle if user_info is a JSON string
        if isinstance(user_info, str):
            try:
                user_info = json.loads(user_info)
            except json.JSONDecodeError:
                user_info = {}
        
        # Extract individual fields
        name = str(user_info.get('name', '')) if isinstance(user_info, dict) else ''
        email = str(user_info.get('email', '')) if isinstance(user_info, dict) else ''
        zipcode = str(user_info.get('zipcode', '')) if isinstance(user_info, dict) else ''
        
        return name, email, zipcode
    
    def get_session_answers(self, conn, session_id):
        """
        Retrieve all answers for a specific session from the database.
        
        Fetches user answers from the database, parses JSON strings back to objects,
        and maps question IDs to their corresponding key names for easy access.
        
        Args:
            - conn: Database connection object (SQLite connection)
            - session_id (str): The unique session identifier
            
        Returns:
            - dict: Dictionary mapping question keys to their answers.
                  Keys are from self.question_mapping values.
                  
        Usage:
            import sqlite3
            conn = sqlite3.connect('database.db')
            answers = manager.get_session_answers(conn, 'session_123')
            age = answers.get('age')
            availability = answers.get('availability', [])
        """
        try:
            answers = conn.execute('''
                SELECT question_id, answer
                FROM user_answers 
                WHERE session_id = ?
                ORDER BY question_id
            ''', (session_id,)).fetchall()
            
            # Convert to dictionary with question keys
            answer_dict = {}
            for row in answers:
                question_id = str(row["question_id"])  # Convert to string for lookup
                answer = row["answer"]
                
                # Parse JSON strings back to objects
                if isinstance(answer, str) and answer.startswith(('[', '{')):
                    try:
                        answer = json.loads(answer)
                    except json.JSONDecodeError:
                        pass
                
                # Map question ID to key name - handle both int and string IDs
                try:
                    int_id = int(question_id)
                    if int_id in self.question_mapping:
                        key = self.question_mapping[int_id]
                        answer_dict[key] = answer
                except ValueError:
                    # Handle non-numeric question IDs if needed
                    pass
            
            return answer_dict
            
        except Exception as e:
            print(f"Error getting session answers: {e}")
            return {}
    
    def _get_applicable_questions(self, answers_dict):
        """
        Determine which assessment questions are applicable based on skip logic.
        
        Analyzes user answers to determine which questions should be counted
        for completion rate calculation, excluding questions that were skipped
        due to conditional logic (e.g., physical ability sub-questions).
        
        Args:
            - answers_dict (dict): Dictionary of user answers with question keys
            
        Returns:
            - set: Set of applicable question keys that should be counted
            
        Usage:
            answers = {'physical_ability': 'NO', 'age': '25'}
            applicable = manager._get_applicable_questions(answers)
            # Returns set excluding physical ability sub-questions
        """
        applicable = set(self.question_mapping.values())  

        # Remove unapplicable questions from being counted in user data
        if answers_dict.get("physical_ability") in ["NO", False, "no", "No"]:
            applicable.discard("physical_ability_stand")
            applicable.discard("physical_ability_move")

        return applicable
    
    def update_session(self, session_data, answers_dict):
        """
        Update or create a session record in Google Sheets with assessment data.
        
        Combines session metadata with user answers, calculates completion rate,
        and either updates an existing row or creates a new one in the spreadsheet.
        Handles multiselect formatting and applies skip logic for completion calculations.
        Automatically ensures headers are set up before writing data.
        
        Args:
            - session_data (dict): Session metadata including session_id, status, 
                               created_at, user_email, etc.
            - answers_dict (dict): User answers mapped by question keys
            
        Returns:
            - bool: True if update was successful, False otherwise
            
        Usage:
            session_data = {
                'session_id': 'abc123',
                'status': 'completed',
                'created_at': '2025-01-15T10:30:00',
                'user_email': 'user@example.com'
            }
            answers_dict = {
                'age': '25',
                'physical_ability': 'YES',
                'availability': ['Monday', 'Tuesday'],
                'required_skills': ['Programming', 'Leadership'],
                'user_info': {'name': 'John Doe', 'email': 'john@example.com', 'zipcode': '12345'}
            }
            success = manager.update_session(session_data, answers_dict)
        """
        try:
            # Ensure headers are set up before writing data
            if not self._check_and_setup_headers():
                print("Failed to set up headers, but continuing with data write")
            
            # Determine applicable questions based on skip logic
            applicable_questions = self._get_applicable_questions(answers_dict)

            answered_count = sum(1 for k in applicable_questions if answers_dict.get(k))

            total_applicable = len(applicable_questions)

            completion_rate = round((answered_count / total_applicable) * 100, 1) if total_applicable else 0

            # Extract user info fields
            name, email, zipcode = self._extract_user_info(answers_dict)

            # Format data for Google Sheets as a single row (flat list)
            row_data = [
                str(session_data.get('session_id', '')),
                str(session_data.get('status', '')),
                str(session_data.get('created_at', '')),
                datetime.now().isoformat(),  # updated_at
                answered_count,
                completion_rate,
                # User Information
                name,
                email,
                zipcode,
                # Individual question answers
                str(answers_dict.get('age', '')),
                str(answers_dict.get('physical_ability', '')),
                str(answers_dict.get('physical_ability_stand', '')),
                str(answers_dict.get('physical_ability_move', '')),
                self._format_multiselect(answers_dict.get('availability', [])),
                str(answers_dict.get('working_preference', '')),
                str(answers_dict.get('leadership_preference', '')),
                str(answers_dict.get('prior_experience', '')),
                str(answers_dict.get('game_knowledge', '')),
                self._format_multiselect(answers_dict.get('required_skills', [])),
                self._format_multiselect(answers_dict.get('experience', []))
            ]
            
            # Calculate the correct range based on number of columns
            end_column = chr(ord('A') + len(row_data) - 1)
            
            # Check if session already exists
            session_id = session_data.get('session_id')
            existing_row = self._find_session_row(session_id)
            
            if existing_row:
                # Update existing row - use calculated range
                url = f"{self.base_url}/{self.sheet_id}/values/Responses!A{existing_row}:{end_column}{existing_row}"
                params = {'valueInputOption': 'RAW'}
                data = {'values': [row_data]}
                
                self._make_request('PUT', url, params=params, json=data)
                print(f"Updated existing row {existing_row} for session {session_id}")
            else:
                # Append new row - use calculated range
                url = f"{self.base_url}/{self.sheet_id}/values/Responses!A:{end_column}:append"
                params = {
                    'valueInputOption': 'RAW',
                    'insertDataOption': 'INSERT_ROWS'
                }
                data = {'values': [row_data]}
                
                self._make_request('POST', url, params=params, json=data)
                print(f"Created new row for session {session_id}")
            
            print(f"Successfully updated Google Sheets for session {session_data.get('session_id')}")
            return True
                
        except Exception as e:
            print(f"Error updating Google Sheets: {str(e)}")
            return False
    
    def setup_sheet_headers(self):
        """
        Set up the header row in the Google Sheet with column names.
        
        Creates or updates the first row of the 'Responses' sheet with
        appropriate column headers for session data and assessment questions.
        This is called automatically when needed.
        
        Returns:
            - bool: True if headers were set up successfully, False otherwise
            
        Usage:
            # Usually called automatically, but can be called manually
            if manager.setup_sheet_headers():
                print("Sheet is ready for data")
            else:
                print("Failed to set up headers")
        """
        try:
            # Calculate the correct range based on number of headers
            end_column = chr(ord('A') + len(self.headers) - 1)
            
            url = f"{self.base_url}/{self.sheet_id}/values/Responses!A1:{end_column}1"
            params = {'valueInputOption': 'RAW'}
            data = {'values': [self.headers]}
            
            self._make_request('PUT', url, params=params, json=data)
            print("Headers set up successfully")
            return True
            
        except Exception as e:
            print(f"Error setting up headers: {str(e)}")
            return False

    def test_connection(self):
        """
        Test the connection to Google Sheets API and verify sheet access.
        
        Performs a simple API call to verify that credentials are working
        and the specified sheet is accessible. Also automatically sets up
        headers if they don't exist.
        
        Returns:
            - bool: True if connection is successful, False otherwise
            
        Usage:
            if manager.test_connection():
                print("Ready to work with Google Sheets")
            else:
                print("Check your credentials and sheet ID")
        """
        try:
            url = f"{self.base_url}/{self.sheet_id}"
            result = self._make_request('GET', url)
            
            if result:
                print(f"Google Sheets connection successful. Sheet title: {result.get('properties', {}).get('title')}")
                
                # Automatically check and set up headers
                self._check_and_setup_headers()
                
                return True
            else:
                print("Google Sheets connection failed")
                return False
                
        except Exception as e:
            print(f"Google Sheets connection error: {e}")
            return False