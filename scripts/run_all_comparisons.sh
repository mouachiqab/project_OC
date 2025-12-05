#!/bin/bash
# Script pour lancer toutes les expériences et comparer CP vs MILP
# Auteurs: Abdelkarim & Marin

echo "=========================================="
echo "LANCEMENT DE TOUTES LES EXPÉRIENCES"
echo "Comparaison CP vs MILP"
echo "=========================================="
echo ""

# Vérifier que les instances existent
if [ ! -d "data/instances" ] || [ -z "$(ls -A data/instances/*.json 2>/dev/null)" ]; then
    echo "⚠️  Aucune instance trouvée. Génération en cours..."
    python scripts/generate_instances.py
    echo ""
fi

# Compter les instances
TOTAL_INSTANCES=$(ls data/instances/*.json 2>/dev/null | wc -l | tr -d ' ')
echo "📊 Instances à traiter: $TOTAL_INSTANCES"
echo ""

# Lancer toutes les expériences
COUNTER=0
for instance in data/instances/*.json; do
    COUNTER=$((COUNTER + 1))
    BASENAME=$(basename "$instance")
    
    echo "[$COUNTER/$TOTAL_INSTANCES] ▶ $BASENAME"
    python scripts/run_experiment.py --instance "$instance" 2>&1 | grep -E "(Replication|SIMULATION COMPLETED|Total|Completed in|Results saved)"
    echo ""
done

echo "=========================================="
echo "✅ TOUTES LES EXPÉRIENCES TERMINÉES"
echo "=========================================="
echo ""

# Résumé des résultats
echo "📈 RÉSUMÉ DES RÉSULTATS:"
echo ""
ls -lh data/results/*_results.json | awk '{print $9}' | sort

echo ""
echo "🔍 Pour analyser les résultats:"
echo "   python scripts/analyze_results.py"
