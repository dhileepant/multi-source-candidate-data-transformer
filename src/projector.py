from typing import Dict, Any, List
from pydantic import BaseModel
from src.schema import CanonicalProfile
import re

def project_output(profile: CanonicalProfile, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applies runtime config to project the canonical profile into the final requested shape.
    """
    if config.get("passthrough"):
        return profile.model_dump(exclude_none=False)
        
    profile_dict = profile.model_dump(exclude_none=True)
    output = {}
    
    # helper for resolving paths like "emails[0]" or "skills[].name"
    def resolve_path(data: Any, path: str) -> Any:
        # Simplistic jsonpath implementation for the example config
        if not path:
            return data
            
        parts = re.split(r'\.|\[|\]', path)
        parts = [p for p in parts if p] # filter empty
        
        current = data
        for p in parts:
            if current is None:
                return None
                
            if isinstance(current, dict):
                current = current.get(p)
            elif isinstance(current, list):
                if p.isdigit():
                    idx = int(p)
                    if idx < len(current):
                        current = current[idx]
                    else:
                        return None
                elif p == '':
                    # This means we had []
                    # We expect the next part to map over the list
                    pass 
                else:
                    # we have a list but part is a string. means map property
                    current = [item.get(p) for item in current if isinstance(item, dict) and p in item]
            else:
                return None
                
        return current

    fields_config = config.get("fields", [])
    
    for field in fields_config:
        target_path = field.get("path")
        source_path = field.get("from", target_path) # defaults to same name
        
        val = resolve_path(profile_dict, source_path)
        
        # apply missing logic
        if val is None or (isinstance(val, list) and len(val) == 0):
            on_missing = config.get("on_missing", "null")
            if on_missing == "omit":
                continue
            elif on_missing == "error":
                raise ValueError(f"Required field missing: {target_path}")
            else:
                val = None
                
        output[target_path] = val
        
    if config.get("include_confidence", False) and "overall_confidence" in profile_dict:
        output["overall_confidence"] = profile_dict["overall_confidence"]
        
    if config.get("include_provenance", False) and "provenance" in profile_dict:
        output["provenance"] = profile_dict["provenance"]
        
    return output
