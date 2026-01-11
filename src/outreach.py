import sqlite3
import json
from .agents import Agent
from .llm_utils import llm
from config import DB_PATH, logger

class OutreachAgent(Agent):
    def __init__(self):
        super().__init__("Outreach")

    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        action = message.get("action")
        if action == "generate_email":
            return self.generate_email(message.get("professor_id"), message.get("student_profile"))
        return {"status": "error", "message": "Unknown action"}

    def generate_email(self, professor_id: int, student_profile: str) -> Dict[str, Any]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name, p.department, u.name 
            FROM professors p 
            JOIN universities u ON p.university_id = u.id 
            WHERE p.id = ?
        """, (professor_id,))
        prof = cursor.fetchone()
        conn.close()
        
        if not prof:
            return {"status": "error", "message": "Professor not found"}
            
        prof_name, dept, uni_name = prof
        
        self.log_decision(
            task="Generate Personalized Email",
            decision=f"Drafting email for {prof_name}",
            reasoning=f"Creating a non-template email based on {prof_name}'s profile at {uni_name}.",
            confidence=0.9,
            success=True
        )
        
        system_prompt = """
        You are an elite PhD application consultant. Write a highly personalized, 
        non-generic email from a student to a professor. 
        Rules:
        - No templates.
        - Reference specific interests.
        - Tone: Professional, passionate but humble.
        - Mention the university and department.
        - Maximum 300 words.
        """
        user_prompt = f"""
        Student Profile:
        {student_profile}
        
        Professor: {prof_name}
        Department: {dept}
        University: {uni_name}
        
        Output in JSON format: {{"subject": "...", "body": "...", "quality_score": 90, "reasoning": "..."}}
        """
        
        response = llm.generate_response(system_prompt, user_prompt)
        email_data = llm.parse_json_response(response)
        
        # Save to DB
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO emails (professor_id, subject, body, quality_score, generation_reasoning)
            VALUES (?, ?, ?, ?, ?)
        """, (professor_id, email_data.get('subject'), email_data.get('body'), 
              email_data.get('quality_score'), email_data.get('reasoning')))
        conn.commit()
        conn.close()
        
        return email_data
        
