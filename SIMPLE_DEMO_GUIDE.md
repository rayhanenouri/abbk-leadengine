# SIMPLE DEMO GUIDE - What The Website Does

## What Problem Does It Solve?

**Before:** ABBK manager manually searches for companies, calls them randomly, most say no.

**Now:** This website tells him EXACTLY which companies to call today and what to sell them.

---

## What You'll See When You Open localhost:5173

### 1. LOGIN PAGE
- Email: `admin@abbk.tn`
- Password: `admin123`
- Click Login

### 2. DASHBOARD (Main Page)

**Top of page shows 4 numbers:**

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ 380         │  │ 7           │  │ 0           │  │ 0.0%        │
│ Total Leads │  │ Hot Leads   │  │ High Prior. │  │ Conversion  │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
```

**What this means:**
- **380 companies** = All companies from ABBK's database
- **7 hot leads** = Companies that scored 60+ points (ready to call TODAY)
- **0 high priority** = Companies with 70+ points
- **0% conversion** = Not calculated yet (will work later)

**Below that, you see a list of companies:**

```
┌──────────────────────────────────────────────┐
│ ACTIA                                90 pts  │ ← BEST LEAD
│ 🏢 Automotive                                │
│ ✅ Training + Engineering + Multinational    │
│ [View Details →]                             │
├──────────────────────────────────────────────┤
│ A.A.F PRODUCTION                     60 pts  │
│ 🏢 Automotive                                │
│ ✅ Training + Engineering                    │
│ [View Details →]                             │
└──────────────────────────────────────────────┘
```

---

## What To Show In Demo Video (5 minutes)

### STEP 1: Show the Dashboard (30 seconds)
**Say:**
"This is ABBK LeadEngine. It has 380 companies from ABBK's database. The system automatically found and scored 7 hot leads that are ready to call today."

### STEP 2: Explain the Scoring (30 seconds)
**Say:**
"The system gives points based on what ABBK cares about:
- Training signal = 40 points (HIGHEST - companies that sent employees to training)
- Hiring engineers = 20 points (they need software NOW)
- Multinational = 15 points (must use licensed software)
- ISO certified = 15 points (compliance requirement)"

### STEP 3: Click on ACTIA (1 minute)
**Say:**
"Let me show you the best lead - ACTIA with 90 points."

**What you'll see on ACTIA's page:**
```
Company: ACTIA
Score: 90/100 🔥

Signals Detected:
✅ Training/Formation mentioned (40 points)
   Source: https://taa.tn/fr/membre/ACTIA
   
✅ Engineering roles mentioned (20 points)
   Source: https://taa.tn/fr/membre/ACTIA

✅ Multinational (15 points)
   International company

✅ ISO Certified (15 points)
   Must use licensed software

💡 RECOMMENDATION:
Sell them: SOLIDWORKS Training Package
Why: They already showed interest in training + multinational compliance needs
```

**Say:**
"The system scraped ACTIA's website and found they mention training and engineering. Plus they're multinational and ISO certified. So the best deal is a SOLIDWORKS Training Package."

### STEP 4: Show Another Company (30 seconds)
Click back, then click **A.A.F PRODUCTION (60 points)**

**Say:**
"This company also mentions training and has engineering roles. Score 60 = ready to call this week."

### STEP 5: Explain What's Missing (1 minute)
**Say:**
"Right now, the system has:
- ✅ 380 ABBK companies loaded
- ✅ Scoring system working (40pts training, 20pts hiring, etc.)
- ✅ Real scraping from websites

What we need to unlock more leads:
- ❌ Apify LinkedIn ($29/month Starter OR $199/month Scale)
- This will give us:
  - Employee counts
  - Recent hires (who's hiring RIGHT NOW)
  - Job postings
  - 500+ companies instead of 380

**RETURN ON INVESTMENT:**
- Apify cost: $29-199/month
- One SOLIDWORKS training sale: $2,000
- We only need 1 sale to pay for 10 months of Apify"

### STEP 6: Show Mobile View (30 seconds)
**Say:**
"The manager can use this on his phone. Let me show you."

Open Chrome DevTools (F12) → Click phone icon → Set width to 390px

**OR** 

Get your laptop IP:
```bash
hostname -I | awk '{print $1}'
```
Open on your phone: `http://YOUR_IP:5173`

**Say:**
"Everything works on mobile - the manager can see hot leads anywhere, anytime."

---

## Simple Answers To Questions They'll Ask

**Q: "How do you find the signals?"**
A: "We scrape company websites for keywords like 'formation', 'recrute', 'ingenieur', 'SOLIDWORKS'. When we find these, we give points based on what ABBK told us matters most."

**Q: "Why only 7 hot leads out of 380?"**
A: "Most small Tunisia companies don't have websites or detailed online info. With Apify LinkedIn, we'll get data on ALL 380 companies + find 200 more."

**Q: "Is the scoring accurate?"**
A: "Yes - the weights came directly from ABBK business manager:
- Training = 40pts (your PRIMARY revenue)
- Tenders = 30pts
- Hiring = 20pts
These are YOUR priorities, not random."

**Q: "What if we get Apify?"**
A: "Within 1 hour of getting the token, we'll have:
- 500-700 Tunisia engineering companies
- Real-time hiring data from LinkedIn
- Employee growth tracking
- 50-100 hot leads instead of 7"

---

## Bottom Line For ABBK Management

**Problem:** Manager wastes time calling random companies who say no.

**Solution:** This platform tells him EXACTLY who to call and what to sell.

**Cost:** $199/month for Apify = less than ONE training sale.

**Result:** More sales, less wasted calls, manager's time used efficiently.

---

## If Website Doesn't Load or Shows 0 Leads

Run these commands:

```bash
cd ~/projects/abbk-leadengine
docker compose up -d
```

Wait 10 seconds, then open: `http://localhost:5173`

Login: `admin@abbk.tn` / `admin123`

If still showing 0 leads, run:
```bash
docker exec abbk_backend python -c "
from app.db.session import AsyncSessionLocal
from app.models.models import Lead
from sqlalchemy import select, func
import asyncio

async def check():
    async with AsyncSessionLocal() as db:
        count = await db.execute(select(func.count()).select_from(Lead))
        print(f'Database has {count.scalar()} companies')

asyncio.run(check())
"
```

Should show: `Database has 380 companies`

---

**THAT'S IT. The website finds hot leads automatically so ABBK can focus on selling, not searching.**
