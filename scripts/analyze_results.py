"""
Script d'analyse et visualisation des résultats
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from visualization.results_plotter import ResultsPlotter

def main():
    parser = argparse.ArgumentParser(description='Analyze and visualize experiment results')
    parser.add_argument('--results-dir', type=str, default='data/results',
                       help='Directory containing result JSON files')
    parser.add_argument('--output-dir', type=str, default='data/results/plots',
                       help='Directory for output plots')
    parser.add_argument('--table-only', action='store_true',
                       help='Generate only summary table')
    
    args = parser.parse_args()
    
    print("RESULTS ANALYSIS")
    
    plotter = ResultsPlotter(args.results_dir)
    
    if args.table_only:
        plotter.generate_summary_table(Path(args.output_dir) / 'summary_table.csv')
    else:
        plotter.generate_all_plots(args.output_dir)
        plotter.generate_summary_table(Path(args.output_dir) / 'summary_table.csv')

if __name__ == '__main__':
    main()
