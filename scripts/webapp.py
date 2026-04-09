#!/usr/bin/env python3
"""
Citation Validator Web Application
Simple Flask app for detecting hallucinated citations via web interface
"""

import os
import json
import requests
from pathlib import Path
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from citation_validator import CitationValidator

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# HTML Template
HTML_TEMPLATE = r'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Citation Validator - Detect AI-Hallucinated References</title>
    <style>
        :root {
            --bg: #f5f7fb;
            --card: #ffffff;
            --text: #142033;
            --muted: #58657a;
            --line: #d7deea;
            --primary: #1f6feb;
            --valid: #138a42;
            --warning: #8a5b00;
            --suspicious: #be2f2f;
            --invalid: #be2f2f;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(180deg, #eef2f9 0%, #f8fafc 100%);
            color: var(--text);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 980px;
            margin: 0 auto;
            padding: 24px;
        }
        
        header {
            margin-bottom: 24px;
        }
        
        header h1 {
            font-size: 28px;
            margin-bottom: 4px;
            color: var(--text);
        }
        
        header p {
            color: var(--muted);
            font-size: 1em;
        }
        
        .nature-badge {
            display: inline-block;
            background: var(--card);
            border: 1px solid var(--line);
            padding: 4px 12px;
            border-radius: 6px;
            margin-top: 8px;
            font-size: 0.85em;
            color: var(--muted);
        }
        
        .main-content {
            /* no extra padding needed */
        }
        
        .section {
            margin-bottom: 18px;
        }
        
        .section h2 {
            color: var(--text);
            margin-bottom: 10px;
            font-size: 18px;
        }
        
        textarea {
            width: 100%;
            min-height: 250px;
            padding: 14px;
            border: 1px solid var(--line);
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            resize: vertical;
            transition: border-color 0.2s;
            background: var(--card);
        }
        
        textarea:focus {
            outline: none;
            border-color: var(--primary);
        }
        
        .file-upload {
            border: 2px dashed var(--line);
            border-radius: 8px;
            padding: 24px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
            margin-bottom: 14px;
            background: var(--card);
        }
        
        .file-upload:hover {
            border-color: var(--primary);
            background: #f0f4ff;
        }
        
        .file-upload input {
            display: none;
        }
        
        .button {
            background: var(--primary);
            color: white;
            border: none;
            padding: 10px 28px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .button:hover {
            background: #1a5cc7;
        }
        
        .button:active {
            background: #174ea6;
        }
        
        .button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .checkbox-group {
            margin: 10px 0;
        }
        
        .checkbox-group label.ai-toggle {
            display: flex;
            align-items: center;
            cursor: pointer;
            font-size: 14px;
            color: var(--text);
            padding: 0;
        }
        
        .checkbox-group input[type="checkbox"] {
            margin-right: 8px;
            width: 16px;
            height: 16px;
            cursor: pointer;
        }
        
        .security-notice {
            background: rgba(40,120,60,0.08);
            border: 1px solid rgba(40,120,60,0.2);
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 13px;
            color: #2d5a2d;
            margin-bottom: 12px;
            line-height: 1.5;
        }
        
        /* AI Settings Button */
        .ai-settings-btn {
            font-size: 13px;
            font-weight: 600;
            padding: 8px 16px;
            border: 1px solid var(--line);
            border-radius: 8px;
            background: var(--card);
            color: var(--muted);
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        
        .ai-settings-btn:hover {
            border-color: var(--primary);
            color: var(--primary);
        }
        
        .ai-settings-btn.ai-active {
            border-color: var(--valid);
            color: var(--valid);
            background: rgba(19,138,66,0.04);
        }
        
        .ai-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: currentColor;
            display: inline-block;
        }
        
        /* AI Settings Modal */
        .ai-modal-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.65);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        
        .ai-modal-overlay.open {
            display: flex;
        }
        
        .ai-modal {
            background: #1e2738;
            border: 1px solid rgba(212,168,67,0.2);
            border-radius: 16px;
            padding: 32px;
            width: 600px;
            max-width: calc(100vw - 40px);
            box-shadow: 0 24px 64px rgba(0,0,0,0.6);
            animation: modalSlideIn 0.3s ease;
        }
        
        @keyframes modalSlideIn {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .ai-modal h2 {
            font-family: 'Crimson Pro', serif;
            font-weight: 400;
            color: #e8dcc8;
            font-size: 1.8em;
            margin-bottom: 24px;
        }
        
        .ai-provider-cards {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-bottom: 24px;
        }
        
        .ai-provider-card {
            background: rgba(255,255,255,0.04);
            border: 2px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 16px;
            cursor: pointer;
            transition: all 0.2s;
            position: relative;
        }
        
        .ai-provider-card:hover {
            background: rgba(255,255,255,0.07);
            border-color: rgba(212,168,67,0.3);
            transform: translateY(-2px);
        }
        
        .ai-provider-card.selected {
            border-color: #d4a843;
            background: rgba(212,168,67,0.1);
        }
        
        .ai-card-title {
            font-family: 'DM Sans', sans-serif;
            font-weight: 600;
            font-size: 0.95em;
            color: #e8dcc8;
            margin-bottom: 6px;
        }
        
        .ai-card-desc {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.8em;
            color: #8a8a7a;
            line-height: 1.5;
        }
        
        .ai-card-badge {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.7em;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            margin-top: 10px;
        }
        
        .ai-badge-paid {
            background: rgba(122,59,16,0.35);
            color: #d4956a;
        }
        
        .ai-badge-free {
            background: rgba(40,120,60,0.35);
            color: #7ec88a;
        }
        
        .ai-badge-none {
            background: rgba(90,90,90,0.35);
            color: #999;
        }
        
        .ai-key-section {
            margin-bottom: 24px;
            display: none;
        }
        
        .ai-key-section input {
            width: 100%;
            padding: 12px 14px;
            background: rgba(255,255,255,0.06);
            border: 2px solid rgba(212,168,67,0.2);
            border-radius: 8px;
            color: #e8dcc8;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            outline: none;
            margin-bottom: 8px;
        }
        
        .ai-key-section input:focus {
            border-color: rgba(212,168,67,0.5);
        }
        
        .ai-key-hint {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.8em;
            color: #6a6a5a;
            line-height: 1.6;
        }
        
        .ai-key-hint a {
            color: #d4a843;
            text-decoration: none;
        }
        
        .ai-key-hint a:hover {
            text-decoration: underline;
        }
        
        .ai-modal-actions {
            display: flex;
            gap: 12px;
        }
        
        .ai-modal-actions button {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.9em;
            font-weight: 500;
            padding: 12px 24px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .am-save {
            background: #d4a843;
            color: #1e2738;
            flex: 1;
        }
        
        .am-save:hover {
            background: #e0b84e;
            transform: translateY(-1px);
        }
        
        .am-cancel {
            background: rgba(255,255,255,0.08);
            color: #9a9083;
        }
        
        .am-cancel:hover {
            background: rgba(255,255,255,0.14);
        }
        
        #results {
            margin-top: 18px;
            display: none;
        }
        
        .stats {
            display: flex;
            gap: 12px;
            margin-bottom: 18px;
        }
        
        .stat-card {
            flex: 1;
            background: var(--card);
            border: 1px solid var(--line);
            padding: 14px;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-card.valid {
            border-left: 3px solid var(--valid);
        }
        
        .stat-card.warning {
            border-left: 3px solid #c09000;
        }
        
        .stat-card.suspicious {
            border-left: 3px solid #d46a00;
        }
        
        .stat-card.invalid {
            border-left: 3px solid var(--invalid);
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 2px;
            color: var(--text);
        }
        
        .stat-label {
            font-size: 13px;
            color: var(--muted);
        }
        
        .citation-list {
            /* no wrapper background needed */
        }
        
        .citation-item {
            background: var(--card);
            border: 1px solid var(--line);
            border-left: 3px solid var(--line);
            padding: 14px 16px;
            margin-bottom: 10px;
            border-radius: 8px;
            box-shadow: 0 1px 4px rgba(20,32,51,0.04);
        }
        
        .citation-item.valid {
            border-left-color: var(--valid);
        }
        
        .citation-item.warning {
            border-left-color: #c09000;
        }
        
        .citation-item.suspicious {
            border-left-color: #d46a00;
        }
        
        .citation-item.invalid {
            border-left-color: var(--invalid);
        }
        
        .citation-key {
            font-weight: 600;
            font-size: 15px;
            margin-bottom: 6px;
            color: var(--text);
        }
        
        .citation-status {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            margin-left: 8px;
        }
        
        .citation-status.valid {
            background: rgba(19,138,66,0.1);
            color: var(--valid);
        }
        
        .citation-status.warning {
            background: rgba(138,91,0,0.1);
            color: var(--warning);
        }
        
        .citation-status.suspicious {
            background: rgba(190,47,47,0.1);
            color: var(--suspicious);
        }
        
        .citation-status.invalid {
            background: rgba(190,47,47,0.12);
            color: var(--invalid);
        }
        
        .issue-list {
            margin-top: 8px;
        }
        
        .issue-item {
            padding: 3px 0;
            font-size: 13px;
            color: var(--muted);
        }
        
        .issue-item.error {
            color: var(--invalid);
        }
        
        .issue-item.warning {
            color: var(--warning);
        }
        
        .ai-analysis {
            background: rgba(31,111,235,0.04);
            border: 1px solid rgba(31,111,235,0.15);
            padding: 10px 12px;
            border-radius: 6px;
            margin-top: 8px;
            font-size: 13px;
        }
        
        .ai-analysis strong {
            color: var(--primary);
        }
        
        #loading {
            display: none;
            text-align: center;
            padding: 30px;
        }
        
        .spinner {
            border: 3px solid var(--line);
            border-top: 3px solid var(--primary);
            border-radius: 50%;
            width: 36px;
            height: 36px;
            animation: spin 1s linear infinite;
            margin: 0 auto 14px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .export-buttons {
            margin-top: 14px;
            display: flex;
            gap: 8px;
        }
        
        .export-buttons button {
            flex: 1;
            background: var(--card);
            color: var(--primary);
            border: 1px solid var(--primary);
            font-size: 13px;
            padding: 8px 14px;
        }
        
        .export-buttons button:hover {
            background: rgba(31,111,235,0.05);
        }
        
        footer {
            margin-top: 32px;
            padding: 18px;
            text-align: center;
            color: var(--muted);
            font-size: 13px;
        }
        
        footer a {
            color: var(--primary);
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
            <h1>Citation Validator</h1>
            <p>Detect AI-hallucinated references in scientific literature</p>
            <div class="nature-badge">
                In response to Nature article (April 8, 2026)
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
            
            <div class="section" style="display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; background: var(--card); border: 1px solid var(--line); border-radius: 8px;">
                <div>
                    <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; font-size: 14px;">
                        <input type="checkbox" id="useAI" style="width: 16px; height: 16px; cursor: pointer;">
                        <span>Enable AI-powered analysis</span>
                    </label>
                    <p style="font-size: 12px; color: var(--muted); margin-top: 4px; margin-left: 24px;">
                        Detect Frankenstein citations using AI
                    </p>
                </div>
                <button class="ai-settings-btn" id="aiBtn" onclick="openAIModal()">
                    <span class="ai-dot"></span>
                    <span id="aiBtnLabel">Configure AI</span>
                </button>
            </div>
            
            <div class="section" style="text-align: center;">
                <button class="button" onclick="validateCitations()">
                    Validate Citations
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
                        <button class="button" onclick="exportHTML()">Export HTML</button>
                        <button class="button" onclick="exportJSON()">Export JSON</button>
                        <button class="button" onclick="exportCSV()">Export CSV</button>
                    </div>
                </div>
            </div>
        </div>
        
        <footer>
            <p><strong>Built to protect academic integrity</strong></p>
            <p>Free, open-source | <a href="https://github.com/OhioMathTeacher/Ohio-Journal-of-School-Mathematics" target="_blank">View on GitHub</a></p>
            <p style="margin-top: 6px;">
                Developed in response to Nature's report that 2–6% of 2025 papers contain hallucinated citations
            </p>
        </footer>
    </div>
    
    <!-- AI Settings Modal -->
    <div class="ai-modal-overlay" id="aiModalOverlay" onclick="if(event.target===this)closeAIModal()">
        <div class="ai-modal">
            <h2>AI Provider Settings</h2>
            
            <div class="ai-provider-cards">
                <div class="ai-provider-card" id="card-anthropic" onclick="selectProvider('anthropic')">
                    <div class="ai-card-title">Anthropic Claude</div>
                    <div class="ai-card-desc">Claude Sonnet 4 — Most powerful for nuanced analysis</div>
                    <div class="ai-card-badge ai-badge-paid">Paid Key</div>
                </div>
                
                <div class="ai-provider-card" id="card-gemini" onclick="selectProvider('gemini')">
                    <div class="ai-card-title">Google Gemini</div>
                    <div class="ai-card-desc">Gemini 2.5 Flash — Free tier (use personal Gmail)</div>
                    <div class="ai-card-badge ai-badge-free">Free</div>
                </div>
                
                <div class="ai-provider-card" id="card-groq" onclick="selectProvider('groq')">
                    <div class="ai-card-title">Groq (Llama 3.3)</div>
                    <div class="ai-card-desc">Fast & free — No Google account needed</div>
                    <div class="ai-card-badge ai-badge-free">Free</div>
                </div>
                
                <div class="ai-provider-card" id="card-openai" onclick="selectProvider('openai')">
                    <div class="ai-card-title">OpenAI GPT-4</div>
                    <div class="ai-card-desc">GPT-4o — Fast, accurate, widely used</div>
                    <div class="ai-card-badge ai-badge-paid">Paid Key</div>
                </div>
            </div>
            
            <div class="ai-key-section" id="aiKeySection">
                <input type="password" id="aiKeyInput" placeholder="Paste your API key here…" 
                       autocomplete="off" spellcheck="false"
                       onkeydown="if(event.key==='Enter')saveAISettings();if(event.key==='Escape')closeAIModal()">
                <div class="ai-key-hint" id="aiKeyHint">
                    🔒 Stored only in your browser • Never sent to our server • Never in source code
                </div>
            </div>
            
            <div class="ai-modal-actions">
                <button class="am-save" onclick="saveAISettings()">Save</button>
                <button class="am-cancel" onclick="closeAIModal()">Cancel</button>
            </div>
        </div>
    </div>
    
    <script>
        let validationResults = null;
        
        // ═══ AI PROVIDER MANAGEMENT (pattern from close-reader) ═══
        const PROVIDER_KEY    = 'cv_provider';
        const ANTHROPIC_KEY   = 'cv_anthropic_key';
        const GEMINI_KEY      = 'cv_gemini_key';
        const GROQ_KEY        = 'cv_groq_key';
        const OPENAI_KEY      = 'cv_openai_key';
        
        let _modalProvider = '';
        
        function getProvider() {
            return localStorage.getItem(PROVIDER_KEY) || '';
        }
        
        function getStoredKey(provider) {
            if (provider === 'anthropic') return localStorage.getItem(ANTHROPIC_KEY) || '';
            if (provider === 'gemini')    return localStorage.getItem(GEMINI_KEY) || '';
            if (provider === 'groq')      return localStorage.getItem(GROQ_KEY) || '';
            if (provider === 'openai')    return localStorage.getItem(OPENAI_KEY) || '';
            return '';
        }
        
        function updateAIBtn() {
            const btn   = document.getElementById('aiBtn');
            const label = document.getElementById('aiBtnLabel');
            const p = getProvider();
            
            if (p === 'anthropic' && getStoredKey('anthropic')) {
                btn.classList.add('ai-active');
                label.textContent = 'AI: Claude ✓';
            } else if (p === 'gemini' && getStoredKey('gemini')) {
                btn.classList.add('ai-active');
                label.textContent = 'AI: Gemini ✓';
            } else if (p === 'groq' && getStoredKey('groq')) {
                btn.classList.add('ai-active');
                label.textContent = 'AI: Groq ✓';
            } else if (p === 'openai' && getStoredKey('openai')) {
                btn.classList.add('ai-active');
                label.textContent = 'AI: OpenAI ✓';
            } else {
                btn.classList.remove('ai-active');
                label.textContent = 'Configure AI';
            }
        }
        
        function openAIModal() {
            _modalProvider = getProvider() || 'groq'; // Default to Groq (free)
            _refreshModalCards();
            _refreshKeySection();
            document.getElementById('aiModalOverlay').classList.add('open');
            setTimeout(() => document.getElementById('aiKeyInput').focus(), 100);
        }
        
        function closeAIModal() {
            document.getElementById('aiModalOverlay').classList.remove('open');
        }
        
        function selectProvider(p) {
            _modalProvider = p;
            _refreshModalCards();
            _refreshKeySection();
            setTimeout(() => document.getElementById('aiKeyInput').focus(), 50);
        }
        
        function _refreshModalCards() {
            ['anthropic', 'gemini', 'groq', 'openai'].forEach(p => {
                document.getElementById('card-' + p).classList.toggle('selected', p === _modalProvider);
            });
        }
        
        function _refreshKeySection() {
            const section = document.getElementById('aiKeySection');
            const input   = document.getElementById('aiKeyInput');
            const hint    = document.getElementById('aiKeyHint');
            
            section.style.display = 'block';
            const stored = getStoredKey(_modalProvider);
            input.value = stored ? '••••••••••••••••' : '';
            
            if (_modalProvider === 'anthropic') {
                input.placeholder = 'sk-ant-…';
                hint.innerHTML = '🔒 Stored only in your browser • Never shared • Get key at <a href="https://console.anthropic.com" target="_blank">console.anthropic.com</a>';
            } else if (_modalProvider === 'gemini') {
                input.placeholder = 'AIza…';
                hint.innerHTML = '🔒 Get free key at <a href="https://aistudio.google.com/app/apikey" target="_blank">aistudio.google.com</a> — <strong style="color:#d4a843">use personal Gmail, not school account</strong>';
            } else if (_modalProvider === 'groq') {
                input.placeholder = 'gsk_…';
                hint.innerHTML = '🔒 Get free key at <a href="https://console.groq.com/keys" target="_blank">console.groq.com</a> — any email works, no Google account needed';
            } else if (_modalProvider === 'openai') {
                input.placeholder = 'sk-…';
                hint.innerHTML = '🔒 Get key at <a href="https://platform.openai.com/api-keys" target="_blank">platform.openai.com</a> — Stored only in your browser';
            }
        }
        
        function saveAISettings() {
            const val = document.getElementById('aiKeyInput').value.trim();
            localStorage.setItem(PROVIDER_KEY, _modalProvider);
            
            if (val && !val.startsWith('•')) {
                const storageKey = _modalProvider === 'anthropic' ? ANTHROPIC_KEY
                                 : _modalProvider === 'gemini'    ? GEMINI_KEY
                                 : _modalProvider === 'groq'      ? GROQ_KEY
                                 :                                  OPENAI_KEY;
                localStorage.setItem(storageKey, val);
            }
            
            closeAIModal();
            updateAIBtn();
        }
        
        // Initialize on page load
        window.addEventListener('DOMContentLoaded', function() {
            updateAIBtn();
        });
        
        // ═══ FILE UPLOAD HANDLING ═══
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
            const provider = getProvider();
            const apiKey = getStoredKey(provider);
            
            if (useAI && (!provider || !apiKey)) {
                openAIModal();
                alert('Please configure an AI provider first');
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
                // ✅ AI API called directly from browser with user's key!
                if (useAI) {
                    await addAIAnalysis(data.details, provider, apiKey);
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
        async function addAIAnalysis(citations, provider, apiKey) {
            for (const citation of citations) {
                // Only analyze suspicious/invalid/warning citations
                if (['suspicious', 'invalid', 'warning'].includes(citation.status)) {
                    citation.ai_analysis = await analyzeWithAI(citation, provider, apiKey);
                }
            }
        }
        
        // Call AI API directly from browser (supports 4 providers)
        async function analyzeWithAI(citation, provider, apiKey) {
            try {
                const suspicionReasons = [
                    ...(citation.issues || []),
                    ...(citation.warnings || [])
                ].join('; ');
                
                // Build citation details from BibTeX fields
                const fields = citation.fields || {};
                const fieldLines = Object.entries(fields)
                    .filter(([k,v]) => v && v.trim())
                    .map(([k,v]) => '  ' + k + ': ' + v)
                    .join('\\n');

                const prompt = 'Analyze this academic citation and determine if it is REAL or FABRICATED.\\n\\n'
                    + 'BibTeX fields:\\n'
                    + (fieldLines || '  (very sparse - only key and type available)') + '\\n\\n'
                    + 'Our automated checks found these notes:\\n'
                    + (suspicionReasons || '(none)') + '\\n\\n'
                    + 'IMPORTANT INSTRUCTIONS:\\n'
                    + '- A citation is NOT hallucinated just because it lacks a title or DOI in the BibTeX entry. Many real references are entered with sparse metadata.\\n'
                    + '- Low metadata similarity warnings occur when our BibTeX entry is incomplete - this does NOT mean the paper is fake.\\n'
                    + '- No DOI and no title for OpenAlex search means we could not LOOK IT UP, not that it does not exist.\\n'
                    + '- Only flag as suspicious if there are genuine red flags: impossible combinations of author + journal + year, non-existent journals, or implausible metadata.\\n'
                    + '- When in doubt, assume the citation is REAL.\\n\\n'
                    + 'Respond with JSON only:\\n'
                    + '{"is_suspicious": true/false, "confidence": 0-100, "reason": "brief explanation"}';

                if (provider === 'anthropic') {
                    const res = await fetch('https://api.anthropic.com/v1/messages', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'x-api-key': apiKey,
                            'anthropic-version': '2023-06-01',
                            'anthropic-dangerous-allow-browser': 'true'
                        },
                        body: JSON.stringify({
                            model: 'claude-sonnet-4-20250514',
                            max_tokens: 300,
                            messages: [{ role: 'user', content: prompt }]
                        })
                    });
                    if (!res.ok) return null;
                    const data = await res.json();
                    const content = data.content?.map(b => b.text || '').join('') || '';
                    const jsonMatch = content.match(/\{.*\}/s);
                    return jsonMatch ? JSON.parse(jsonMatch[0]) : null;
                }
                
                if (provider === 'gemini') {
                    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${encodeURIComponent(apiKey)}`;
                    const res = await fetch(url, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            contents: [{ parts: [{ text: prompt }] }],
                            generationConfig: { maxOutputTokens: 300, temperature: 0.1 }
                        })
                    });
                    if (!res.ok) return null;
                    const data = await res.json();
                    const content = data.candidates?.[0]?.content?.parts?.[0]?.text || '';
                    const jsonMatch = content.match(/\{.*\}/s);
                    return jsonMatch ? JSON.parse(jsonMatch[0]) : null;
                }
                
                if (provider === 'groq') {
                    const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${apiKey}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            model: 'llama-3.3-70b-versatile',
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
                            max_tokens: 300
                        })
                    });
                    if (!res.ok) return null;
                    const data = await res.json();
                    const content = data.choices?.[0]?.message?.content || '';
                    const jsonMatch = content.match(/\{.*\}/s);
                    return jsonMatch ? JSON.parse(jsonMatch[0]) : null;
                }
                
                if (provider === 'openai') {
                    const res = await fetch('https://api.openai.com/v1/chat/completions', {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${apiKey}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            model: 'gpt-4o',
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
                            max_tokens: 300
                        })
                    });
                    if (!res.ok) return null;
                    const data = await res.json();
                    const content = data.choices?.[0]?.message?.content || '';
                    const jsonMatch = content.match(/\{.*\}/s);
                    return jsonMatch ? JSON.parse(jsonMatch[0]) : null;
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
    return Response(HTML_TEMPLATE, mimetype='text/html')

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

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    """Proxy AI analysis requests to bypass CORS restrictions."""
    import re, sys, traceback
    
    # Handle preflight requests
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.json
        provider = data.get('provider')
        api_key = data.get('apiKey')
        prompt = data.get('prompt')
        
        print(f"[ANALYZE] Provider: {provider}, Key length: {len(api_key) if api_key else 0}", flush=True)
        
        if not all([provider, api_key, prompt]):
            return jsonify({'error': 'Missing required fields: provider, apiKey, prompt'}), 400
        
        # Route to appropriate AI provider
        if provider == 'anthropic':
            print("[ANALYZE] Calling Anthropic API...", flush=True)
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'Content-Type': 'application/json',
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01'
                },
                json={
                    'model': 'claude-sonnet-4-20250514',
                    'max_tokens': 300,
                    'messages': [{'role': 'user', 'content': prompt}]
                },
                timeout=30
            )
            print(f"[ANALYZE] Claude status: {response.status_code}", flush=True)
            
            if not response.ok:
                print(f"[ANALYZE] Claude error: {response.text[:500]}", flush=True)
                return jsonify({'error': f'Anthropic API error: {response.text}'}), response.status_code
            
            result = response.json()
            content = ''.join(block.get('text', '') for block in result.get('content', []))
            print(f"[ANALYZE] Claude content: {content[:500]}", flush=True)
            
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
                return jsonify(parsed)
            return jsonify({'error': 'No JSON in Claude response', 'raw': content}), 500
        
        elif provider == 'gemini':
            url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}'
            response = requests.post(
                url,
                headers={'Content-Type': 'application/json'},
                json={
                    'contents': [{'parts': [{'text': prompt}]}],
                    'generationConfig': {
                        'maxOutputTokens': 2048,
                        'temperature': 0.1,
                        'responseMimeType': 'application/json',
                        'thinkingConfig': {'thinkingBudget': 0}
                    }
                },
                timeout=60
            )
            print(f"[ANALYZE] Gemini status: {response.status_code}", flush=True)
            
            if not response.ok:
                print(f"[ANALYZE] Gemini error: {response.text[:500]}", flush=True)
                return jsonify({'error': f'Gemini API error: {response.text}'}), response.status_code
            
            result = response.json()
            candidates = result.get('candidates', [])
            finish_reason = candidates[0].get('finishReason', 'unknown') if candidates else 'none'
            content = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '') if candidates else ''
            print(f"[ANALYZE] Gemini finishReason: {finish_reason}", flush=True)
            print(f"[ANALYZE] Gemini content: {content[:500]}", flush=True)
            
            # Strip markdown code fences if present (```json ... ```)
            content = re.sub(r'^```(?:json)?\s*', '', content.strip())
            content = re.sub(r'\s*```$', '', content.strip())
            
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return jsonify(json.loads(json_match.group(0)))
            return jsonify({'error': 'No JSON found in Gemini response', 'raw': content[:300]}), 500
        
        elif provider == 'groq':
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'llama-3.3-70b-versatile',
                    'messages': [
                        {'role': 'system', 'content': 'You are an expert at detecting fabricated academic citations. Respond only with valid JSON.'},
                        {'role': 'user', 'content': prompt}
                    ],
                    'temperature': 0.1,
                    'max_tokens': 300
                },
                timeout=30
            )
            if not response.ok:
                return jsonify({'error': f'Groq API error: {response.text}'}), response.status_code
            
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return jsonify(json.loads(json_match.group(0)))
            return jsonify({'error': 'No JSON found in response'}), 500
        
        elif provider == 'openai':
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-4o',
                    'messages': [
                        {'role': 'system', 'content': 'You are an expert at detecting fabricated academic citations. Respond only with valid JSON.'},
                        {'role': 'user', 'content': prompt}
                    ],
                    'temperature': 0.1,
                    'max_tokens': 300
                },
                timeout=30
            )
            if not response.ok:
                return jsonify({'error': f'OpenAI API error: {response.text}'}), response.status_code
            
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return jsonify(json.loads(json_match.group(0)))
            return jsonify({'error': 'No JSON found in response'}), 500
        
        else:
            return jsonify({'error': f'Unsupported provider: {provider}'}), 400
    
    except requests.exceptions.Timeout:
        return jsonify({'error': 'AI API request timed out'}), 504
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
