import requests
import json
import os

BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    print("\n--- Testing Health Check ---")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_parse_resume(file_path):
    print("\n--- Testing Resume Parsing ---")
    if not os.path.exists(file_path):
        print(f"File {file_path} not found!")
        return None

    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{BASE_URL}/parse", files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Successfully parsed: {data['name']}")
        print(f"Candidate ID: {data['candidate_id']}")
        return data['candidate_id']
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_list_candidates():
    print("\n--- Testing List Candidates ---")
    response = requests.get(f"{BASE_URL}/candidates")
    print(f"Status: {response.status_code}")
    print(f"Candidates Found: {len(response.json())}")
    return response.json()

def test_match_candidate(candidate_id):
    print("\n--- Testing Candidate Matching ---")
    job_description = {
        "title": "Senior Digital Marketing Specialist",
        "description": "We are seeking a marketing expert to lead our SEO, SEM, and social media campaigns. Experience with Google Ads, Meta Ads, and content strategy is essential. Deep knowledge of CRM and conversion optimization is required.",
        "required_skills": ["SEO", "SEM", "Google Ads", "Content Marketing", "Social Media Management"],
        "nice_to_have_skills": ["Email Marketing", "CRM"]
    }
    
    payload = {
        "candidate_id": candidate_id,
        "job_description": job_description
    }
    
    response = requests.post(f"{BASE_URL}/match", json=payload)
    if response.status_code == 200:
        data = response.json()
        print(f"Match Score: {data['match_score']}%")
        print(f"Recommendation: {data['recommendation']}")
        print(f"Gap Analysis: {data['gap_analysis']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_health()
    candidate_id = test_parse_resume("test_resume.txt")
    if candidate_id:
        test_list_candidates()
        test_match_candidate(candidate_id)
