# Federated NL2SQL

**Modern Full-Stack Application** for executing natural language queries across federated databases with AI-powered ETL merging.

## 🌟 Features

- 🎨 **Modern React Frontend** with Tailwind CSS and shadcn/ui
- 🤖 **AI-Powered Query Decomposition** using Groq LLM
- 🔄 **Intelligent ETL Merging** (Innovation #1)
- 📊 **Interactive Data Visualization** with export capabilities
- 🌓 **Dark/Light Mode** support
- 📱 **Fully Responsive** design
- ⚡ **Real-time Results** with loading states

## 🚀 Quick Start

### Option 1: Automated Start (Recommended)

**PowerShell:**
```powershell
.\start.ps1
```

**Bash:**
```bash
./start.sh
```

### Option 2: Manual Start

**Terminal 1 - Backend:**
```powershell
.\shrm\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python backend/app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Then open **http://localhost:3000** in your browser.

## 📖 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get running in 3 steps
- **[Full Documentation](README_FRONTEND.md)** - Complete setup and features
- **[Frontend README](frontend/README.md)** - React app details

## 🎯 Usage

### Web Interface (Modern UI)
1. Open http://localhost:3000
2. Enter a natural language query
3. View generated SQL, results, and AI answer
4. Export data as CSV or JSON

### CLI (Legacy)
```powershell
.\shrm\Scripts\Activate.ps1
python run_demo.py "jobs that prefer female candidates"
```

## 🏗️ Architecture

```
┌─────────────────┐
│  React Frontend │  (Port 3000)
│  Vite + Tailwind│
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│   Flask API     │  (Port 5000)
│   Backend       │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│Course  │ │  Job   │
│  DB    │ │  DB    │
└────────┘ └────────┘
```

## 🛠️ Tech Stack

**Frontend:**
- React 18 + TypeScript
- Vite
- Tailwind CSS
- shadcn/ui components
- Lucide Icons (no emojis!)
- React Syntax Highlighter

**Backend:**
- Flask + Flask-CORS
- Groq LLM
- PyMySQL
- AI-driven ETL (Innovation #1)

## 📝 Notes

- **Innovation #1**: Executes AI-generated ETL snippets in a restricted sandbox. See `docs/SANDBOX.md` for security details.
- **Python Version**: Use Python 3.11 or 3.12 for best compatibility with `google-generativeai`
- **Environment**: Configure `.env` file with database credentials (see README_FRONTEND.md)

## 👥 Authors

- Aman Sharma (MT24013)
- Hariharan (MT24038)

## 📄 License

MIT License - See LICENSE file for details

---

**Need help?** Check [QUICKSTART.md](QUICKSTART.md) or the full documentation.
