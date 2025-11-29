# Quick Start Guide - Federated NL2SQL

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```powershell
# Backend
.\shrm\Scripts\Activate.ps1
pip install -r backend/requirements.txt

# Frontend (new terminal)
cd frontend
npm install
```

### Step 2: Start Backend

```powershell
# Terminal 1
.\shrm\Scripts\Activate.ps1
python backend/app.py
```

### Step 3: Start Frontend

```powershell
# Terminal 2
cd frontend
npm run dev
```

### Step 4: Open Browser

Navigate to: **http://localhost:3000**

---

## 📋 Available Scripts

### Frontend (`frontend/` directory)
```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

### Backend (project root)
```bash
python backend/app.py              # Start Flask server
python run_demo.py "your query"    # CLI demo
```

---

## 🎨 UI Features

- **Modern glassmorphism design**
- **Dark/Light mode** (toggle in header)
- **Syntax-highlighted SQL** with copy button
- **Export results** as CSV or JSON
- **Responsive design** - works on mobile
- **Lucide icons** throughout (no emojis!)

---

## 💡 Example Queries

Try these in the app:

1. `courses that teach React and frontend jobs requiring React`
2. `compare software courses with cloud skills and frontend jobs`
3. `list courses for BTech graduates and matching jobs`
4. `frontend jobs with remote work options`

---

## 🆘 Troubleshooting

**Backend not connecting?**
- Check if Flask is running on port 5000
- Verify .env database credentials

**Frontend errors?**
- Run `npm install` again
- Clear cache: `rm -rf node_modules && npm install`

**CORS issues?**
- Ensure Flask-CORS is installed
- Check backend/app.py has `CORS(app)`

---

See **README_FRONTEND.md** for complete documentation.
