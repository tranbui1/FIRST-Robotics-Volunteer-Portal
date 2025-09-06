# FIRST-Robotics-Volunteer-Portal

## Tech Stack
- Frontend: React, CSS  
- Backend: Python with Flask
- Database: sqlite3
- Authentication: Session tokens  

## Getting started

### Prerequisites (including but not limited to)
External modules/libraries can be install via command `pip install [module name]`

- Python 3.10+
- Flask
- python-dotenv
- requests
- google-auth
- SQLite3 (built-in)
- An `api.env` file with your API keys and configuration
    - API keys needed:
        1. Google Sheet ID for storing user data
        2. Google Service Account File for authorization
    - Admin Token
- And more ... (can be found via imported modules are the top of each file)

## Installation
1. Clone the repository
```bash
git clone https://github.com/tranbui1/FIRST-Robotics-Volunteer-Portal.git
cd FIRST-Robotics-Volunteer-Portal
```

2. Set up Python environment
```bash
pip install -r requirements.txt
```

3. Set up the frontend
```bash
cd frontend
npm install
```

4. Set up API file
```bash
cd backend
touch api.env
```

## Folder Structure
```
first_volunteer_project/
├── backend/
│   ├── api.env                         # API keys & config (not included)
│   ├── app.py                          # Main Flask app
│   ├── assessment.db                   # SQLite database (not included, will be auto-created by app.py)
│   ├── config_utils.py                 # Helper functions for dynamic CSV path management for matching and role links
│   ├── google_sheets.py                # Google Sheets integration
│   ├── links.py                        # Role and Express links management
│   ├── model/
│   │   ├── keywords.py                 # Logic for keyword handling
│   │   ├── matching_logic.py           # Matching logic for volunteers and roles
│   │   └── responses.py                # Response parsing and handling
│   ├── questions.py                    # Question definitions & handling
│   ├── tests/
│   │   └── test_google_sheets.py       # Tests for Google Sheets integration
│   └── workspace.code-workspace        # VS Code workspace
├── frontend/
│   ├── public/                         # Public assets (HTML, images)
│   ├── src/                            # React source code
│   │   ├── App.css                     
│   │   ├── App.js                      # Contains all web page routes of the program
│   │   ├── App.test.js     
│   │   ├── index.css
│   │   ├── index.js
│   │   ├── reportWebVitals.js
│   │   ├── setupTests.js
│   │   ├── components/                 # Subfolder containing React JSX and JS components used
│   │   │   ├── AgeDropDown.jsx         # Drop down for age component
│   │   │   ├── CreateNumButtons.jsx    # Creates custom number of buttons
│   │   │   ├── CustomDropDown.jsx      # Creates custom drop down (single answer)
│   │   │   ├── DynamicFontSize.js      # Dynamically calculates and resizes question font size
│   │   │   ├── Modal.jsx               # Creates the exit pop-up modal
│   │   │   ├── MultiChoiceDropDown.jsx # Creates custom drop down (multi-choice)
│   │   │   ├── NavigationMenu.jsx      # Creates the navigation menu (next, back, submit)
│   │   │   ├── RenderContent.jsx       # Controls what is displayed on the frontend
│   │   │   └── UserInfoForm.jsx        # User info form (name, email, address)
│   │   ├── pages/                      # Subfolder containing all frontend page templates
│   │   │   ├── AdminUpload.jsx         # Template for the page to upload data, requires admin password
│   │   │   ├── first_volunteer_project.code-workspace
│   │   │   ├── Home.css                # CSS styling for Home.jsx
│   │   │   ├── Home.jsx                # Template for landing/integration page (placeholder)
│   │   │   ├── Page.css                
│   │   │   ├── Page.jsx                # Template for the displaying general information about matched roles
│   │   │   ├── Questionnaire.css       
│   │   │   ├── Questionnaire.jsx       # Template for the questionnaire
│   │   │   ├── Results.css             
│   │   │   └── Results.jsx             # Template for the page displaying top 3 matched roles
│   │   └── utils/
│   │       └── questionnaireUtils.js   # Utilities for the questionnaire
│   ├── package.json                    # Frontend dependencies
│   └── README.md                       # Frontend README
├── LICENSE
├── package.json
├── package-lock.json
└── first_volunteer_project.code-workspace  # VS Code workspace
```

