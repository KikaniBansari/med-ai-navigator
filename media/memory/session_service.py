from typing import Dict, List, Any, Optional
from datetime import datetime


class MemoryBank:
    """
    Memory bank for storing patient facts and session history
    Implements simple compaction to manage memory efficiently
    """
    
    def __init__(self):
        """Initialize memory bank with empty storage"""
        self._sessions: Dict[str, List[Dict[str, Any]]] = {}
        self._facts: Dict[str, Dict[str, Any]] = {}
        self._max_session_messages = 20  # Compaction threshold

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of message dictionaries
        """
        return self._sessions.get(session_id, [])

    def add_interaction(
        self, 
        session_id: str, 
        user_input: str, 
        ai_output: str
    ) -> None:
        """
        Add interaction to session history
        
        Args:
            session_id: Session identifier
            user_input: User message
            ai_output: AI response
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        
        self._sessions[session_id].append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        self._sessions[session_id].append({
            "role": "assistant",
            "content": ai_output,
            "timestamp": datetime.now().isoformat()
        })
        
        # Simple compaction logic: Keep last 10 messages
        if len(self._sessions[session_id]) > self._max_session_messages:
            self._sessions[session_id] = self._sessions[session_id][-10:]

    def store_patient_fact(self, patient_id: str, key: str, value: Any) -> None:
        """
        Store a fact about a patient
        
        Args:
            patient_id: Patient identifier
            key: Fact key
            value: Fact value
        """
        if patient_id not in self._facts:
            self._facts[patient_id] = {}
        self._facts[patient_id][key] = value
        self._facts[patient_id][f"{key}_timestamp"] = datetime.now().isoformat()

    def get_patient_facts(self, patient_id: str) -> Dict[str, Any]:
        """
        Get all facts for a patient
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            Dictionary of patient facts
        """
        return self._facts.get(patient_id, {}).copy()

    def clear_patient_facts(self, patient_id: str) -> bool:
        """
        Clear all facts for a patient
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            True if facts were cleared, False if patient not found
        """
        if patient_id in self._facts:
            del self._facts[patient_id]
            return True
        return False


# Singleton instance
memory_bank = MemoryBank()