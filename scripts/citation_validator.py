#!/usr/bin/env python3
"""
Citation Validator for Ohio Journal of School Mathematics
Validates citations in BibTeX files to detect hallucinated or invalid references.
"""

import re
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import quote
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


class CitationValidator:
    """Validates academic citations against CrossRef and OpenAlex APIs."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.crossref_api = "https://api.crossref.org/works/"
        self.openalex_api = "https://api.openalex.org/works/"
        self.rate_limit_delay = 0.1  # Polite delay between API calls
        
    def parse_bibtex(self, filepath: Path) -> List[Dict]:
        """Parse a BibTeX file and extract citation entries."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match BibTeX entries
        entry_pattern = r'@(\w+)\{([^,]+),\s*(.*?)\n\}'
        entries = []
        
        for match in re.finditer(entry_pattern, content, re.DOTALL):
            entry_type = match.group(1)
            cite_key = match.group(2)
            fields_str = match.group(3)
            
            # Parse fields
            fields = {}
            field_pattern = r'(\w+)\s*=\s*[{"](.*?)[}"]'
            for field_match in re.finditer(field_pattern, fields_str, re.DOTALL):
                field_name = field_match.group(1).lower()
                field_value = field_match.group(2).strip()
                fields[field_name] = field_value
            
            entries.append({
                'type': entry_type,
                'key': cite_key,
                'fields': fields
            })
        
        return entries
    
    def validate_doi(self, doi: str) -> Tuple[bool, Dict]:
        """Validate a DOI using CrossRef API."""
        if not doi:
            return False, {'error': 'No DOI provided'}
        
        # Clean DOI
        doi = doi.strip().replace('https://doi.org/', '').replace('http://dx.doi.org/', '')
        
        url = f"{self.crossref_api}{quote(doi)}"
        
        try:
            time.sleep(self.rate_limit_delay)  # Be polite to API
            req = Request(url, headers={'User-Agent': 'OJSM-CitationValidator/1.0'})
            response = urlopen(req, timeout=10)
            data = json.loads(response.read().decode('utf-8'))
            
            if data.get('status') == 'ok':
                return True, data.get('message', {})
            else:
                return False, {'error': 'DOI not found'}
                
        except (URLError, HTTPError) as e:
            return False, {'error': f'API error: {str(e)}'}
        except Exception as e:
            return False, {'error': f'Unexpected error: {str(e)}'}
    
    def check_citation(self, entry: Dict) -> Dict:
        """Check a single citation entry for issues."""
        result = {
            'key': entry['key'],
            'type': entry['type'],
            'status': 'valid',
            'issues': [],
            'warnings': []
        }
        
        fields = entry['fields']
        doi = fields.get('doi', '')
        
        # Check for DOI
        if not doi:
            result['warnings'].append('No DOI found')
            result['status'] = 'warning'
            return result
        
        # Validate DOI
        is_valid, doi_data = self.validate_doi(doi)
        
        if not is_valid:
            result['status'] = 'invalid'
            result['issues'].append(f"Invalid DOI: {doi_data.get('error', 'Unknown error')}")
            return result
        
        # Compare metadata
        if 'title' in fields and 'title' in doi_data:
            bib_title = fields['title'].lower().strip()
            doi_title = ' '.join(doi_data['title']).lower().strip() if isinstance(doi_data['title'], list) else doi_data['title'].lower().strip()
            
            # Simple similarity check
            if bib_title not in doi_title and doi_title not in bib_title:
                result['warnings'].append(f"Title mismatch: BibTeX='{fields['title'][:50]}...' vs DOI='{doi_data.get('title', [''])[0][:50]}...'")
                result['status'] = 'suspicious'
        
        # Check year
        if 'year' in fields and 'published' in doi_data:
            bib_year = fields['year']
            doi_year = str(doi_data['published'].get('date-parts', [[None]])[0][0])
            
            if bib_year != doi_year:
                result['warnings'].append(f"Year mismatch: BibTeX={bib_year} vs DOI={doi_year}")
                if result['status'] == 'valid':
                    result['status'] = 'warning'
        
        return result
    
    def validate_file(self, filepath: Path) -> Dict:
        """Validate all citations in a BibTeX file."""
        print(f"\nValidating citations in: {filepath}")
        print("=" * 70)
        
        entries = self.parse_bibtex(filepath)
        print(f"Found {len(entries)} citations to check\n")
        
        results = {
            'file': str(filepath),
            'total': len(entries),
            'valid': 0,
            'warnings': 0,
            'suspicious': 0,
            'invalid': 0,
            'details': []
        }
        
        for i, entry in enumerate(entries, 1):
            if self.verbose:
                print(f"Checking [{i}/{len(entries)}]: {entry['key']}")
            
            check_result = self.check_citation(entry)
            results['details'].append(check_result)
            
            # Update counts
            if check_result['status'] == 'valid':
                results['valid'] += 1
            elif check_result['status'] == 'warning':
                results['warnings'] += 1
            elif check_result['status'] == 'suspicious':
                results['suspicious'] += 1
            elif check_result['status'] == 'invalid':
                results['invalid'] += 1
        
        return results
    
    def print_report(self, results: Dict):
        """Print a human-readable report."""
        print("\n" + "=" * 70)
        print("CITATION VALIDATION REPORT")
        print("=" * 70)
        print(f"File: {results['file']}")
        print(f"Total citations: {results['total']}")
        print(f"  ✓ Valid: {results['valid']}")
        print(f"  ⚠ Warnings: {results['warnings']}")
        print(f"  ⚠⚠ Suspicious: {results['suspicious']}")
        print(f"  ✗ Invalid: {results['invalid']}")
        
        # Show details for problematic citations
        problematic = [d for d in results['details'] if d['status'] != 'valid']
        
        if problematic:
            print("\n" + "-" * 70)
            print("ISSUES FOUND:")
            print("-" * 70)
            
            for detail in problematic:
                print(f"\n[{detail['status'].upper()}] {detail['key']}")
                for issue in detail['issues']:
                    print(f"  ✗ {issue}")
                for warning in detail['warnings']:
                    print(f"  ⚠ {warning}")
        else:
            print("\n✓ No issues found! All citations appear valid.")
        
        print("\n" + "=" * 70)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python citation_validator.py <path_to_bib_file> [--verbose]")
        print("\nExample:")
        print("  python citation_validator.py ../Ohio-Journal-Spring-2026/6622\\ Lozano/bibliography.bib")
        sys.exit(1)
    
    bib_file = Path(sys.argv[1])
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    
    if not bib_file.exists():
        print(f"Error: File not found: {bib_file}")
        sys.exit(1)
    
    validator = CitationValidator(verbose=verbose)
    results = validator.validate_file(bib_file)
    validator.print_report(results)
    
    # Exit with error code if invalid citations found
    if results['invalid'] > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
