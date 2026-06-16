const API_BASE = 'http://localhost:5000/api';

const api = {
    // Generate Dictionary
    generateDictionary: async (baseWords, mutations) => {
        try {
            const res = await fetch(`${API_BASE}/dictionary/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ base_words: baseWords.join(','), mutations: mutations })
            });
            const data = await res.json();
            
            if (data.status === 'started') {
                return new EventSource(`${API_BASE}/dictionary/stream`);
            } else {
                throw new Error(data.message || 'Failed to start generator');
            }
        } catch (err) {
            console.error("API Error:", err);
            throw err;
        }
    },

    // Extract Hashes
    extractHashes: async (formData) => {
        try {
            const res = await fetch(`${API_BASE}/hash/extract`, {
                method: 'POST',
                body: formData
            });
            return await res.json();
        } catch (err) {
            console.error("API Error:", err);
            return { success: false, message: err.message };
        }
    },

    // Start Brute Force
    startBruteForce: async (hashValue, hashType, mode, wordlistFile) => {
        try {
            const formData = new FormData();
            formData.append('hash', hashValue);
            formData.append('hash_type', hashType);
            formData.append('mode', mode);
            
            if (mode === 'wordlist' && wordlistFile) {
                formData.append('wordlist', wordlistFile);
            }

            const res = await fetch(`${API_BASE}/bruteforce/crack`, {
                method: 'POST',
                body: formData
            });
            const data = await res.json();

            if (data.status === 'started') {
                return new EventSource(`${API_BASE}/bruteforce/stream`);
            } else {
                throw new Error(data.message || 'Failed to start brute force');
            }
        } catch (err) {
            console.error("API Error:", err);
            throw err;
        }
    },

    // Analyze Strength
    analyzeStrength: async (password) => {
        try {
            const res = await fetch(`${API_BASE}/strength/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: password })
            });
            const data = await res.json();
            
            if (data.status === 'success') {
                const apiData = data.data;
                return {
                    success: true,
                    data: {
                        level: apiData.rating,
                        score: apiData.score,
                        entropy: apiData.entropy.toString(),
                        requirements: apiData.checks,
                        tips: apiData.tips
                    }
                };
            }
            return { success: false };
        } catch (err) {
            console.error("API Error:", err);
            return { success: false };
        }
    },

    // Full Vulnerability Scan (Real HIBP Check via Backend SSE)
    fullAnalyzeStrength: async (password) => {
        try {
            const res = await fetch(`${API_BASE}/strength/full_scan`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: password })
            });
            // We can't easily return an EventSource from a POST request natively in browser unless using fetch streaming
            // So we'll use a hack or implement a custom stream reader.
            if (!res.body) throw new Error('ReadableStream not yet supported in this browser.');
            
            return res.body.getReader();
        } catch (err) {
            console.error("API Error:", err);
            throw err;
        }
    },

    // Generate Report
    generateReport: async () => {
        try {
            const res = await fetch(`${API_BASE}/report/generate`, {
                method: 'GET'
            });
            return await res.json();
        } catch (err) {
            console.error("API Error:", err);
            return { success: false, message: err.message };
        }
    }
};
