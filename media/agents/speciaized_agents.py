import json
import re
from typing import Dict, Any
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from media.agents.base import BaseAgent


class SymptomAgent(BaseAgent):
    """Extracts structured symptoms from natural language."""
    
    async def run(self, text: str) -> Dict[str, Any]:
        """
        Extract structured symptom information from patient text
        
        Args:
            text: Patient symptom description
            
        Returns:
            Dictionary with symptoms, duration, and severity
        """
        if not text or not text.strip():
            return {"symptoms": [], "duration": "unknown", "severity": "Low"}
        
        prompt = PromptTemplate.from_template(
            """You are a medical AI expert. Analyze the following patient complaint:
"{text}"

Extract:
1. Main symptoms (list of strings) - be specific and detailed
2. Duration (string, e.g., "2 hours", "3 days", "1 week")
3. Severity (Low/Medium/High/Critical) based on keywords and context

Consider:
- Pain descriptors (sharp, dull, throbbing)
- Associated symptoms
- Patient's description of impact

Return ONLY a valid JSON object with keys: symptoms, duration, severity.
Do not include markdown formatting, only the JSON object."""
        )
        
        try:
            chain = prompt | self.llm | StrOutputParser()
            result = await chain.ainvoke({"text": text})
            
            # Cleanup json markdown if present
            clean_json = result.replace("```json", "").replace("```", "").strip()
            # Extract JSON from response if there's extra text
            json_match = re.search(r'\{.*\}', clean_json, re.DOTALL)
            if json_match:
                clean_json = json_match.group(0)
            
            parsed = json.loads(clean_json)
            return {
                "symptoms": parsed.get("symptoms", []),
                "duration": parsed.get("duration", "unknown"),
                "severity": parsed.get("severity", "Low")
            }
        except (json.JSONDecodeError, Exception) as e:
            # Fallback parsing
            return {
                "symptoms": [text[:50]] if text else [],
                "duration": "unknown",
                "severity": "Medium",
                "error": str(e)
            }

class DocAgent(BaseAgent):
    """Simulates processing medical documents/EHR text."""
    
    async def run(self, doc_text: str) -> Dict[str, Any]:
        """
        Process medical document/EHR text
        
        Args:
            doc_text: Medical record text
            
        Returns:
            Dictionary with conditions, medications, and vitals
        """
        if not doc_text or not doc_text.strip():
            return {"conditions": [], "medications": [], "vitals": {}}
        
        prompt = PromptTemplate.from_template(
            """Analyze the following medical record excerpt:
"{doc_text}"

Extract:
1. Chronic conditions (list of strings)
2. Current medications (list of strings)
3. Most recent vitals (object with keys like bp, temperature, heart_rate if available)

Return ONLY a valid JSON object with keys: conditions, medications, vitals.
Do not include markdown formatting, only the JSON object."""
        )
        
        try:
            chain = prompt | self.llm | StrOutputParser()
            result = await chain.ainvoke({"doc_text": doc_text})
            
            clean_json = result.replace("```json", "").replace("```", "").strip()
            json_match = re.search(r'\{.*\}', clean_json, re.DOTALL)
            if json_match:
                clean_json = json_match.group(0)
            
            parsed = json.loads(clean_json)
            return {
                "conditions": parsed.get("conditions", []),
                "medications": parsed.get("medications", []),
                "vitals": parsed.get("vitals", {})
            }
        except (json.JSONDecodeError, Exception) as e:
            return {
                "conditions": [],
                "medications": [],
                "vitals": {},
                "error": str(e)
            }