## Setting up the Google Sheet API
We currently use Google Cloud to update a Google Sheet with user data. 

1. Create a project: https://console.cloud.google.com/welcome/new

2. Enable the Google Sheets API
    - Go to your project dashboard in Google Cloud Console.
    - Navigate to APIs & Services → Library.
    - Search for Google Sheets API and click Enable.

3. Create Service Account Credentials
    - Go to APIs & Services → Credentials → Create Credentials → Service Account.
    - Fill in a name and description, then click Create.
    - Assign a role like Editor (or more restrictive if needed).

4. Generate a JSON Key File
    - In the service account, go to Keys → Add Key → Create new key → JSON.
    - Download the JSON file, which serves as our API authorization file.
    - Copy the path link and paste it to `GOOGLE_SERVICE_ACCOUNT_FILE` in the api.env file.

5. Share the Google Sheet with the Service Account
    - Open your Google Sheet in the browser.
    - Click Share, then enter the service account email (from the JSON, it usually looks like your-project@your-project-id.iam.gserviceaccount.com).
    - Give it Editor access so it can read/write data.

6. Set up the spreadsheet
    - Rename the spreadsheet page to `Responses` at the bottom left
        - The default name will be `Sheet1`
    - Done!
    - The end point Google Sheet can be customized aesthetically however needed
        for easy readability as long as header names and column order remain the same.

7. For uploading Google Sheets of role description and express links, create an admin
password via `ADMIN_TOKEN`.

Example api.env file:
```
GOOGLE_SHEET_ID=your-google-sheet-id
GOOGLE_SERVICE_ACCOUNT_FILE=/absolute/path/to/credentials.json
ADMIN_TOKEN=your-admin-password
```

## Environment Variables Reference
| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `GOOGLE_SHEET_ID` | ID of the Google Sheet for storing responses | Yes | `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms` |
| `GOOGLE_SERVICE_ACCOUNT_FILE` | Path to service account JSON file | Yes | `/path/to/credentials.json` |
| `ADMIN_TOKEN` | Password for admin functionality | Yes | `your-secure-password` |

# Setting Up Necessary Google Sheet Files
## Overview

This volunteer matching system requires a properly formatted Google Sheet to function correctly. The sheet contains role data that the matching algorithm uses to score and recommend volunteer positions based on user preferences and qualifications.

## Required Sheet: Matching Logic

### Required Columns

The Google Sheet must contain the following columns in order:

| Column Name | Description | Values |
|-------------|-------------|---------|
| `role_name` | Name of the volunteer role | Text (e.g., "Control System Advisor", "Head Referee") |
| `work_pref` | Work environment preference | "BTS" (Behind the Scenes) or "Front-Facing" |
| `age_min` | Minimum age requirement | Number or "Students" |
| `age_preference` | Preferred age | Number or FALSE if no preference |
| `leadership_pref` | Leadership role indicator | TRUE/FALSE |
| `required_certifications` | Required certifications | Text description or FALSE |
| `required_skills` | Required technical skills | Text description or FALSE |
| `prior_first_exp` | Prior FIRST experience needed | TRUE/FALSE/"Preferred" | 
| `required_experience` | Specific experience requirements | Text description or FALSE |
| `preferred_experience` | Preferred experience | Text description or FALSE | *** Currently unused ***
| `basic_game_knowledge` | Game knowledge requirement | TRUE/FALSE or text description |
| `physical_req` | Physical requirements | Text description or FALSE |
| `regionals_day_commitment` | Days needed for regionals | Space-separated numbers (0-3) or FALSE |
| `district_day_commitment` | Days needed for districts | Space-separated numbers (0-2) or FALSE |

### Data Entry Guidelines

#### Boolean Values
- Use `TRUE` when a column is applicable but no specific details are provided
- Use `FALSE` when a column is not applicable to the role

