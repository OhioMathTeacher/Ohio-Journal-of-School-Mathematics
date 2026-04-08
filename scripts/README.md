# OJSM Scripts

## Citation Validator

A multi-tiered tool to detect hallucinated or invalid citations in article bibliographies.

### Purpose

Validates citations in BibTeX files using three methods:
1. **DOI Validation** - Checks DOI validity using the CrossRef API
2. **OpenAlex Fallback** - Searches OpenAlex for citations without DOIs
3. **AI Analysis** (optional) - Uses Groq AI to detect "Frankenstein citations"

Compares metadata (title, year) between .bib file and verified sources to flag suspicious citations.

### Usage

Basic validation (CrossRef + OpenAlex):
```bash
python3 scripts/citation_validator.py <path_to_bib_file> [options]
```

### Options

- `--verbose, -v` - Show detailed progress for each citation
- `--ai` - Enable AI-powered Frankenstein citation detection (requires Groq API key)
- `--groq-key KEY` - Provide Groq API key (or set `GROQ_API_KEY` environment variable)
- `--help, -h` - Show help message

### Examples

Basic validation with CrossRef and OpenAlex:
```bash
python3 scripts/citation_validator.py Ohio-Journal-Spring-2026/6622\ Lozano/bibliography.bib
```

Verbose output:
```bash
python3 scripts/citation_validator.py bibliography.bib --verbose
```

With AI analysis (requires Groq API key):
```bash
export GROQ_API_KEY='your-groq-api-key-here'
python3 scripts/citation_validator.py bibliography.bib --ai --verbose
```

### Output

The script generates a report showing:
- **Valid** ✓ - Citation verified with matching metadata
- **Warning** ⚠ - Minor issues (missing DOI, year mismatch)
- **Suspicious** ⚠⚠ - Major metadata mismatches (title doesn't match)
- **Invalid** ✗ - DOI doesn't exist or can't be validated
- **AI Analysis** 🤖 - AI assessment of fabrication likelihood (when --ai enabled)

### How It Works

1. **Parse BibTeX** - Extracts citation entries from .bib file
2. **Validate DOIs** - Checks each DOI against CrossRef database
3. **OpenAlex Fallback** - For citations without DOIs, searches OpenAlex by title/author
4. **Metadata Comparison** - Compares BibTeX fields with verified publication data
5. **AI Analysis** (optional) - For suspicious/invalid citations, AI analyzes patterns

### Requirements

- Python 3.6+
- No additional packages needed (uses standard library)
- Internet connection (queries CrossRef and OpenAlex APIs)
- Groq API key (optional, for AI features - free tier available at https://console.groq.com/)

### Getting a Groq API Key (Free)

1. Visit https://console.groq.com/
2. Sign up for free account
3. Generate API key
4. Set environment variable: `export GROQ_API_KEY='your-key'`

### Note on Rate Limiting

The script includes polite delays between API calls. For large bibliographies:
- CrossRef/OpenAlex validation: ~0.1s per citation
- With AI analysis: ~0.5s per suspicious citation

### Future Enhancements

Planned features:
- Batch processing of multiple files at once
- JSON/CSV export of results for tracking
- Integration with OJSM workflow automation
- Custom AI prompts for domain-specific detection
