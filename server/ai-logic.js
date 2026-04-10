// Add fetch polyfill for Node.js 14
if (!global.fetch) {
    global.fetch = require('node-fetch');
}

require('dotenv').config();
const { GoogleGenerativeAI } = require("@google/generative-ai");

const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);

// RIASEC categories for mapping
const RIASEC_CATEGORIES = ['Realistic', 'Investigative', 'Artistic', 'Social', 'Enterprising', 'Conventional'];

async function generateCareerQuiz() {
    try {
        if (!process.env.GOOGLE_API_KEY) {
            return getMockQuestions();
        }

        const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

        const prompt = `Generate exactly 20 career discovery questions for the RIASEC interest model (Realistic, Investigative, Artistic, Social, Enterprising, Conventional).

Requirements:
- Create 20 diverse, engaging questions about careers and work preferences
- Each question should have RIASEC mappings that score each category
- Distribute questions to cover all 6 RIASEC types equally (approximately 3-4 questions per type)
- Questions should help determine the user's career path preferences
- Make questions practical and relatable

Return ONLY a JSON array with no additional text, markdown, or commentary.

Format (IMPORTANT - no markdown, pure JSON):
[
    {
        "question": "Question text?",
        "riasec_mapping": {
            "Realistic": 0.8,
            "Investigative": 0.2,
            "Artistic": 0.0,
            "Social": 0.0,
            "Enterprising": 0.0,
            "Conventional": 0.0
        }
    },
    ...20 total questions...
]

Note: RIASEC values should sum to 1.0, distribute weights to indicate which categories the question primarily maps to.`;

        const result = await model.generateContent(prompt);
        const responseText = result.response.text();
        
        // Parse JSON from response - remove markdown code blocks if present
        let jsonText = responseText;
        
        // Remove markdown code blocks
        jsonText = jsonText.replace(/```json\n?/g, '').replace(/```\n?/g, '');
        
        // Extract JSON array
        const jsonMatch = jsonText.match(/\[[\s\S]*\]/);
        if (jsonMatch) {
            const questions = JSON.parse(jsonMatch[0]);
            
            if (questions.length === 20) {
                return questions;
            } else {
                return getMockQuestions();
            }
        } else {
            return getMockQuestions();
        }
    } catch (error) {
        return getMockQuestions();
    }
}

