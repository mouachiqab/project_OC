"""
Classe Patient pour la simulation des urgences
Auteur: Abdelkarim Mouachiq
"""
import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class Priority(Enum):
    """Niveaux de priorité selon l'échelle de triage"""
    P1_RESUSCITATION = 1
    P2_EMERGENT = 2
    P3_URGENT = 3
    P4_LESS_URGENT = 4
    P5_NON_URGENT = 5

@dataclass
class PatientState:
    """État d'un patient à un moment donné"""
    current_priority: Priority
    arrival_time: float
    start_treatment_time: Optional[float] = None
    end_treatment_time: Optional[float] = None

class Patient:
    """Patient dans le système des urgences"""
    
    _id_counter = 0
    
    def __init__(self, arrival_time: float, initial_priority: Priority):
        """
        Initialise un patient
        
        Args:
            arrival_time: Temps d'arrivée en minutes
            initial_priority: Priorité initiale (P1-P5)
        """
        Patient._id_counter += 1
        self.id = Patient._id_counter
        self.arrival_time = arrival_time
        self.priority = initial_priority
        self.initial_priority = initial_priority
        
        # Temps de traitement (distribution log-normale)
        mean_treatment = self._get_mean_treatment_time()
        self.treatment_duration = np.random.lognormal(
            mean=np.log(mean_treatment),
            sigma=0.5
        )
        
        # État du patient
        self.state = PatientState(
            current_priority=initial_priority,
            arrival_time=arrival_time
        )
        
        # Ressources assignées
        self.assigned_doctor = None
        self.assigned_bed = None
        
    def _get_mean_treatment_time(self) -> float:
        """Retourne la durée moyenne de traitement selon la priorité"""
        treatment_times = {
            Priority.P1_RESUSCITATION: 120,  # 2 heures
            Priority.P2_EMERGENT: 90,        # 1.5 heures
            Priority.P3_URGENT: 60,          # 1 heure
            Priority.P4_LESS_URGENT: 45,     # 45 minutes
            Priority.P5_NON_URGENT: 30       # 30 minutes
        }
        return treatment_times[self.priority]
    
    def get_max_wait_time(self) -> float:
        """Temps d'attente maximum recommandé selon priorité (minutes)"""
        max_wait_times = {
            Priority.P1_RESUSCITATION: 0,
            Priority.P2_EMERGENT: 15,
            Priority.P3_URGENT: 30,
            Priority.P4_LESS_URGENT: 60,
            Priority.P5_NON_URGENT: 120
        }
        return max_wait_times[self.priority]
    
    def get_wait_time(self, current_time: float) -> float:
        """Calcule le temps d'attente actuel"""
        if self.state.start_treatment_time is not None:
            return self.state.start_treatment_time - self.arrival_time
        return current_time - self.arrival_time
    
    def deteriorate(self):
        """Détérioration de l'état du patient (passe à priorité supérieure)"""
        if self.priority.value > 1:
            new_priority_value = self.priority.value - 1
            self.priority = Priority(new_priority_value)
            self.state.current_priority = self.priority
            print(f"Patient {self.id} deteriorated to {self.priority.name}")
    
    def start_treatment(self, current_time: float, doctor_id: int, bed_id: int):
        """Commence le traitement"""
        self.state.start_treatment_time = current_time
        self.assigned_doctor = doctor_id
        self.assigned_bed = bed_id
    
    def end_treatment(self, current_time: float):
        """Termine le traitement"""
        self.state.end_treatment_time = current_time
    
    def __repr__(self):
        return f"Patient({self.id}, {self.priority.name}, wait={self.get_wait_time(0):.1f}min)"
