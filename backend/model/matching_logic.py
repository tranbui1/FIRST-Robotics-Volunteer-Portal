from .response import *
from .keywords import *
import pandas as pd
import re

# Hard coded data path containing each role's requirements
data = ""

class Matches:
    def __init__(self, student_status, data_path=None):
        """
        Initialize the role matching and scoring system.

        Args:
            student_status (bool): Whether the user is a student.
            data_path (str, optional): Path to the CSV file containing role data.
            
        Usage:
            matcher = Matches(student_status=True, data_path="roles.csv")
        """
        self.df = pd.read_csv(data_path)
        self.all_role_names = self.df["role_name"].tolist()
        self.dataset = self._create_dataset(convert_booleans=True)
        self.scoreboard = {role["role_name"] : 0 for role in self.dataset}
        self.eliminated_roles = set()
        self.student_status = student_status

    def _create_dataset(self, convert_booleans: bool = False) -> list[dict]:
        """
        Convert pandas DataFrame to list of dictionaries with optional boolean conversion.

        Args: 
            convert_booleans (bool): Convert string "true"/"false" to Python booleans.

        Returns: 
            list[dict]: Dataset as list of role dictionaries.
        """
        df_copy = self.df.copy()

        if convert_booleans:
            target = {"true", "false"}
            df_copy = df_copy.map(
                lambda word: word.lower() if isinstance(word, str) \
                and word.lower() in target else word
            )
            df_copy.replace({"true": True, "false": False}, inplace=True)

        return df_copy.to_dict(orient="records")

    def filter_by_attribute(self, attribute: str) -> list[dict]:
        """
        Filter dataset to include only roles where the specified attribute is truthy.

        Args:
            attribute (str): The attribute to filter on.

        Returns:
            list[dict]: Filtered dataset.
            
        Usage:
            leadership_roles = matcher.filter_by_attribute("leadership_pref")

        Raises:
            ValueError: If attribute doesn't exist in dataset.
        """
        if attribute not in self.dataset[0].keys():
            raise ValueError(f"{attribute} is not an attribute in the dataset.")

        return [role for role in self.dataset if role.get(attribute)]

    def eliminate_role(self, role_name: str) -> None:
        """
        Mark a role as eliminated while preserving its score for fallback.
        
        Args:
            role_name (str): Name of the role to eliminate.
            
        Usage:
            matcher.eliminate_role("Software Engineer")
        """
        self.eliminated_roles.add(role_name)

    def get_active_roles(self) -> list[dict]:
        """
        Get roles that haven't been eliminated.
        
        Returns:
            list[dict]: Non-eliminated roles.
        """
        return [role for role in self.dataset if role["role_name"] not in self.eliminated_roles]

    def _extract_number(self, text: str) -> int | float:
        """
        Extract first numerical value from text (supports integers, decimals, fractions).

        Args:
            text (str): String to extract number from.

        Returns:
            int | float: Extracted value or -1 if extraction fails.
        """
        if not text or pd.isna(text):
            return -1
            
        text = str(text).strip()

        if not any(digit.isnumeric() for digit in text):
            return -1  

        # Extract fractions first (most specific)
        fraction_match = re.search(r"(-?\d+)\s*/\s*(\d+)", text)
        if fraction_match:
            numerator, denominator = fraction_match.groups()
            if int(denominator) == 0:
                return -1  
            return float(numerator) / float(denominator)

        # Extract decimals
        decimal_match = re.search(r"-?\d+\.\d+", text)
        if decimal_match:
            return float(decimal_match.group())
        
        # Extract integers
        int_match = re.search(r"-?\d+", text) 
        if int_match:
            return int(int_match.group())

        return -1

    def score_age_match(self, dataset: list[dict], response: str, eliminate_unqualified: bool = False) -> None:
        """
        Score roles based on age requirements and user's age range.

        Args:
            dataset (list[dict]): Role data.
            response (str): User's age range ("13 to 15 years old", "16 to 17 years old", "18 and older").
            eliminate_unqualified (bool): Whether to eliminate age-ineligible roles.
            
        Usage:
            matcher.score_age_match(matcher.dataset, "18 and older", eliminate_unqualified=True)
        """
        if not isinstance(self.student_status, bool):
            raise TypeError("Student status must be boolean.")

        age_ranges = {
            "13 to 15 years old" : 15,
            "16 to 17 years old" : 17,
            "18 and older" : 100
        }
        
        user_max_age = age_ranges[response.lower()]

        for role in dataset:
            role_name = role["role_name"]
            age_min_raw = role["age_min"]
            age_pref_raw = role["age_preference"]

            # Parse age minimum
            if str(age_min_raw).isnumeric():
                age_min = int(age_min_raw)
            elif age_min_raw == "Students":
                age_min = "Students"
            else:
                age_min = self._extract_number(age_min_raw)
            
            # Parse age preference
            age_pref = False
            if age_pref_raw:
                if str(age_pref_raw).isnumeric():
                    age_pref = int(age_pref_raw)
                else:
                    age_pref = self._extract_number(age_pref_raw)

            # Check qualification and score
            age_qualified = False
            
            if isinstance(age_min, int) and age_min <= user_max_age:
                age_qualified = True
                score = 5 if not age_pref or age_pref <= user_max_age else 3
                self.scoreboard[role_name] += score
            
            # Student status override
            if self.student_status and age_min == "Students":
                age_qualified = True
                self.scoreboard[role_name] += 5
            
            # Handle elimination - simplified without age exception
            if eliminate_unqualified and not age_qualified:
                self.eliminate_role(role_name)

    def _score_physical_requirement(self, dataset: list[dict], response: PreferenceResponse, 
                                   requirement_key: str, movement_terms: list[str] = None, 
                                   eliminate_unqualified: bool = False) -> None:
        """
        Generic method to score physical requirements.
        
        Args:
            dataset (list[dict]): Role data.
            response (PreferenceResponse): User's preference/ability.
            requirement_key (str): Key to check in role data.
            movement_terms (list[str]): Terms to search for in physical requirements.
            eliminate_unqualified (bool): Whether to eliminate mismatched roles.
        """
        if response.no_pref:
            return
            
        for role in dataset:
            role_name = role["role_name"]
            
            if movement_terms:
                # Check if physical_req contains any movement terms
                physical_req = str(role.get("physical_req", "")).lower()
                has_requirement = any(term in physical_req for term in movement_terms)
            else:
                # Direct boolean check
                has_requirement = bool(role.get(requirement_key, False))
            
            if response.yes and has_requirement:
                self.scoreboard[role_name] += 3 if movement_terms else 5
            elif response.no and not has_requirement:
                self.scoreboard[role_name] += 3 if movement_terms else 5
            elif eliminate_unqualified:
                if (response.yes and not has_requirement) or (response.no and has_requirement):
                    self.eliminate_role(role_name)

    def score_physical_activity(self, dataset: list[dict], response: PreferenceResponse, 
                               eliminate_unqualified: bool = False) -> None:
        """
        Score roles based on physical activity requirements.
        
        Usage:
            matcher.score_physical_activity(matcher.dataset, PreferenceResponse("yes"))
        """
        self._score_physical_requirement(dataset, response, "physical_req", 
                                       eliminate_unqualified=eliminate_unqualified)

    def score_standing_ability(self, dataset: list[dict], response: PreferenceResponse, 
                              eliminate_unqualified: bool = False) -> None:
        """
        Score roles based on standing/walking requirements.
        
        Usage:
            matcher.score_standing_ability(matcher.dataset, PreferenceResponse("no"), eliminate_unqualified=True)
        """
        self._score_physical_requirement(dataset, response, None, 
                                       movement_terms=["stand", "walk"],
                                       eliminate_unqualified=eliminate_unqualified)

    def score_mobility_needs(self, dataset: list[dict], response: PreferenceResponse, 
                            eliminate_unqualified: bool = False) -> None:
        """
        Score roles based on general mobility requirements.
        
        Usage:
            matcher.score_mobility_needs(matcher.dataset, PreferenceResponse("yes"))
        """
        movement_terms = ["move", "walk", "run", "carry", "lift", "transport", "stand"]
        self._score_physical_requirement(dataset, response, None, 
                                       movement_terms=movement_terms,
                                       eliminate_unqualified=eliminate_unqualified)
    
    def score_time_commitment(self, dataset: list[dict], user_time_commitment: str, 
                             commitment_type: str, eliminate_unqualified: bool = False) -> None:
        """
        Score roles based on time commitment compatibility.

        Args:
            dataset (list[dict]): Role data.
            user_time_commitment (str): User's available time commitment.
            commitment_type (str): "district" or "regional".
            eliminate_unqualified (bool): Whether to eliminate incompatible roles.
            
        Usage:
            matcher.score_time_commitment(matcher.dataset, "Friday Saturday", "district")
        """
        if not isinstance(user_time_commitment, str):
            raise TypeError("Time commitment must be a string.")
        
        column_name = f"{commitment_type}_day_commitment"
        user_commitment = TimeCommitmentResponse(user_time_commitment, commitment_type)
        
        for role in dataset:
            role_name = role["role_name"]
            
            if column_name not in role:
                continue
                
            role_commitment = role[column_name]
            
            # Handle unavailable roles
            if role_commitment == "FALSE":
                self.eliminate_role(role_name)
                continue
            
            # Skip invalid data
            if role_commitment in ["?", "", None] or pd.isna(role_commitment):
                continue
                
            # Clean up commitment string
            if isinstance(role_commitment, str):
                role_commitment = role_commitment.replace("?", "").strip()
                if not role_commitment:
                    continue
                    
            score = user_commitment.calculate_match_score(role_commitment)
            if eliminate_unqualified and score == TimeCommitmentResponse.ELIMINATE_ROLE:
                self.eliminate_role(role_name)
            else:
                self.scoreboard[role_name] += score

    def score_preference_match(self, dataset: list[dict], response: PreferenceResponse, 
                              attribute: str, eliminate_unqualified: bool = False) -> None:
        """
        Generic method to score boolean preference matches (leadership, etc).

        Args:
            dataset (list[dict]): Role data.
            response (PreferenceResponse): User's preference.
            attribute (str): Boolean attribute to check in role data.
            eliminate_unqualified (bool): Whether to eliminate mismatched roles.
            
        Usage:
            matcher.score_preference_match(matcher.dataset, PreferenceResponse("yes"), "leadership_pref")
        """
        if response.no_pref:
            return

        for role in dataset:
            role_name = role["role_name"]
            role_has_attribute = bool(role.get(attribute, False))

            if response.yes and role_has_attribute:
                self.scoreboard[role_name] += 5
            elif response.no and not role_has_attribute:
                self.scoreboard[role_name] += 5
            elif eliminate_unqualified:
                if (response.yes and not role_has_attribute) or (response.no and role_has_attribute):
                    self.eliminate_role(role_name)

    def score_working_preference(self, dataset: list[dict], pref: MultiChoiceResponse,
                                eliminate_unqualified: bool = False) -> None:
        """
        Score roles based on working environment preference (BTS vs FRONT).
        
        Usage:
            matcher.score_working_preference(matcher.dataset, MultiChoiceResponse("BTS", {"BTS", "FRONT"}))
        """
        valid_choices = ["NO_PREF", "NO PREFERENCE", "NO PREF", "BTS", "FRONT"]
        if pref.choice not in valid_choices:
            raise ValueError(f"Invalid choice: {pref.choice}. Expected one of {valid_choices}")

        if pref.choice in ["NO_PREF", "NO PREFERENCE", "NO PREF"]:
            return

        for role in dataset:
            role_name = role["role_name"]
            role_pref = role["work_pref"]

            if pref.choice == role_pref:
                self.scoreboard[role_name] += 5
            elif eliminate_unqualified and pref.choice != role_pref:
                self.eliminate_role(role_name)

    def _parse_experience_level(self, raw_value: str | bool, level_map: dict) -> str:
        """
        Generic parser for experience/knowledge levels.
        
        Args:
            raw_value (str | bool): Raw value to parse.
            level_map (dict): Mapping of keywords to levels.
            
        Returns:
            str: Parsed level or "UNKNOWN".
        """
        if not raw_value:
            return "UNKNOWN"

        if isinstance(raw_value, bool):
            return level_map.get("bool_true" if raw_value else "bool_false", "UNKNOWN")

        if isinstance(raw_value, str):
            text = raw_value.strip().upper()
            
            # Direct matches
            for key, value in level_map.items():
                if key in text:
                    return value
            
            # Keyword searches
            for keyword_list, level in level_map.get("keyword_search", {}).items():
                if any(keyword in raw_value.lower() for keyword in keyword_list):
                    return level

        return "UNKNOWN"

    def _parse_prior_experience(self, raw_value: str | bool) -> str:
        """Parse prior FIRST experience requirements."""
        level_map = {
            "FALSE": "FALSE",
            "TRUE": "REQUIRED", 
            "PREFERRED": "PREFERRED",
            "bool_true": "REQUIRED",
            "bool_false": "FALSE",
            "keyword_search": {
                ("must", "required", "years", "minimum", "experience required"): "REQUIRED",
                ("recommended", "helpful", "knowledge of", "general knowledge"): "PREFERRED"
            }
        }
        return self._parse_experience_level(raw_value, level_map)

    def _parse_game_knowledge(self, raw_value: str | bool) -> str:
        """Parse game knowledge requirements."""
        level_map = {
            "FALSE": "NONE",
            "TRUE": "LIMITED",
            "bool_true": "LIMITED", 
            "bool_false": "NONE",
            "keyword_search": {
                ("thorough", "advanced", "in-depth"): "THOROUGH",
                ("average", "familiar", "general knowledge"): "AVERAGE",
                ("can learn", "basic", "some knowledge"): "LIMITED"
            }
        }
        return self._parse_experience_level(raw_value, level_map)

    def score_prior_experience(self, dataset: list[dict], has_experience: bool) -> None:
        """
        Score roles based on user's prior FIRST experience.
        
        Usage:
            matcher.score_prior_experience(matcher.dataset, has_experience=True)
        """
        if not isinstance(has_experience, bool):
            raise TypeError("Experience must be boolean.")

        for role in dataset:
            role_name = role["role_name"]
            required_exp = self._parse_prior_experience(role["prior_first_exp"])

            if has_experience:
                score_map = {"REQUIRED": 8, "PREFERRED": 5}
                self.scoreboard[role_name] += score_map.get(required_exp, 3)
            else:  # No experience
                if required_exp == "FALSE":
                    self.scoreboard[role_name] += 5
                elif required_exp == "PREFERRED":
                    self.scoreboard[role_name] -= 2

    def score_game_knowledge(self, dataset: list[dict], user_level: str, 
                            eliminate_unqualified: bool = False) -> None:
        """
        Score roles based on game knowledge level.
        
        Args:
            user_level (str): One of "NONE", "LIMITED", "AVERAGE", "THOROUGH".
            
        Usage:
            matcher.score_game_knowledge(matcher.dataset, "AVERAGE", eliminate_unqualified=True)
        """
        knowledge_levels = ["NONE", "LIMITED", "AVERAGE", "THOROUGH"]
        user_level = user_level.upper()
        
        try:
            user_index = knowledge_levels.index(user_level)
        except ValueError:
            raise ValueError(f"Invalid level: {user_level}. Must be one of {knowledge_levels}")

        for role in dataset:
            role_name = role["role_name"]
            required_level = self._parse_game_knowledge(role["basic_game_knowledge"])
            
            if required_level == "UNKNOWN":
                continue
                
            try:
                required_index = knowledge_levels.index(required_level)
            except ValueError:
                continue
            
            if user_index >= required_index:
                score = 8 if user_level == required_level else 5
                self.scoreboard[role_name] += score
            elif eliminate_unqualified:
                self.eliminate_role(role_name)

    def _get_top_skill_category(self, skill_data: str | bool, keywords: dict) -> str | None:
        """Extract top skill category from role data using keyword matching."""
        if isinstance(skill_data, bool):
            if not skill_data:
                return "NONE"
            else:
                raise ValueError("Boolean True found where specific skills expected.")
    
        categorizer = RegexSkillCategorizer(keywords)
        role_skills = categorizer.categorize_skills(skill_data)
        return categorizer.get_top_category(role_skills)

    def score_skill_requirements(self, dataset: list[dict], req_field: str, keywords: dict,
                                user_skills: set[str], score_weight: int, 
                                eliminate_unqualified: bool = False) -> None:
        """
        Generic method to score skill/experience requirements.

        Args:
            dataset (list[dict]): Role data.
            req_field (str): Column name to assess ("required_skills", "required_experience").
            keywords (dict): Keyword mapping for skill categorization.
            user_skills (set[str]): User's skills/experience.
            score_weight (int): Points to award for matches.
            eliminate_unqualified (bool): Whether to eliminate unmatched roles.
            
        Usage:
            matcher.score_skill_requirements(
                matcher.dataset, "required_skills", SKILL_KEYWORDS, 
                {"programming", "teamwork"}, score_weight=8
            )
        """
        if not isinstance(user_skills, set):
            raise TypeError(f"Expected set, got {type(user_skills)}")

        user_skills.add("NONE")  # Always allow "no requirements"

        for role in dataset:
            role_name = role["role_name"]
            req_skill = role[req_field]

            top_skill = self._get_top_skill_category(req_skill, keywords)
            if not top_skill:
                continue

            if top_skill in user_skills:
                self.scoreboard[role_name] += score_weight
            elif eliminate_unqualified:
                self.eliminate_role(role_name)

    def score_categorical_match(self, dataset: list[dict], column_name: str,
                               user_response: str | list[str], score_boost: int = 5,
                               eliminate_unqualified: bool = False) -> None:
        """
        Score any categorical column match.
        
        Args:
            column_name (str): Column name in dataset.
            user_response (str | list[str]): User's response(s).
            score_boost (int): Points for matches.
            
        Usage:
            matcher.score_categorical_match(matcher.dataset, "work_environment", "remote")
        """
        if isinstance(user_response, str):
            user_responses = {user_response.lower().strip()}
        elif isinstance(user_response, list):
            user_responses = {resp.lower().strip() for resp in user_response}
        else:
            raise TypeError(f"Expected str or list[str], got {type(user_response)}")
        
        for role in dataset:
            role_name = role["role_name"]
            
            if column_name not in role or not role[column_name] or pd.isna(role[column_name]):
                continue
                
            role_value = str(role[column_name]).lower().strip()
            
            if role_value in user_responses:
                self.scoreboard[role_name] += score_boost
            elif eliminate_unqualified:
                self.eliminate_role(role_name)

    # Assessment orchestration methods
    def process_assessment(self, data: dict, eliminate_unqualified: bool = False) -> None:
        """
        Process a single assessment based on question_id.

        Args:
            data (dict): Contains question_id and answer data.
            eliminate_unqualified (bool): Whether to eliminate unqualified roles.
            
        Usage:
            matcher.process_assessment({"question_id": 0, "answer": "18 and older"})
        """
        assessment_map = {
            0: self._assess_age,
            1: self._assess_physical_activity,
            2: self._assess_standing,
            3: self._assess_mobility,
            4: self._assess_time_commitment,
            5: self._assess_work_preference,
            6: self._assess_leadership,
            7: self._assess_prior_experience,
            8: self._assess_game_knowledge,
            9: self._assess_required_skills,
            10: self._assess_experience_requirements,
        }
        
        question_id = data["question_id"]
        if question_id not in assessment_map:
            raise ValueError(f"Invalid question_id: {question_id}")
        
        assessment_method = assessment_map[question_id]
        params = self._get_assessment_params(question_id, data, eliminate_unqualified)
        assessment_method(**params)

    def process_assessment(self, data: dict, eliminate_unqualified: bool = False) -> None:
        """
        Process a single assessment based on question_id.

        Args:
            data (dict): Contains question_id and answer data.
            eliminate_unqualified (bool): Whether to eliminate unqualified roles.
            
        Usage:
            matcher.process_assessment({"question_id": 0, "answer": "18 and older"})
        """
        question_id = data["question_id"]
        answer = data["answer"]
        
        # Route to specific assessment function
        if question_id == 0:
            self._assess_age(answer, eliminate_unqualified)
        elif question_id == 1:
            self._assess_physical_activity(answer, eliminate_unqualified)
        elif question_id == 2:
            self._assess_standing(answer, eliminate_unqualified)
        elif question_id == 3:
            self._assess_mobility(answer, eliminate_unqualified)
        elif question_id == 4:
            commitment_type = data.get("commitment_type", "district")
            self._assess_time_commitment(answer, commitment_type, eliminate_unqualified)
        elif question_id == 5:
            self._assess_work_preference(answer, eliminate_unqualified)
        elif question_id == 6:
            self._assess_leadership(answer, eliminate_unqualified)
        elif question_id == 7:
            self._assess_prior_experience(answer, eliminate_unqualified)
        elif question_id == 8:
            self._assess_game_knowledge(answer, eliminate_unqualified)
        elif question_id == 9:
            self._assess_required_skills(answer, eliminate_unqualified)
        elif question_id == 10:
            self._assess_experience_requirements(answer, eliminate_unqualified)
        else:
            raise ValueError(f"Invalid question_id: {question_id}")

    # Individual assessment functions with proper parameter handling

    def _assess_age(self, answer: str, eliminate_unqualified: bool):
        """Age assessment - expects direct string answer"""
        self.score_age_match(
            dataset=self.dataset,
            response=answer,
            eliminate_unqualified=eliminate_unqualified
        )

    def _assess_physical_activity(self, answer: str, eliminate_unqualified: bool):
        """Physical activity assessment - expects YES/NO/NO PREFERENCE"""
        response = PreferenceResponse(answer)
        self.score_physical_activity(
            dataset=self.dataset,
            response=response,
            eliminate_unqualified=eliminate_unqualified
        )

    def _assess_standing(self, answer: str, eliminate_unqualified: bool):
        """Standing ability assessment - expects YES/NO/NO PREFERENCE"""
        response = PreferenceResponse(answer)
        self.score_standing_ability(
            dataset=self.dataset,
            response=response,
            eliminate_unqualified=eliminate_unqualified
        )

    def _assess_mobility(self, answer: str, eliminate_unqualified: bool):
        """Mobility needs assessment - expects YES/NO/NO PREFERENCE"""
        response = PreferenceResponse(answer)
        self.score_mobility_needs(
            dataset=self.dataset,
            response=response,
            eliminate_unqualified=eliminate_unqualified
        )

    def _assess_time_commitment(self, answer: str, commitment_type: str, eliminate_unqualified: bool):
        """Time commitment assessment - expects time commitment string"""
        self.score_time_commitment(
            dataset=self.dataset,
            user_time_commitment=answer,
            commitment_type=commitment_type,
            eliminate_unqualified=eliminate_unqualified
        )

    def _assess_work_preference(self, answer: str, eliminate_unqualified: bool):
        """Work preference assessment - expects BTS/FRONT/NO PREFERENCE"""
        pref = MultiChoiceResponse(answer, {"NO PREFERENCE", "BTS", "FRONT"})
        self.score_working_preference(
            dataset=self.dataset,
            pref=pref,
            eliminate_unqualified=eliminate_unqualified
        )

    def _assess_leadership(self, answer: str, eliminate_unqualified: bool):
        """Leadership assessment - expects YES/NO/NO PREFERENCE"""
        response = PreferenceResponse(answer)
        self.score_preference_match(
            dataset=self.dataset,
            response=response,
            attribute="leadership_pref",
            eliminate_unqualified=eliminate_unqualified
        )

    def _assess_prior_experience(self, answer: str, eliminate_unqualified: bool):
        """Prior experience assessment - expects YES/NO"""
        has_experience = self._convert_to_bool(answer)
        # Note: score_prior_experience doesn't support eliminate_unqualified
        self.score_prior_experience(
            dataset=self.dataset,
            has_experience=has_experience
        )

    def _assess_game_knowledge(self, answer: str, eliminate_unqualified: bool):
        """Game knowledge assessment - expects NONE/LIMITED/AVERAGE/THOROUGH"""
        self.score_game_knowledge(
            dataset=self.dataset,
            user_level=answer,
            eliminate_unqualified=eliminate_unqualified
        )

    def _assess_required_skills(self, answer: str, eliminate_unqualified: bool):
        """Required skills assessment - expects skill category string"""
        self.score_skill_requirements(
            dataset=self.dataset,
            req_field="required_skills",
            keywords=REQ_SKILLS_KEYWORDS,
            user_skills={answer},
            score_weight=8,
            eliminate_unqualified=eliminate_unqualified
        )

    def _assess_experience_requirements(self, answer: str, eliminate_unqualified: bool):
        """Experience requirements assessment - expects experience category string"""
        # Note: This version doesn't use eliminate_unqualified
        self.score_skill_requirements(
            dataset=self.dataset,
            req_field="required_experience",
            keywords=REQ_EXPERIENCE_KEYWORDS,
            user_skills={answer},
            score_weight=3,
            eliminate_unqualified=False  # Force to False for experience requirements
        )

    def _convert_to_bool(self, value: str | bool) -> bool:
        """Convert string answer to boolean."""
        if isinstance(value, str):
            return value.upper() == 'YES'
        return value

    # Results methods
    def get_remaining_count(self) -> int:
        """Get number of non-eliminated roles."""
        return len(self.dataset) - len(self.eliminated_roles)

    def get_eliminated_list(self) -> list[str]:
        """Get list of eliminated role names."""
        return list(self.eliminated_roles)

    def get_top_matches(self, num: int = 3) -> dict:
        """
        Get top scoring roles with fallback to eliminated roles if needed.
        
        Args:
            num (int): Number of top roles to return.
            
        Returns:
            dict: Contains "Best fit roles" and "Next best roles".
            
        Usage:
            results = matcher.get_top_matches(5)
            print(results["Best fit roles"])
        """
        # Get active (non-eliminated) roles with scores
        active_roles = [
            (role["role_name"], self.scoreboard[role["role_name"]]) 
            for role in self.dataset 
            if role["role_name"] not in self.eliminated_roles
        ]
        
        active_roles.sort(key=lambda x: x[1], reverse=True)
        active_names = [role[0] for role in active_roles]
        
        result = {}
        
        if active_names:
            best_count = min(num, len(active_names))
            result["Best fit roles"] = ", ".join(active_names[:best_count])
            
            # If we need more roles, include eliminated ones
            if len(active_names) < num:
                all_sorted = sorted(self.scoreboard.items(), key=lambda x: x[1], reverse=True)
                next_best = [name for name, _ in all_sorted 
                            if name not in active_names[:best_count]][:num - best_count]
                result["Next best roles"] = ", ".join(next_best) if next_best else "None"
            else:
                result["Next best roles"] = "None"
        else:
            # All roles eliminated - show top scoring eliminated roles
            all_sorted = sorted(self.scoreboard.items(), key=lambda x: x[1], reverse=True)
            result["Best fit roles"] = ", ".join([name for name, _ in all_sorted[:num]])
            result["Next best roles"] = "None"

        return result
