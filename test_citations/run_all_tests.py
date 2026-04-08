#!/usr/bin/env python3
"""
Test Runner for Citation Validator
Runs validation on all test citations and compares against ground truth
Calculates precision, recall, F1, false positive/negative rates
"""

import sys
import json
import subprocess
import time
from pathlib import Path
from collections import defaultdict
import argparse

def run_validator(bib_file, validator_script='../scripts/citation_validator.py'):
    """Run citation validator on a BibTeX file"""
    try:
        result = subprocess.run(
            ['python3', validator_script, str(bib_file)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Parse output to identify invalid/warning citations
        output = result.stdout + result.stderr
        
        # Parse the summary section
        import re
        total_match = re.search(r'Total citations:\s*(\d+)', output)
        valid_match = re.search(r'✓ Valid:\s*(\d+)', output)
        warnings_match = re.search(r'⚠ Warnings:\s*(\d+)', output)
        suspicious_match = re.search(r'⚠⚠ Suspicious:\s*(\d+)', output)
        invalid_match = re.search(r'✗ Invalid:\s*(\d+)', output)
        
        total = int(total_match.group(1)) if total_match else 0
        valid = int(valid_match.group(1)) if valid_match else 0
        warnings = int(warnings_match.group(1)) if warnings_match else 0
        suspicious = int(suspicious_match.group(1)) if suspicious_match else 0
        invalid = int(invalid_match.group(1)) if invalid_match else 0
        
        # Only suspicious and invalid are truly "problematic"
        # Warnings are FYI only (e.g., missing DOI is normal for arXiv)
        problematic = suspicious + invalid
        
        return {
            'file': str(bib_file),
            'total': total,
            'valid': valid,
            'warnings': warnings,
            'suspicious': suspicious,
            'invalid': invalid,
            'problematic': problematic,
            'output': output
        }
    
    except subprocess.TimeoutExpired:
        return {'file': str(bib_file), 'error': 'timeout'}
    except Exception as e:
        return {'file': str(bib_file), 'error': str(e)}

def load_ground_truth(test_dirs):
    """Load ground truth labels from all test directories"""
    ground_truth = {}
    
    for test_dir in test_dirs:
        test_path = Path(test_dir)
        
        # Automatically determine expected results baseon directory structure
        if 'real_citations' in str(test_path):
            expected = 'VALID'
        elif 'false_negative' in str(test_path):
            expected = 'INVALID'
        elif 'false_positive' in str(test_path):
            expected = 'VALID'  # Real citations that might be incorrectly flagged
        else:
            expected = 'UNKNOWN'
        
        # Find all .bib files
        if test_path.exists():
            for bib_file in test_path.rglob('*.bib'):
                ground_truth[str(bib_file)] = expected
    
    return ground_truth

def evaluate_results(results, ground_truth):
    """Calculate precision, recall, F1, etc."""
    
    # Confusion matrix
    tp = 0  # True positive: Correctly identified as VALID
    tn = 0  # True negative: Correctly identified as INVALID
    fp = 0  # False positive: Real citation flagged as INVALID
    fn = 0  # False negative: Fake citation marked as VALID
    
    for result in results:
        file_path = result['file']
        expected = ground_truth.get(file_path, 'UNKNOWN')
        
        if expected == 'UNKNOWN':
            continue
        
        # Determine what validator said
        # If any citations have warnings/suspicious/invalid, consider file as problematic
        has_issues = result.get('problematic', 0) > 0
        
        if expected == 'VALID':
            if not has_issues:
                tp += 1  # Correctly said it's valid
            else:
                fp += 1  # Incorrectly flagged valid citation
        
        elif expected == 'INVALID':
            if has_issues:
                tn += 1  # Correctly caught fake
            else:
                fn += 1  # Fake slipped through
    
    # Calculate metrics
    total = tp + tn + fp + fn
    
    accuracy = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0  # False positive rate
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0  # False negative rate
    
    return {
        'confusion_matrix': {
            'true_positive': tp,
            'true_negative': tn,
            'false_positive': fp,
            'false_negative': fn,
            'total': total
        },
        'metrics': {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'false_positive_rate': fpr,
            'false_negative_rate': fnr
        }
    }

def print_report(evaluation, results):
    """Print human-readable test report"""
    
    cm = evaluation['confusion_matrix']
    metrics = evaluation['metrics']
    
    print("\n" + "="*70)
    print("CITATION VALIDATOR TEST RESULTS")
    print("="*70)
    
    print("\nConfusion Matrix:")
    print(f"  True Positives (TP):   {cm['true_positive']:4d}  (Real citations correctly validated)")
    print(f"  True Negatives (TN):   {cm['true_negative']:4d}  (Fake citations correctly caught)")
    print(f"  False Positives (FP):  {cm['false_positive']:4d}  (Real citations incorrectly flagged) ⚠️")
    print(f"  False Negatives (FN):  {cm['false_negative']:4d}  (Fake citations that slipped through) ⚠️")
    print(f"  Total:                 {cm['total']:4d}")
    
    print("\nPerformance Metrics:")
    print(f"  Accuracy:              {metrics['accuracy']:.2%}")
    print(f"  Precision:             {metrics['precision']:.2%}  (When we say it's real, how often are we right?)")
    print(f"  Recall:                {metrics['recall']:.2%}  (Of all real citations, how many did we validate?)")
    print(f"  F1 Score:              {metrics['f1_score']:.2%}  (Harmonic mean of precision and recall)")
    print(f"  False Positive Rate:   {metrics['false_positive_rate']:.2%}  (Real citations incorrectly flagged)")
    print(f"  False Negative Rate:   {metrics['false_negative_rate']:.2%}  (Fake citations that slipped through)")
    
    print("\n" + "="*70)
    
    # Interpretation
    print("\nInterpretation:")
    if metrics['false_positive_rate'] < 0.05:
        print("✓ Low false positive rate - won't annoy users with false alarms")
    else:
        print(f"⚠️ High false positive rate ({metrics['false_positive_rate']:.1%}) - may flag too many real citations")
    
    if metrics['false_negative_rate'] < 0.10:
        print("✓ Low false negative rate - catches most fake citations")
    else:
        print(f"⚠️ High false negative rate ({metrics['false_negative_rate']:.1%}) - many fakes slipping through")
    
    if metrics['f1_score'] > 0.90:
        print("✓ Excellent overall performance (F1 > 0.90)")
    elif metrics['f1_score'] > 0.80:
        print("✓ Good overall performance (F1 > 0.80)")
    else:
        print("⚠️ Performance needs improvement")
    
    print("="*70 + "\n")

def main():
    parser = argparse.ArgumentParser(description='Run citation validator tests')
    parser.add_argument('--validator', default='../scripts/citation_validator.py',
                       help='Path to citation validator script')
    parser.add_argument('--test-dirs', nargs='+',
                       default=['real_citations/', 'false_negative_tests/', 'false_positive_tests/'],
                       help='Directories containing test citations')
    parser.add_argument('--limit', type=int, help='Limit number of files to test (for quick testing)')
    parser.add_argument('--output', default='test_results.json', help='Output file for results')
    
    args = parser.parse_args()
    
    print("Citation Validator Test Runner")
    print("=" * 70)
    print(f"Validator: {args.validator}")
    print(f"Test directories: {', '.join(args.test_dirs)}\n")
    
    # Load ground truth
    print("Loading ground truth labels...")
    ground_truth = load_ground_truth(args.test_dirs)
    print(f"✓ Loaded {len(ground_truth)} test cases\n")
    
    # Find all .bib files to test
    test_files = []
    for test_dir in args.test_dirs:
        test_path = Path(test_dir)
        if test_path.exists():
            test_files.extend(test_path.rglob('*.bib'))
    
    if args.limit:
        test_files = test_files[:args.limit]
    
    print(f"Testing {len(test_files)} files...\n")
    
    # Run validator on each file
    results = []
    start_time = time.time()
    
    for i, bib_file in enumerate(test_files, 1):
        print(f"[{i}/{len(test_files)}] Testing {bib_file.name}... ", end='', flush=True)
        
        result = run_validator(bib_file, args.validator)
        results.append(result)
        
        if 'error' in result:
            print(f"✗ {result['error']}")
        else:
            prob = result.get('problematic', 0)
            total = result.get('total', 0)
            warn = result.get('warnings', 0)
            susp = result.get('suspicious', 0)
            inv = result.get('invalid', 0)
            print(f"✓ ({prob} issues: {warn}W {susp}S {inv}I / {total} total)")
    
    elapsed = time.time() - start_time
    print(f"\n✓ Completed {len(results)} tests in {elapsed:.1f} seconds")
    print(f"  Average: {elapsed/len(results):.2f} seconds per file\n")
    
    # Evaluate results
    print("Evaluating results against ground truth...")
    evaluation = evaluate_results(results, ground_truth)
    
    # Print report
    print_report(evaluation, results)
    
    # Save detailed results
    output_data = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'validator': args.validator,
        'test_dirs': args.test_dirs,
        'total_files': len(test_files),
        'elapsed_seconds': elapsed,
        'evaluation': evaluation,
        'results': results
    }
    
    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"✓ Detailed results saved to {args.output}")

if __name__ == '__main__':
    main()
