# Federated NL2SQL - Modern Full-Stack Application

A modern full-stack application for executing natural language queries across federated databases with AI-powered ETL merging.

## 🚀 Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Beautiful, accessible component library
- **Lucide Icons** - Modern icon set
- **React Syntax Highlighter** - SQL syntax highlighting
- **Axios** - HTTP client

### Backend
- **Flask** - Python web framework
- **Flask-CORS** - Cross-origin resource sharing
- **Groq LLM** - AI model for query decomposition
- **PyMySQL** - MySQL database connector
- **Innovation #1** - AI-driven ETL merging

## 📁 Project Structure

```
federated-nl2sql/
├── backend/
│   ├── app.py                 # Flask API server
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── ui/           # shadcn/ui base components
│   │   │   ├── QueryInput.tsx
│   │   │   ├── SQLDisplay.tsx
│   │   │   ├── ResultsTable.tsx
│   │   │   ├── FinalAnswer.tsx
│   │   │   └── ThemeToggle.tsx
│   │   ├── lib/
│   │   │   ├── api.ts        # API client
│   │   │   └── utils.ts      # Utility functions
│   │   ├── App.tsx           # Main app component
│   │   ├── main.tsx          # Entry point
│   │   └── index.css         # Global styles
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
├── executor.py               # Database executor
├── query_analyzer.py         # Query analysis
├── innovation1.py            # AI-ETL merging
├── groq_client.py           # LLM client
└── [other Python modules]
```

## 🛠️ Setup Instructions

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** and npm
- **MySQL databases** (configured in .env)

### 1. Backend Setup

```bash
# Navigate to project root
cd "e:\Aman Sharma & Hariharan(MT24013 & MT24038)\Aman Sharma & Hariharan(MT24013 & MT24038)\federated-nl2sql"

# Activate virtual environment (if using shrm)
.\shrm\Scripts\Activate.ps1

# Install backend dependencies
pip install -r backend/requirements.txt

# Set up environment variables
# Create .env file with database credentials
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file (optional)
cp .env.example .env
# Edit .env if needed (default API URL: http://localhost:5000)
```

## 🚀 Running the Application

### Development Mode

**Terminal 1 - Backend (Flask API):**
```bash
# From project root
.\shrm\Scripts\Activate.ps1
python backend/app.py
```
Backend will run on: `http://localhost:5000`

**Terminal 2 - Frontend (Vite Dev Server):**
```bash
# From frontend directory
cd frontend
npm run dev
```
Frontend will run on: `http://localhost:3000`

### Production Build

```bash
# Build frontend
cd frontend
npm run build

# Serve built files with Flask (modify backend/app.py to serve static files)
# Or use a production server like Nginx
```

## 📡 API Endpoints

### Health Check
```
GET /api/health
```

### Execute Query
```
POST /api/query
Content-Type: application/json

{
  "query": "courses that teach React and jobs requiring React",
  "max_rows": 100
}
```

### Batch Queries
```
POST /api/query/batch
Content-Type: application/json

{
  "queries": ["query1", "query2"],
  "max_rows": 50
}
```

### Get Examples
```
GET /api/fallback-examples
```

## 🎨 Features

### Modern UI/UX
- ✨ **Glassmorphism design** with backdrop blur
- 🌓 **Dark/Light mode** toggle
- 📱 **Responsive layout** - works on all devices
- 🎭 **Smooth animations** with Framer Motion
- 🎨 **Gradient accents** and modern color palette

### Functional Features
- 🔍 **Natural language query input**
- 💾 **SQL syntax highlighting** with copy-to-clipboard
- 📊 **Interactive data tables** with sorting
- 📥 **Export results** as CSV or JSON
- 🤖 **AI-generated final answers**
- ⚡ **Real-time loading states**
- ❌ **Error handling** with user-friendly messages

### Components

#### QueryInput
- Natural language text area
- Example query suggestions
- Loading state handling

#### SQLDisplay
- Tabbed SQL view (Course DB / Job DB)
- Syntax highlighting
- Copy to clipboard functionality

#### ResultsTable
- Tabbed results view (Merged / Course / Job)
- Row count indicators
- CSV/JSON export buttons
- Scrollable tables with sticky headers

#### FinalAnswer
- AI-generated natural language answer
- Gradient background styling
- Message bubble design

## 🔧 Configuration

### Environment Variables

**Backend (.env in project root):**
```env
# Database Configuration
SOFTWARE_DB_HOST=localhost
SOFTWARE_DB_USER=root
SOFTWARE_DB_PASSWORD=yourpassword
SOFTWARE_DB_NAME=software_db

FRONTEND_DB_HOST=localhost
FRONTEND_DB_USER=root
FRONTEND_DB_PASSWORD=yourpassword
FRONTEND_DB_NAME=frontend_db

# Groq API
GROQ_API_KEY=your_groq_api_key
```

**Frontend (frontend/.env):**
```env
VITE_API_URL=http://localhost:5000
```

## 🎯 Usage Examples

### Example Queries
1. "courses that teach React and frontend jobs requiring React"
2. "compare software engineering courses that teach cloud skills with frontend jobs"
3. "list courses for BTech graduates and frontend roles that accept BTech"
4. "frontend jobs with remote work and software courses offering online delivery"

## 🐛 Troubleshooting

### Backend Issues
- **Import errors:** Ensure virtual environment is activated
- **Database connection:** Check .env credentials
- **CORS errors:** Verify Flask-CORS is installed

### Frontend Issues
- **Module not found:** Run `npm install` again
- **API connection:** Check backend is running on port 5000
- **Build errors:** Clear node_modules and reinstall: `rm -rf node_modules && npm install`

## 📦 Deployment

### Frontend (Static Hosting)
```bash
cd frontend
npm run build
# Deploy dist/ folder to Vercel, Netlify, or any static host
```

### Backend (Python Hosting)
```bash
# Use Gunicorn for production
pip install gunicorn
gunicorn -w 4 backend.app:app
```

## 🔐 Security Notes

- Never commit `.env` files
- Use environment variables for sensitive data
- Enable HTTPS in production
- Implement rate limiting for API endpoints
- Validate and sanitize all inputs

## 📄 License

MIT License - See LICENSE file for details

## 👥 Authors

- Aman Sharma (MT24013)
- Hariharan (MT24038)

---

**Need help?** Check the documentation or raise an issue in the repository.