#### Text Descriptions
For skill and experience columns, use descriptive text that contains keywords from the matching system. The algorithm will parse these descriptions using the keyword dictionaries. Additional keywords can be added
in case of missing/incomplete dictionaries. `TRUE` can also be combined with text description via a
comma.

#### Day Commitments
Days are represented by numbers:

**Regional Events (Thursday-Sunday):**
- 0 = Thursday
- 1 = Friday  
- 2 = Saturday
- 3 = Sunday

**District Events (Friday-Sunday):**
- 0 = Friday
- 1 = Saturday
- 2 = Sunday

Examples:
- `1 2 3` = Friday, Saturday, Sunday
- `2` = Saturday only
- `FALSE` = Role not available for this event type

### Keyword Matching

The system uses keyword dictionaries to categorize skills and experiences. When entering text descriptions in the following columns, include relevant keywords:

- `required_skills`
- `required_experience` 
- `preferred_experience` !!! Currently unused !!!

#### Expandable Keywords
You can add new keywords to the keyword dictionaries in the code if needed. The current categories include:

**Skills:**
- Programming Proficiency
- Mechanical/Technical Skills
- Control Systems & Diagnostics
- Photo/Video Processing
- Advanced Machine Shop Skills
- And more...

**Experience:**
- FRC Control System Experience
- Robot Build Experience
- Machine Shop Experience  
- Management/Supervision Experience
- And more...

### Setup Steps

1. Create a new Google Sheet or copy the existing template
2. Add all required columns as headers in the first row
3. Fill in data for every volunteer role 
4. Ensure proper formatting of day commitments and boolean values
5. Export as CSV when ready to use with the matching system

### Data Validation

Before using the sheet:
- Verify all role names are unique
- Check that day commitment numbers are within valid ranges
- Ensure required columns don't have empty cells (use FALSE if not applicable)
- Test that skill/experience descriptions contain recognizable keywords

### Troubleshooting

**Common Issues:**
- Missing or misspelled column names will cause parsing errors
- Invalid day numbers (e.g., 4 for regionals) will be ignored
- Empty cells in critical columns may affect matching accuracy
- Inconsistent TRUE/FALSE capitalization can cause parsing issues

## Required Sheet: Role Links

### Overview

The Role Links file is a supplementary CSV that contains URLs for role descriptions, 
signup links, and introduction videos. 

### File Format

CSV file containing role information links (name can be anything).

### Required Columns

| Column Name | Description | Values |
|-------------|-------------|---------|
| `role_name` | Name of the volunteer role | Text (must match role names in main data file) |
| `desc_link` | Link to detailed role description | URL |
| `express_link` | Link for express signup/application | URL |
| `video_link` | Link to introduction video | URL |

### Data Guidelines

#### Role Name Matching
- Role names must **exactly match** those in the main matching logic data file
- Case sensitive matching
- Include all roles from the main matching logic data file

#### Link Requirements
- All URLs should be complete and valid
- Use consistent formatting across all links

### Setup Steps

1. **Create the CSV file**
   - Add the four required column headers
   - Ensure exact spelling and capitalization

2. **Add role data**
   - One row per volunteer role
   - Add corresponding URLs for each role

3. **Validate data**
   - Check that all role names match the main matching logic file
   - Test that all URLs are working
   - Verify no missing data

4. **Export and save**
   - Save as CSV format
   - Note the file path for system configuration

### Troubleshooting

**Common Issues:**
- **Role name mismatch**: Ensure exact spelling and capitalization match the main matching logic data file
- **Broken links**: Test all URLs before deployment
- **Missing roles**: Include every role from the main  matching logic data file

## Running the program
1. Start the backend server 
```bash
cd backend
flask --app app run
```

2. Start the frontend development server
```bash
cd frontend
npm start
```

## Database Schema
The SQLite database (`assessment.db`) contains the following tables:

### `assessment_sessions`
- **id** (INTEGER PRIMARY KEY) - Auto-incrementing session identifier
- **session_id** (TEXT UNIQUE) - UUID for session tracking
- **created_at** (TIMESTAMP) - Session creation timestamp
- **status** (TEXT) - Session status ('in_progress' or 'completed')