function getMockQuestions() {
    return [
        // REALISTIC (working with hands, tools, fixing things)
        {
            "question": "Do you enjoy building or fixing things with your hands?",
            "riasec_mapping": { "Realistic": 0.8, "Investigative": 0.1, "Artistic": 0.05, "Social": 0.05, "Enterprising": 0.0, "Conventional": 0.0 }
        },
        {
            "question": "Would you prefer working outdoors in nature vs. in an office?",
            "riasec_mapping": { "Realistic": 0.7, "Investigative": 0.1, "Artistic": 0.1, "Social": 0.05, "Enterprising": 0.05, "Conventional": 0.0 }
        },
        {
            "question": "Do you like working with machines, tools, or mechanical systems?",
            "riasec_mapping": { "Realistic": 0.85, "Investigative": 0.1, "Artistic": 0.0, "Social": 0.0, "Enterprising": 0.05, "Conventional": 0.0 }
        },
        
        // INVESTIGATIVE (research, analysis, problem-solving)
        {
            "question": "Do you like solving complex problems and conducting research?",
            "riasec_mapping": { "Realistic": 0.1, "Investigative": 0.8, "Artistic": 0.05, "Social": 0.0, "Enterprising": 0.05, "Conventional": 0.0 }
        },
        {
            "question": "Do you enjoy analyzing data and finding patterns?",
            "riasec_mapping": { "Realistic": 0.0, "Investigative": 0.85, "Artistic": 0.0, "Social": 0.0, "Enterprising": 0.1, "Conventional": 0.05 }
        },
        {
            "question": "Would you prefer a career that requires continuous learning and discovery?",
            "riasec_mapping": { "Realistic": 0.05, "Investigative": 0.8, "Artistic": 0.1, "Social": 0.0, "Enterprising": 0.05, "Conventional": 0.0 }
        },
        
        // ARTISTIC (creative expression, innovation, design)
        {
            "question": "Do you love creative expression like art, music, design, or writing?",
            "riasec_mapping": { "Realistic": 0.0, "Investigative": 0.05, "Artistic": 0.9, "Social": 0.0, "Enterprising": 0.05, "Conventional": 0.0 }
        },
        {
            "question": "Do you like working on projects that allow you to express your creativity?",
            "riasec_mapping": { "Realistic": 0.05, "Investigative": 0.0, "Artistic": 0.85, "Social": 0.05, "Enterprising": 0.05, "Conventional": 0.0 }
        },
        {
            "question": "Would you prefer a job that involves innovation and breaking conventional rules?",
            "riasec_mapping": { "Realistic": 0.0, "Investigative": 0.1, "Artistic": 0.75, "Social": 0.05, "Enterprising": 0.1, "Conventional": 0.0 }
        },
        
        // SOCIAL (helping people, teamwork, communication)
        {
            "question": "Do you enjoy helping others and supporting people's growth?",
            "riasec_mapping": { "Realistic": 0.0, "Investigative": 0.0, "Artistic": 0.05, "Social": 0.85, "Enterprising": 0.1, "Conventional": 0.0 }
        },
        {
            "question": "Do you prefer working in teams vs. working alone?",
            "riasec_mapping": { "Realistic": 0.05, "Investigative": 0.05, "Artistic": 0.05, "Social": 0.75, "Enterprising": 0.1, "Conventional": 0.0 }
        },
        {
            "question": "Would you rather work in roles where you can directly impact people's lives?",
            "riasec_mapping": { "Realistic": 0.0, "Investigative": 0.0, "Artistic": 0.1, "Social": 0.8, "Enterprising": 0.05, "Conventional": 0.05 }
        },
        
        // ENTERPRISING (leadership, persuasion, ambition)
        {
            "question": "Do you like taking charge and leading projects or teams?",
            "riasec_mapping": { "Realistic": 0.05, "Investigative": 0.0, "Artistic": 0.0, "Social": 0.15, "Enterprising": 0.8, "Conventional": 0.0 }
        },
        {
            "question": "Do you have a natural ability to persuade and influence others?",
            "riasec_mapping": { "Realistic": 0.0, "Investigative": 0.0, "Artistic": 0.05, "Social": 0.2, "Enterprising": 0.75, "Conventional": 0.0 }
        },
        {
            "question": "Would you prefer pursuing ambitious goals and climbing the ladder?",
            "riasec_mapping": { "Realistic": 0.0, "Investigative": 0.0, "Artistic": 0.0, "Social": 0.1, "Enterprising": 0.85, "Conventional": 0.05 }
        },
        
        // CONVENTIONAL (organization, order, detail-oriented)
        {
            "question": "Do you prefer working in well-organized, structured environments?",
            "riasec_mapping": { "Realistic": 0.1, "Investigative": 0.05, "Artistic": 0.0, "Social": 0.0, "Enterprising": 0.05, "Conventional": 0.8 }
        },
        {
            "question": "Do you have strong attention to detail and accuracy?",
            "riasec_mapping": { "Realistic": 0.1, "Investigative": 0.15, "Artistic": 0.0, "Social": 0.0, "Enterprising": 0.0, "Conventional": 0.75 }
        },
        {
            "question": "Would you prefer following clear procedures and guidelines over improvisation?",
            "riasec_mapping": { "Realistic": 0.1, "Investigative": 0.05, "Artistic": 0.0, "Social": 0.0, "Enterprising": 0.0, "Conventional": 0.85 }
        },
        {
            "question": "Do you excel at administrative tasks and managing information systems?",
            "riasec_mapping": { "Realistic": 0.05, "Investigative": 0.15, "Artistic": 0.0, "Social": 0.0, "Enterprising": 0.0, "Conventional": 0.8 }
        },
        {
            "question": "Do you prefer stability and predictability in your career over uncertainty?",
            "riasec_mapping": { "Realistic": 0.1, "Investigative": 0.05, "Artistic": 0.0, "Social": 0.05, "Enterprising": 0.0, "Conventional": 0.8 }
        }
    ];
}

