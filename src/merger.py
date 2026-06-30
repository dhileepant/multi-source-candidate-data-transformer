from typing import List, Dict, Any, Optional
from src.schema import CanonicalProfile, Provenance, Skill, Experience, Education
from src.normalizers import normalize_phone, normalize_date, normalize_skills_list, normalize_country

def is_deterministic_match(record_a: Dict[str, Any], record_b: Dict[str, Any]) -> bool:
    """
    Returns True if the two records share at least one strong identifier:
    Email, Phone, GitHub URL, or LinkedIn URL.
    """
    data_a = record_a.get("data", {})
    data_b = record_b.get("data", {})
    
    # 1. Email Match
    emails_a = set([e.lower() for e in data_a.get("emails", [])])
    emails_b = set([e.lower() for e in data_b.get("emails", [])])
    if emails_a and emails_b and not emails_a.isdisjoint(emails_b):
        return True
        
    # 2. Phone Match
    phones_a = set([normalize_phone(p) for p in data_a.get("phones", [])])
    phones_b = set([normalize_phone(p) for p in data_b.get("phones", [])])
    if phones_a and phones_b and not phones_a.isdisjoint(phones_b):
        return True
        
    # 3. GitHub URL Match
    github_a = data_a.get("links", {}).get("github", "").lower()
    github_b = data_b.get("links", {}).get("github", "").lower()
    if github_a and github_b and github_a == github_b:
        return True
        
    # 4. LinkedIn URL Match (Future-proofing, though not currently extracted)
    linkedin_a = data_a.get("links", {}).get("linkedin", "").lower()
    linkedin_b = data_b.get("links", {}).get("linkedin", "").lower()
    if linkedin_a and linkedin_b and linkedin_a == linkedin_b:
        return True
        
    return False

def merge_records(extracted_records: List[Dict[str, Any]]) -> List[CanonicalProfile]:
    """
    Groups records by finding connected components (indirect matches) and merges them.
    """
    n = len(extracted_records)
    adj = {i: [] for i in range(n)}
    
    for i in range(n):
        for j in range(i + 1, n):
            if is_deterministic_match(extracted_records[i], extracted_records[j]):
                adj[i].append(j)
                adj[j].append(i)
                
    visited = set()
    clusters = []
    
    for i in range(n):
        if i not in visited:
            component = []
            queue = [i]
            visited.add(i)
            
            while queue:
                curr = queue.pop(0)
                component.append(extracted_records[curr])
                for neighbor in adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
                        
            clusters.append(component)
            
    canonical_profiles = []
    for cluster in clusters:
        profile = _merge_group(cluster)
        canonical_profiles.append(profile)
        
    return canonical_profiles

def _merge_group(group: List[Dict[str, Any]]) -> CanonicalProfile:
    # Sort group by confidence (highest first)
    group = sorted(group, key=lambda x: x["confidence_base"], reverse=True)
    
    merged = {}
    provenance = []
    total_conf = 0.0
    field_count = 0
    
    # Helper to set field
    def set_field(field_name: str, value: Any, source: str, conf: float, method: str):
        nonlocal total_conf, field_count
        if field_name not in merged and value:
            merged[field_name] = value
            provenance.append(Provenance(field=field_name, source=source, method=method))
            total_conf += conf
            field_count += 1
            
    # Iterate through records and populate fields (first-writer wins because we sorted by confidence)
    for rec in group:
        data = rec["data"]
        src = rec["source"]
        conf = rec["confidence_base"]
        
        set_field("full_name", data.get("full_name"), src, conf, "direct_extract")
        set_field("headline", data.get("headline"), src, conf, "direct_extract")
        
        if data.get("links") and "links" not in merged:
            merged["links"] = data["links"]
            provenance.append(Provenance(field="links", source=src, method="extracted"))
            total_conf += conf
            field_count += 1
            
        # Arrays like emails and phones we might want to extend rather than overwrite, 
        # but for simplicity, we'll take the highest confidence list.
        if data.get("emails") and "emails" not in merged:
            merged["emails"] = data["emails"]
            provenance.append(Provenance(field="emails", source=src, method="regex_or_direct"))
            total_conf += conf
            field_count += 1
            
        if data.get("phones") and "phones" not in merged:
            phones = [normalize_phone(p) for p in data["phones"]]
            merged["phones"] = phones
            provenance.append(Provenance(field="phones", source=src, method="normalized_e164"))
            total_conf += conf
            field_count += 1
            
        if data.get("skills") and "skills" not in merged:
            merged["skills"] = normalize_skills_list(data["skills"], conf, src)
            provenance.append(Provenance(field="skills", source=src, method="normalized_canonical"))
            total_conf += conf
            field_count += 1
            
        if data.get("experience") and "experience" not in merged:
            exps = []
            for e in data["experience"]:
                exp = Experience(
                    company=e.get("company"),
                    title=e.get("title"),
                    summary=e.get("summary")
                )
                exps.append(exp)
            merged["experience"] = exps
            provenance.append(Provenance(field="experience", source=src, method="extracted"))
            total_conf += conf
            field_count += 1
            
    # Calculate overall confidence
    overall = (total_conf / field_count) if field_count > 0 else 0.0
    merged["overall_confidence"] = round(overall, 2)
    merged["provenance"] = provenance
    
    return CanonicalProfile(**merged)
