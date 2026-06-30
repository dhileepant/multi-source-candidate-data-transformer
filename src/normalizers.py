import phonenumbers
from dateutil import parser
import re

def normalize_phone(phone_str: str) -> str:
    """
    Normalizes a phone number to E.164 format.
    Returns the original string if parsing fails (to avoid data loss on strict errors, 
    but downstream might have lower confidence).
    """
    if not phone_str:
        return phone_str
    try:
        # Defaulting region to US if no country code provided for demo purposes.
        parsed = phonenumbers.parse(phone_str, "US")
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        pass
    return phone_str

def normalize_date(date_str: str) -> str:
    """
    Normalizes a date string to YYYY-MM format.
    """
    if not date_str:
        return date_str
    try:
        parsed = parser.parse(date_str, fuzzy=True)
        return parsed.strftime("%Y-%m")
    except Exception:
        return date_str

SKILL_MAP = {
    "react": "React.js",
    "reactjs": "React.js",
    "react.js": "React.js",
    "next": "Next.js",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "cpp": "C++",
    "c++": "C++",
    "c": "C",
    "git hub": "GitHub",
    "github": "GitHub",
    "springboot": "Spring Boot",
    "spring boot": "Spring Boot",
    "git": "Git",
    "bootstrap": "Bootstrap",
    "python": "Python",
    "mongodb": "MongoDB",
    "sql": "SQL",
    "java": "Java",
    "mysql": "MySQL"
}

def normalize_skills_list(raw_skills: list, conf: float, source: str) -> list:
    """
    Takes a list of raw skill dicts (e.g., [{"name": "react.js node.js"}])
    Tokenizes by spaces, commas, newlines, maps to canonical names, deduplicates,
    and returns a list of canonical Skill objects.
    """
    from src.schema import Skill
    
    # 1. Combine all raw skill strings into one large string
    combined = " ".join([s.get("name", "") for s in raw_skills])
    
    # 2. Tokenize (by whitespace, comma, newline)
    tokens = re.split(r'[\s,]+', combined)
    
    # 3. Normalize and deduplicate
    seen = set()
    canonical_skills = []
    
    for token in tokens:
        token = token.strip().lower()
        if not token:
            continue
            
        # Map to canonical name if it exists, otherwise title case it
        canonical_name = SKILL_MAP.get(token, token.title())
        
        if canonical_name not in seen:
            seen.add(canonical_name)
            canonical_skills.append(Skill(name=canonical_name, confidence=conf, sources=[source]))
            
    return canonical_skills

def normalize_country(country_str: str) -> str:
    """
    Normalizes country to ISO-3166 alpha-2.
    """
    if not country_str:
        return country_str
    
    # Mock lookup table for simplicity
    lookup = {
        "united states": "US",
        "usa": "US",
        "india": "IN",
        "uk": "GB",
        "united kingdom": "GB",
        "canada": "CA"
    }
    s = country_str.lower().strip()
    return lookup.get(s, country_str[:2].upper() if len(country_str) == 2 else country_str)
