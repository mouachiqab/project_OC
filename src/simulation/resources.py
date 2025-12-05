"""
Gestion des ressources médicales (médecins, civières)
"""
import simpy
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Doctor:
    """Médecin dans le service des urgences"""
    id: int
    name: str
    is_available: bool = True
    current_patient: Optional[int] = None
    total_patients_treated: int = 0
    total_treatment_time: float = 0.0
    
    def assign_patient(self, patient_id: int):
        """Assigne un patient au médecin"""
        self.is_available = False
        self.current_patient = patient_id
        self.total_patients_treated += 1
    
    def release_patient(self, treatment_time: float):
        """Libère le médecin après traitement"""
        self.is_available = True
        self.current_patient = None
        self.total_treatment_time += treatment_time
    
    def get_utilization_rate(self, total_time: float) -> float:
        """Calcule le taux d'utilisation du médecin"""
        if total_time == 0:
            return 0.0
        return (self.total_treatment_time / total_time) * 100

@dataclass
class Bed:
    """Civière dans le service des urgences"""
    id: int
    is_available: bool = True
    current_patient: Optional[int] = None
    total_occupancy_time: float = 0.0
    
    def assign_patient(self, patient_id: int):
        """Assigne un patient à la civière"""
        self.is_available = False
        self.current_patient = patient_id
    
    def release_patient(self, occupancy_time: float):
        """Libère la civière"""
        self.is_available = True
        self.current_patient = None
        self.total_occupancy_time += occupancy_time
    
    def get_occupancy_rate(self, total_time: float) -> float:
        """Calcule le taux d'occupation de la civière"""
        if total_time == 0:
            return 0.0
        return (self.total_occupancy_time / total_time) * 100

class EmergencyResources:
    """Gestion centralisée des ressources des urgences"""
    
    def __init__(self, env: simpy.Environment, num_doctors: int, num_beds: int):
        """
        Initialise les ressources
        
        Args:
            env: Environnement SimPy
            num_doctors: Nombre de médecins
            num_beds: Nombre de civières
        """
        self.env = env
        
        # Créer les médecins
        self.doctors: List[Doctor] = [
            Doctor(id=i, name=f"Dr. {chr(65+i)}")
            for i in range(num_doctors)
        ]
        
        # Créer les civières
        self.beds: List[Bed] = [
            Bed(id=i)
            for i in range(num_beds)
        ]
        
        # Ressources SimPy
        self.doctor_resource = simpy.Resource(env, capacity=num_doctors)
        self.bed_resource = simpy.Resource(env, capacity=num_beds)
    
    def get_available_doctors(self) -> List[Doctor]:
        """Retourne la liste des médecins disponibles"""
        return [doc for doc in self.doctors if doc.is_available]
    
    def get_available_beds(self) -> List[Bed]:
        """Retourne la liste des civières disponibles"""
        return [bed for bed in self.beds if bed.is_available]
    
    def get_doctor_by_id(self, doctor_id: int) -> Optional[Doctor]:
        """Récupère un médecin par son ID"""
        for doctor in self.doctors:
            if doctor.id == doctor_id:
                return doctor
        return None
    
    def get_bed_by_id(self, bed_id: int) -> Optional[Bed]:
        """Récupère une civière par son ID"""
        for bed in self.beds:
            if bed.id == bed_id:
                return bed
        return None
    
    def get_statistics(self) -> Dict:
        """Retourne les statistiques d'utilisation des ressources"""
        total_time = self.env.now
        
        return {
            'doctors': {
                'count': len(self.doctors),
                'available': len(self.get_available_doctors()),
                'utilization_rates': [
                    doc.get_utilization_rate(total_time) 
                    for doc in self.doctors
                ],
                'total_patients_treated': sum(
                    doc.total_patients_treated for doc in self.doctors
                )
            },
            'beds': {
                'count': len(self.beds),
                'available': len(self.get_available_beds()),
                'occupancy_rates': [
                    bed.get_occupancy_rate(total_time) 
                    for bed in self.beds
                ]
            }
        }
    
    def __repr__(self):
        available_docs = len(self.get_available_doctors())
        available_beds = len(self.get_available_beds())
        return f"Resources(Doctors: {available_docs}/{len(self.doctors)}, Beds: {available_beds}/{len(self.beds)})"