### `user_answers`  
- **id** (INTEGER PRIMARY KEY) - Auto-incrementing answer identifier
- **session_id** (TEXT) - Foreign key to assessment_sessions
- **question_id** (TEXT) - Question identifier (0-10)
- **question** (TEXT) - Question text for reference
- **answer** (TEXT) - User's response (JSON string for complex answers)
- **created_at** (TIMESTAMP) - Answer submission timestamp
- **UNIQUE(session_id, question_id)** - Prevents duplicate answers per session

## API Endpoints

### Core Assessment Endpoints
- **`POST /api/start-session`** - Create new assessment session with UUID
- **`POST /api/save-answer`** - Save individual question response to database
- **`POST /api/submit`** - Complete assessment and generate role matches
- **`POST /api/get-question`** - Retrieve question data by question ID
- **`POST /api/update-role`** - Update matching algorithm with new answer (real-time)
- **`GET /api/get-roles`** - Get current best-fit role recommendations
- **`POST /api/reset`** - Reset matching system to initial state

### Role Information Endpoints
- **`POST /api/role-links`** - Get express links, descriptions, and videos for specific roles

### Admin Endpoints (Requires X-Admin-Token header)
- **`POST /api/admin-login`** - Authenticate and receive session token
- **`POST /api/upload-match-data`** - Upload new matching data CSV file
- **`POST /api/upload-role-links`** - Upload new role links CSV file

### Utility Endpoints
- **`GET|POST /api/test`** - Test CORS configuration and API connectivity

## Matching Algorithm
The volunteer-role matching system uses a comprehensive multi-factor scoring algorithm implemented in the `Matches` class. The algorithm evaluates volunteers across multiple dimensions and assigns weighted scores to determine compatibility with available roles.

### Core Algorithm Components

#### 1. **Age Requirements** (Critical Filter)
- **Hard Requirements**: Roles specify minimum age (numeric or "Students")
- **Student Override**: Student status bypasses numeric age requirements for student-designated roles
- **Scoring**: Perfect age matches (5 points), acceptable matches (3 points)
- **Elimination**: Age-ineligible volunteers are filtered out when `eliminate_unqualified=True`

#### 2. **Physical Requirements** (5-8 points per category)
- **Physical Activity**: Matches volunteer's physical activity preference with role demands
- **Standing/Walking**: Evaluates ability to stand/walk using keyword detection in role descriptions
- **General Mobility**: Assesses movement requirements (walk, run, carry, lift, transport)
- **Smart Matching**: Uses regex pattern matching to detect physical requirements in role descriptions

#### 3. **Time Commitment** (Variable scoring)
- **District vs Regional**: Separate evaluation for different event types
- **Flexible Matching**: Uses `TimeCommitmentResponse` class to parse and compare time ranges
- **Compatibility Scoring**: Exact matches receive highest scores, with graduated scoring for compatible ranges
- **Elimination**: Roles marked as unavailable ("FALSE") are automatically eliminated

#### 4. **Work Environment Preferences** (5 points) !! PLACEHOLDER !!
- **Behind-the-Scenes (BTS)** vs **Front-facing (FRONT)** role preferences
- **No Preference**: Volunteers with no preference don't receive scoring penalties
- **Binary Matching**: Direct preference alignment with role requirements

#### 5. **Leadership Preferences** (5 points)
- **Boolean Matching**: Aligns volunteer leadership interest with role leadership requirements
- **Flexible Preferences**: "No preference" responses don't penalize scores
- **Elimination Option**: Can filter out leadership mismatches when enabled

#### 6. **FIRST Robotics Experience** (3-8 points)
- **Experience Levels**: 
  - Required experience: 8 points for experienced volunteers
  - Preferred experience: 5 points for experienced, -2 penalty for inexperienced
  - No requirement: 3 points for experienced, 5 points for inexperienced (newcomer-friendly)
- **Smart Parsing**: Uses keyword detection to categorize experience requirements from text

