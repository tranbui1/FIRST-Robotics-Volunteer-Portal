"""
Assessment Questions Module

This module defines the question structure and provides access methods for 
a volunteer role assessment questionnaire. Questions include demographics,
physical abilities, availability, preferences, and experience levels.
"""

# Global question data structure containing all assessment questions
questions = {
    "user_info": {
        "question": "Please provide your contact information",
        "type": "user-info",
        "prompt": "We need some basic information to continue",
        "id": 0
    },
    "age": {
        "question": "What is your age?",
        "type": "custom-dropdown",
        "options": ["13 to 15 years old", "16 to 17 years old", "18 and older"],
        "prompt": "Select your age",
        "id": 1
    },
    "physical_ability": {
        "question": "Do you prefer roles with physical activity?",
        "type": "select-3",
        "options": ["Yes", "No", "No Preference"],
        "id": 2
    },
    "physical_ability_stand": {
        "question": "Are you able to stand for long periods of time?",
        "type": "select-2",
        "options": ["Yes", "No"],
        "id": 3
    },
    "physical_ability_move": {
        "question": "Are you able to move around for long periods of time (e.g., walking, lifting)?",
        "type": "select-2",
        "options": ["Yes", "No"],
        "id": 4
    },
    "availability": {
        "question": "How many days are you available to volunteer for?",
        "type": "multiselect",
        "options": [
            "Friday",
            "Saturday",
            "Sunday"
        ],
        "prompt": "Select your availability",
        "description": "You can select multiple answers.",
        "id": 5
    },
    # NOTE: Placeholder question.
    "working_preference": {
        "question": "Do you prefer working behind the scenes, front-facing, or no preference?",
        "type": "select-3",
        "options": ["BTS", "Front-facing", "No Preference"],
        "id": 6
    },
    "leadership_preference": {
        "question": "Do you prefer roles with leadership responsibilities?",
        "type": "select-3",
        "options": ["Yes", "No", "No Preference"],
        "id": 7
    },
    "prior_experience": {
        "question": "Do you have any prior experience with FIRST, volunteering or participating in the competitions?",
        "type": "select-2",
        "options": ["Yes", "No"],
        "id": 8
    },
    "game_knowledge": {
        "question": "How much knowledge do you have of the FIRST Robotics Competition and game rules?",
        "type": "custom-dropdown",
        "options": ["None", "Limited", "Average", "Thorough"],
        "prompt": "Select your level of knowledge",
        "description": "Select one option from the dropdown.",
        "id": 9
    },
    "required_skills": {
        "question": "Which of the following required skills do you have?",
        "type": "multiselect",
        "options": [
            "Basic computer literacy",
            "Programming (C++, Java, Python, or LabVIEW)",
            "Photo and video editing",
            "Control systems and diagnostics",
            "Technical writing",
            "Event coordination",
            "FIRST Robotics safety protocol compliance",
            "None"
        ],
        "prompt": "Select your skills",
        "description": "You can select multiple answers.",
        "id": 10
    },
    "experience": {
        "question": "Which of the following experiences do you have?",
        "type": "multiselect",
        "options": [
            "FIRST Robotics Competition Control System experience",
            "4 years of FIRST Robotics Competition referee experience",
            "2 years of FIRST robot build experience",
            "Event management experience",
            "3 years of Robotics Competition judging experience",
            "Technical inspection experience",
            "None"
        ],
        "prompt": "Select your experience",
        "description": "You can select multiple answers.",
        "id": 11
    }
}

# Ordered list of question keys for sequential access
keys = ["user_info", "age", "physical_ability", "physical_ability_stand",
        "physical_ability_move", "availability", "working_preference",
        "leadership_preference", "prior_experience",
        "game_knowledge", "required_skills", "experience"]


