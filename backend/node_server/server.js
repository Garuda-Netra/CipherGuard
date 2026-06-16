// CipherGuard Node.js Server
// Engineered & Crafted by Raj

// Root level se .env load karo
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../../.env') });

const express = require('express');
const cors = require('cors');
const fetch = require('node-fetch');
const { GoogleGenerativeAI } = require('@google/generative-ai');

// Express app initialize karo
const app = express();

// CORS enable karo sabhi origins ke liye
app.use(cors());

// JSON body parser enable karo
app.use(express.json());

// Port set karo, .env se ya default 3001
const PORT = process.env.NODE_PORT || 3001;
const FLASK_PORT = process.env.FLASK_PORT || 5000;

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: "ok",
        server: "CipherGuard Node Server",
        port: PORT,
        credits: "Engineered & Crafted by Raj"
    });
});

// Proxy status endpoint — Flask backend check karne ke liye
app.get('/api/proxy/status', async (req, res) => {
    try {
        // Flask health endpoint call karo
        const response = await fetch(`http://localhost:${FLASK_PORT}/api/health`);
        if (response.ok) {
            res.json({ flask: "online", node: "online" });
        } else {
            res.json({ flask: "offline", node: "online" });
        }
    } catch (error) {
        // Agar connection fail ho jaye toh offline report karo
        res.json({ flask: "offline", node: "online" });
    }
});

// Proxy forward endpoint — requests Flask ko forward karne ke liye
app.post('/api/proxy/forward', async (req, res) => {
    try {
        const { endpoint, method, data } = req.body;

        if (!endpoint || !method) {
            return res.status(400).json({ error: "Endpoint aur method zaruri hain" });
        }

        const options = {
            method: method.toUpperCase(),
            headers: { 'Content-Type': 'application/json' }
        };

        // Agar data hai toh body mein add karo
        if (data && (options.method === 'POST' || options.method === 'PUT')) {
            options.body = JSON.stringify(data);
        }

        // Request forward karo
        const response = await fetch(`http://localhost:${FLASK_PORT}${endpoint}`, options);
        
        // Response text ke roop mein lo pehle
        const text = await response.text();
        
        try {
            // JSON parse karne ki koshish karo
            const json = JSON.parse(text);
            res.status(response.status).json(json);
        } catch (e) {
            // Agar JSON nahi hai toh plain text bhej do
            res.status(response.status).send(text);
        }

    } catch (error) {
        console.error("[ERROR] Proxy forwarding fail ho gayi:", error);
        res.status(500).json({ error: "Internal Server Error", message: error.message });
    }
});

// Gemini API Chat Endpoint
app.post('/api/chat', async (req, res) => {
    try {
        const { message } = req.body;
        
        if (!process.env.GEMINI_API_KEY) {
            return res.status(500).json({ error: "Gemini API key is missing from .env" });
        }

        const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
        const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });

        const prompt = `You are 'The Warden', a medieval guardian of CipherGuard (a cybersecurity suite crafted by Raj). 
Your task is to explain things in a mix of Hinglish and English. 
Use very simple words. 
Always stay in character as a wise, slightly dramatic medieval warden. 
Keep your answers concise and directly answer the user's query.

User query: ${message}`;

        const result = await model.generateContent(prompt);
        const responseText = result.response.text();
        
        res.json({ response: responseText });
    } catch (error) {
        console.error("[ERROR] Gemini API failed:", error);
        res.status(500).json({ error: "Failed to communicate with the Oracle.", details: error.message });
    }
});

// Server start karo
app.listen(PORT, () => {
    console.log("╔══════════════════════════════════════╗");
    console.log("║   CipherGuard Node.js Server         ║");
    console.log(`║   Running on port: ${PORT.toString().padEnd(17, ' ')} ║`);
    console.log("║   Engineered & Crafted by Raj        ║");
    console.log("╚══════════════════════════════════════╝");
});
