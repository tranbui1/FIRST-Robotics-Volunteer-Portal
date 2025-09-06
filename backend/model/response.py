from enum import Enum

class Response:
    def __init__(self, response: str) -> None:
        self.response = response
        self.parse_response()

    def parse_response(self):
        raise NotImplementedError("Subclasses must implement parse_response() \
                themselves.")

class PreferenceResponse(Response):
    """
    Parses user response into yes, no, or no preference booleans.
    """
    def __init__(self, response: str):
        super().__init__(response.upper())

    def parse_response(self):
        """
        Parses user response into three booleans indicating truthy 
        yes, no, or no preference. 

        Returns:
            - None. Initializes class attributes to be retrieved.
        """
        # Initialize all attributes to 0
        self.yes = 0
        self.no = 0
        self.no_pref = 0
        
        if self.response == "YES":
            self.yes = 1
        elif self.response == "NO":
            self.no = 1
        elif self.response in ["NO_PREF", "NO PREFERENCE", "NO PREF"]:
            self.no_pref = 1
        else:
            raise ValueError(f"Invalid preference response input value. The \
                value is {self.response} when it should be 'YES', 'NO', \
                'NO PREFERENCE'")

class MultiChoiceResponse(Response):
    """
    Parses a response with multiple categorical choices, such as
    'BTS', 'FRONT', or 'NO_PREF'. Supports arbitrary labeled options.

    Attributes:
        - self.choice (str): The parsed and standardized user choice.
    """
    def __init__(self, response: str, valid_options: set[str]) -> None:
        self.response = response
        self.valid_options = {opt.upper() for opt in valid_options}
        self.choice = self.parse_response()

    def parse_response(self) -> str:
        response_upper = self.response.upper()

        if response_upper in self.valid_options:
            return response_upper
        else:
            raise ValueError(
                f"Invalid option '{self.response}'. "
                f"Expected one of: {', '.join(self.valid_options)}"
            )

class RegionalDays(Enum):
    """
    Enum for regional competition days (Thursday-Sunday).
    """
    THURSDAY = 0
    FRIDAY = 1  
    SATURDAY = 2
    SUNDAY = 3
    
    def __str__(self):
        return self.name.title()

class DistrictDays(Enum):
    """
    Enum for district competition days (Friday-Sunday).
    """
    FRIDAY = 0
    SATURDAY = 1
    SUNDAY = 2
    
    def __str__(self):
        return self.name.title()

class TimeCommitmentResponse(Response):
    ELIMINATE_ROLE = -5
    
    def __init__(self, response: str, commitment_type: str):
        self.commitment_type = commitment_type
        if self.commitment_type.lower() not in ["district", "regionals"]:
            raise ValueError("commitment_type must be 'regionals' or 'district'")

        super().__init__(response)

    def parse_response(self):
        """
        Parses user response into available days.
        
        Expected formats:
        - Numeric: "0 1 2 3" (space-separated day numbers)
        - Day names: "thursday friday saturday" (space-separated names, not case sensitive)
            - Partial day names also accepted: "thurs fri sat"
        - "NONE", "FALSE", or empty string for no availability
        
        Sets:
        - self.available_days: Set of day enums
        - self.has_availability: Boolean indicating if user has any days
        """
        day_class = RegionalDays if self.commitment_type == "regionals" else DistrictDays

        self.available_days = set()
        self.has_availability = False

        # No availability
        if isinstance(self.response, str): 
            if self.response.lower() in ["none", "false", ""]:
                return
        elif isinstance(self.response, bool):
            if self.response == False:
                return

        days_token = self.response.upper().split()

        if len(days_token) <= 0:
            return

        for token in days_token:
            try:
                # Numeric case
                if token.isdigit():
                    day_num = int(token)

                    if day_num < len(day_class):
                        self.available_days.add(day_class(day_num))
                    else:
                        raise ValueError(f"Day number {day_num} is out of range for {self.commitment_type}")

                else:
                    # Day names case
                    matching_day = None
                    
                    for day in day_class:
                        # Either match full or partial
                        if day.name == token or day.name.startswith(token[:3]):
                            matching_day = day
                            break
                        
                    if matching_day:
                        self.available_days.add(matching_day)
                    else:
                        raise ValueError(f"Unrecognized day: {token}")
                
            except (ValueError, KeyError) as e:
                raise ValueError(f"Invalid day token '{token}' in response '{self.response}': {str(e)}")
        
        self.has_availability = len(self.available_days) > 0
    
    def calculate_match_score(self, required_days: str) -> int:
        """
        Calculate compatibility score with role requirements.
        
        Returns:
            int: Score based on day overlap:
                 ELIMINATE_ROLE = completely remove role
                 0 = user has no availability or parse error  
                 1 = limited coverage (< 50%)
                 3 = good coverage (≥ 50%) or role is dependent
                 5 = full coverage (100%)
        """
        if required_days == "Dependent":
            return 3
            
        if not self.has_availability:
            return 0
            
        try:
            required_response = TimeCommitmentResponse(required_days, self.commitment_type)
            
            # Role doesn't exist for this regionals/district competition
            if not required_response.has_availability:
                return self.ELIMINATE_ROLE
                
            overlap = self.available_days.intersection(required_response.available_days)
            if not overlap:
                return self.ELIMINATE_ROLE
                
            # Score based on coverage
            coverage_ratio = len(overlap) / len(required_response.available_days)
            if coverage_ratio >= 1.0:
                return 5  # Can cover all required days
            elif coverage_ratio >= 0.5:
                return 3  # Can cover most required days
            else:
                return 1  # Limited coverage
                
        except ValueError:
            return 0




    
