import re

PREF_EXPERIENCE_KEYWORDS = {
    "FRC CONTROL SYSTEM EXPERIENCE": [
        "frc control system", "hands-on frc control system", "control system experience",
        "diagnostic tools", "first robotics competition control system",
        "control system wiring", "understanding of control system wiring"
    ],
    
    "FIELD MANAGEMENT SYSTEM EXPERIENCE": [
        "field management system", "fms", "game field", "field electronics",
        "field mechanical", "field electrical"
    ],
    
    "FRC REFEREE EXPERIENCE": [
        "frc referee", "referee experience", "prior years of first robotics competition referee",
        "referee", "refereeing"
    ],
    
    "FRC JUDGE EXPERIENCE": [
        "judge", "frc judge", "judge at frc event", "judging experience",
        "years as a judge"
    ],
    
    "ROBOT BUILD EXPERIENCE": [
        "robot build experience", "team robot build experience", "first robot build experience",
        "robot build", "build experience", "current season experience",
        "current season robo build experience"
    ],
    
    "MACHINE SHOP EXPERIENCE": [
        "machine tools", "variety of machine tools", "experience machinist",
        "experienced machinist", "welder experience", "significant machine shop experience",
        "machinist/welder experience"
    ],
    
    "FIRST SAFETY KNOWLEDGE": [
        "first safety principles", "safety principles", "knowledge of first safety",
        "thorough knowledge of first safety"
    ],
    
    "MANAGEMENT/SUPERVISION EXPERIENCE": [
        "supervise", "manage", "evaluate volunteers", "volunteer management",
        "event management", "able to supervise", "supervision experience"
    ],
    
    "GAME RULES KNOWLEDGE": [
        "game rules", "event rules", "safety rules", "game & event rules",
        "game and safety rules", "basic game knowledge", "match process knowledge",
        "basic knowledge of match process", "basic game and match process knowledge"
    ],
    
    "TEAM EXPERIENCE": [
        "team mentors", "team experience", "team match participation",
        "alumni", "team mentor experience"
    ],
    
    "PUBLIC SPEAKING/PRESENTATION EXPERIENCE": [
        "public speaking", "emcee", "first emcee", "prior first emcee",
        "tv experience", "radio experience", "acting experience",
        "tv/radio/acting experience"
    ],
    
    "FACILITY/EVENT KNOWLEDGE": [
        "facility layout", "event layout", "facility and event layout",
        "general knowledge of facility", "general knowledge of first",
        "first robotics competition knowledge", "can learn on site"
    ],
    
    "PIT VOLUNTEER EXPERIENCE": [
        "pit volunteer", "first pit volunteer", "years as first pit volunteer",
        "pit volunteer preferred"
    ]
}

REQ_SKILLS_KEYWORDS = {
    "pv": [
        "computer skills", "basic computer skills", "email", "websites", 
        "spreadsheets", "word", "excel", "online forms", "competent computer skills"
    ],
    
    "PROFICIENT USE OF OFFICE MATERIALS": [
        "word", "excel", "printers", "copiers", "office software", 
        "office technology", "spreadsheets", "proficient use of office software"
    ],
    
    "PROGRAMMING PROFICIENCY": [
        "programming", "c++", "java", "python", "labview", "programming proficiency",
        "computer proficiency", "proficient use of", "proficiency in"
    ],
    
    "PHOTO/VIDEO PROCESSING SOFTWARE SKILLS": [
        "photo processing", "video processing", "photo processing software", 
        "shooting indoor", "low light", "fast-paced environment", "photography",
        "video editing", "image processing"
    ],
    
    "MECHANICAL/TECHNICAL SKILLS": [
        "mechanical", "technical", "robot inspection", "tools", "mechanical skills",
        "technical skills", "mechanical/technical", "basic mechanical", 
        "technical experience", "mechanical aptitude", "electrical aptitude",
        "game rules", "robot control", "diagnostics"
    ],
    
    "ADVANCED MACHINE SHOP SKILLS": [
        "welding", "milling", "lathes", "machinist", "welder", "machine shop",
        "vertical milling machine", "engine lathes", "torches", "drill press",
        "saws", "tig welder", "advanced machine shop", "mechanical/technical skills"
    ],
    
    "CONTROL SYSTEMS & DIAGNOSTICS": [
        "control systems", "diagnostics", "fms", "electronics", "field management system",
        "field electronics", "diagnostic tools", "robot control system", 
        "control systems & diagnostics", "electrical", "electronic systems"
    ],
}

