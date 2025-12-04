"""
Interface commune pour les optimiseurs
Auteurs: Abdelkarim & Marin
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple

class OptimizerInterface(ABC):
    """Interface abstraite pour tous les optimiseurs"""
    
    @abstractmethod
    def optimize(self, state: Dict) -> List[Tuple[int, int, int]]:
        """
        Optimise l'affectation des patients aux ressources
        
        Args:
            state: État actuel du système

        """
        pass
    
    @abstractmethod
    def get_solver_stats(self, *args) -> Dict:
        """Retourne les statistiques du solveur"""
        pass

def create_optimizer(method: str, **kwargs):
    """
    Factory pour créer un optimiseur
    
    Args:
        method: 'CP' ou 'MILP'
        **kwargs: Arguments pour l'optimiseur
    """
    if method.upper() == 'CP':
        from .cp_model import CPOptimizer
        return CPOptimizer(**kwargs)
    elif method.upper() == 'MILP':
        from .milp_model import MILPOptimizer
        return MILPOptimizer(**kwargs)
    else:
        raise ValueError(f"Unknown optimization method: {method}")
