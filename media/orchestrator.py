import asyncio
import time
from typing import Dict, Any, Optional
from media.agents import SymptomAgent, DocAgent, RiskAgent, TriageAgent
from media.agents.diagnosis_agent import DiagnosisAgent
from media.memory import memory_bank
from media.observability import metrics_service
from media.tools.web_search_tool import WebSearchTool


class MedAIOrchestrator:
    """Main orchestrator for MedAI platform"""
    
    def __init__(self):
        """Initialize all agents and tools"""
        self.symptom_agent = SymptomAgent()
        self.doc_agent = DocAgent()
        self.risk_agent = RiskAgent()
        self.triage_agent = TriageAgent()
        self.diagnosis_agent = DiagnosisAgent()
        self.web_search = WebSearchTool()

    async def process_patient_query(
        self, 
        patient_id: str, 
        symptoms_text: str, 
        doc_text: str = ""
    ) -> Dict[str, Any]:
        """
        Process patient query through multi-agent pipeline
        
        Args:
            patient_id: Unique patient identifier
            symptoms_text: Patient symptom description
            doc_text: Optional medical document/EHR text
            
        Returns:
            Complete analysis result with triage recommendation
        """
        start_time = time.time()
        
        try:
            # 1. PARALLEL EXECUTION (Symptom Parsing + Document/EHR Retrieval)
            print(f"--- Starting Parallel Processing for {patient_id} ---")
            
            if not doc_text or not doc_text.strip():
                doc_text = "No significant medical history."
            
            # Run both agents in parallel
            symptom_task = self.symptom_agent.run(symptoms_text)
            doc_task = self.doc_agent.run(doc_text)
            
            symptom_data, history_data = await asyncio.gather(symptom_task, doc_task)
            
            metrics_service.log_latency("agent_parallel_processing", start_time)
            
            # Store intermediate results in Memory Bank
            memory_bank.store_patient_fact(patient_id, "latest_symptoms", symptom_data)
            memory_bank.store_patient_fact(patient_id, "medical_history", history_data)

            # 1.5. WEB SEARCH for medical guidelines (if symptoms found)
            web_info = {}
            if symptom_data and symptom_data.get("symptoms"):
                symptoms_list = symptom_data.get("symptoms", [])
                if isinstance(symptoms_list, list) and len(symptoms_list) > 0:
                    # Create comprehensive search query
                    primary_symptom = symptoms_list[0] if isinstance(symptoms_list[0], str) else str(symptoms_list[0])
                    all_symptoms = ', '.join([str(s) for s in symptoms_list[:3]])
                    
                    # Search for diagnosis and treatment information
                    search_query = f"{all_symptoms} diagnosis treatment medication"
                    print(f"--- Searching web for diagnosis and treatment: {search_query} ---")
                    search_start = time.time()
                    web_info = await self.web_search.search(search_query, num_results=5)
                    metrics_service.log_latency("web_search", search_start)
                    
                    if web_info.get("success") and web_info.get("results"):
                        memory_bank.store_patient_fact(patient_id, "web_guidelines", web_info)
            
            # 1.6. DIAGNOSIS SUGGESTIONS with medication recommendations
            print("--- Generating Diagnosis Suggestions ---")
            diagnosis_start = time.time()
            try:
                diagnosis_data = await self.diagnosis_agent.suggest_diagnosis(symptom_data, web_info)
                metrics_service.log_latency("agent_diagnosis", diagnosis_start)
                
                if diagnosis_data:
                    memory_bank.store_patient_fact(patient_id, "diagnosis_suggestions", diagnosis_data)
            except Exception as e:
                print(f"Warning: Diagnosis agent failed: {str(e)}")
                # Use fallback diagnosis
                diagnosis_data = self.diagnosis_agent._fallback_diagnosis(symptom_data)
                memory_bank.store_patient_fact(patient_id, "diagnosis_suggestions", diagnosis_data)

            # 2. SEQUENTIAL EXECUTION
            print("--- Starting Risk Assessment ---")
            risk_start = time.time()
            # RiskAgent and TriageAgent are synchronous
            risk_data = self.risk_agent.run(symptom_data, history_data)
            metrics_service.log_latency("agent_risk", risk_start)

            print("--- Starting Triage Generation ---")
            triage_start = time.time()
            # TriageAgent is synchronous
            triage_data = self.triage_agent.run(risk_data, symptom_data)
            metrics_service.log_latency("agent_triage", triage_start)

            # 3. BIAS DETECTION & SAFETY CHECK (Simple Rules Engine)
            bias_detected = False
            if triage_data.get('action') == "Home Care" and risk_data.get('score', 0) > 7:
                # Safety net: High risk shouldn't stay home
                triage_data['warning'] = "OVERRIDE: AI detected safety inconsistency. Escalated to Nurse Review."
                metrics_service.log_mistriage()
                bias_detected = True
            
            metrics_service.log_bias_check(bias_detected)

            total_time = time.time() - start_time
            
            return {
                "success": True,
                "session_id": f"sess_{patient_id}_{int(time.time())}",
                "processing_time": round(total_time, 2),
                "analysis": {
                    "symptoms_parsed": symptom_data,
                    "history_context": history_data,
                    "risk_assessment": risk_data,
                    "triage_recommendation": triage_data,
                    "web_guidelines": web_info if web_info.get("success") else None,
                    "diagnosis_suggestions": diagnosis_data
                },
                "bias_detected": bias_detected
            }
        except Exception as e:
            metrics_service.log_mistriage()
            return {
                "success": False,
                "error": str(e),
                "session_id": f"sess_{patient_id}_{int(time.time())}",
                "processing_time": round(time.time() - start_time, 2)
            }