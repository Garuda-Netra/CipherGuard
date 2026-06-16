// MEDIEVAL TOAST NOTIFICATIONS
function showToast(message, type) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('toast-leave');
        toast.addEventListener('animationend', () => {
            toast.remove();
            if (container.children.length === 0) {
                container.remove();
            }
        });
    }, 3500);
}

// TERMINAL OUTPUT
function appendToTerminal(panelId, text) {
    const termWindow = document.getElementById(`term-${panelId}`);
    if (!termWindow) return;
    
    const contentDiv = termWindow.querySelector('.terminal-content');
    const cursor = termWindow.querySelector('.terminal-cursor');
    
    const newLine = document.createElement('div');
    newLine.textContent = text;
    
    contentDiv.appendChild(newLine);
    
    // Auto-scroll
    termWindow.scrollTop = termWindow.scrollHeight;
}

// PROGRESS BAR
function updateProgressBar(percent, etaString) {
    const fill = document.getElementById('brute-progress-fill');
    const text = document.getElementById('brute-progress-text');
    const eta = document.getElementById('brute-eta');
    
    fill.style.width = `${percent}%`;
    
    if (percent > 75) {
        fill.style.backgroundColor = '#8B1A1A'; // danger red
    } else if (percent > 40) {
        fill.style.backgroundColor = '#C9A84C'; // gold
    } else {
        fill.style.backgroundColor = '#2D5016'; // green
    }
    
    // Draw ascii block progress
    const blocksTotal = 16;
    const blocksFilled = Math.floor((percent / 100) * blocksTotal);
    const bar = '█'.repeat(blocksFilled) + '░'.repeat(blocksTotal - blocksFilled);
    
    text.textContent = `[${bar}] ${Math.floor(percent)}%`;
    eta.textContent = `ETA: ${etaString}`;
}

