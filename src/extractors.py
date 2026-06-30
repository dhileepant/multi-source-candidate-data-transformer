import csv
import re
import os
import urllib.request
import json
from typing import List, Dict, Any
from pypdf import PdfReader
from src.schema import CanonicalProfile, Skill, Experience, Education

def extract_from_csv(filepath: str) -> List[Dict[str, Any]]:
    """
    Extracts raw data from a structured CSV source.
    """
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Basic mapping from CSV headers to canonical dict
                record = {
                    "full_name": row.get("name"),
                    "emails": [row.get("email")] if row.get("email") else [],
                    "phones": [row.get("phone")] if row.get("phone") else [],
                    "experience": [{"company": row.get("current_company"), "title": row.get("title")}] if row.get("current_company") else []
                }
                results.append({"data": record, "source": f"csv_export ({os.path.basename(filepath)})", "confidence_base": 0.9})
    except Exception as e:
        print(f"Error extracting from CSV {filepath}: {e}")
    return results

def extract_from_pdf(filepath: str) -> List[Dict[str, Any]]:
    """
    Extracts raw data from an unstructured PDF (Resume).
    Simulates an NLP/LLM extraction pipeline using regex heuristics.
    """
    results = []
    try:
        reader = PdfReader(filepath)
        text = ""
        urls = []
        for page in reader.pages:
            text += page.extract_text() + "\n"
            annots = page.get('/Annots', [])
            if hasattr(annots, 'get_object'): # Sometimes it's an IndirectObject
                annots = annots.get_object()
            if isinstance(annots, list):
                for annot in annots:
                    try:
                        obj = annot.get_object()
                        uri = obj.get('/A', {}).get('/URI')
                        if uri:
                            urls.append(uri)
                    except:
                        pass
        
        # Heuristics for simulated extraction
        record = {
            "emails": [],
            "phones": [],
            "skills": [],
            "experience": [],
            "education": [],
            "links": {}
        }
        
        # 1. Name (Assuming it's at the top of the resume)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            record["full_name"] = lines[0]
            
        # 2. Email
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        if email_match:
            record["emails"].append(email_match.group(0))
            
        # 3. Phone (Basic regex)
        phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        if phone_match:
            record["phones"].append(phone_match.group(0))
            
        # 4. Skills
        # Support multiple common resume headers for skills
        skills_match = re.search(r'(?:technical\s+skills|skills|tech\s+stack|technologies|core\s+skills)\s*:?\n(.*?)(?=\n\n|\n[A-Z\s]+(?:\n|$))', text, re.IGNORECASE | re.DOTALL)
        if skills_match:
            skills_str = skills_match.group(1)
            # Split by commas or newlines if it's a list
            raw_skills = re.split(r'[,|]', skills_str)
            skills = [s.strip() for s in raw_skills if s.strip()]
            record["skills"] = [{"name": s} for s in skills]
            
        # 5. Experience
        exp_matches = re.finditer(r'(.*?) at (.*?) \((.*?)\)', text)
        for match in exp_matches:
            record["experience"].append({
                "title": match.group(1).strip(),
                "company": match.group(2).strip(),
                "summary": match.group(3).strip()
            })
            
        # 6. Education
        edu_match = re.search(r'Education\s*\n(.*?)(?=\n\n|$)', text, re.IGNORECASE)
        if edu_match:
            record["education"].append({
                "institution": edu_match.group(1).strip()
            })
            
        # 7. GitHub URL
        # Check text first
        github_match = re.search(r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9-]+)', text, re.IGNORECASE)
        if github_match:
            record["links"]["github"] = f"https://github.com/{github_match.group(1)}"
        else:
            # Check URLs from annotations
            for url in urls:
                if isinstance(url, str) and "github.com/" in url:
                    username = url.rstrip('/').split('/')[-1]
                    record["links"]["github"] = f"https://github.com/{username}"
                    break

        results.append({"data": record, "source": f"resume_pdf ({os.path.basename(filepath)})", "confidence_base": 0.8})
        
        
    except Exception as e:
        print(f"Error extracting from PDF {filepath}: {e}")
        
    return results

def extract_from_github(url: str) -> List[Dict[str, Any]]:
    """
    Extracts raw data from a GitHub profile URL via the public API.
    """
    results = []
    try:
        # Basic heuristic to extract username from url
        username = url.rstrip('/').split('/')[-1]
        api_url = f"https://api.github.com/users/{username}"
        
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Candidate-Transformer'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        record = {
            "full_name": data.get("name"),
            "headline": data.get("bio"),
            "links": {"github": data.get("html_url")},
            "emails": [data.get("email")] if data.get("email") else []
        }
        
        # We could also fetch repos and languages here, but keeping it simple for the canonical schema
        results.append({"data": record, "source": f"github_api ({username})", "confidence_base": 0.95})
        
    except Exception as e:
        print(f"Error extracting from GitHub {url}: {e}")
        
    return results

