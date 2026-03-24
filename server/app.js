const express = require('express');
const cors = require('cors');
const path = require('path');
const { generateCareerQuiz } = require('./ai-logic');

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

// Start server
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});