class RiskAgent(BaseAgent):
    """Calculates risk score based on aggregated data."""
    
    def run(self, symptoms_data: Dict[str, Any], history_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate patient risk score
        
        Args:
            symptoms_data: Parsed symptom data
            history_data: Medical history data
            
        Returns:
            Dictionary with score, category, and reasoning
        """
        prompt = PromptTemplate.from_template(
            """Patient Profile:
Symptoms: {symptoms}
History: {conditions}
Medications: {meds}

Task: Calculate a risk score (1-10) and category.
Logic: 
- Chest pain + Cardiac history = High Risk (8-10)
- Mild symptoms + No history = Low Risk (1-3)
- Moderate symptoms = Medium Risk (4-7)

Return ONLY a valid JSON object with keys: score (int), category (str), reasoning (str).
Do not include markdown formatting, only the JSON object."""
        )
        
        try:
            chain = prompt | self.llm | StrOutputParser()
            result = chain.invoke({
                "symptoms": json.dumps(symptoms_data) if isinstance(symptoms_data, dict) else str(symptoms_data),
                "conditions": json.dumps(history_data.get("conditions", [])) if isinstance(history_data, dict) else "[]",
                "meds": json.dumps(history_data.get("medications", [])) if isinstance(history_data, dict) else "[]"
            })
            
            clean_json = result.replace("```json", "").replace("```", "").strip()
            json_match = re.search(r'\{.*\}', clean_json, re.DOTALL)
            if json_match:
                clean_json = json_match.group(0)
            
            parsed = json.loads(clean_json)
            return {
                "score": int(parsed.get("score", 5)),
                "category": parsed.get("category", "Medium"),
                "reasoning": parsed.get("reasoning", "Standard assessment")
            }
        except (json.JSONDecodeError, AttributeError, Exception) as e:
            # Fallback risk calculation
            severity = symptoms_data.get("severity", "Medium")
            base_score = {"Low": 3, "Medium": 6, "High": 9}.get(severity, 5)
            return {
                "score": base_score,
                "category": "Medium" if base_score < 7 else "High",
                "reasoning": f"Fallback calculation: {str(e)}"
            }

class TriageAgent(BaseAgent):
    """Determines the final triage recommendation."""
    
    def run(self, risk_data: Dict[str, Any], symptoms: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate triage recommendation
        
        Args:
            risk_data: Risk assessment data
            symptoms: Symptom data
            
        Returns:
            Dictionary with action, timeframe, and specialist
        """
        prompt = PromptTemplate.from_template(
            """Risk Assessment: {risk}
Symptoms: {symptoms}

Provide a triage recommendation based on the risk assessment and symptoms:
1. Action (e.g., "Call 911", "Schedule Urgent Appointment", "Schedule Appointment", "Home Care with Monitoring")
2. Timeframe (e.g., "Immediate", "Within 1 hour", "Within 24 hours", "Next available", "Within 1 week")
3. Specialist (e.g., "Emergency Medicine", "Cardiology", "General Practice", "Internal Medicine")

Guidelines:
- Risk score 8-10: Emergency care (Call 911 or Emergency Department)
- Risk score 5-7: Urgent care (Within 24 hours)
- Risk score 1-4: Routine care (Next available appointment)

Return ONLY a valid JSON object with keys: action, timeframe, specialist.
Do not include markdown formatting, only the JSON object."""
        )
        
        try:
            chain = prompt | self.llm | StrOutputParser()
            result = chain.invoke({
                "risk": json.dumps(risk_data) if isinstance(risk_data, dict) else str(risk_data),
                "symptoms": json.dumps(symptoms) if isinstance(symptoms, dict) else str(symptoms)
            })
            
            clean_json = result.replace("```json", "").replace("```", "").strip()
            json_match = re.search(r'\{.*\}', clean_json, re.DOTALL)
            if json_match:
                clean_json = json_match.group(0)
            
            parsed = json.loads(clean_json)
            return {
                "action": parsed.get("action", "Schedule Appointment"),
                "timeframe": parsed.get("timeframe", "Next available"),
                "specialist": parsed.get("specialist", "General Practice")
            }
        except (json.JSONDecodeError, AttributeError, Exception) as e:
            # Fallback triage based on risk score
            risk_score = risk_data.get("score", 5)
            if risk_score >= 8:
                action = "Call 911"
                timeframe = "Immediate"
                specialist = "Emergency Medicine"
            elif risk_score >= 5:
                action = "Schedule Appointment"
                timeframe = "24 hours"
                specialist = "General Practice"
            else:
                action = "Home Care"
                timeframe = "Next available"
                specialist = "General Practice"
            
            return {
                "action": action,
                "timeframe": timeframe,
                "specialist": specialist,
                "warning": f"Fallback logic used: {str(e)}"
            }