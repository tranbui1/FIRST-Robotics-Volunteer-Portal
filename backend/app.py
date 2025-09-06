"""
Flask Assessment API

A web API for managing volunteer role assessment sessions, collecting user responses,
and providing role matching recommendations. Includes admin functionality for
managing assessment data and role links.

Features:
- Session management with unique IDs
- Question/answer storage in SQLite database
- Role matching based on user responses
- Google Sheets integration for data export
- Admin panel for uploading assessment data
- CORS support for cross-origin requests

Endpoints:
- POST /api/start-session: Create new assessment session
- POST /api/save-answer: Save user answer to database
- POST /api/submit: Complete assessment and get role matches
- POST /api/get-question: Retrieve question by ID
- POST /api/role-links: Get links for specific roles
- POST /api/admin-login: Admin authentication
- POST /api/upload-match-data: Admin upload of matching data
- POST /api/upload-role-links: Admin upload of role links
"""

from flask import Flask, request, make_response, jsonify
from questions import Questions
from model.matching_logic import Matches
from contextlib import contextmanager
import sqlite3
import uuid
import json
from dotenv import load_dotenv
from google_sheets import GoogleSheetsManager
from links import RoleLinks
from config_utils import load_config, save_config
import os
from functools import wraps
import tempfile
import shutil

import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, template_folder="../templates")

TOTAL_ID = 11

# Default file paths (fallbacks if no config exists)
DEFAULT_MAIN_DATA_PATH = ""
DEFAULT_ROLE_LINK_PATH = ""

# Load configuration and get current file paths
config = load_config()
MAIN_DATA_PATH = config.get('main_data_path', DEFAULT_MAIN_DATA_PATH)
ROLE_LINK_PATH = config.get('role_link_path', DEFAULT_ROLE_LINK_PATH)

# Simple admin session storage
AUTHORIZED_SESSIONS = set()

@app.before_request
def handle_preflight():
    """
    Handle CORS preflight OPTIONS requests for cross-origin access.
    
    Automatically responds to all OPTIONS requests with appropriate CORS headers
    to allow frontend applications to access the API from different domains.
    
    Returns:
        - Response: Empty 200 response with CORS headers for OPTIONS requests,
                 None for other request methods (continues normal processing)
                 
    Usage:
        # Automatically called by Flask for all OPTIONS requests
        # No manual usage required - handles browser preflight checks
    """
    if request.method == "OPTIONS":
        response = make_response("", 200)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Max-Age"] = "86400"
        return response

@app.after_request
def after_request(response):
    """
    Add CORS headers to all API responses for cross-origin access.
    
    Ensures that all responses include necessary CORS headers to allow
    frontend applications to access the API from different domains.
    
    Args:
        - response: Flask response object to modify
        
    Returns:
        - Response: Modified response object with CORS headers added
        
    Usage:
        # Automatically called by Flask after each request
        # No manual usage required - adds headers to all responses
    """
    if 'Access-Control-Allow-Origin' not in response.headers:
        response.headers['Access-Control-Allow-Origin'] = '*'
    if 'Access-Control-Allow-Headers' not in response.headers:
        response.headers['Access-Control-Allow-Headers'] = '*'
    if 'Access-Control-Allow-Methods' not in response.headers:
        response.headers['Access-Control-Allow-Methods'] = '*'
    return response

