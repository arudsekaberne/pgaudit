#####################################################
# Packages                                          #
#####################################################

import re
from typing import List, Union


#####################################################
# Main Class                                        #
#####################################################


class Validation:

    """A class to handle reading and validating job configurations from a database."""


    @staticmethod
    def validate_email(p_value: Union[str, List[str]]) -> List[str]:
            
        """Validates emails against the 'altimetrik.com' domain."""
    
        def _validate_single_email(_email: str) -> str:

            pattern: str = r"@(altimetrik.com)$"
            email_cleaned: str = _email.strip()

            if not re.search(pattern, email_cleaned, re.IGNORECASE):
                raise ValueError(f"Invalid email: '{email_cleaned}'. Must belong to 'altimetrik.com' domain.")
            
            return email_cleaned
        

        if not p_value:
            return p_value
        
        elif isinstance(p_value, str):
            return [_validate_single_email(email) for email in p_value.split(",")]
        
        elif isinstance(p_value, list):
            return [_validate_single_email(email) for email in p_value]
        
        else:
            raise TypeError("Expected a string or a list of strings.")