// DOM CONTENT LOADED
document.addEventListener('DOMContentLoaded', () => {
    // 1. Init Dust Particles
    if (typeof initDustParticles === 'function') initDustParticles();
    
    // 1.5 Init Dashboard Stats (Real-time)
    window.appStats = {
        'stat-words': 0,
        'stat-hashes': 0,
        'stat-cracked': 0,
        'stat-analyzed': 0
    };
    
    if (typeof animateValue === 'function') {
        for (const [id, endVal] of Object.entries(window.appStats)) {
            const el = document.getElementById(id);
            if (el) el.innerHTML = "0"; // initialize to 0
        }
    }
    
    // 2. Navigation Logic
    const navItems = document.querySelectorAll('.nav-item');
    const panels = document.querySelectorAll('.panel-section');
    const headings = {
        'dashboard': 'Welcome to CipherGuard',
        'dictionary': 'Dictionary Generator',
        'hash': 'Hash Extractor',
        'brute': 'Brute Force Engine',
        'strength': 'Password Strength Analyzer',
        'report': 'Security Audit Report'
    };
    
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetId = item.getAttribute('data-target');
            
            // Hide all panels
            panels.forEach(p => {
                p.classList.add('hidden');
                p.classList.remove('active');
            });
            
            // Show target panel
            const targetPanel = document.getElementById(`panel-${targetId}`);
            if(targetPanel) {
                targetPanel.classList.remove('hidden');
                targetPanel.classList.add('active');
                
                // Animations
                if (typeof unfurlPanel === 'function') unfurlPanel(targetPanel);
                
                const headingElem = targetPanel.querySelector('.panel-heading');
                if (headingElem && typeof typeHeading === 'function') {
                    typeHeading(headingElem, headings[targetId]);
                }
            }
            
            // Highlight nav
            navItems.forEach(n => n.classList.remove('text-highlight'));
            item.classList.add('text-highlight');
        });
    });
    
    // 3. Dictionary Generator Form
    const btnGenDict = document.getElementById('btn-generate-dict');
    if (btnGenDict) {
        btnGenDict.addEventListener('click', async () => {
            const baseWordsStr = document.getElementById('dict-base-words').value;
            const baseWords = baseWordsStr.split(',').map(s=>s.trim()).filter(Boolean);
            const mutCheckboxes = document.querySelectorAll('#panel-dictionary .custom-checkbox:checked');
            const mutations = Array.from(mutCheckboxes).map(cb => cb.value);
            
            if (baseWords.length === 0) {
                showToast('Please enter base words.', 'warning');
                return;
            }
            
            const btnText = btnGenDict.querySelector('span');
            btnText.textContent = 'Processing...';
            btnGenDict.disabled = true;
            
            document.querySelector('#term-dictionary .terminal-content').innerHTML = '';
            
            try {
                const sse = await api.generateDictionary(baseWords, mutations);
                let totalWordsDisplay = document.getElementById('dict-total-words');
                totalWordsDisplay.style.opacity = '0';
                
                sse.addEventListener('message', (e) => {
                    const data = JSON.parse(e.data);
                    if (data.word) {
                        appendToTerminal('dictionary', `[GEN] ${data.word}`);
                    } else if (data.done) {
                        showToast('Dictionary generation complete.', 'success');
                        btnText.textContent = 'Generate Wordlist';
                        btnGenDict.disabled = false;
                        sse.close();
                        
                        const count = data.total;
                        totalWordsDisplay.querySelector('span').textContent = count;
                        totalWordsDisplay.style.opacity = '1';
                        
                        if (window.appStats) {
                            const oldVal = window.appStats['stat-words'];
                            window.appStats['stat-words'] += count;
                            const el = document.getElementById('stat-words');
                            if (el && typeof animateValue === 'function') {
                                animateValue(el, oldVal, window.appStats['stat-words'], 1000);
                            }
                        }
                    }
                });
                sse.addEventListener('error', (err) => {
                    console.error("SSE Error:", err);
                    sse.close();
                    btnText.textContent = 'Generate Wordlist';
                    btnGenDict.disabled = false;
                    showToast('Stream error', 'error');
                });
            } catch (err) {
                showToast('API Error', 'error');
                btnText.textContent = 'Generate Wordlist';
                btnGenDict.disabled = false;
            }
        });
    }
    
    // 4. Hash Extractor Form
    const radiosHashOs = document.querySelectorAll('input[name="hash-os"]');
    const uploadLinux = document.getElementById('hash-upload-linux');
    const uploadWindows = document.getElementById('hash-upload-windows');
    
    radiosHashOs.forEach(r => {
        r.addEventListener('change', (e) => {
            if (e.target.value === 'linux') {
                uploadLinux.classList.remove('hidden');
                uploadWindows.classList.add('hidden');
            } else {
                uploadLinux.classList.add('hidden');
                uploadWindows.classList.remove('hidden');
            }
        });
    });
    
    const btnExtract = document.getElementById('btn-extract-hashes');
    if (btnExtract) {
        btnExtract.addEventListener('click', async () => {
            const isLinux = document.querySelector('input[name="hash-os"]:checked').value === 'linux';
            const formData = new FormData();
            
            if (isLinux) {
                const file = document.getElementById('file-shadow').files[0];
                if (!file) { showToast('Please upload shadow file.', 'warning'); return; }
                formData.append('shadow', file);
            } else {
                const sam = document.getElementById('file-sam').files[0];
                const sys = document.getElementById('file-system').files[0];
                if (!sam || !sys) { showToast('Please upload both SAM and SYSTEM files.', 'warning'); return; }
                formData.append('sam', sam);
                formData.append('system', sys);
            }
            
            const btnText = btnExtract.querySelector('span');
            btnText.textContent = 'Extracting...';
            btnExtract.disabled = true;
            
            document.querySelector('#term-hash .terminal-content').innerHTML = '';
            appendToTerminal('hash', '[INIT] Starting hash extraction...');
            
            try {
                const result = await api.extractHashes(formData);
                if (result.success) {
                    appendToTerminal('hash', `[SUCCESS] Extracted ${result.data.length} hashes successfully.`);
                    showToast('Hashes extracted successfully.', 'success');
                    
                    // Populate table
                    const tbody = document.getElementById('hash-results-body');
                    tbody.innerHTML = '';
                    result.data.forEach(item => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td class="p-4 border-b border-[#6B3A2A]">${item.username}</td>
                            <td class="p-4 border-b border-[#6B3A2A]">${item.algorithm}</td>
                            <td class="p-4 border-b border-[#6B3A2A] break-all">${item.hash}</td>
                        `;
                        tbody.appendChild(tr);
                    });
                    
                    document.getElementById('hash-results-container').classList.remove('hidden');
                    
                    // Real-time stat update
                    if (window.appStats) {
                        const count = result.data.length;
                        const oldVal = window.appStats['stat-hashes'];
                        window.appStats['stat-hashes'] += count;
                        const el = document.getElementById('stat-hashes');
                        if (el && typeof animateValue === 'function') {
                            animateValue(el, oldVal, window.appStats['stat-hashes'], 1000);
                        }
                    }
                }
            } catch (e) {
                showToast('Extraction failed.', 'error');
                appendToTerminal('hash', '[ERROR] Extraction failed.');
            }
            
            btnText.textContent = 'Extract Hashes';
            btnExtract.disabled = false;
        });
    }
    
    // 5. Brute Force Form
    const radiosBruteMode = document.querySelectorAll('input[name="brute-mode"]');
    const wordlistSec = document.getElementById('brute-wordlist-section');
    const incSec = document.getElementById('brute-incremental-section');
    
    radiosBruteMode.forEach(r => {
        r.addEventListener('change', (e) => {
            if (e.target.value === 'wordlist') {
                wordlistSec.classList.remove('hidden');
                incSec.classList.add('hidden');
            } else {
                wordlistSec.classList.add('hidden');
                incSec.classList.remove('hidden');
            }
        });
    });
    
    const btnCrack = document.getElementById('btn-start-cracking');
    if (btnCrack) {
        btnCrack.addEventListener('click', async () => {
            const hash = document.getElementById('brute-hash').value;
            const type = document.getElementById('brute-type').value;
            const mode = document.querySelector('input[name="brute-mode"]:checked').value;
            const file = document.getElementById('brute-wordlist-file').files[0];
            
            if (!hash) { showToast('Please enter target hash.', 'warning'); return; }
            if (mode === 'wordlist' && !file) { showToast('Please upload wordlist.', 'warning'); return; }
            
            const btnText = btnCrack.querySelector('span');
            btnText.textContent = 'Cracking...';
            btnCrack.disabled = true;
            
            document.querySelector('#term-brute .terminal-content').innerHTML = '';
            const resDisplay = document.getElementById('brute-result-display');
            resDisplay.classList.add('hidden');
            resDisplay.innerHTML = '';
            updateProgressBar(0, '--:--:--');
            
            appendToTerminal('brute', `[INIT] Initializing cracking engine for ${type}...`);
            
            try {
                const sse = await api.startBruteForce(hash, type, mode, file);
                
                sse.addEventListener('message', (e) => {
                    const data = JSON.parse(e.data);
                    
                    if (data.type === 'progress') {
                        updateProgressBar(data.percent, data.eta);
                        appendToTerminal('brute', data.log);
                    } else if (data.found || data.exhausted) {
                        btnText.textContent = 'Start Cracking';
                        btnCrack.disabled = false;
                        sse.close();
                        
                        if (data.found) {
                            updateProgressBar(100, '00:00:00');
                            appendToTerminal('brute', `[SUCCESS] Match found: ${data.password}`);
                            resDisplay.innerHTML = `
                                <div class="text-sm opacity-70 mb-1">PASSWORD CRACKED</div>
                                <div class="text-3xl tracking-widest text-[#00FF41]">${data.password}</div>
                            `;
                            resDisplay.classList.remove('hidden');
                            showToast('Password Cracked Successfully!', 'success');
                            
                            if (window.appStats) {
                                const oldVal = window.appStats['stat-cracked'];
                                window.appStats['stat-cracked'] += 1;
                                const el = document.getElementById('stat-cracked');
                                if (el && typeof animateValue === 'function') {
                                    animateValue(el, oldVal, window.appStats['stat-cracked'], 1000);
                                }
                            }
                        } else {
                            appendToTerminal('brute', `[FAILED] Exhausted. Password not found.`);
                            showToast('Brute force exhausted.', 'error');
                        }
                    } else if (data.log) {
                        appendToTerminal('brute', data.log);
                    }
                });
                sse.addEventListener('error', () => {
                    sse.close();
                    btnText.textContent = 'Start Cracking';
                    btnCrack.disabled = false;
                }
            });
        });
    }
    
    // 6. Password Strength Analyzer
    const pwdInput = document.getElementById('strength-input');
    const togglePwd = document.getElementById('toggle-password');
    let debounceTimer;
    
    if (togglePwd && pwdInput) {
        togglePwd.addEventListener('click', () => {
            if (pwdInput.type === 'password') {
                pwdInput.type = 'text';
                togglePwd.style.opacity = '1';
            } else {
                pwdInput.type = 'password';
                togglePwd.style.opacity = '';
            }
        });
        
        pwdInput.addEventListener('keyup', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(async () => {
                const val = pwdInput.value;
                if (!val) {
                    // reset
                    document.getElementById('strength-label').textContent = '-';
                    document.getElementById('entropy-score').textContent = 'Entropy: 0.0 bits';
                    for(let i=1; i<=4; i++) document.getElementById(`meter-${i}`).style.backgroundColor = 'transparent';
                    document.querySelectorAll('.req-item').forEach(el => {
                        el.innerHTML = `<span class="icon text-danger">✖</span> ${el.textContent.replace('✖', '').replace('✔', '').trim()}`;
                    });
                    document.getElementById('strength-tips').innerHTML = '<li>Start typing to see personalized recommendations.</li>';
                    return;
                }
                
                const res = await api.analyzeStrength(val);
                if (res.success) {
                    const data = res.data;
                    document.getElementById('strength-label').textContent = data.level;
                    document.getElementById('entropy-score').textContent = `Entropy: ${data.entropy} bits`;
                    
                    // Colors
                    const colors = { 1: '#8B1A1A', 2: '#D4831A', 3: '#2D5016', 4: '#00FF41' };
                    const color = colors[data.score];
                    
                    for(let i=1; i<=4; i++) {
                        document.getElementById(`meter-${i}`).style.backgroundColor = i <= data.score ? color : 'transparent';
                    }
                    
                    // Checklist
                    const reqsMap = {
                        length: 'Minimum 8 characters',
                        upper: 'Uppercase letter',
                        lower: 'Lowercase letter',
                        number: 'Number',
                        special: 'Special symbol'
                    };
                    
                    Object.keys(data.requirements).forEach(key => {
                        const passed = data.requirements[key];
                        const item = document.querySelector(`.req-item[data-req="${key}"]`);
                        if (item) {
                            if (passed) {
                                item.innerHTML = `<span class="icon text-[#4A7C2F]">✔</span> ${reqsMap[key]}`;
                            } else {
                                item.innerHTML = `<span class="icon text-[#8B1A1A]">✖</span> ${reqsMap[key]}`;
                            }
                        }
                    });
                    
                    // Tips
                    const tipsHtml = data.tips.map(t => `<li>${t}</li>`).join('');
                    document.getElementById('strength-tips').innerHTML = tipsHtml;
                }
            }, 300);
        });
    }
    
    const btnAnalyzeFull = document.getElementById('btn-analyze-full');
    if (btnAnalyzeFull && pwdInput) {
        btnAnalyzeFull.addEventListener('click', async () => {
            const val = pwdInput.value;
            if (!val) { showToast('Enter password to analyze.', 'warning'); return; }
            
            const term = document.querySelector('#term-strength .terminal-content');
            term.innerHTML = '';
            
            try {
                const reader = await api.fullAnalyzeStrength(val);
                const decoder = new TextDecoder("utf-8");
                let buffer = "";
                
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    
                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n');
                    buffer = lines.pop(); // keep the incomplete line in buffer
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.substring(6));
                                if (data.log) {
                                    appendToTerminal('strength', data.log);
                                }
                                if (data.done) {
                                    showToast('Full analysis complete.', 'success');
                                    // Real-time stat update
                                    if (window.appStats) {
                                        const oldVal = window.appStats['stat-analyzed'];
                                        window.appStats['stat-analyzed'] += 1;
                                        const el = document.getElementById('stat-analyzed');
                                        if (el && typeof animateValue === 'function') {
                                            animateValue(el, oldVal, window.appStats['stat-analyzed'], 1000);
                                        }
                                    }
                                }
                            } catch (e) {
                                console.error("SSE parse error", e, line);
                            }
                        }
                    }
                }
            } catch (err) {
                showToast('Analysis error', 'error');
                console.error(err);
            }
        });
    }
    
    // 7. Report Panel
    const btnGenReport = document.getElementById('btn-generate-report');
    if (btnGenReport) {
        btnGenReport.addEventListener('click', async () => {
            const btnText = btnGenReport.querySelector('span');
            btnText.textContent = 'Generating...';
            btnGenReport.disabled = true;
            
            try {
                const res = await api.generateReport();
                if (res.success) {
                    const data = res.data;
                    const d = new Date();
                    document.getElementById('report-date').textContent = `Date: ${d.toISOString().replace('T', ' ').substring(0, 19)}`;
                    
                    const rbody = document.getElementById('report-body');
                    rbody.innerHTML = `
                        <div class="mb-6">
                            <h2 class="font-heading text-lg font-bold uppercase border-b border-[#6B3A2A] pb-2 mb-3">Executive Summary</h2>
                            <p>${data.executiveSummary}</p>
                        </div>
                        <div class="mb-6">
                            <h2 class="font-heading text-lg font-bold uppercase border-b border-[#6B3A2A] pb-2 mb-3">Dictionary Results</h2>
                            <p>${data.dictionaryResults}</p>
                        </div>
                        <div class="mb-6">
                            <h2 class="font-heading text-lg font-bold uppercase border-b border-[#6B3A2A] pb-2 mb-3">Hash Findings</h2>
                            <p>${data.hashFindings}</p>
                        </div>
                        <div class="mb-6">
                            <h2 class="font-heading text-lg font-bold uppercase border-b border-[#6B3A2A] pb-2 mb-3">Brute Force Results</h2>
                            <p>${data.bruteForceResults}</p>
                        </div>
                        <div class="mb-6">
                            <h2 class="font-heading text-lg font-bold uppercase border-b border-[#6B3A2A] pb-2 mb-3">Strength Summary</h2>
                            <p>${data.strengthSummary}</p>
                        </div>
                        <div class="mb-6">
                            <h2 class="font-heading text-lg font-bold uppercase border-b border-[#6B3A2A] pb-2 mb-3">Recommendations</h2>
                            <ul class="list-disc pl-5 space-y-2">
                                ${data.recommendations.map(r => `<li>${r}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                    showToast('Report generated successfully.', 'success');
                }
            } catch (e) {
                showToast('Failed to generate report.', 'error');
            }
            
            btnText.textContent = 'Generate Report';
            btnGenReport.disabled = false;
        });
    }
    
    const btnCopyReport = document.getElementById('btn-copy-report');
    if (btnCopyReport) {
        btnCopyReport.addEventListener('click', () => {
            const reportContent = document.getElementById('report-content-area').innerText;
            if (reportContent.includes('Click "Generate Report"')) {
                showToast('Please generate report first.', 'warning');
                return;
            }
            navigator.clipboard.writeText(reportContent).then(() => {
                showToast('Report copied to clipboard.', 'success');
            }).catch(err => {
                showToast('Failed to copy.', 'error');
            });
        });
    }
    
    const btnPrintReport = document.getElementById('btn-print-report');
    if (btnPrintReport) {
        btnPrintReport.addEventListener('click', () => {
            window.print();
        });
    }
});