def initialize_systems():
    """
    Initialize all system components (matching, questions, sheets, role links).
    
    Loads and initializes the core systems needed for the assessment API,
    including the matching algorithm, question system, Google Sheets integration,
    and role links manager. Uses configured file paths with fallbacks.
    
    Returns:
        - tuple: (match_system, questions_system, sheets_manager, role_links_manager)
               Any component that fails to initialize will be None
               
    Usage:
        # Called during app startup
        match, questions, sheets_manager, role_links = initialize_systems()
        
        # Check initialization status
        if match and questions:
            print("Core systems ready")
        else:
            print("System initialization failed")
    """
    global MAIN_DATA_PATH, ROLE_LINK_PATH
    
    # Initialize matching system
    try:
        match_system = Matches(data_path=MAIN_DATA_PATH, student_status=True)
        questions_system = Questions()
        print("\nSuccessfully initialized the matching and questions system\n")
    except Exception as e:
        print(f"\nFailed to initialize the matching system and questions system: {e}\n")
        match_system, questions_system = None, None

    # Load env variables
    load_dotenv('api.env')

    # Initialize Google Sheets API
    try:
        sheets_mgr = GoogleSheetsManager()
        if sheets_mgr.test_connection():
            print("Google sheets API and integration ready\n")
        else:
            print("Google sheets API connection failed\n")
            sheets_mgr = None
    except Exception as e:
        print(f"Google Sheets initialization failed: {e}\n")
        sheets_mgr = None

    # Initialize role links module
    try:
        role_links_mgr = RoleLinks(ROLE_LINK_PATH)
        if role_links_mgr.is_loaded():
            print("Successfully loaded role links data\n")
        else:
            print("Failed to load role links data\n")
            role_links_mgr = None
    except Exception as e:
        print(f"Role links module initialization failed: {e}\n")
        role_links_mgr = None
        
    return match_system, questions_system, sheets_mgr, role_links_mgr

# Initialize all systems
match, questions, sheets_manager, role_links = initialize_systems()

@contextmanager
def get_db_connection():
    """
    Context manager for SQLite database connections with proper cleanup.
    
    Provides a database connection with row factory for dictionary-like access
    and ensures proper connection cleanup even if exceptions occur.
    
    Yields:
        - sqlite3.Connection: Database connection with row factory configured
        
    Usage:
        with get_db_connection() as conn:
            result = conn.execute('SELECT * FROM sessions').fetchall()
            conn.commit()
        # Connection automatically closed
    """
    conn = sqlite3.connect("assessment.db")
    conn.row_factory = sqlite3.Row
    try: 
        yield conn
    finally:
        conn.close()