REQ_EXPERIENCE_KEYWORDS = {
    "FRC CONTROL SYSTEM EXPERIENCE": [
        "frc control system", "hands-on frc control system", "control system experience",
        "diagnostic tools", "first robotics competition control system"
    ],
    
    "FIELD MANAGEMENT SYSTEM EXPERIENCE": [
        "field management system", "fms", "game field", "field electronics",
        "field mechanical", "field electrical"
    ],
    
    "FRC REFEREE EXPERIENCE": [
        "frc referee", "referee experience", "prior years of first robotics competition referee",
        "referee", "refereeing"
    ],
    
    "FRC JUDGE EXPERIENCE": [
        "judge", "frc judge", "judge at frc event", "judging experience",
        "years as a judge"
    ],
    
    "ROBOT BUILD EXPERIENCE": [
        "robot build experience", "team robot build experience", "first robot build experience",
        "robot build", "build experience", "current season experience"
    ],
    
    "MACHINE SHOP EXPERIENCE": [
        "machine tools", "variety of machine tools", "experience machinist",
        "experienced machinist", "welder experience", "significant machine shop experience",
        "machinist/welder experience"
    ],
    
    "FIRST SAFETY KNOWLEDGE": [
        "first safety principles", "safety principles", "knowledge of first safety",
        "thorough knowledge of first safety"
    ],
    
    "MANAGEMENT/SUPERVISION EXPERIENCE": [
        "supervise", "manage", "evaluate volunteers", "volunteer management",
        "event management", "able to supervise", "supervision experience"
    ],
    
    "GAME RULES KNOWLEDGE": [
        "game rules", "event rules", "safety rules", "game & event rules",
        "game and safety rules"
    ]
}

class RegexSkillCategorizer:
    """
    A text analysis tool that categorizes skills and experience using keyword matching.
    
    This class uses regular expressions to identify and count skill-related keywords
    in text input, allowing for automated categorization of user responses, resumes,
    or other text containing skill descriptions. Uses case-insensitive whole-word matching.
    
    Usage:
        # Initialize with keyword dictionary
        categorizer = RegexSkillCategorizer(REQ_SKILLS_KEYWORDS)
        
        # Analyze text
        text = "I have programming experience with Python and Java"
        scores = categorizer.categorize_skills(text)
        top_category = categorizer.get_top_category(scores)
        
        print(f"Top skill area: {top_category}")
        print(f"All scores: {scores}")
    """
    
    def __init__(self, keywords: dict):
        """
        Initialize the RegexSkillCategorizer with keyword categories.

        Compiles regular expression patterns from the provided keyword dictionary
        for efficient text matching. Each category's keywords are combined into
        a single regex pattern that matches whole words only.

        Args:
            - keywords (dict): Dictionary mapping category names (str) to 
                           keyword lists (list[str]). Each category's keywords are 
                           converted into compiled regex patterns for matching.
                           
        Usage:
            # Initialize with predefined keywords
            categorizer = RegexSkillCategorizer(REQ_SKILLS_KEYWORDS)
            
            # Initialize with custom keywords
            custom_keywords = {
                "LEADERSHIP": ["manage", "lead", "supervise"],
                "TECHNICAL": ["programming", "coding", "software"]
            }
            categorizer = RegexSkillCategorizer(custom_keywords)
        """
        self.category_patterns = {}

        for category, keyword in keywords.items():
            escaped_keywords = [re.escape(kw) for kw in keyword if kw]
            pattern = r'\b(' + '|'.join(escaped_keywords) + r')\b'
            self.category_patterns[category] = re.compile(pattern, re.IGNORECASE)

    def categorize_skills(self, raw_str: str) -> dict:
        """
        Count keyword matches for each skill category in the given text.

        Searches the input text for keywords from all categories and returns
        a count of matches per category. Uses case-insensitive whole-word matching
        to avoid false positives from partial word matches.

        Args:
            - raw_str (str): Input text to analyze for potential skill-related 
                          keywords. Can be user responses, resume text, etc.

        Returns:
            - dict: Dictionary mapping category names (str) to the number of 
                  keyword matches (int) found in the input text.
                  
        Usage:
            categorizer = RegexSkillCategorizer(REQ_SKILLS_KEYWORDS)
            
            user_text = "I have Python programming and basic computer skills"
            results = categorizer.categorize_skills(user_text)
            
            # Example output:
            # {
            #     "PROGRAMMING PROFICIENCY": 2,  # "programming", "python"
            #     "pv": 1,  # "computer skills"
            #     "MECHANICAL/TECHNICAL SKILLS": 0,
            #     ...
            # }
            
            programming_score = results.get("PROGRAMMING PROFICIENCY", 0)
        """
        if not raw_str:
            return {}
        
        category_scores = {}
        for category, pattern in self.category_patterns.items():
            matches = pattern.findall(raw_str)
            category_scores[category] = len(matches)

        return category_scores

    def get_top_category(self, category_skills: dict) -> str:
        """
        Identify the category with the highest match score.

        Finds the category that had the most keyword matches from the
        categorize_skills() output, indicating the strongest skill area.

        Args:
            - category_skills (dict): Dictionary mapping category names (str) to 
                                  keyword match counts (int), typically the output of 
                                  categorize_skills() method.

        Returns:
            - str: The category name with the highest score.
            - int: Returns -1 if the input dictionary is empty.
        
        Raises:
            - TypeError: If category_skills is not a dictionary.
            
        Usage:
            categorizer = RegexSkillCategorizer(REQ_SKILLS_KEYWORDS)
            
            text = "Extensive programming experience with C++ and Python"
            scores = categorizer.categorize_skills(text)
            top_skill = categorizer.get_top_category(scores)
            
            if top_skill != -1:
                print(f"Primary skill area: {top_skill}")
                score = scores[top_skill]
                print(f"Match count: {score}")
            else:
                print("No skills identified in text")
        """
        if not isinstance(category_skills, dict):
            raise TypeError(
                f"Invalid type for skill categorizing input. "
                f"Expected a dict but got {type(category_skills)}"
            )

        if not category_skills:
            return -1

        max_score = max(category_skills, key=category_skills.get)
        return max_score