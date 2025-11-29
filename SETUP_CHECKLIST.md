# ✅ Setup Checklist - Federated NL2SQL

Follow this checklist to get your modern full-stack application running.

## Prerequisites

- [ ] **Python 3.11 or 3.12** installed
- [ ] **Node.js 18+** and npm installed
- [ ] **MySQL databases** set up (software_db and frontend_db)
- [ ] **Code editor** (VS Code recommended)
- [ ] **Terminal** (PowerShell, bash, or Git Bash)

## Step 1: Backend Setup

### 1.1 Virtual Environment
- [ ] Navigate to project root directory
- [ ] Activate virtual environment:
  ```powershell
  .\shrm\Scripts\Activate.ps1
  ```

### 1.2 Install Backend Dependencies
- [ ] Install/upgrade pip:
  ```powershell
  python -m pip install --upgrade pip
  ```
- [ ] Install Flask and dependencies:
  ```powershell
  pip install -r backend/requirements.txt
  ```

### 1.3 Configure Environment
- [ ] Create `.env` file in project root (copy from example below)
- [ ] Update database credentials in `.env`
- [ ] Update Groq API key in `.env`

**Example .env file:**
```env
SOFTWARE_DB_HOST=localhost
SOFTWARE_DB_USER=root
SOFTWARE_DB_PASSWORD=your_password
SOFTWARE_DB_NAME=software_db

FRONTEND_DB_HOST=localhost
FRONTEND_DB_USER=root
FRONTEND_DB_PASSWORD=your_password
FRONTEND_DB_NAME=frontend_db

GROQ_API_KEY=your_groq_api_key
```

### 1.4 Test Backend
- [ ] Start Flask server:
  ```powershell
  python backend/app.py
  ```
- [ ] Verify it's running on http://localhost:5000
- [ ] Test health endpoint: http://localhost:5000/api/health
- [ ] You should see: `{"status":"healthy",...}`

## Step 2: Frontend Setup

### 2.1 Navigate to Frontend
- [ ] Open new terminal
- [ ] Navigate to frontend directory:
  ```bash
  cd frontend
  ```

### 2.2 Install Frontend Dependencies
- [ ] Install npm packages:
  ```bash
  npm install
  ```
- [ ] Wait for installation to complete (may take 2-5 minutes)

### 2.3 Configure Frontend (Optional)
- [ ] Create `.env` file in frontend directory (optional):
  ```env
  VITE_API_URL=http://localhost:5000
  ```
- [ ] Default is `http://localhost:5000`, so this step is optional

### 2.4 Test Frontend
- [ ] Start Vite dev server:
  ```bash
  npm run dev
  ```
- [ ] Verify it's running on http://localhost:3000
- [ ] Open browser to http://localhost:3000
- [ ] You should see the modern UI

## Step 3: Verify Full Stack

### 3.1 Test Query Execution
- [ ] Enter a test query in the UI:
  ```
  courses that teach React and jobs requiring React
  ```
- [ ] Click "Execute Query"
- [ ] Verify you see:
  - [ ] Loading state appears
  - [ ] SQL queries display
  - [ ] Results tables populate
  - [ ] AI-generated answer appears

### 3.2 Test Features
- [ ] Click example query buttons
- [ ] Toggle dark/light mode
- [ ] Copy SQL to clipboard
- [ ] Export results as CSV
- [ ] Export results as JSON
- [ ] Switch between tabs (Merged/Course/Job)

## Step 4: Alternative Startup (Automated)

### 4.1 Using Startup Scripts
- [ ] Close both terminal windows
- [ ] Run automated script:
  
  **PowerShell:**
  ```powershell
  .\start.ps1
  ```
  
  **Bash:**
  ```bash
  ./start.sh
  ```

- [ ] Verify both servers start automatically
- [ ] Access application at http://localhost:3000

## Troubleshooting

### Backend Issues

**Problem:** Import errors
- [ ] Solution: Activate virtual environment first
- [ ] Command: `.\shrm\Scripts\Activate.ps1`

**Problem:** Database connection errors
- [ ] Solution: Check `.env` file credentials
- [ ] Test: Connect to MySQL manually
- [ ] Verify: Database names are correct

**Problem:** Port 5000 already in use
- [ ] Solution: Kill process using port 5000
- [ ] Or change port in `backend/app.py`

### Frontend Issues

**Problem:** TypeScript errors in editor
- [ ] Solution: These are normal before `npm install`
- [ ] Run `npm install` to fix

**Problem:** Module not found errors
- [ ] Solution: Delete and reinstall:
  ```bash
  rm -rf node_modules package-lock.json
  npm install
  ```

**Problem:** Port 3000 already in use
- [ ] Solution: Vite will prompt to use different port
- [ ] Or kill process using port 3000

**Problem:** API connection errors
- [ ] Solution: Verify backend is running
- [ ] Check: http://localhost:5000/api/health
- [ ] Verify: No CORS errors in browser console

### CORS Issues

**Problem:** CORS policy errors in browser
- [ ] Solution: Verify Flask-CORS installed:
  ```powershell
  pip install Flask-CORS
  ```
- [ ] Check: `CORS(app)` is in `backend/app.py`
- [ ] Restart backend server

## Success Indicators

### Backend Running Successfully
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

### Frontend Running Successfully
```
  VITE v5.0.8  ready in XXX ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

### Application Working
- [ ] UI loads without errors
- [ ] Can submit queries
- [ ] Results appear correctly
- [ ] No console errors
- [ ] All features functional

## Next Steps After Setup

1. **Explore the UI**
   - Try different example queries
   - Test dark/light mode
   - Export some data

2. **Read Documentation**
   - [ ] `README_FRONTEND.md` - Full documentation
   - [ ] `QUICKSTART.md` - Quick reference
   - [ ] `frontend/DESIGN_SYSTEM.md` - UI design guide

3. **Customize (Optional)**
   - Modify colors in `tailwind.config.js`
   - Add new components
   - Adjust API endpoints

4. **Deploy (Production)**
   - Build frontend: `npm run build`
   - Set up production server (Nginx, etc.)
   - Configure environment variables

## Quick Reference Commands

### Backend
```powershell
# Start backend
.\shrm\Scripts\Activate.ps1
python backend/app.py

# Test API
curl http://localhost:5000/api/health
```

### Frontend
```bash
# Install
npm install

# Development
npm run dev

# Build
npm run build

# Preview build
npm run preview
```

### Both (Automated)
```powershell
# PowerShell
.\start.ps1

# Bash
./start.sh
```

## Completion

- [ ] All prerequisites met
- [ ] Backend running successfully
- [ ] Frontend running successfully
- [ ] Test query executed
- [ ] All features tested
- [ ] Documentation reviewed

**🎉 Congratulations! Your modern full-stack application is ready!**

---

**Need help?** Check the documentation or review error messages carefully.