#### 7. **Game Knowledge Requirements** (5-8 points)
- **Knowledge Levels**: NONE → LIMITED → AVERAGE → THOROUGH
- **Hierarchical Matching**: Higher knowledge levels satisfy lower requirements
- **Perfect Match Bonus**: 8 points for exact level matches, 5 points for sufficient knowledge
- **Elimination**: Insufficient knowledge can eliminate candidates

#### 8. **Skills & Experience Requirements** (3-8 points)
- **Keyword Categorization**: Uses `RegexSkillCategorizer` to parse free-text skill requirements
- **Skill Categories**: Programming, mechanical, electrical, communication, teamwork, etc.
- **Weighted Scoring**: Required skills (8 points), experience requirements (3 points)
- **Flexible Matching**: "NONE" category always matches (for roles with no specific requirements)

### Algorithm Workflow

#### Assessment Processing
```python
# Example assessment flow
matcher = Matches(student_status=True, data_path="roles.csv")

# Process each questionnaire response
for question_data in user_responses:
    matcher.process_assessment(question_data, eliminate_unqualified=True)

# Get final results
top_matches = matcher.get_top_matches(num=3)
```

#### Scoring Strategy
1. **Additive Scoring**: Each compatible factor adds points to the role's total score
2. **No Negative Scoring**: Mismatches don't subtract points (except experience preferences)
3. **Elimination Over Penalization**: Poor matches are eliminated rather than heavily penalized
4. **Fallback System**: If all roles are eliminated, returns highest-scoring eliminated roles

#### Result Generation
- **Primary Results**: Top-scoring non-eliminated roles
- **Fallback Results**: If insufficient active roles remain, includes best eliminated roles
- **Dual Categories**: "Best fit roles" (active) and "Next best roles" (fallback)

### Technical Implementation Details

#### Data Processing
- **CSV Integration**: Loads role data from dynamic CSV files
- **Boolean Conversion**: Handles string "true"/"false" values in data
- **Regex Parsing**: Extracts numerical values and keywords from free-text fields
- **Error Handling**: Graceful handling of malformed or missing data

## Common Issues & Troubleshooting

### CORS Issues
CORS is a built-in security feature that prevents random websites from 
using our own website's authenticated cookies to send API requests to our
backend and retrieve sensitive data.

A common CORS issue that will be encountered during this step is our 
backend and frontend running on different ports. When our backend and frontend 
are running on different ports (e.g., localhost:5000 for backend and localhost:3000 
for frontend), browsers consider them different origins, which triggers CORS 
restrictions, preventing our backend from communicating with our frontend.

The current frontend and backend are programmed to run on localhost:3000 and port 5001
for the development phase. 

Troubleshooting steps: 
1. Ensure that port 5001 on your local device is free with the terminal command: 
   - MacOS: `lsof -i :5001` 
   - Windows: `netstat -ano | findstr :5001`
   
   If the command returns nothing, then we are good to go!

2. Restart the backend and rerun with command `flask --app app run --port=5001` to
   force the backend to run on port 5001 as it sometimes defaults to port 5000.

### Database Issues
- **Database not found**: The SQLite database will be auto-created on first run
- **Permission errors**: Ensure the backend directory has write permissions
- **Corrupted database**: Delete `assessment.db` and restart the Flask app

### Google Sheets Authentication
- **401 Unauthorized**: Check that the service account email has been shared with the spreadsheet
- **403 Forbidden**: Verify the Google Sheets API is enabled in your Google Cloud project
- **File not found**: Ensure the path to the service account JSON file is correct and absolute

### Node/NPM Issues
- **Module not found**: Run `npm install` in the frontend directory
- **Port already in use**: Kill processes on port 3000 or use `npm start -- --port 3001`
- **Build errors**: Clear npm cache with `npm cache clean --force`

## Performance Considerations
- The matching algorithm processes in O(n*m) time where n = volunteers, m = roles
- Google Sheets API has rate limits: 100 requests per 100 seconds per user
- SQLite is suitable for up to ~1000 concurrent volunteers