# OJSM Scripts

## Citation Validator

A tool to detect hallucinated or invalid citations in article bibliographies.

### Purpose

Validates citations in BibTeX files by:
- Checking DOI validity using the CrossRef API
- Comparing metadata (title, year) between .bib file and registered DOI
- Flagging suspicious citations that may be AI-generated

### Usage

```bash
python scripts/citation_validator.py <path_to_bib_file> [--verbose]
```

### Examples

Check a single article:
```bash
python scripts/citation_validator.py Ohio-Journal-Spring-2026/6622\ Lozano/bibliography.bib
```

With verbose output:
```bash
python scripts/citation_validator.py Ohio-Journal-Spring-2026/6622\ Lozano/bibliography.bib --verbose
```

### Output

The script generates a report showing:
- **Valid** ✓ - Citation verified with matching metadata
- **Warning** ⚠ - Minor issues (missing DOI, year mismatch)
- **Suspicious** ⚠⚠ - Major metadata mismatches (title doesn't match)
- **Invalid** ✗ - DOI doesn't exist or can't be validated

### Requirements

- Python 3.6+
- No additional packages needed (uses standard library)
- Internet connection (queries CrossRef API)

### Note on Rate Limiting

The script includes polite delays between API calls. For large bibliographies, validation may take a few minutes.

### Future Enhancements

Planned features:
- OpenAlex API fallback for citations without DOIs
- AI-powered "Frankenstein citation" detection
- Batch processing of multiple files
- JSON/CSV export of results
