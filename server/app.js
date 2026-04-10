const express = require('express');
const cors = require('cors');
const path = require('path');
const { generateCareerQuiz, generateCareerSuggestions, analyzeCareerPivot } = require('./ai-logic');
const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// Supabase Client
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseKey) {
    console.warn('⚠️ Supabase credentials not found. Database features disabled.');
}

const supabase = supabaseUrl && supabaseKey 
    ? createClient(supabaseUrl, supabaseKey)
    : null;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../public')));

// Supabase Auth Middleware - verify JWT token
const verifySupabaseToken = async (req, res, next) => {
    const token = req.headers.authorization?.replace('Bearer ', '');
    
    if (!token || !supabase) {
        return res.status(401).json({ error: 'Authorization token required' });
    }
    
    try {
        const { data: { user }, error } = await supabase.auth.getUser(token);
        if (error) throw error;
        req.user = user;
        next();
    } catch (error) {
        res.status(401).json({ error: 'Invalid or expired token' });
    }
};

// Health check - no auth required
app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

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

// Protected route - requires auth
app.post('/api/save-quiz-results', verifySupabaseToken, async (req, res) => {
    try {
        if (!supabase) {
            return res.status(503).json({ error: 'Database service unavailable' });
        }

        const { scores, timestamp } = req.body;
        const userId = req.user.id;

        const { data, error } = await supabase
            .from('quiz_results')
            .insert([
                {
                    user_id: userId,
                    scores: scores,
                    created_at: timestamp || new Date().toISOString()
                }
            ]);

        if (error) throw error;
        res.json({ success: true, data });
    } catch (error) {
        console.error('Error saving quiz results:', error.message);
        res.status(500).json({ error: 'Error saving results.' });
    }
});

// Protected route - get user's quiz history
app.get('/api/user-quiz-history', verifySupabaseToken, async (req, res) => {
    try {
        if (!supabase) {
            return res.status(503).json({ error: 'Database service unavailable' });
        }

        const userId = req.user.id;
        const { data, error } = await supabase
            .from('quiz_results')
            .select('*')
            .eq('user_id', userId)
            .order('created_at', { ascending: false });

        if (error) throw error;
        res.json(data);
    } catch (error) {
        console.error('Error fetching quiz history:', error.message);
        res.status(500).json({ error: 'Error fetching history.' });
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
    console.log(`🚀 Server running at http://localhost:${PORT}`);
    if (supabase) {
        console.log('✅ Supabase connected');
    } else {
        console.log('⚠️ Supabase not configured - database features disabled');
    }
});