class Questions:
    """
    A manager class for accessing assessment question data and metadata.
    
    This class provides methods to retrieve question information by ID,
    including question text, input types, available options, and prompts.
    Questions are designed for a volunteer role assessment system.
    
    Question Types:
        - "user-info": Form for collecting name, email, and zipcode
        - "custom-dropdown": Dropdown with custom prompt text
        - "select-2": Binary choice (Yes/No)
        - "select-3": Three-option choice (Yes/No/No Preference)
        - "multiselect": Multiple selection allowed
    
    Usage:
        # Initialize questions manager
        q_manager = Questions()
        
        # Get question by sequential ID
        question_0 = q_manager.get_question(0)  # User info question
        
        # Get question components
        q_type = q_manager.get_type(0)
        options = q_manager.get_options(0)
        
        # Iterate through all questions
        for i in range(len(keys)):
            question = q_manager.get_question(i)
            print(f"Q{i}: {question['question']}")
    """
    
    def get_question(self, question_id):
        """
        Retrieve complete question data by sequential question ID.
        
        Gets the full question dictionary containing all metadata including
        question text, type, options, prompt, and internal ID. Handles
        out-of-range IDs by wrapping to the first question.
        
        Args:
            - question_id (int): Sequential question number (0-based index).
                              Values outside valid range wrap to 0.
                              
        Returns:
            - dict: Complete question dictionary with keys:
                  - 'question': The question text
                  - 'type': Input type (user-info, custom-dropdown, select-2, etc.)
                  - 'options': List of available answer options (if applicable)
                  - 'prompt': Display prompt (if applicable)
                  - 'id': Internal question ID
                  
        Usage:
            q_manager = Questions()
            
            # Get first question (user info)
            user_info_question = q_manager.get_question(0)
            print(user_info_question['question'])  # "Please provide your contact information"
            print(user_info_question['type'])      # "user-info"
            
            # Get second question (age)
            age_question = q_manager.get_question(1)
            print(age_question['options'])   # ["13 to 15 years old", ...]
            
            # Out of range wraps to first question
            invalid_q = q_manager.get_question(999)  # Returns user info question
        """
        if question_id > len(questions) - 1:
            question_id = 0
        return questions[keys[question_id]]

    def get_type(self, question_id):
        """
        Get the input type for a specific question by ID.
        
        Retrieves the question type which determines how the question
        should be rendered in the user interface.
        
        Args:
            - question_id (int): Sequential question number (0-based index)
            
        Returns:
            - str: Question type string. Possible values:
                 - "user-info": Form for name, email, zipcode
                 - "custom-dropdown": Dropdown with custom prompt
                 - "select-2": Binary choice
                 - "select-3": Three-option choice  
                 - "multiselect": Multiple selection allowed
                 
        Usage:
            q_manager = Questions()
            
            q_type = q_manager.get_type(0)  # "user-info"
            if q_type == "user-info":
                # Render user information form
                pass
            elif q_type == "multiselect":
                # Allow multiple selections
                pass
            elif q_type == "select-2":
                # Show Yes/No buttons
                pass
        """
        return questions[keys[question_id]]["type"]

    def get_options(self, question_id):
        """
        Get the available answer options for a specific question by ID.
        
        Retrieves the list of possible answers that users can select from
        for the specified question. Returns None for questions without options
        (like user-info forms).
        
        Args:
            - question_id (int): Sequential question number (0-based index)
            
        Returns:
            - list or None: List of answer option strings available for the question,
                           or None if the question doesn't have predefined options
            
        Usage:
            q_manager = Questions()
            
            # Get age options
            age_options = q_manager.get_options(1)
            # Returns: ["13 to 15 years old", "16 to 17 years old", "18 and older"]
            
            # Get availability options
            avail_options = q_manager.get_options(5)
            # Returns: ["Friday", "Saturday", "Sunday"]
            
            # User info question has no predefined options
            user_options = q_manager.get_options(0)
            # Returns: None
            
            # Use in UI rendering
            options = q_manager.get_options(question_id)
            if options:
                for option in options:
                    render_option_button(option)
        """
        return questions[keys[question_id]].get("options")
    
    def get_question_by_key(self, question_key):
        """
        Retrieve complete question data by question key name.
        
        Alternative access method using the question key instead of numeric ID.
        Useful when you know the specific question name.
        
        Args:
            - question_key (str): The question key name (e.g., 'user_info', 'age', 'availability')
            
        Returns:
            - dict: Complete question dictionary, or None if key not found
            
        Usage:
            q_manager = Questions()
            
            # Get question by key name
            user_info_q = q_manager.get_question_by_key('user_info')
            age_q = q_manager.get_question_by_key('age')
            avail_q = q_manager.get_question_by_key('availability')
            
            if user_info_q:
                print(user_info_q['question'])
        """
        return questions.get(question_key)
    
    def get_total_questions(self):
        """
        Get the total number of questions in the assessment.
        
        Returns the count of all questions available in the system,
        useful for progress tracking and validation.
        
        Returns:
            - int: Total number of questions available
            
        Usage:
            q_manager = Questions()
            total = q_manager.get_total_questions()
            print(f"Assessment has {total} questions")
            
            # Calculate progress
            current_question = 5
            progress = (current_question / total) * 100
        """
        return len(questions)
    
    def get_all_question_keys(self):
        """
        Get an ordered list of all question keys.
        
        Returns the complete list of question keys in the order they
        should be presented to users.
        
        Returns:
            - list: Ordered list of question key strings
            
        Usage:
            q_manager = Questions()
            all_keys = q_manager.get_all_question_keys()
            
            # Iterate through all questions in order
            for key in all_keys:
                question = q_manager.get_question_by_key(key)
                process_question(question)
        """
        return keys.copy()
    
    def is_valid_question_id(self, question_id):
        """
        Check if a question ID is within the valid range.
        
        Validates that the provided question ID corresponds to an actual
        question in the assessment.
        
        Args:
            - question_id (int): The question ID to validate
            
        Returns:
            - bool: True if question ID is valid, False otherwise
            
        Usage:
            q_manager = Questions()
            
            if q_manager.is_valid_question_id(5):
                question = q_manager.get_question(5)
            else:
                print("Invalid question ID")
        """
        return 0 <= question_id < len(questions)