# 🚀 QUICK START GUIDE

## How to Run the Project

### Option 1: Direct Open (Easiest)
1. Double-click `index.html` to open in browser
2. Click "📤 Upload Dataset"
3. Upload `drivers.json` and `riders.json`
4. View dashboard automatically

### Option 2: Local Server (Better)
```powershell
# In project folder
python -m http.server 8000
```
Then open: http://localhost:8000

---

## What You'll See

### 1️⃣ Homepage (index.html)
- Neon glowing hero section
- Project description
- Upload button → takes you to upload page

### 2️⃣ Upload Page (upload.html)
- Two file upload boxes
- Validates JSON structure
- Shows success/error messages
- Auto-redirects to dashboard

### 3️⃣ Dashboard (dashboard.html)
- **4 Metric Cards**: Driver count, Rider count, Matches, Avg rating
- **Bar Chart**: Drivers vs Riders comparison
- **Pie Chart**: Vehicle type distribution
- **Match List**: Top 3 driver recommendations for each rider
- **Export Button**: Download results as JSON

---

## Sample Data Included

- **drivers.json**: 15 drivers with varied locations, vehicles, ratings
- **riders.json**: 8 riders with different preferences and urgency

---

## Features Implemented

✅ Haversine distance calculation  
✅ Smart match scoring algorithm  
✅ Traffic zone weighting  
✅ Urgency-based prioritization  
✅ Vehicle preference matching  
✅ Input validation & error handling  
✅ Chart.js visualizations  
✅ Export to JSON  
✅ Fully responsive design  
✅ Neon/glass UI with animations  

---

## Scoring Formula

**Final Score** = (Distance Score + Vehicle Bonus + Rating Bonus) × Traffic Weight × Urgency Weight

- Distance Score: 0-100 (closer = higher)
- Vehicle Match: +30 points
- Rating Bonus: 0-25 points (based on 0-5 stars)
- Traffic Weight: 0.75× to 1.0×
- Urgency Weight: 0.8× to 1.3×

---

## Project Structure

```
RDM/
├── index.html           # Landing page
├── upload.html          # Upload interface
├── dashboard.html       # Analytics dashboard
├── assets/
│   ├── styles.css       # Neon styling
│   ├── upload.js        # File processing
│   └── dashboard.js     # Matching logic
├── drivers.json         # Sample drivers
├── riders.json          # Sample riders
└── README.md            # Full documentation
```

---

## Perfect For

✓ Academic projects (mini/major)  
✓ Viva demonstrations  
✓ Lab exams  
✓ Portfolio showcase  
✓ Learning algorithms  

---

## Troubleshooting

**Charts not showing?**
→ Check internet (Chart.js from CDN)

**No matches found?**
→ Ensure drivers have `status: "available"`

**Invalid JSON error?**
→ Validate at jsonlint.com

---

Made with ❤️ using HTML, CSS, JavaScript
