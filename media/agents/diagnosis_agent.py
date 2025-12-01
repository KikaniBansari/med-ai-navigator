"""
Diagnosis Agent - Provides diagnosis suggestions and medication recommendations
Uses web search results to suggest possible conditions and treatments
"""

import json
import re
from typing import Dict, Any, List
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from media.agents.base import BaseAgent


class DiagnosisAgent(BaseAgent):
    """Agent that suggests possible diagnoses and medications based on symptoms and web search"""
    
    async def suggest_diagnosis(
        self, 
        symptoms: Dict[str, Any], 
        web_guidelines: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Suggest possible diagnoses based on symptoms and web information
        
        Args:
            symptoms: Parsed symptom data
            web_guidelines: Web search results with medical guidelines
            
        Returns:
            Dictionary with possible diagnoses and medications
        """
        symptoms_text = self._format_symptoms(symptoms)
        web_info_text = self._format_web_info(web_guidelines) if web_guidelines else ""
        
        prompt = PromptTemplate.from_template(
            """You are a medical AI expert. Based on the following patient symptoms and medical guidelines, suggest possible diagnoses and treatments.

Patient Symptoms:
{symptoms}

Medical Guidelines from Web:
{web_info}

Task:
1. Suggest 2-3 most likely diagnoses (e.g., "Common Cold", "Influenza", "Upper Respiratory Infection")
2. For each diagnosis, provide:
   - Likelihood (High/Medium/Low)
   - Brief explanation
   - Common medications/treatments (over-the-counter and prescription)
   - When to see a doctor

Important:
- For common conditions like cold, flu, allergies, provide specific medication names
- Include both OTC and prescription options
- Always recommend seeing a doctor for severe symptoms
- Be specific about medication types (e.g., "Ibuprofen for fever", "Antihistamines for allergies")

Return ONLY a valid JSON object with this structure:
{{
  "possible_diagnoses": [
    {{
      "condition": "condition name",
      "likelihood": "High/Medium/Low",
      "explanation": "why this might be the case",
      "medications": [
        {{
          "name": "medication name",
          "type": "OTC/Prescription",
          "purpose": "what it treats",
          "dosage": "general dosage info if known"
        }}
      ],
      "when_to_see_doctor": "guidance on when professional care is needed"
    }}
  ],
  "general_recommendations": "overall advice"
}}

Do not include markdown formatting, only the JSON object."""
        )
        
        try:
            chain = prompt | self.llm | StrOutputParser()
            result = await chain.ainvoke({
                "symptoms": symptoms_text,
                "web_info": web_info_text
            })
            
            # Cleanup and parse JSON
            clean_json = result.replace("```json", "").replace("```", "").strip()
            json_match = re.search(r'\{.*\}', clean_json, re.DOTALL)
            if json_match:
                clean_json = json_match.group(0)
            
            parsed = json.loads(clean_json)
            
            # Validate structure
            if "possible_diagnoses" not in parsed:
                parsed["possible_diagnoses"] = []
            
            return parsed
            
        except (json.JSONDecodeError, Exception) as e:
            # Fallback diagnosis based on symptoms
            return self._fallback_diagnosis(symptoms)
    
    def _format_symptoms(self, symptoms: Dict[str, Any]) -> str:
        """Format symptoms for prompt"""
        symptoms_list = symptoms.get("symptoms", [])
        if isinstance(symptoms_list, str):
            symptoms_list = [symptoms_list]
        elif not isinstance(symptoms_list, list):
            symptoms_list = []
        
        return f"""
- Symptoms: {', '.join(symptoms_list) if symptoms_list else 'Not specified'}
- Duration: {symptoms.get('duration', 'Unknown')}
- Severity: {symptoms.get('severity', 'Unknown')}
"""
    
    def _format_web_info(self, web_guidelines: Dict[str, Any]) -> str:
        """Format web search results for prompt"""
        if not web_guidelines or not web_guidelines.get("success"):
            return "No additional medical guidelines available."
        
        results = web_guidelines.get("results", [])
        if not results:
            return "No additional medical guidelines available."
        
        formatted = "Medical Guidelines Found:\n"
        for i, result in enumerate(results[:3], 1):
            formatted += f"\n{i}. {result.get('title', '')}\n"
            formatted += f"   {result.get('snippet', '')}\n"
        
        return formatted
    
    def _fallback_diagnosis(self, symptoms: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback diagnosis when AI parsing fails"""
        symptoms_list = symptoms.get("symptoms", [])
        symptom_text = ' '.join(symptoms_list) if isinstance(symptoms_list, list) else str(symptoms_list)
        symptom_lower = symptom_text.lower()
        
        # Simple keyword-based fallback
        diagnoses = []
        
        if any(word in symptom_lower for word in ['cough', 'sneeze', 'runny nose', 'congestion']):
            diagnoses.append({
                "condition": "Common Cold",
                "likelihood": "Medium",
                "explanation": "Symptoms suggest a common cold",
                "medications": [
                    {
                        "name": "Acetaminophen (Tylenol)",
                        "type": "OTC",
                        "purpose": "Fever and pain relief",
                        "dosage": "As directed on package"
                    },
                    {
                        "name": "Ibuprofen (Advil)",
                        "type": "OTC",
                        "purpose": "Fever and pain relief",
                        "dosage": "As directed on package"
                    },
                    {
                        "name": "Decongestants",
                        "type": "OTC",
                        "purpose": "Nasal congestion",
                        "dosage": "As directed on package"
                    }
                ],
                "when_to_see_doctor": "If symptoms persist for more than 10 days or worsen"
            })
        
        if any(word in symptom_lower for word in ['fever', 'chills', 'body ache', 'fatigue']):
            diagnoses.append({
                "condition": "Influenza (Flu)",
                "likelihood": "Medium",
                "explanation": "Symptoms may indicate influenza",
                "medications": [
                    {
                        "name": "Oseltamivir (Tamiflu)",
                        "type": "Prescription",
                        "purpose": "Antiviral treatment",
                        "dosage": "As prescribed by doctor"
                    },
                    {
                        "name": "Acetaminophen or Ibuprofen",
                        "type": "OTC",
                        "purpose": "Fever and body aches",
                        "dosage": "As directed on package"
                    }
                ],
                "when_to_see_doctor": "Seek medical attention if high fever persists or breathing difficulties occur"
            })
        
        if not diagnoses:
            diagnoses.append({
                "condition": "General Symptoms",
                "likelihood": "Low",
                "explanation": "Insufficient information for specific diagnosis",
                "medications": [
                    {
                        "name": "Consult healthcare provider",
                        "type": "Medical Advice",
                        "purpose": "Proper diagnosis needed",
                        "dosage": "N/A"
                    }
                ],
                "when_to_see_doctor": "Consult a healthcare professional for proper evaluation"
            })
        
        return {
            "possible_diagnoses": diagnoses,
            "general_recommendations": "Rest, stay hydrated, and monitor symptoms. Seek medical attention if symptoms worsen."
        }

