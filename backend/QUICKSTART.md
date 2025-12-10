# 🚀 PySpark Backend Quick Start

## Installation (1 Minute)

### Windows
```powershell
cd backend
.\start.bat
```

### Unix/Linux/macOS
```bash
cd backend
chmod +x start.sh
./start.sh
```

Server starts at **http://localhost:5000**

---

## Test It (30 Seconds)

```bash
# Run test suite
python test_matcher.py
```

---

## API Examples

### Upload Data
```bash
curl -X POST http://localhost:5000/api/upload \
  -H "Content-Type: application/json" \
  -d '{
    "drivers": [...],
    "riders": [...]
  }'
```

### Get Matches
```bash
curl http://localhost:5000/api/match
```

### Get Analytics
```bash
curl http://localhost:5000/api/analytics
```

---

## Architecture

```
Frontend (JS) ←→ REST API ←→ PySpark Engine
  Still works      Flask      Matching Logic
  independently                (Identical Algorithm)
```

---

## Key Points

✅ **No Frontend Changes** - All existing code preserved  
✅ **Same Algorithm** - 100% identical matching logic  
✅ **Scalable** - Handle thousands of records  
✅ **Optional** - Frontend works standalone  

---

## Files Created

- `spark_matcher.py` - PySpark matching engine
- `app.py` - Flask REST API
- `requirements.txt` - Dependencies
- `config.ini` - Settings
- `start.bat/.sh` - Startup scripts
- `test_matcher.py` - Test suite
- `README.md` - Full documentation

---

**See `backend/README.md` for complete documentation**
