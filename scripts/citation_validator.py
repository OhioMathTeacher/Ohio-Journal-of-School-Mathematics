#!/usr/bin/env python3
"""
Citation Validator for Ohio Journal of School Mathematics
Validates citations in BibTeX files to detect hallucinated or invalid references.
"""

import re
import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from urllib.parse import quote, urlencode
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# Import enhanced validation heuristics
try:
    from citation_enhancements import EnhancedValidator
    HAS_ENHANCEMENTS = True
except ImportError:
    HAS_ENHANCEMENTS = False


class CitationValidator:
    """Validates academic citations against CrossRef and OpenAlex APIs."""
    
    def __init__(self, verbose=False, use_ai=False, groq_api_key=None):
        self.verbose = verbose
        self.use_ai = use_ai
        self.groq_api_key = groq_api_key or os.environ.get('GROQ_API_KEY')
        self.crossref_api = "https://api.crossref.org/works/"
        self.openalex_api = "https://api.openalex.org/works"
        self.groq_api = "https://api.groq.com/openai/v1/chat/completions"
        self.rate_limit_delay = 0.1  # Polite delay between API calls
        
        if self.use_ai and not self.groq_api_key:
            print("Warning: AI analysis requested but no GROQ_API_KEY found")
            print("Set GROQ_API_KEY environment variable or pass --groq-key")
            self.use_ai = False
        
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
        """Validate a DOI using CrossRef API, with DataCite/arXiv fallback."""
        if not doi:
            return False, {'error': 'No DOI provided'}
        
        # Clean DOI
        doi = doi.strip().replace('https://doi.org/', '').replace('http://dx.doi.org/', '')
        
        # arXiv DOIs use DataCite, not CrossRef - check arXiv API directly
        arxiv_match = re.match(r'10\.48550/arXiv\.(\d+\.\d+)', doi)
        if arxiv_match:
            return self._validate_arxiv(arxiv_match.group(1))
        
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
            # CrossRef returned 404 - try DOI resolver as fallback
            # This catches DataCite DOIs (Zenodo, Figshare, Dryad, etc.)
            return self._validate_doi_resolver(doi)
        except Exception as e:
            return False, {'error': f'Unexpected error: {str(e)}'}
    
    def _validate_arxiv(self, arxiv_id: str) -> Tuple[bool, Dict]:
        """Validate an arXiv paper using the arXiv API."""
        url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
        
        try:
            time.sleep(self.rate_limit_delay)
            req = Request(url, headers={'User-Agent': 'OJSM-CitationValidator/1.0'})
            response = urlopen(req, timeout=10)
            data = response.read().decode('utf-8')
            
            # Check for valid entry (arXiv API returns XML)
            if '<title>' in data and 'Error' not in data.split('<title>')[1].split('</title>')[0]:
                # Extract title from XML
                title_match = re.search(r'<title[^>]*>(.*?)</title>', data, re.DOTALL)
                title = ''
                if title_match:
                    # Skip the feed title, get the entry title
                    titles = re.findall(r'<title[^>]*>(.*?)</title>', data, re.DOTALL)
                    title = titles[-1].strip() if len(titles) > 1 else titles[0].strip()
                
                # Extract authors
                authors = re.findall(r'<name>(.*?)</name>', data)
                
                return True, {
                    'title': [title],
                    'author': [{'given': a.split()[-1], 'family': ' '.join(a.split()[:-1])} for a in authors] if authors else [],
                    'source': 'arxiv',
                    'arxiv_id': arxiv_id
                }
            else:
                return False, {'error': f'arXiv paper {arxiv_id} not found'}
                
        except (URLError, HTTPError) as e:
            return False, {'error': f'arXiv API error: {str(e)}'}
        except Exception as e:
            return False, {'error': f'Unexpected error: {str(e)}'}
    
    def _validate_doi_resolver(self, doi: str) -> Tuple[bool, Dict]:
        """Fallback: check if a DOI resolves via doi.org (catches DataCite, Zenodo, Figshare, etc.)."""
        url = f"https://doi.org/api/handles/{doi}"
        
        try:
            time.sleep(self.rate_limit_delay)
            req = Request(url, headers={'User-Agent': 'OJSM-CitationValidator/1.0'})
            response = urlopen(req, timeout=10)
            data = json.loads(response.read().decode('utf-8'))
            
            # DOI handle API returns responseCode 1 for valid DOIs
            if data.get('responseCode') == 1:
                return True, {'source': 'doi_resolver', 'doi': doi}
            else:
                return False, {'error': 'DOI not found in any registry'}
                
        except (URLError, HTTPError):
            return False, {'error': f'DOI {doi} not found in CrossRef or DOI resolver'}
        except Exception as e:
            return False, {'error': f'Unexpected error: {str(e)}'}
    
    def search_openalex(self, title: str, author: str = None) -> Tuple[bool, Dict]:
        """Search OpenAlex for a publication by title and optional author."""
        if not title:
            return False, {'error': 'No title provided'}
        
        # Build search query
        query_parts = [f'title.search:"{title}"']
        if author:
            query_parts.append(f'author.search:"{author}"')
        
        params = {
            'filter': ','.join(query_parts),
            'per_page': 1,
            'mailto': 'editor@ohiomathjournal.org'  # Polite pool
        }
        
        url = f"{self.openalex_api}?{urlencode(params)}"
        
        try:
            time.sleep(self.rate_limit_delay)
            req = Request(url, headers={'User-Agent': 'OJSM-CitationValidator/1.0'})
            response = urlopen(req, timeout=10)
            data = json.loads(response.read().decode('utf-8'))
            
            results = data.get('results', [])
            if results:
                return True, results[0]
            else:
                return False, {'error': 'No matching publication found'}
                
        except (URLError, HTTPError) as e:
            return False, {'error': f'API error: {str(e)}'}
        except Exception as e:
            return False, {'error': f'Unexpected error: {str(e)}'}
    
    def analyze_with_ai(self, entry: Dict, metadata: Dict, suspicion_reasons: List[str] = None) -> Optional[Dict]:
        """Use Groq AI to analyze if citation looks like a Frankenstein citation."""
        if not self.use_ai or not self.groq_api_key:
            return None
        
        # Build enhanced prompt with more context
        if HAS_ENHANCEMENTS and suspicion_reasons:
            prompt = EnhancedValidator.improved_ai_prompt(entry, metadata, suspicion_reasons)
        else:
            # Fallback to original prompt
            fields = entry['fields']
            prompt = f"""Analyze this academic citation for signs of being AI-hallucinated or a "Frankenstein citation" (combining fragments from multiple real papers).

BibTeX Entry:
- Type: {entry['type']}
- Title: {fields.get('title', 'N/A')}
- Author(s): {fields.get('author', 'N/A')}
- Year: {fields.get('year', 'N/A')}
- Journal: {fields.get('journal', 'N/A')}
- DOI: {fields.get('doi', 'N/A')}

Verified Metadata (if found):
{json.dumps(metadata, indent=2) if metadata else 'None found'}

Does this citation show signs of being fabricated or assembled from fragments? Consider:
1. Are the components (title, author, journal, year) internally consistent?
2. Do they match any verified publication data?
3. Are there unusual patterns (generic titles, mismatched metadata)?

Respond with JSON: {{"is_suspicious": true/false, "confidence": 0-100, "reason": "brief explanation"}}"""

        payload = {
            "model": "llama-3.1-8b-instant",  # Fast, cheap Groq model
            "messages": [
                {"role": "system", "content": "You are an expert at detecting fabricated academic citations. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 200
        }
        
        try:
            time.sleep(self.rate_limit_delay)
            req = Request(
                self.groq_api,
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    'Authorization': f'Bearer {self.groq_api_key}',
                    'Content-Type': 'application/json'
                }
            )
            response = urlopen(req, timeout=30)
            data = json.loads(response.read().decode('utf-8'))
            
            # Extract AI response
            content = data['choices'][0]['message']['content']
            # Try to parse JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return None
                
        except Exception as e:
            if self.verbose:
                print(f"  AI analysis failed: {str(e)}")
            return None
    
    def check_citation(self, entry: Dict) -> Dict:
        """Check a single citation entry for issues."""
        result = {
            'key': entry['key'],
            'type': entry['type'],
            'fields': entry['fields'],
            'status': 'valid',
            'issues': [],
            'warnings': [],
            'ai_analysis': None,
            'suspicion_reasons': []
        }
        
        fields = entry['fields']
        doi = fields.get('doi', '')
        verified_metadata = None
        is_arxiv_doi = doi.lower().startswith('10.48550/arxiv.') if doi else False
        
        # ENHANCEMENT: Check for suspicious patterns first
        if HAS_ENHANCEMENTS:
            suspicion_warnings = EnhancedValidator.check_suspicious_patterns(entry)
            result['suspicion_reasons'].extend(suspicion_warnings)
            if suspicion_warnings:
                result['warnings'].extend(suspicion_warnings)
                if result['status'] == 'valid':
                    result['status'] = 'warning'
        
        # Try DOI validation first
        if doi:
            is_valid, doi_data = self.validate_doi(doi)
            
            if not is_valid:
                result['status'] = 'invalid'
                result['issues'].append(f"Invalid DOI: {doi_data.get('error', 'Unknown error')}")
                result['suspicion_reasons'].append("DOI validation failed")
                
                # AI analysis for invalid DOI
                if self.use_ai:
                    result['ai_analysis'] = self.analyze_with_ai(entry, None, result['suspicion_reasons'])
                
                return result
            
            verified_metadata = doi_data
            
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
        
        else:
            # No DOI - try OpenAlex search
            title = fields.get('title', '')
            author = fields.get('author', '')
            
            if title:
                found, openalex_data = self.search_openalex(title, author)
                
                if found:
                    verified_metadata = openalex_data
                    # OpenAlex match is acceptable evidence for sparse/no-DOI references.
                    if result['status'] == 'invalid':
                        result['status'] = 'warning'
                    elif result['status'] == 'valid':
                        result['status'] = 'valid'
                    
                    # Compare with OpenAlex data
                    oa_title = openalex_data.get('title', '').lower().strip()
                    bib_title = title.lower().strip()
                    
                    if oa_title and bib_title not in oa_title and oa_title not in bib_title:
                        result['warnings'].append(f"Title mismatch with OpenAlex")
                        result['status'] = 'suspicious'
                else:
                    result['warnings'].append('No DOI found and not in OpenAlex')
                    result['status'] = 'warning'
            else:
                # Only warn if metadata is too sparse to perform any meaningful lookup.
                has_author_or_venue = bool(fields.get('author') or fields.get('journal') or fields.get('booktitle'))
                if not has_author_or_venue:
                    result['warnings'].append('Insufficient metadata to validate (missing DOI/title/author/venue)')
                    result['status'] = 'warning'
        
        # ENHANCEMENT: Calculate similarity score if we have verified metadata
        if HAS_ENHANCEMENTS and verified_metadata:
            has_rich_metadata = bool(fields.get('title')) and bool(fields.get('author'))
            title_word_count = len(re.findall(r'\w+', fields.get('title', '')))
            if has_rich_metadata and not is_arxiv_doi and title_word_count >= 4:
                similarity = EnhancedValidator.calculate_metadata_similarity(fields, verified_metadata)
                if similarity < 0.30:  # More conservative threshold to reduce false positives.
                    result['warnings'].append(f"Low metadata similarity score: {similarity:.2f}")
                    result['suspicion_reasons'].append(f"Metadata similarity only {similarity:.2f}")
                    if result['status'] == 'valid':
                        result['status'] = 'warning'
        
        # AI analysis for suspicious/invalid citations
        if self.use_ai and result['status'] in ['suspicious', 'invalid', 'warning']:
            result['ai_analysis'] = self.analyze_with_ai(entry, verified_metadata, result['suspicion_reasons'])
        
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
                
                # Show enhanced suspicion reasons if available
                if detail.get('suspicion_reasons'):
                    print(f"  🔍 Suspicion flags:")
                    for reason in detail['suspicion_reasons']:
                        print(f"     - {reason}")
                
                # Show AI analysis if available
                if detail.get('ai_analysis'):
                    ai = detail['ai_analysis']
                    confidence = ai.get('confidence', 0)
                    is_suspicious = ai.get('is_suspicious', False)
                    reason = ai.get('reason', 'No reason provided')
                    hallucination_type = ai.get('hallucination_type', 'unknown')
                    red_flags = ai.get('red_flags', [])
                    
                    if is_suspicious:
                        print(f"  🤖 AI Analysis: LIKELY HALLUCINATED ({confidence}% confidence)")
                        if hallucination_type != 'none':
                            print(f"     Type: {hallucination_type}")
                    else:
                        print(f"  🤖 AI Analysis: Appears legitimate ({confidence}% confidence)")
                    print(f"     Reason: {reason}")
                    if red_flags:
                        print(f"     Red flags: {', '.join(red_flags)}")
        else:
            print("\n✓ No issues found! All citations appear valid.")
        
        print("\n" + "=" * 70)


def main():
    """Main entry point."""
    if len(sys.argv) < 2 or '--help' in sys.argv or '-h' in sys.argv:
        print("OJSM Citation Validator - Detect hallucinated academic references")
        print("\nUsage: python3 citation_validator.py <path_to_bib_file> [options]")
        print("\nOptions:")
        print("  --verbose, -v       Show detailed progress")
        print("  --ai                Enable AI-powered Frankenstein citation detection")
        print("  --groq-key KEY      Groq API key (or set GROQ_API_KEY env var)")
        print("\nExamples:")
        print("  Basic validation:")
        print("    python3 citation_validator.py bibliography.bib")
        print("\n  With OpenAlex fallback for non-DOI citations:")
        print("    python3 citation_validator.py bibliography.bib --verbose")
        print("\n  With AI analysis (requires Groq API key):")
        print("    export GROQ_API_KEY='your-key-here'")
        print("    python3 citation_validator.py bibliography.bib --ai")
        print("\nGet free Groq API key at: https://console.groq.com/")
        sys.exit(0)
    
    # Parse arguments
    bib_file = Path(sys.argv[1])
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    use_ai = '--ai' in sys.argv
    
    # Get Groq API key if provided
    groq_key = None
    for i, arg in enumerate(sys.argv):
        if arg == '--groq-key' and i + 1 < len(sys.argv):
            groq_key = sys.argv[i + 1]
            break
    
    if not bib_file.exists():
        print(f"Error: File not found: {bib_file}")
        sys.exit(1)
    
    validator = CitationValidator(verbose=verbose, use_ai=use_ai, groq_api_key=groq_key)
    results = validator.validate_file(bib_file)
    validator.print_report(results)
    
    # Exit with error code if invalid citations found
    if results['invalid'] > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
