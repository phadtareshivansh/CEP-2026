const express = require('express');
const cors = require('cors');
const path = require('path');
const { generateCareerQuiz, generateCareerSuggestions, analyzeCareerPivot } = require('./ai-logic');

const app = express();
const PORT = 5000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../public')));

// Routes
app.get('/api/get-questions', async (req, res) => {
    try {
        const questions = await generateCareerQuiz();
        res.json(questions);
    } catch (error) {
        console.error('Error generating quiz:', error.message);
        res.status(500).json({ error: 'Error generating quiz. Please try again.' });
    }
});

app.post('/api/generate-career-suggestions', async (req, res) => {
    try {
        const { scores } = req.body;
        
        if (!scores) {
            return res.status(400).json({ error: 'Scores are required' });
        }
        
        const suggestions = await generateCareerSuggestions(scores);
        res.json(suggestions);
    } catch (error) {
        console.error('Error generating career suggestions:', error.message);
        res.status(500).json({ error: 'Error generating suggestions. Please try again.' });
    }
});

app.post('/api/analyze-career-pivot', async (req, res) => {
    try {
        const { current_role, target_career, current_skills, required_skills } = req.body;
        
        if (!current_role || !target_career) {
            return res.status(400).json({ error: 'current_role and target_career are required' });
        }
        
        const analysis = await analyzeCareerPivot(
            current_role,
            target_career,
            current_skills || [],
            required_skills || []
        );
        
        res.json(analysis);
    } catch (error) {
        console.error('Error analyzing career pivot:', error.message);
        res.status(500).json({ error: 'Error analyzing career pivot. Please try again.' });
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});