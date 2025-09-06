import pandas as pd

class RoleLinks:
    """
    A manager class for loading and accessing role-related links from CSV data.
    
    This class loads role information from a CSV file and provides methods to
    retrieve different types of links (express, description, video) for specific roles.
    The CSV should have 'role_name' as the index column and link columns.
    
    Usage:
        # Initialize with CSV file path
        role_manager = RoleLinks('roles_data.csv')
        
        # Check if data loaded successfully
        if role_manager.is_loaded():
            # Get different types of links
            express_link = role_manager.get_express_link('Field Resetter')
            desc_link = role_manager.get_description_link('Field Resetter')
            video_link = role_manager.get_video_link('Field Resetter')
    
    CSV Format Expected:
        role_name,express_link,desc_link,video_link
        Field Resetter,https://...,https://...,https://...
        Field Supervisor,https://...,https://...,https://...
    """
    
    def __init__(self, data_path):
        """
        Initialize the RoleLinks manager with a CSV data source.
        
        Loads role data from the specified CSV file and sets up the internal
        data structure for fast role lookup by name.
        
        Args:
            - data_path (str): Path to the CSV file containing role data.
                           CSV must have 'role_name' column and link columns.
                           
        Usage:
            role_manager = RoleLinks('data/roles.csv')
            # or with relative path
            role_manager = RoleLinks('./roles_data.csv')
        """
        self.data_path = data_path
        self.data = self._load_data()
              
    def _load_data(self):
        """
        Load and process CSV data into a dictionary structure for fast lookup.
        
        Reads the CSV file, handles missing values, and converts the DataFrame
        to a dictionary with role names as keys for efficient access.
        
        Returns:
            - dict: Dictionary with role names as keys and role data as values.
                  Empty dict if file cannot be loaded.
                  
        Usage:
            # Called automatically during initialization
            data = manager._load_data()
            # data structure: {'Role Name': {'express_link': '...', 'desc_link': '...', ...}}
        """
        try:
            df = pd.read_csv(self.data_path)
            df = df.fillna("")  # Fill in missing values with empty str
            df.set_index("role_name", inplace=True)
            return df.to_dict(orient="index")
        except FileNotFoundError:
            print(f"Error: Could not find file at {self.data_path}")
            return {}
        except pd.errors.EmptyDataError:
            print("Error: CSV file is empty")
            return {}
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return {}

    def is_loaded(self):
        """
        Check if role data was successfully loaded from the CSV file.
        
        Verifies that the data dictionary is not empty, indicating successful
        file loading and processing.
        
        Returns:
            - bool: True if data loaded successfully, False if data is empty or failed to load
            
        Usage:
            role_manager = RoleLinks('roles.csv')
            if role_manager.is_loaded():
                print("Data ready for use")
            else:
                print("Failed to load role data")
        """
        return bool(self.data)

    def _get_role_field(self, role_name, field_name):
        """
        Generic method to retrieve any field value for a specified role.
        
        Provides a centralized way to access role data with proper error
        handling and validation. Used internally by specific getter methods.
        
        Args:
            - role_name (str): The name of the role to look up (must match CSV data exactly)
            - field_name (str): The field/column name to retrieve (e.g., 'express_link')
            
        Returns:
            - str: The field value if found, empty string if role or field not found
            
        Usage:
            # Used internally by public methods
            link = manager._get_role_field('Software Developer', 'express_link')
            description = manager._get_role_field('Manager', 'desc_link')
        """
        if not self.data:
            return ""
                  
        try:
            role = self.data.get(role_name)
            if not role:
                return ""
                                      
            return role.get(field_name, "")
        except Exception as e:
            print(f"Error fetching role {field_name}: {e}")
            return ""

    def get_express_link(self, role_name):
        """
        Retrieve the express link for a specific role.
        
        Gets the express link URL associated with the given role name.
        Express links typically provide quick access or summary information.
        
        Args:
            - role_name (str): The exact name of the role as it appears in the CSV
            
        Returns:
            - str: The express link URL, or empty string if not found
            
        Usage:
            express_url = role_manager.get_express_link('Software Developer')
            if express_url:
                print(f"Express link: {express_url}")
            else:
                print("No express link available for this role")
        """
        return self._get_role_field(role_name, "express_link")

    def get_description_link(self, role_name):
        """
        Retrieve the description link for a specific role.
        
        Gets the description link URL that provides detailed information
        about the role's responsibilities, requirements, and expectations.
        
        Args:
            - role_name (str): The exact name of the role as it appears in the CSV
            
        Returns:
            - str: The description link URL, or empty string if not found
            
        Usage:
            desc_url = role_manager.get_description_link('Project Manager')
            if desc_url:
                # Open or process the detailed description
                webbrowser.open(desc_url)
        """
        return self._get_role_field(role_name, "desc_link")

    def get_video_link(self, role_name):
        """
        Retrieve the video link for a specific role.
        
        Gets the video link URL that provides visual information about the role,
        such as training videos, role demonstrations, or explanatory content.
        
        Args:
            - role_name (str): The exact name of the role as it appears in the CSV
            
        Returns:
            - str: The video link URL, or empty string if not found
            
        Usage:
            video_url = role_manager.get_video_link('Team Lead')
            if video_url:
                print(f"Training video available: {video_url}")
            else:
                print("No video available for this role")
        """
        return self._get_role_field(role_name, "video_link")

    def get_all_links_for_role(self, role_name):
        """
        Get all available links for a specific role in a single call.
        
        Retrieves express, description, and video links for the specified role
        and returns them in a structured dictionary format.
        
        Args:
            - role_name (str): The exact name of the role as it appears in the CSV
            
        Returns:
            - dict: Dictionary containing all link types for the role.
                  Keys: 'express_link', 'desc_link', 'video_link'
                  Values: URL strings or empty strings if not available
                  
        Usage:
            all_links = role_manager.get_all_links_for_role('Software Developer')
            print(f"Express: {all_links['express_link']}")
            print(f"Description: {all_links['desc_link']}")
            print(f"Video: {all_links['video_link']}")
            
            # Check if any links are available
            has_links = any(all_links.values())
        """
        return {
            "express_link": self.get_express_link(role_name),
            "desc_link": self.get_description_link(role_name),
            "video_link": self.get_video_link(role_name)
        }