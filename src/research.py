import sqlite3
import json
from typing import Dict, Any, List
from .agents import Agent
from .tools import WebSearch, WebScraper, RankingCalculator
from .llm_utils import llm
from config import DB_PATH, logger

class ResearchAgent(Agent):
    def __init__(self, search_tool: WebSearch, scraper_tool: WebScraper, ranker: RankingCalculator):
        super().__init__("Research")
        self.search_tool = search_tool
        self.scraper_tool = scraper_tool
        self.ranker = ranker

    def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        action = message.get("action")
        if action == "find_universities":
            return self.find_universities(message.get("country"))
        elif action == "find_professors":
            return self.find_professors(message.get("university_id"))
        return {"status": "error", "message": "Unknown action"}

    def find_universities(self, country: str) -> Dict[str, Any]:
        self.log_decision(
            task="Discover Universities",
            decision=f"Initiating discovery for {country}",
            reasoning=f"Need a comprehensive list of universities in {country} with research programs.",
            confidence=1.0,
            success=True
        )
        
        # 1. Search for university list
        queries = [
            f"list of universities in {country} with computer science research",
            f"top universities in {country} QS rankings 2025",
            f"universities in {country} for PhD in AI"
        ]
        
        all_unis = []
        for query in queries:
            results = self.search_tool.search(query)
            # In a real scenario, we parse these results. 
            # For this demo, we'll simulate finding some key universities.
            # But the logic is: search -> extract names -> deduplicate -> save.
        
        # Simulated discovery for trial if search returns empty
        # (This keeps the demo working even without real search API)
        if country.lower() == "germany":
            all_unis = [
                {"name": "Technical University of Munich", "country": "Germany", "ranking_qs": 37},
                {"name": "Ludwig Maximilian University of Munich", "country": "Germany", "ranking_qs": 59},
                {"name": "RWTH Aachen University", "country": "Germany", "ranking_qs": 106}
            ]
        
        # 2. Save to DB
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        found_count = 0
        for uni in all_unis:
            cursor.execute("SELECT id FROM universities WHERE name = ?", (uni['name'],))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO universities (name, country, ranking_qs, verification_status)
                    VALUES (?, ?, ?, 'needs_check')
                """, (uni['name'], uni['country'], uni.get('ranking_qs')))
                found_count += 1
        conn.commit()
        conn.close()

        return {
            "status": "success", 
            "message": f"Found and saved {found_count} new universities for {country}.",
            "count": found_count
        }

    def analyze_university_match(self, university_id: int, student_profile: str) -> Dict[str, Any]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, research_areas FROM universities WHERE id = ?", (university_id,))
        uni = cursor.fetchone()
        conn.close()
        
        if not uni:
            return {"status": "error", "message": "University not found"}
        
        name, research_areas = uni
        
        system_prompt = "You are an expert PhD matching assistant. Analyze if a university is a good fit for a student."
        user_prompt = f"""
        Student Profile:
        {student_profile}
        
        University: {name}
        Known Research Areas: {research_areas or 'Not yet scraped'}
        
        Please provide:
        1. Match Score (0-100)
        2. Match Reasoning (2-3 sentences)
        3. Confidence Score (0.0-1.0)
        
        Output in JSON format: {{"score": 85, "reasoning": "...", "confidence": 0.9}}
        """
        
        response = llm.generate_response(system_prompt, user_prompt)
        match_data = llm.parse_json_response(response)
        
        # Save results
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE universities 
            SET match_score = ?, match_reasoning = ?, confidence_score = ?
            WHERE id = ?
        """, (match_data.get('score'), match_data.get('reasoning'), match_data.get('confidence'), university_id))
        conn.commit()
        conn.close()
        
        return match_data

    def find_professors(self, university_id: int) -> Dict[str, Any]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, website_url FROM universities WHERE id = ?", (university_id,))
        uni = cursor.fetchone()
        conn.close()
        
        if not uni:
            return {"status": "error", "message": "University not found"}
            
        uni_name, uni_url = uni
        self.log_decision(
            task="Discover Professors",
            decision=f"Searching for faculty at {uni_name}",
            reasoning=f"Need to identify research-active professors in CS/AI for university {university_id}.",
            confidence=0.7,
            success=True
        )
        
        # Logic: 
        # 1. Search for "Faculty list {uni_name} Computer Science"
        # 2. Scrape the page
        # 3. Extract names and profiles
        
        # Simulation for trials
        if "Munich" in uni_name:
            profs = [
                {"name": "Prof. Nassim Labidi", "department": "AI & Robotics", "priority": 5, "accepting": "yes"},
                {"name": "Prof. Hans Muller", "department": "Deep Learning", "priority": 4, "accepting": "yes"}
            ]
        else:
            profs = []
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for prof in profs:
            cursor.execute("""
                INSERT INTO professors (university_id, name, department, contact_priority, accepting_students)
                VALUES (?, ?, ?, ?, ?)
            """, (university_id, prof['name'], prof['department'], prof['priority'], prof['accepting']))
        conn.commit()
        conn.close()
        
        return {"status": "success", "count": len(profs)}
