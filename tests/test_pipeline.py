import pytest
from src.normalizers import normalize_phone, normalize_country, normalize_skills_list, normalize_date
from src.merger import merge_records, is_deterministic_match

def test_normalize_phone():
    assert normalize_phone("(415) 555-2671") == "+14155552671"
    assert normalize_phone("invalid phone") == "invalid phone"

def test_normalize_country():
    assert normalize_country("United States") == "US"
    assert normalize_country("india") == "IN"
    assert normalize_country("unknown") == "unknown"

def test_normalize_skills_list():
    raw = [{"name": " React.js, node.js "}, {"name": "PYTHON "}, {"name": "React"}]
    skills = normalize_skills_list(raw, 0.9, "test")
    assert len(skills) == 3
    names = [s.name for s in skills]
    assert "React.js" in names
    assert "Node.js" in names
    assert "Python" in names

def test_is_deterministic_match():
    # Email match
    rec_a = {"data": {"emails": ["test@example.com"], "full_name": "John Doe"}}
    rec_b = {"data": {"emails": ["test@example.com"], "full_name": "John Smith"}}
    assert is_deterministic_match(rec_a, rec_b) == True
    
    # Github Match
    rec_c = {"data": {"full_name": "John Doe", "links": {"github": "https://github.com/john"}}}
    rec_d = {"data": {"full_name": "John Doe", "links": {"github": "https://github.com/john"}}}
    assert is_deterministic_match(rec_c, rec_d) == True
    
    # Name ONLY match (should be False)
    rec_e = {"data": {"full_name": "John Doe", "experience": [{"company": "Google"}]}}
    rec_f = {"data": {"full_name": "John Doe", "experience": [{"company": "Google"}]}}
    assert is_deterministic_match(rec_e, rec_f) == False

def test_merge_records():
    # Should merge because email matches
    records = [
        {"data": {"emails": ["test@test.com"], "full_name": "Test"}, "source": "csv", "confidence_base": 0.9},
        {"data": {"emails": ["test@test.com"], "skills": [{"name": "Python"}]}, "source": "resume", "confidence_base": 0.8}
    ]
    canonical = merge_records(records)
    assert len(canonical) == 1
    assert canonical[0].full_name == "Test"
    assert len(canonical[0].skills) == 1
    assert canonical[0].skills[0].name == "Python"
    
    # Should NOT merge because only name matches
    records2 = [
        {"data": {"full_name": "Test User"}, "source": "csv", "confidence_base": 0.9},
        {"data": {"full_name": "Test User"}, "source": "resume", "confidence_base": 0.8}
    ]
    canonical2 = merge_records(records2)
    assert len(canonical2) == 2
