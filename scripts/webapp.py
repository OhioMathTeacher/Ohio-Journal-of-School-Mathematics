#!/usr/bin/env python3
"""
Citation Validator Web Application
Simple Flask app for detecting hallucinated citations via web interface
"""

import os
import json
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string
from citation_validator import CitationValidator

app = Flask(__name__)

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Citation Validator - Detect AI-Hallucinated References</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .nature-badge {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            margin-top: 10px;
            font-size: 0.9em;
        }
        
        .main-content {
            padding: 40px;
        }
        
        .section {
            margin-bottom: 30px;
        }
        
        .section h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
        }
        
        textarea {
            width: 100%;
            min-height: 300px;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            resize: vertical;
            transition: border-color 0.3s;
        }
        
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .file-upload {
            border: 2px dashed #667eea;
            border-radius: 10px;
            padding: 30px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 20px;
        }
        
        .file-upload:hover {
            background: #f8f9ff;
            border-color: #764ba2;
        }
        
        .file-upload input {
            display: none;
        }
        
        .button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        
        .button:active {
            transform: translateY(0);
        }
        
        .button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .checkbox-group {
            margin: 15px 0;
        }
        
        .checkbox-group label.ai-toggle {
            display: flex;
            align-items: center;
            cursor: pointer;
            font-size: 0.95em;
            color: #555;
            padding: 8px 12px;
            background: #f8f9fa;
            border-radius: 8px;
            transition: background 0.2s;
        }
        
        .checkbox-group label.ai-toggle:hover {
            background: #e9ecef;
        }
        
        .checkbox-group input[type="checkbox"] {
            margin-right: 10px;
            width: 18px;
            height: 18px;
            cursor: pointer;
        }
        
        .help-icon {
            margin-left: 8px;
            color: #667eea;
            font-size: 1.1em;
            cursor: help;
        }
        
        .options-section {
            background: #fafbfc;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .api-key-section {
            display: none;
            margin-top: 15px;
            padding: 15px;
            background: white;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            animation: slideDown 0.3s ease;
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .api-key-input-group {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .api-key-input {
            flex: 1;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            transition: border-color 0.3s;
        }
        
        .api-key-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .clear-key-btn {
            background: #dc3545;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            transition: background 0.2s;
        }
        
        .clear-key-btn:hover {
            background: #c82333;
        }
        
        .get-key-link {
            padding: 10px 15px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-size: 0.85em;
            white-space: nowrap;
            transition: background 0.2s;
        }
        
        .get-key-link:hover {
            background: #5568d3;
        }
        
        .api-help-text {
            font-size: 0.85em;
            color: #666;
            margin-top: 8px;
            margin-bottom: 0;
        }
        
        .security-notice {
            background: rgba(40,120,60,0.12);
            border: 1px solid rgba(40,120,60,0.25);
            padding: 10px 12px;
            border-radius: 6px;
            font-size: 0.85em;
            color: #2d5a2d;
            margin-bottom: 14px;
            line-height: 1.5;
        }
        
        #results {
            margin-top: 30px;
            display: none;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        
        .stat-card.valid {
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        }
        
        .stat-card.warning {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        }
        
        .stat-card.suspicious {
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        }
        
        .stat-card.invalid {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }
        
        .stat-value {
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 1em;
            opacity: 0.8;
        }
        
        .citation-list {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
        }
        
        .citation-item {
            background: white;
            border-left: 4px solid #e0e0e0;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
        }
        
        .citation-item.valid {
            border-left-color: #28a745;
        }
        
        .citation-item.warning {
            border-left-color: #ffc107;
        }
        
        .citation-item.suspicious {
            border-left-color: #ff6b6b;
        }
        
        .citation-item.invalid {
            border-left-color: #dc3545;
        }
        
        .citation-key {
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 10px;
            color: #333;
        }
        
        .citation-status {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 5px;
            font-size: 0.8em;
            margin-left: 10px;
        }
        
        .citation-status.valid {
            background: #28a745;
            color: white;
        }
        
        .citation-status.warning {
            background: #ffc107;
            color: #333;
        }
        
        .citation-status.suspicious {
            background: #ff6b6b;
            color: white;
        }
        
        .citation-status.invalid {
            background: #dc3545;
            color: white;
        }
        
        .issue-list {
            margin-top: 10px;
        }
        
        .issue-item {
            padding: 5px 0;
            font-size: 0.9em;
        }
        
        .issue-item.error {
            color: #dc3545;
        }
        
        .issue-item.warning {
            color: #ff6b6b;
        }
        
        .ai-analysis {
            background: #f0f4ff;
            border: 1px solid #667eea;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
        }
        
        .ai-analysis strong {
            color: #667eea;
        }
        
        #loading {
            display: none;
            text-align: center;
            padding: 40px;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .export-buttons {
            margin-top: 20px;
            display: flex;
            gap: 10px;
        }
        
        .export-buttons button {
            flex: 1;
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
        }
        
        footer {
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
        }
        
        footer a {
            color: #667eea;
            text-decoration: none;
        }
        
        footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 Citation Validator</h1>
            <p>Detect AI-Hallucinated References in Scientific Literature</p>
            <div class="nature-badge">
                📄 In response to Nature article (April 8, 2026)
            </div>
        </header>
        
        <div class="main-content">
            <div class="section">
                <h2>Upload or Paste BibTeX</h2>
                
                <div class="file-upload" id="fileUpload">
                    <input type="file" id="fileInput" accept=".bib,.txt" onchange="handleFileUpload(event)">
                    <p>📁 Click to upload .bib file or drag and drop</p>
                    <p style="font-size: 0.9em; opacity: 0.7;">Supports BibTeX (.bib) files</p>
                </div>
                
                <textarea id="bibInput" placeholder="Or paste your BibTeX entries here...

Example:
@article{AuthorYear,
  title={Paper Title},
  author={Author, First and Author, Second},
  journal={Journal Name},
  year={2025},
  doi={10.1234/example}
}"></textarea>
            </div>
            
            <div class="section options-section">
                <div class="checkbox-group">
                    <label class="ai-toggle">
                        <input type="checkbox" id="useAI">
                        <span>🤖 Enable AI-powered analysis</span>
                        <span class="help-icon" title="Uses Llama 3.1 via free Groq API to detect 'Frankenstein citations'">ⓘ</span>
                    </label>
                </div>
                
                <div id="apiKeySection" class="api-key-section">
                    <div class="security-notice">
                        🔒 <strong>Privacy:</strong> Your API key never leaves your browser. AI analysis happens client-side.
                    </div>
                    <div class="api-key-input-group">
                        <input type="password" id="apiKey" placeholder="Groq API key (gsk_...)" class="api-key-input">
                        <button class="clear-key-btn" onclick="clearApiKey()" title="Clear saved key">✕</button>
                        <a href="https://console.groq.com/" target="_blank" class="get-key-link">Get free key →</a>
                    </div>
                    <p class="api-help-text">
                        🔒 Key saved locally in browser • Free tier: 30 req/min, 7,000/day
                    </p>
                </div>
            </div>
            
            <div class="section" style="text-align: center;">
                <button class="button" onclick="validateCitations()">
                    🔍 Validate Citations
                </button>
            </div>
            
            <div id="loading">
                <div class="spinner"></div>
                <p>Validating citations... This may take a moment.</p>
            </div>
            
            <div id="results">
                <div class="section">
                    <h2>Results</h2>
                    
                    <div class="stats" id="stats"></div>
                    
                    <div class="citation-list" id="citationList"></div>
                    
                    <div class="export-buttons">
                        <button class="button" onclick="exportHTML()">📄 Export HTML Report</button>
                        <button class="button" onclick="exportJSON()">📊 Export JSON</button>
                        <button class="button" onclick="exportCSV()">📈 Export CSV</button>
                    </div>
                </div>
            </div>
        </div>
        
        <footer>
            <p><strong>Built to protect academic integrity</strong></p>
            <p>Free, open-source tool | <a href="https://github.com/OhioMathTeacher/Ohio-Journal-of-School-Mathematics" target="_blank">View on GitHub</a></p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                Developed in response to Nature's report that 2-6% of 2025 papers contain hallucinated citations
            </p>
        </footer>
    </div>
    
    <script>
        let validationResults = null;
        
        // Load saved API key from localStorage
        window.addEventListener('DOMContentLoaded', function() {
            const savedKey = localStorage.getItem('groqApiKey');
            if (savedKey) {
                document.getElementById('apiKey').value = savedKey;
            }
        });
        
        // Save API key to localStorage when changed
        document.getElementById('apiKey').addEventListener('input', function() {
            if (this.value) {
                localStorage.setItem('groqApiKey', this.value);
            }
        });
        
        // Toggle AI section with smooth animation
        document.getElementById('useAI').addEventListener('change', function() {
            const apiSection = document.getElementById('apiKeySection');
            apiSection.style.display = this.checked ? 'block' : 'none';
        });
        
        // Clear API key
        function clearApiKey() {
            if (confirm('Clear saved API key from browser?')) {
                localStorage.removeItem('groqApiKey');
                document.getElementById('apiKey').value = '';
            }
        }
        
        // File upload handling
        function handleFileUpload(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('bibInput').value = e.target.result;
                };
                reader.readAsText(file);
            }
        }
        
        // Drag and drop
        const fileUpload = document.getElementById('fileUpload');
        fileUpload.addEventListener('dragover', (e) => {
            e.preventDefault();
            fileUpload.style.background = '#f8f9ff';
        });
        
        fileUpload.addEventListener('dragleave', () => {
            fileUpload.style.background = '';
        });
        
        fileUpload.addEventListener('drop', (e) => {
            e.preventDefault();
            fileUpload.style.background = '';
            const file = e.dataTransfer.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('bibInput').value = e.target.result;
                };
                reader.readAsText(file);
            }
        });
        
        fileUpload.addEventListener('click', () => {
            document.getElementById('fileInput').click();
        });
        
        // Validate citations
        async function validateCitations() {
            const bibText = document.getElementById('bibInput').value.trim();
            if (!bibText) {
                alert('Please paste BibTeX or upload a file');
                return;
            }
            
            const useAI = document.getElementById('useAI').checked;
            const apiKey = document.getElementById('apiKey').value;
            
            if (useAI && !apiKey) {
                alert('Please provide a Groq API key for AI analysis');
                return;
            }
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').style.display = 'none';
            
            try {
                // Step 1: Server-side validation (CrossRef + OpenAlex)
                // ✅ API key NEVER sent to server!
                const response = await fetch('/validate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        bibtex: bibText
                    })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    alert('Error: ' + data.error);
                    return;
                }
                
                // Step 2: Client-side AI analysis (if enabled)
                // ✅ Groq API called directly from browser with user's key!
                if (useAI) {
                    await addAIAnalysis(data.details, apiKey);
                }
                
                validationResults = data;
                displayResults(data);
                
            } catch (error) {
                alert('Validation failed: ' + error.message);
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
        
        // Client-side AI analysis - API key stays in browser!
        async function addAIAnalysis(citations, apiKey) {
            for (const citation of citations) {
                // Only analyze suspicious/invalid/warning citations
                if (['suspicious', 'invalid', 'warning'].includes(citation.status)) {
                    citation.ai_analysis = await analyzeWithGroq(citation, apiKey);
                }
            }
        }
        
        // Call Groq API directly from browser
        async function analyzeWithGroq(citation, apiKey) {
            try {
                const suspicionReasons = [
                    ...(citation.issues || []),
                    ...(citation.warnings || [])
                ].join('; ');
                
                const prompt = `You are analyzing a potentially hallucinated academic citation.

Citation details:
- Type: ${citation.type}
- Key: ${citation.key}
- Suspicious because: ${suspicionReasons}

Is this likely a "Frankenstein citation" (AI-hallucinated, mixing real authors/titles/journals into non-existent papers)?

Respond with JSON only:
{
  "is_suspicious": true/false,
  "confidence": 0-100,
  "reason": "brief explanation"
}`;

                const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${apiKey}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        model: 'llama-3.1-8b-instant',
                        messages: [
                            {
                                role: 'system',
                                content: 'You are an expert at detecting fabricated academic citations. Respond only with valid JSON.'
                            },
                            {
                                role: 'user',
                                content: prompt
                            }
                        ],
                        temperature: 0.1,
                        max_tokens: 200
                    })
                });
                
                if (!response.ok) {
                    console.error('Groq API error:', response.status);
                    return null;
                }
                
                const data = await response.json();
                const content = data.choices[0].message.content;
                
                // Parse JSON from response
                const jsonMatch = content.match(/\{.*\}/s);
                if (jsonMatch) {
                    return JSON.parse(jsonMatch[0]);
                }
                return null;
                
            } catch (error) {
                console.error('AI analysis failed:', error);
                return null;
            }
        }
        
        // Display results
        function displayResults(data) {
            // Show results section
            document.getElementById('results').style.display = 'block';
            
            // Update stats
            const stats = document.getElementById('stats');
            stats.innerHTML = `
                <div class="stat-card valid">
                    <div class="stat-value">${data.valid}</div>
                    <div class="stat-label">✓ Valid</div>
                </div>
                <div class="stat-card warning">
                    <div class="stat-value">${data.warnings}</div>
                    <div class="stat-label">⚠ Warnings</div>
                </div>
                <div class="stat-card suspicious">
                    <div class="stat-value">${data.suspicious}</div>
                    <div class="stat-label">⚠⚠ Suspicious</div>
                </div>
                <div class="stat-card invalid">
                    <div class="stat-value">${data.invalid}</div>
                    <div class="stat-label">✗ Invalid</div>
                </div>
            `;
            
            // Display citations
            const citationList = document.getElementById('citationList');
            citationList.innerHTML = '<h3>Citation Details</h3>';
            
            data.details.forEach(citation => {
                const div = document.createElement('div');
                div.className = `citation-item ${citation.status}`;
                
                let html = `
                    <div class="citation-key">
                        ${citation.key}
                        <span class="citation-status ${citation.status}">${citation.status.toUpperCase()}</span>
                    </div>
                `;
                
                if (citation.issues && citation.issues.length > 0) {
                    html += '<div class="issue-list">';
                    citation.issues.forEach(issue => {
                        html += `<div class="issue-item error">✗ ${issue}</div>`;
                    });
                    html += '</div>';
                }
                
                if (citation.warnings && citation.warnings.length > 0) {
                    html += '<div class="issue-list">';
                    citation.warnings.forEach(warning => {
                        html += `<div class="issue-item warning">⚠ ${warning}</div>`;
                    });
                    html += '</div>';
                }
                
                if (citation.ai_analysis) {
                    const ai = citation.ai_analysis;
                    html += `
                        <div class="ai-analysis">
                            <strong>🤖 AI Analysis:</strong>
                            ${ai.is_suspicious ? 
                                `LIKELY HALLUCINATED (${ai.confidence}% confidence)` :
                                `Appears legitimate (${ai.confidence}% confidence)`
                            }<br>
                            <em>${ai.reason}</em>
                        </div>
                    `;
                }
                
                div.innerHTML = html;
                citationList.appendChild(div);
            });
            
            // Scroll to results
            document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
        }
        
        // Export functions
        function exportHTML() {
            const html = document.getElementById('results').innerHTML;
            const blob = new Blob([`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Citation Validation Report</title>
                    <style>${document.querySelector('style').textContent}</style>
                </head>
                <body>
                    <div class="container">
                        <header><h1>Citation Validation Report</h1></header>
                        <div class="main-content">${html}</div>
                    </div>
                </body>
                </html>
            `], { type: 'text/html' });
            downloadFile(blob, 'citation-report.html');
        }
        
        function exportJSON() {
            const blob = new Blob([JSON.stringify(validationResults, null, 2)], { type: 'application/json' });
            downloadFile(blob, 'citation-report.json');
        }
        
        function exportCSV() {
            let csv = 'Key,Status,Issues,Warnings\\n';
            validationResults.details.forEach(citation => {
                const issues = citation.issues ? citation.issues.join('; ') : '';
                const warnings = citation.warnings ? citation.warnings.join('; ') : '';
                csv += `"${citation.key}","${citation.status}","${issues}","${warnings}"\\n`;
            });
            const blob = new Blob([csv], { type: 'text/csv' });
            downloadFile(blob, 'citation-report.csv');
        }
        
        function downloadFile(blob, filename) {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Serve the main page."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/validate', methods=['POST'])
def validate():
    """Validate citations endpoint - NO AI analysis (done client-side)."""
    try:
        data = request.json
        bibtex = data.get('bibtex', '')
        
        if not bibtex:
            return jsonify({'error': 'No BibTeX content provided'}), 400
        
        # Save to temporary file
        temp_file = Path('/tmp/temp_citations.bib')
        temp_file.write_text(bibtex)
        
        # Validate WITHOUT AI (AI happens client-side for privacy)
        validator = CitationValidator(
            verbose=False,
            use_ai=False,  # Never use AI server-side
            groq_api_key=None
        )
        
        results = validator.validate_file(temp_file)
        
        # Clean up
        temp_file.unlink()
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🔍 Citation Validator Web App")
    print("="*70)
    print("\nStarting server...")
    print("\n📱 Open in your browser:")
    print("   http://localhost:5000")
    print("\n💡 To share with others, deploy to:")
    print("   - Heroku (free tier)")
    print("   - Vercel")
    print("   - PythonAnywhere")
    print("\n Press Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
