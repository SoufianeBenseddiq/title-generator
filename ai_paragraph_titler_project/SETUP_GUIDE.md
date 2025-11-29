# 🚀 Quick Setup Guide - AI Paragraph Titler Backend

Follow these steps to get your backend running:

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] MySQL Server installed and running
- [ ] Git (optional, if cloning)

---

## Step-by-Step Setup

### 1️⃣ Navigate to Backend Directory

```powershell
cd ai_paragraph_titler_project
```

### 2️⃣ Activate Virtual Environment

Since you already have a `venv` folder, activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again.

### 3️⃣ Install/Update Dependencies

```powershell
pip install -r requirements.txt
```

### 4️⃣ Set Up MySQL Database

**Option A: Using MySQL Command Line**

```powershell
mysql -u root -p
```

Then run:
```sql
source setup_database.sql
```

Or copy-paste the SQL from `setup_database.sql` file.

**Option B: Using MySQL Workbench**

1. Open MySQL Workbench
2. Connect to your MySQL server
3. Open `setup_database.sql` file
4. Execute the script

### 5️⃣ Create `.env` File

Create a `.env` file in the `ai_paragraph_titler_project` directory:

```powershell
New-Item .env
```

Edit the `.env` file and add:

```env
# Security - CHANGE THIS to a random string!
SECRET_KEY=your-super-secret-key-change-this-to-random-string-123456789

# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password_here
DB_NAME=paragraph_titler_db
```

**⚠️ Important:**
- Replace `your_mysql_password_here` with your actual MySQL root password
- Change `SECRET_KEY` to a random secure string (you can generate one online)

### 6️⃣ Verify Model Files

Make sure the AI model directory exists:
```
ai_paragraph_titler_project/
├── ai_paragraph_titler_model/
│   ├── config.json
│   ├── model.safetensors
│   ├── tokenizer_config.json
│   └── ... (other model files)
```

### 7️⃣ Run the Backend

```powershell
python main.py
```

The server should start at: **http://localhost:8000**

---

## ✅ Verify It's Working

1. **Health Check:**
   Open browser: http://localhost:8000

2. **API Documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. **Test Registration:**
   Go to http://localhost:8000/docs and try the `/register` endpoint

---

## 🐛 Troubleshooting

### MySQL Connection Error
- Make sure MySQL is running: `net start MySQL80` (Windows)
- Check your password in `.env` file
- Verify database exists: `SHOW DATABASES;` in MySQL

### Model Loading Error
- Check that `ai_paragraph_titler_model` folder exists
- Verify all model files are present

### Port Already in Use
- Change port in `main.py` (line 612): `port=8001`

### Virtual Environment Issues
- If venv doesn't work, create a new one:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```

---

## 📝 Next Steps

Once the backend is running, you can:
1. Test the API using the Swagger UI at http://localhost:8000/docs
2. Link it with your React frontend (we'll do this next)

---

**Need Help?** Check the main `README.md` for more detailed information.