def init_db():
    """
    Initialize the SQLite database with required tables for assessment data.
    
    Creates the assessment_sessions and user_answers tables if they don't exist.
    Sets up proper foreign key relationships and indexes for efficient queries.
    
    Usage:
        # Called once during app startup
        init_db()
        
        # Database schema created:
        # - assessment_sessions: session metadata
        # - user_answers: individual question responses
    """
    try:
        print("\nOpening database connection...")
        with get_db_connection() as conn:
            print("Database connection opened successfully\n")
            
            # Parent table: sessions 
            conn.execute('''
                CREATE TABLE IF NOT EXISTS assessment_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'in_progress'
                )
            ''')

            # Child table: user answers
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES assessment_sessions (session_id),
                    UNIQUE(session_id, question_id)
                )
            ''')

            conn.commit()
            print("Database initialized successfully\n")
            
    except Exception as e:
        print(f"\nERROR in init_db: {e}\n")

def require_admin(f):
    """
    Decorator to require admin authentication for protected endpoints.
    
    Checks for valid admin session token in X-Admin-Token header
    and returns 403 Unauthorized if token is invalid or missing.
    
    Args:
        - f (function): Flask route function to protect
        
    Returns:
        - function: Decorated function with admin check
        
    Usage:
        @app.route("/api/admin-endpoint", methods=["POST"])
        @require_admin
        def protected_endpoint():
            return jsonify({"data": "sensitive_info"})
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        session_token = request.headers.get("X-Admin-Token")
        if session_token not in AUTHORIZED_SESSIONS:
            return jsonify({"error": "Unauthorized"}), 403
        return f(*args, **kwargs)
    return wrapper

def update_file_paths(main_data_path=None, role_link_path=None):
    """
    Update file paths in configuration and reinitialize affected systems.
    
    Updates the stored configuration with new file paths and reinitializes
    the matching system and role links manager to use the new files.
    
    Args:
        - main_data_path (str, optional): New path for matching data CSV
        - role_link_path (str, optional): New path for role links CSV
        
    Usage:
        # Update both paths
        update_file_paths("/new/path/data.csv", "/new/path/links.csv")
        
        # Update just one path
        update_file_paths(main_data_path="/new/data.csv")
    """
    global MAIN_DATA_PATH, ROLE_LINK_PATH, match, role_links
    
    config = load_config()
    
    if main_data_path:
        config['main_data_path'] = main_data_path
        MAIN_DATA_PATH = main_data_path
        
    if role_link_path:
        config['role_link_path'] = role_link_path
        ROLE_LINK_PATH = role_link_path
    
    save_config(config)
    
    # Reinitialize affected systems
    if main_data_path:
        try:
            match = Matches(data_path=MAIN_DATA_PATH, student_status=True)
            print(f"Matching system reinitialized with: {MAIN_DATA_PATH}")
        except Exception as e:
            print(f"Failed to reinitialize matching system: {e}")
            
    if role_link_path:
        try:
            role_links = RoleLinks(ROLE_LINK_PATH)
            print(f"Role links reinitialized with: {ROLE_LINK_PATH}")
        except Exception as e:
            print(f"Failed to reinitialize role links: {e}")

# Initialize database
init_db()

@app.route("/api/test", methods=["GET", "POST", "OPTIONS"])
def test_cors():
    """
    Test endpoint for verifying CORS configuration and API connectivity.
    
    Simple endpoint that returns success message and request method,
    useful for frontend developers to test API connectivity and CORS setup.
    
    Returns:
        - JSON: Success message with request method information
        
    Usage:
        # GET request
        curl http://localhost:5001/api/test
        
        # POST request
        curl -X POST http://localhost:5001/api/test
        
        # Returns: {"message": "CORS test successful!", "method": "GET"}
    """
    print("\n=== TEST ENDPOINT CALLED ===\n")
    return jsonify({"message": "CORS test successful!", "method": request.method}), 200

@app.route("/api/start-session", methods=["POST"])
def start_session():
    """
    Create a new assessment session with unique identifier.
    
    Generates a UUID for the session and creates a new record in the
    assessment_sessions table to track the user's progress.
    
    Returns:
        - JSON: Response containing session_id and status information
        
    Status Codes:
        - 200: Session created successfully
        - 500: Database error or system failure
        
    Usage:
        # Frontend request
        fetch('/api/start-session', {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            const sessionId = data.session_id;
            // Store session ID for subsequent requests
        });
        
        # Response format:
        # {
        #     "status": "Success",
        #     "session_id": "uuid-string",
        #     "message": "Session started successfully"
        # }
    """        
    try:
        session_id = str(uuid.uuid4())
        print(f"Generated session ID: {session_id}\n")

        with get_db_connection() as conn:
            conn.execute('INSERT INTO assessment_sessions (session_id) VALUES (?)', (session_id,))
            conn.commit()

        return jsonify({
            "status": "Success", 
            "session_id": session_id,
            "message": "Session started successfully"
        }), 200
        
    except Exception as e:
        print(f"\nERROR in start_session: {e}\n")
        return jsonify({"error": f"Failed to start session: {str(e)}"}), 500

@app.route("/api/save-answer", methods=["POST"])
def save_answer():
    """
    Save a user's answer to a specific assessment question.
    
    Stores the user's response in the database and updates Google Sheets if configured.
    Handles JSON serialization for complex answer types (lists, objects).
    Implements skip logic for conditional questions.
    
    Request Body:
        {
            "session_id": "uuid-string",
            "question_id": 1,
            "question": "Question text",
            "answer": "user response" | ["option1", "option2"] | {...}
        }
    
    Returns:
        - JSON: Success status with optional skip instruction
        
    Status Codes:
        - 200: Answer saved successfully
        - 400: Missing required fields or invalid data
        - 404: Invalid session ID
        - 500: Database or system error
        
    Usage:
        # Save single choice answer
        fetch('/api/save-answer', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                session_id: 'uuid',
                question_id: 1,
                question: 'Do you prefer physical roles?',
                answer: 'Yes'
            })
        });
        
        # Save multiselect answer
        body: JSON.stringify({
            session_id: 'uuid',
            question_id: 4,
            answer: ['Friday', 'Saturday']
        })
    """        
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400

        required_fields = ["answer", "question_id", "session_id"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400 

        session_id = data["session_id"]
        answer = data["answer"]
        question_id = data["question_id"]
        question = data.get("question", "")

        # Convert answer to string if it's not already
        if isinstance(answer, (list, dict)):
            answer = json.dumps(answer)
        else:
            answer = str(answer)

        with get_db_connection() as conn:
            # Check session exists
            session_check = conn.execute(
                'SELECT id FROM assessment_sessions WHERE session_id = ?', 
                (session_id,)
            ).fetchone()

            if not session_check:
                return jsonify({"error": "Invalid session ID"}), 404 

            conn.execute('''
                INSERT OR REPLACE INTO user_answers 
                (session_id, question_id, question, answer) 
                VALUES (?, ?, ?, ?)
            ''', (session_id, question_id, question, answer))
            conn.commit()

            # Update Google Sheets if available
            if sheets_manager:
                try:
                    session_data = conn.execute(
                        'SELECT session_id, created_at, status FROM assessment_sessions WHERE session_id = ?', 
                        (session_id,)
                    ).fetchone()
                    if session_data:
                        answers_dict = sheets_manager.get_session_answers(conn, session_id)
                        sheets_manager.update_session(dict(session_data), answers_dict)
                except Exception as e:
                    print(f"Failed to update Google Sheets: {e}")

            # Skip logic for physical ability questions
            if question_id == 1 and answer.lower() == "no":
                return jsonify({
                    "status": "Success",
                    "message": "Answer saved successfully",
                    "skip": "true"
                })

            return jsonify({
                "status": "Success",
                "message": "Answer saved successfully"
            }), 200

    except Exception as e:
        print(f"\nERROR in save_answer: {e}\n")
        return jsonify({"error": f"Failed to save answer: {str(e)}"}), 500

@app.route("/api/submit", methods=["POST"])
def submit():
    """
    Complete the assessment and generate role matching recommendations.
    
    Processes all saved answers through the matching algorithm to determine
    the best-fit volunteer roles for the user. Updates session status to completed.
    
    Request Body:
        {
            "session_id": "uuid-string"
        }
    
    Returns:
        - JSON: Role matching results with best fit recommendations
        
    Status Codes:
        - 200: Assessment completed successfully
        - 400: Missing session ID
        - 404: No answers found for session
        - 500: Processing error
        
    Usage:
        fetch('/api/submit', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({session_id: 'uuid-string'})
        })
        .then(response => response.json())
        .then(data => {
            const bestRoles = data.results['Best fit roles'];
            const nextBest = data.results['Next best roles'];
            // Display recommendations to user
        });
    """        
    try:
        data = request.get_json()
        if not data or "session_id" not in data:
            return jsonify({"error": "Session ID is required"}), 400

        session_id = data["session_id"]

        with get_db_connection() as conn:
            answers = conn.execute('''
                SELECT question_id, answer
                FROM user_answers 
                WHERE session_id = ?
                ORDER BY created_at
            ''', (session_id,)).fetchall()

            if not answers:
                return jsonify({"error": "No answers found for this session"}), 404

        # Process answers through matching system
        for row in answers:
            question_id = int(row["question_id"])
            answer = row["answer"]

            # Parse JSON if needed
            if isinstance(answer, str) and answer.startswith(('[', '{')):
                try:
                    answer = json.loads(answer)
                except json.JSONDecodeError:
                    pass

            question_data = {
                "question_id": question_id,
                "answer": answer
            }

            match.process_assessment(question_data)

        best_roles = match.get_top_matches()

        with get_db_connection() as conn:
            conn.execute('''
                UPDATE assessment_sessions
                SET status = 'completed'
                WHERE session_id = ?
            ''', (session_id,))
            conn.commit()

        return jsonify({
            "status": "Success",
            "session_id": session_id,
            "results": best_roles
        }), 200

    except Exception as e:
        print(f"ERROR in submit: {e}")
        return jsonify({"error": f"Failed to submit: {str(e)}"}), 500

@app.route("/api/get-question", methods=["POST"])
def get_question():
    """
    Retrieve question data by question ID for frontend display.
    
    Returns complete question information including text, type, options,
    and display prompts for rendering in the user interface.
    
    Request Body:
        {
            "question_id": 0
        }
    
    Returns:
        - JSON: Complete question object with metadata
        
    Status Codes:
        - 200: Question retrieved successfully
        - 404: Invalid question ID
        - 500: Questions system not initialized
        
    Usage:
        fetch('/api/get-question', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({question_id: 0})
        })
        .then(response => response.json())
        .then(question => {
            console.log(question.question);  // "What is your age?"
            console.log(question.options);   // ["13 to 15 years old", ...]
            console.log(question.type);      // "custom-dropdown"
        });
    """       
    try:
        if not questions:
            return jsonify({"error": "Question system not initialized"}), 500

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 500

        question_id = data["question_id"]

        if question_id > TOTAL_ID:
            return jsonify({"error": "Question ID doesn't exist"}), 404

        question = questions.get_question(question_id)
        return jsonify(question), 200

    except Exception as e:
        return jsonify({"error": f"Failed to get question: {str(e)}"}), 500

@app.route("/api/update-role", methods=["POST"])
def update_role():
    """
    Update role matching with new answer data for real-time assessment.
    
    Processes a single answer through the matching algorithm without saving
    to database. Used for providing live feedback during assessment.
    
    Request Body:
        {
            "question_id": 1,
            "answer": "Yes" | ["option1", "option2"] | {...}
        }
    
    Returns:
        - JSON: Success confirmation
        
    Status Codes:
        - 200: Role matching updated successfully
        - 400: Missing required fields
        - 500: Matching system not initialized
        
    Usage:
        fetch('/api/update-role', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                question_id: 1,
                answer: 'Yes'
            })
        });
    """        
    try:
        if not match:
            return jsonify({"error": "Matching system not initialized"}), 500

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400

        if "answer" not in data or "question_id" not in data:
            return jsonify({"error": "Missing required fields"}), 400

        answer = data["answer"]
        if isinstance(answer, (list, dict)):
            data["answer"] = json.dumps(answer)
        else:
            data["answer"] = str(answer)

        match.process_assessment(data)
        return jsonify({"status": "Success", "message": "Role updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to update role: {str(e)}"}), 500

@app.route("/api/get-roles", methods=["GET"])
def get_best_fit_roles():
    """
    Get current best-fit role recommendations from the matching system.
    
    Returns the current state of role matching results, including
    best fit roles and next best alternatives.
    
    Returns:
        - JSON: Role matching results
        
    Status Codes:
        - 200: Roles retrieved successfully
        - 400: No matching data available
        - 404: Invalid data format
        - 500: Matching system not initialized
        
    Usage:
        fetch('/api/get-roles')
        .then(response => response.json())
        .then(data => {
            const bestRoles = data['Best fit roles'];
            const nextBest = data['Next best roles'];
            // Display role recommendations
        });
    """        
    try:
        if not match:
            return jsonify({"error": "Matching system not initialized"}), 500

        best_roles = match.get_top_matches()

        if not best_roles:
            return jsonify({"error": "No best fit roles data"}), 400

        if "Best fit roles" not in best_roles:
            return jsonify({"error": "Invalid data format"}), 404 

        return jsonify(best_roles), 200

    except Exception as e:
        return jsonify({"error": f"Failed to get best fit roles: {str(e)}"}), 500

@app.route("/api/reset", methods=["POST"])
def reset_assessment():
    """
    Reset the assessment matching system to initial state.
    
    Reinitializes the matching algorithm and questions system,
    clearing any previous assessment state for a fresh start.
    
    Returns:
        - JSON: Reset confirmation
        
    Status Codes:
        - 200: System reset successfully
        - 500: Reset failed
        
    Usage:
        fetch('/api/reset', {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            if (data.status === 'Success') {
                // Assessment system is ready for new session
            }
        });
    """        
    try:
        global match, questions
        match = Matches(data_path=MAIN_DATA_PATH, student_status=True)
        questions = Questions()
        
        return jsonify({
            "status": "Success", 
            "message": "Assessment system reset successfully"
        }), 200

    except Exception as e:
         return jsonify({"error": f"Failed to reset assessment system: {str(e)}"}), 500

@app.route("/api/role-links", methods=["POST"])
def get_role_links():
    """
    Retrieve all available links for a specific volunteer role.
    
    Returns express links, description links, and video links for the
    specified role name, if available in the role links database.
    
    Request Body:
        {
            "role_name": "Software Developer"
        }
    
    Returns:
        - JSON: Links object with express_link, desc_link, and video_link
        
    Status Codes:
        - 200: Links retrieved successfully
        - 400: Missing role_name field
        - 404: No links found for the specified role
        - 500: Role links system not configured
        
    Usage:
        fetch('/api/role-links', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({role_name: 'Software Developer'})
        })
        .then(response => response.json())
        .then(links => {
            window.open(links.express_link);  // Quick info
            window.open(links.desc_link);     // Detailed description
            window.open(links.video_link);    // Training video
        });
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400

        if "role_name" not in data:
            return jsonify({"error": "Missing role_name field"}), 400 

        role_name = data["role_name"]

        if not role_links:
            return jsonify({"error": "Role links module not configured"}), 500

        express_link = role_links.get_express_link(role_name)
        desc_link = role_links.get_description_link(role_name)
        video_link = role_links.get_video_link(role_name)

        if express_link and desc_link:
            return jsonify({
            "status": "Success",
            "express_link": express_link,
            "desc_link": desc_link,
            "video_link": video_link
            }), 200
        else:
            return jsonify({"error": "Links not found for this role"}), 404

    except Exception as e:
        return jsonify({"error": f"Failed to retrieve role links: {str(e)}"}), 500

# ========== ADMIN ENDPOINTS ==========

@app.route("/api/admin-login", methods=["POST"])
def admin_login():
    """
    Authenticate admin user and create session token.
    
    Validates admin password against environment variable and generates
    a session token for accessing protected admin endpoints.
    
    Request Body:
        {
            "password": "admin-password"
        }
    
    Returns:
        - JSON: Session token for authenticated admin access
        
    Status Codes:
        - 200: Login successful
        - 403: Invalid password
        - 500: Admin not configured (missing ADMIN_TOKEN env var)
        
    Usage:
        fetch('/api/admin-login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({password: 'admin-password'})
        })
        .then(response => response.json())
        .then(data => {
            const token = data.session_token;
            // Store token for subsequent admin requests
            localStorage.setItem('adminToken', token);
        });
    """
    data = request.get_json() or {}
    password = data.get("password")
    
    ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")
    if not ADMIN_TOKEN:
        return jsonify({"error": "Admin not configured"}), 500
    
    if password != ADMIN_TOKEN:
        return jsonify({"error": "Invalid password"}), 403
    
    # Generate simple session token
    session_token = str(uuid.uuid4())
    AUTHORIZED_SESSIONS.add(session_token)
    
    return jsonify({"status": "success", "session_token": session_token}), 200

@app.route("/api/upload-match-data", methods=["POST"])
@require_admin
def upload_match_data():
    """
    Upload new matching data CSV file (admin only).
    
    Allows administrators to upload a new CSV file containing role matching
    data. The file is saved permanently and the system is reconfigured to
    use the new data for all future assessments.
    
    Request:
        multipart/form-data with 'file' field containing CSV
        Requires X-Admin-Token header with valid session token
    
    Returns:
        - JSON: Upload confirmation with file details
        
    Status Codes:
        - 200: File uploaded and system updated successfully
        - 400: No file provided or invalid file type
        - 403: Unauthorized (invalid admin token)
        - 500: File processing or system update failed
        
    Usage:
        const formData = new FormData();
        formData.append('file', csvFile);
        
        fetch('/api/upload-match-data', {
            method: 'POST',
            headers: {'X-Admin-Token': adminToken},
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);  // "Updated match data from filename.csv"
        });
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    if not file.filename.endswith('.csv'):
        return jsonify({"error": "Only CSV files allowed"}), 400
    
    try:
        # Create uploads directory if it doesn't exist
        uploads_dir = "uploads"
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
            
        # Save file permanently
        permanent_path = os.path.join(uploads_dir, f"match_data_{uuid.uuid4().hex[:8]}.csv")
        file.save(permanent_path)
        
        # Update configuration and reinitialize system
        update_file_paths(main_data_path=permanent_path)
        
        return jsonify({
            "status": "success", 
            "message": f"Updated match data from {file.filename}",
            "file_path": permanent_path
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500

@app.route("/api/upload-role-links", methods=["POST"])
@require_admin
def upload_role_links():
    """
    Upload new role links CSV file (admin only).
    
    Allows administrators to upload a new CSV file containing role link
    information. The file is saved permanently and the system is reconfigured
    to use the new links for all future role link requests.
    
    Request:
        multipart/form-data with 'file' field containing CSV
        Requires X-Admin-Token header with valid session token
    
    Returns:
        - JSON: Upload confirmation with file details
        
    Status Codes:
        - 200: File uploaded and system updated successfully
        - 400: No file provided or invalid file type
        - 403: Unauthorized (invalid admin token)
        - 500: File processing or system update failed
        
    Usage:
        const formData = new FormData();
        formData.append('file', csvFile);
        
        fetch('/api/upload-role-links', {
            method: 'POST',
            headers: {'X-Admin-Token': adminToken},
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);  // "Updated role links from filename.csv"
        });
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    if not file.filename.endswith('.csv'):
        return jsonify({"error": "Only CSV files allowed"}), 400
    
    try:
        # Create uploads directory if it doesn't exist
        uploads_dir = "uploads"
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
            
        # Save file permanently  
        permanent_path = os.path.join(uploads_dir, f"role_links_{uuid.uuid4().hex[:8]}.csv")
        file.save(permanent_path)
        
        # Update configuration and reinitialize system
        update_file_paths(role_link_path=permanent_path)
        
        return jsonify({
            "status": "success", 
            "message": f"Updated role links from {file.filename}",
            "file_path": permanent_path
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """
    Handle 404 Not Found errors with JSON response.
    
    Returns consistent JSON error format for invalid endpoints
    instead of default HTML 404 page.
    
    Args:
        - error: Flask error object (automatically provided)
        
    Returns:
        - JSON: Error message with 404 status code
        
    Usage:
        # Automatically called for invalid endpoints
        # GET /api/invalid-endpoint -> {"error": "Endpoint not found"}
    """
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """
    Handle 500 Internal Server Error with JSON response.
    
    Returns consistent JSON error format for server errors
    instead of default HTML error page.
    
    Args:
        - error: Flask error object (automatically provided)
        
    Returns:
        - JSON: Error message with 500 status code
        
    Usage:
        # Automatically called for unhandled exceptions
        # Any endpoint with server error -> {"error": "Internal server error"}
    """
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    """
    Start the Flask development server when script is run directly.
    
    Configures the server to run on localhost:5001 with debug mode enabled
    for development. In production, use a proper WSGI server instead.
    
    Usage:
        # Run the server
        python app.py
        
        # Server starts at: http://localhost:5001
        # API endpoints available at: http://localhost:5001/api/*
    """
    print("Starting Flask development server...")
    app.run(debug=True, host="localhost", port=5001)