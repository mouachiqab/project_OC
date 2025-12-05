# Script pour lancer toutes les expériences et comparer CP vs MILP

echo "LANCEMENT DE TOUTES LES EXPÉRIENCES"
echo "Comparaison CP vs MILP"
echo ""

# Compter les instances
TOTAL_INSTANCES=$(ls data/instances/*.json 2>/dev/null | wc -l | tr -d ' ')
echo "Instances a traiter: $TOTAL_INSTANCES"
echo ""

# Lancer toutes les expériences
COUNTER=0
for instance in data/instances/*.json; do
    COUNTER=$((COUNTER + 1))
    BASENAME=$(basename "$instance")
    
    echo "[$COUNTER/$TOTAL_INSTANCES] $BASENAME"
    python scripts/run_experiment.py --instance "$instance" 2>&1 | grep -E "(Replication|SIMULATION COMPLETED|Total|Completed in|Results saved)"
    echo ""
done

echo "EXPERIENCES TERMINEES"
echo ""

ls -lh data/results/*_results.json | awk '{print $9}' | sort

echo ""
echo "   python scripts/analyze_results.py"
