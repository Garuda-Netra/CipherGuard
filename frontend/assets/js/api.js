const API_BASE = 'http://localhost:5000/api';

// Using placeholders with console.log as requested for frontend standalone testing
const api = {
    generateDictionary: (baseWords, mutations) => {
        console.log(`[API] generateDictionary called with bases: ${baseWords}, mutations: ${mutations}`);
        // Mock SSE
        return mockSSE([
            "[INIT] Initializing dictionary generator...",
            `[RULE] Applying mutations: ${mutations.join(', ')}`,
            "[GEN] password -> p@ssw0rd",
            "[GEN] admin -> 4dm1n",
            "[GEN] raj -> R@j2024",
            "[GEN] admin -> Admin!@#",
            "[DONE] Dictionary generation complete. Total words: 2450."
        ], 500);
    },

    extractHashes: async (formData) => {
        console.log(`[API] extractHashes called`);
        for (let pair of formData.entries()) {
            console.log(pair[0]+ ', ' + pair[1]); 
        }
        // Mock API response
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({
                    success: true,
                    data: [
                        { username: 'root', algorithm: 'SHA-512', hash: '$6$xyz...$hash123' },
                        { username: 'raj', algorithm: 'SHA-512', hash: '$6$abc...$hash456' },
                        { username: 'guest', algorithm: 'MD5', hash: '$1$def...$hash789' }
                    ]
                });
            }, 1500);
        });
    },

    startBruteForce: (hashValue, hashType, mode, wordlistFile) => {
        console.log(`[API] startBruteForce called. Hash: ${hashValue}, Type: ${hashType}, Mode: ${mode}`);
        // Mock SSE for cracking progress
        let progress = 0;
        let eventTarget = new EventTarget();
        
        let interval = setInterval(() => {
            progress += Math.floor(Math.random() * 10) + 5;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                
                // Final success message
                setTimeout(() => {
                    const event = new CustomEvent('message', { 
                        detail: JSON.stringify({ type: 'result', success: true, password: 'r@jpassword123', percent: 100 }) 
                    });
                    eventTarget.dispatchEvent(event);
                }, 500);
            }
            
            let eta = `00:00:${Math.max(0, Math.floor((100 - progress) / 5))}`;
            
            const event = new CustomEvent('message', { 
                detail: JSON.stringify({ type: 'progress', percent: progress, eta: eta, log: `[CRACK] Trying hashes... batch #${progress * 1000}` }) 
            });
            eventTarget.dispatchEvent(event);
            
        }, 800);
        
        return eventTarget;
    },

    analyzeStrength: async (password) => {
        console.log(`[API] analyzeStrength called. Length: ${password.length}`);
        return new Promise(resolve => {
            setTimeout(() => {
                let score = 0;
                let entropy = password.length * 4.5;
                let level = 'Weak';
                let reqs = {
                    length: password.length >= 8,
                    upper: /[A-Z]/.test(password),
                    lower: /[a-z]/.test(password),
                    number: /[0-9]/.test(password),
                    special: /[^A-Za-z0-9]/.test(password)
                };
                
                let passed = Object.values(reqs).filter(Boolean).length;
                if (passed >= 4 && password.length >= 12) { level = 'Fortress'; score = 4; }
                else if (passed >= 4) { level = 'Strong'; score = 3; }
                else if (passed >= 2) { level = 'Fair'; score = 2; }
                else if (passed > 0) { level = 'Weak'; score = 1; }
                
                resolve({
                    success: true,
                    data: {
                        level: level,
                        score: score, // 1-4
                        entropy: entropy.toFixed(1),
                        requirements: reqs,
                        tips: [
                            !reqs.length ? "Add more characters to reach at least 8." : null,
                            !reqs.upper ? "Include at least one uppercase letter." : null,
                            !reqs.number ? "Add a number to increase complexity." : null,
                            !reqs.special ? "Use a special symbol like @, #, or $." : null,
                            level === 'Fortress' ? "Excellent! This password is highly secure." : null
                        ].filter(Boolean)
                    }
                });
            }, 300); // 300ms network delay simulation
        });
    },

    generateReport: async () => {
        console.log(`[API] generateReport called`);
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({
                    success: true,
                    data: {
                        executiveSummary: "The security audit revealed multiple vulnerabilities in the provided credential hashes. Several weak passwords were automatically cracked.",
                        dictionaryResults: "Generated a custom wordlist of 14,520 permutations based on user-provided keywords.",
                        hashFindings: "Extracted 3 user hashes from Linux shadow format. 2 uses SHA-512, 1 uses MD5.",
                        bruteForceResults: "Successfully cracked 1/3 passwords. Target hash corresponds to 'r@jpassword123'.",
                        strengthSummary: "Average password entropy across analyzed credentials was 34.2 bits (Fair).",
                        recommendations: [
                            "Enforce a minimum password length of 12 characters.",
                            "Implement multi-factor authentication (MFA) across all administrative accounts.",
                            "Migrate away from MD5 hashing to Argon2id or bcrypt."
                        ]
                    }
                });
            }, 1000);
        });
    }
};

// Helper to mock SSE behavior
function mockSSE(messages, delay) {
    let eventTarget = new EventTarget();
    let i = 0;
    
    let interval = setInterval(() => {
        if (i < messages.length) {
            const event = new CustomEvent('message', { detail: messages[i] });
            eventTarget.dispatchEvent(event);
            i++;
        } else {
            clearInterval(interval);
        }
    }, delay);
    
    return eventTarget;
}
