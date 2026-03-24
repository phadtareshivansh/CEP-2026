# Saarthi - Find Pathway to Your Interests

A career guidance and assessment tool built with Django and Node.js, powered by Google's Generative AI (Gemini API).

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- pip
- npm

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Saarthi - Find Pathway to Your Interests"
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your actual values:
   - Generate a Django SECRET_KEY
   - Add your Google Gemini API key
   - Set admin credentials

3. **Python Setup**
   ```bash
   # Create and activate virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run migrations
   python manage.py migrate
   
   # Create admin user
   python create_admin.py
   
   # Collect static files (optional for development)
   python manage.py collectstatic --noinput
   ```

4. **Node.js Setup**
   ```bash
   cd server
   npm install
   ```

5. **Run the application**
   
   **Terminal 1 - Django Backend:**
   ```bash
   python manage.py runserver
   ```
   
   **Terminal 2 - Node.js Server:**
   ```bash
   cd server
   npm start
   ```

   Access the application at `http://localhost:8000`

## 📁 Project Structure

```
.
├── quiz/                 # Django REST app
├── saarthi/             # Django project settings
├── server/              # Node.js Express server
│   ├── app.js          # Express application
│   ├── ai-logic.js     # Gemini API integration
│   └── routes.js       # API routes
├── templates/          # HTML templates
├── static/            # CSS/JS assets
├── requirements.txt   # Python dependencies
├── package.json       # Node.js dependencies
├── .env.example       # Environment variables template
├── .gitignore         # Git ignore rules
└── manage.py          # Django management script
```

## 🔒 Security Notes

- Never commit `.env` files to version control
- Keep `SECRET_KEY` secret - generate a new one for production
- Rotate API keys regularly
- Set `DEBUG=False` in production
- Use HTTPS in production
- Add your production domain to `ALLOWED_HOSTS`

## 🛠 Development

### Available Django Commands
```bash
# Create admin user
python create_admin.py

# Run migrations
python manage.py migrate

# Create new migration
python manage.py makemigrations

# Access admin panel
# Login at: http://localhost:8000/admin
```

### Environment Variables
See `.env.example` for all available configuration options.

## 🤖 AI Features

The application uses Google's Generative AI (Gemini API) to:
- Generate personalized career discovery questions
- Provide job recommendations based on RIASEC assessment

If the API key is not configured, the app falls back to mock data.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and commit them (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure:
- Code follows the existing style
- All tests pass
- New features include documentation
- Security best practices are maintained

## 📧 Support

For questions or issues, please open a GitHub issue or contact the maintainers.