async function generateCareerSuggestions(scores) {
    try {
        if (!process.env.GOOGLE_API_KEY) {
            return getDefaultCareerSuggestions(scores);
        }

        const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

        // Format scores for the prompt
        const scoresText = Object.entries(scores)
            .map(([key, value]) => `${key}: ${(value).toFixed(1)}`)
            .join(', ');

        const prompt = `Based on these RIASEC career interest scores, generate personalized career pathway recommendations:

Scores: ${scoresText}

Generate a JSON response with exactly this structure (no markdown, pure JSON only):
{
    "primary": "Career pathway name based on top 2 scores",
    "roles": ["4 specific job titles relevant to these scores"],
    "skills": ["5 key skills they should develop"],
    "next_steps": ["3 actionable steps to pursue this career"]
}

Requirements:
- Match recommendations to the actual score values
- For high-scoring categories (9+), prioritize them heavily
- Consider combinations that make sense together
- Provide specific, actionable advice
- Make suggestions realistic and achievable
- Return ONLY valid JSON, no additional text or markdown`;

        const result = await model.generateContent(prompt);
        const responseText = result.response.text();
        
        // Parse JSON from response
        let jsonText = responseText;
        jsonText = jsonText.replace(/```json\n?/g, '').replace(/```\n?/g, '');
        
        const jsonMatch = jsonText.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            const suggestions = JSON.parse(jsonMatch[0]);
            
            // Validate structure
            if (suggestions.primary && suggestions.roles && suggestions.skills && suggestions.next_steps) {
                return suggestions;
            }
        }
        
        return getDefaultCareerSuggestions(scores);
    } catch (error) {
        console.error('Error generating career suggestions:', error.message);
        return getDefaultCareerSuggestions(scores);
    }
}

function getDefaultCareerSuggestions(scores) {
    // Find top 2 categories
    const sorted = Object.entries(scores)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 2)
        .map(entry => entry[0]);

    const defaultSuggestions = {
        primary: `${sorted.join(' & ')} Career Path`,
        roles: [
            'Professional in related field',
            'Specialist consultant',
            'Project manager',
            'Industry coordinator'
        ],
        skills: [
            'Communication',
            'Problem-solving',
            'Technical skills',
            'Leadership',
            'Continuous learning'
        ],
        next_steps: [
            'Research careers matching your profile',
            'Connect with professionals in the field',
            'Take relevant online courses or certifications'
        ]
    };

    return defaultSuggestions;
}

async function analyzeCareerPivot(currentRole, targetCareer, currentSkills, requiredSkills) {
    /**
     * Analyze the feasibility of transitioning from one career to another
     * Returns readiness score, skills gap, timeline, and recommendations
     */
    try {
        if (!process.env.GOOGLE_API_KEY) {
            return getFallbackPivotAnalysis(currentRole, targetCareer);
        }

        const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

        const prompt = `Analyze the career transition feasibility with this data:

Current Role/Career: ${currentRole}
Target Career: ${targetCareer}
Current Skills: ${currentSkills.join(', ')}
Required Skills for Target: ${requiredSkills.join(', ')}

Provide a detailed career pivot analysis in JSON format. Return ONLY valid JSON with NO markdown, NO code blocks.

Format:
{
    "readiness_score": <0-100, higher = more feasible>,
    "retraining_months": <estimated months needed>,
    "salary_change": <estimated salary change from current to target>,
    "skills_gap": [<list of missing critical skills>],
    "top_challenges": [<list of main obstacles to transition>],
    "success_tips": [<list of actionable recommendations>],
    "feasibility_explanation": "<brief explanation of the score>"
}

Base your analysis on:
1. How many skills transfer from current to target (skill overlap)
2. How many new skills must be learned
3. Industry experience that transfers
4. Typical transition timelines for this move
5. Market demand and salary prospects

Ensure all arrays have 3-5 items each.`;

        const result = await model.generateContent(prompt);
        const responseText = result.response.text();
        
        // Clean response text
        let jsonText = responseText;
        jsonText = jsonText.replace(/```json\n?/g, '').replace(/```\n?/g, '');
        
        // Extract JSON object
        const jsonMatch = jsonText.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            const analysis = JSON.parse(jsonMatch[0]);
            return analysis;
        } else {
            return getFallbackPivotAnalysis(currentRole, targetCareer);
        }
    } catch (error) {
        console.error('Error analyzing career pivot:', error.message);
        return getFallbackPivotAnalysis(currentRole, targetCareer);
    }
}

function getFallbackPivotAnalysis(currentRole, targetCareer) {
    /**
     * Fallback analysis when AI is unavailable
     */
    return {
        readiness_score: 55,
        retraining_months: 12,
        salary_change: 15000,
        skills_gap: [
            'Industry-specific technical knowledge',
            'New domain certifications',
            'Specialized tools and frameworks'
        ],
        top_challenges: [
            'Building relevant experience in target field',
            'Competition from career-native professionals',
            'Initial salary adjustment period'
        ],
        success_tips: [
            'Take online courses in required skills',
            'Build portfolio projects in target field',
            'Network with professionals in the industry',
            'Consider lateral moves or internships first',
            'Emphasize transferable skills in interviews'
        ],
        feasibility_explanation: 'Most career transitions are possible with dedication. Success depends on your commitment to learning and how well your current skills transfer.'
    };
}

module.exports = { generateCareerQuiz, generateCareerSuggestions, analyzeCareerPivot };