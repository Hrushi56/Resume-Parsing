from utils.groq_client import GroqClient
from agents.parser_agent import ParserAgent
from agents.normalizer_agent import NormalizerAgent
from agents.matcher_agent import MatcherAgent
from agents.builder_agent import BuilderAgent
from database import db
from models.schemas import CandidateProfile, JobDescription, MatchResult, ResumeInput, OptimizedResume, KeywordSuggestion
from fastapi import HTTPException

class Orchestrator:
    def __init__(self):
        self.groq_client = GroqClient()
        self.parser_agent = ParserAgent(self.groq_client)
        self.normalizer_agent = NormalizerAgent(self.groq_client)
        self.matcher_agent = MatcherAgent(self.groq_client)
        self.builder_agent = BuilderAgent(self.groq_client, self.normalizer_agent)

    async def init_db(self):
        await db.init_db()

    async def process_resume(self, file_path: str, file_type: str, hr_id: str = None) -> CandidateProfile:
        print(f"[Orchestrator] Starting processing for {file_path}")

        parsed = self.parser_agent.parse(file_path, file_type)
        normalized_skills, exp_years = self.normalizer_agent.normalize(parsed)
        final_skills = self.normalizer_agent.infer_implied_skills(normalized_skills)

        profile = CandidateProfile(
            candidate_id=parsed.candidate_id,
            name=parsed.name,
            email=parsed.email,
            normalized_skills=final_skills,
            raw_skills=parsed.skills,
            experience_years=exp_years,
            parsed_resume=parsed
        )

        await db.save_candidate(profile, hr_id=hr_id)
        print(f"[Orchestrator] Completed processing for {profile.name}")
        return profile

    async def process_resume_from_image(self, image_data_url: str, hr_id: str = None) -> CandidateProfile:
        print("[Orchestrator] Starting image resume processing...")

        parsed = self.parser_agent.parse_from_image(image_data_url)
        normalized_skills, exp_years = self.normalizer_agent.normalize(parsed)
        final_skills = self.normalizer_agent.infer_implied_skills(normalized_skills)

        profile = CandidateProfile(
            candidate_id=parsed.candidate_id,
            name=parsed.name,
            email=parsed.email,
            normalized_skills=final_skills,
            raw_skills=parsed.skills,
            experience_years=exp_years,
            parsed_resume=parsed
        )

        await db.save_candidate(profile, hr_id=hr_id)
        print(f"[Orchestrator] Completed image resume processing for {profile.name}")
        return profile


    async def match_candidate_to_job(self, candidate_id: str, job_description: JobDescription) -> MatchResult:
        print(f"[Orchestrator] Matching candidate {candidate_id} to job {job_description.title}")
        
        # Step 1: Get profile
        profile = await db.get_candidate(candidate_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Step 2: Match
        result = self.matcher_agent.match(profile, job_description)
        
        # Step 3: Save results
        await db.save_match_result(result)
        
        print(f"[Orchestrator] Match score: {result.match_score}%")
        return result

    # --- Builder Orchestration ---

    async def build_resume(self, resume_input: ResumeInput) -> OptimizedResume:
        print(f"[Orchestrator] Building optimized resume for {resume_input.name}")
        
        # 1. Optimize
        optimized = self.builder_agent.optimize_resume(resume_input)
        
        # 2. Save
        await db.save_resume(optimized)
        
        return optimized

    async def get_keyword_suggestions(self, resume_id: str, target_job: JobDescription) -> KeywordSuggestion:
        print(f"[Orchestrator] Generating keyword suggestions for resume {resume_id} against job {target_job.title}")
        
        # 1. Fetch Resume
        resume = await db.get_resume(resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        # 2. Re-use existing extract_job_skills from matcher to get JD requirements
        job_skills = target_job.required_skills
        if not job_skills:
            job_skills = self.matcher_agent.extract_job_skills(target_job.description)

        # 3. Compute overlap (case-insensitive)
        candidate_skills = [s.canonical.lower() for s in resume.optimized_skills]
        
        matched_keywords = []
        missing_keywords = []
        
        for js in job_skills:
            if js.lower() in candidate_skills:
                matched_keywords.append(js)
            else:
                # Use semantic matching to see if they have something similar
                sim = self.matcher_agent.calculate_per_skill_similarity([s.canonical for s in resume.optimized_skills], js)
                if sim >= 0.75: # Threshold for semantic match
                    matched_keywords.append(js) # They have something similar enough
                else:
                    missing_keywords.append(js)

        # 4. Generate LLM suggestions
        system_prompt = "You are an ATS optimization expert. Given a candidate's missed keywords for a target job, write a brief, actionable 2-sentence suggestion on how to bridge the gap."
        user_prompt = f"Target Job: {target_job.title}\nMissing Keywords: {missing_keywords}\nCandidate's existing skills: {candidate_skills}\nProvide actionable advice."
        
        suggestions = ""
        if missing_keywords:
            suggestions = self.groq_client.call_llm(user_prompt, system_prompt)
        else:
            suggestions = "Your resume perfectly aligns with the target job description. No missing keywords identified."

        # 5. Build response
        improvement_score = 0.0
        if job_skills:
            # How much the ATS score could go up if they add the missing skills
            improvement_score = min(float(len(missing_keywords)) * 2, 20.0)

        return KeywordSuggestion(
            resume_id=resume_id,
            job_title=target_job.title,
            job_description=target_job.description,
            matched_keywords=matched_keywords,
            missing_keywords=missing_keywords,
            suggestions=suggestions,
            ats_improvement_score=improvement_score
        )
