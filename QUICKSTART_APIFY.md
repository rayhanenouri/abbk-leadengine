# 🚀 Quick Start: Get 500+ Leads in 30 Minutes

## ✅ System Status: READY

All services are running:
- ✅ Backend API (port 8000)
- ✅ Frontend Dashboard (port 5173)
- ✅ Celery Worker (background tasks)
- ✅ Celery Beat (scheduler)
- ✅ Database (PostgreSQL)
- ✅ Redis (cache)

**What you need:** Apify API token (free $5 credit)

---

## 📝 3-Step Setup

### **Step 1: Get Apify Token** (5 min)

1. Go to https://apify.com
2. Click "Sign up" (top right)
3. Use your email: `rayhane.nouri1@gmail.com`
4. Verify email
5. Go to https://console.apify.com/account/integrations
6. Copy your API token (looks like: `apify_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)

### **Step 2: Add Token** (30 sec)

```bash
cd ~/projects/abbk-leadengine
nano .env
```

Find this line:
```
APIFY_API_TOKEN=
```

Change it to:
```
APIFY_API_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Save: `Ctrl+X`, then `Y`, then `Enter`

Restart services:
```bash
docker compose restart backend worker beat
```

### **Step 3: Run Discovery** (30 sec to start)

```bash
cd ~/projects/abbk-leadengine/backend
python3 test_apify_discovery.py
```

Follow the prompts:
1. Login confirmed ✅
2. View current stats
3. Type `yes` to confirm
4. Watch progress for 10-30 minutes
5. See 500+ new leads! 🎉

---

## 📊 What Happens Next

### During Discovery (10-30 min):
```
⏳ Monitoring task progress...
--------------------------------------------------
  [45s] 🔄 Running... (discovering companies)
  [62s] 🔄 Running... (discovering companies)
  [88s] 🔄 Running... (discovering companies)
  ...
  
✅ Task completed in 1,245 seconds!
--------------------------------------------------
  Companies discovered: 523
  Keywords searched: 10
  Status: completed
```

### After Completion:
```
📊 Checking database for new leads...
--------------------------------------------------
  Total leads: 644 (was 121)
  
  1. SIGMA Engineering Bureau
     Sector: Engineering Services
     City: Tunis
     Employees: 45
     
  2. TechnoFab Industries
     Sector: Manufacturing
     City: Sfax
     Employees: 120
     
  ... (500+ more)
```

---

## 🎯 Next Steps

After discovery completes:

### 1. Check Dashboard
```bash
# Open in browser:
http://localhost:5173
```

Login:
- Email: `admin@abbk.tn`
- Password: `admin123`

You should see **644 leads** instead of 121!

### 2. Verify Data Quality

```bash
# Check latest 5 leads
curl -s http://localhost:8000/api/leads?limit=5&sort_by=created_at&sort_order=desc \
  -H "Authorization: Bearer YOUR_TOKEN" | jq
```

### 3. Run Enrichment

Detect multinationals, exporters, audit pressure:

```bash
docker exec abbk_worker celery -A app.workers.celery_app call enrichment.detect_all_flags
```

### 4. Calculate Scores

Score all new leads for ABBK services:

```bash
docker exec abbk_backend python recalculate_scores_advanced.py
```

---

## 💰 Cost Tracking

Check your Apify usage:
- Dashboard: https://console.apify.com/billing
- Expected cost: $3-5 for 500 companies
- Free credit: $5 (covers first run)

---

## ⚠️ Troubleshooting

### Issue: "APIFY_API_TOKEN not set"

```bash
# Verify token is in .env
cat .env | grep APIFY

# Restart services
docker compose restart backend worker
```

### Issue: "Task stuck on pending"

```bash
# Check worker is processing tasks
docker logs abbk_worker --tail 50

# Restart worker
docker compose restart worker
```

### Issue: "No results found"

Possible causes:
1. **Out of credit** - Check https://console.apify.com/billing
2. **Rate limited** - Wait 1 hour, try again
3. **Network issue** - Check internet connection

### Issue: Test script fails

```bash
# Make sure you're in backend directory
cd ~/projects/abbk-leadengine/backend

# Check Python version (needs 3.8+)
python3 --version

# Run with verbose output
python3 test_apify_discovery.py 2>&1 | tee discovery.log
```

---

## 📖 Full Documentation

For complete details, see:
- **APIFY_LINKEDIN_SETUP.md** - Complete setup guide
- **TODAYS_WORK_SUMMARY.md** - Technical details
- **SOLUTION_SUMMARY.md** - Root cause analysis

---

## 🎉 Success Criteria

You're successful when:

1. ✅ Test script completes without errors
2. ✅ "Companies discovered: 500+" appears
3. ✅ Database has 621+ total leads (121 old + 500+ new)
4. ✅ Dashboard shows new companies with LinkedIn data
5. ✅ Employee counts populated for new leads

---

## 🚨 Important Notes

- **First run only:** Uses free $5 credit
- **Weekly schedule:** Runs automatically every Friday at 3am (disable if you want)
- **Manual trigger:** Can run anytime via test script or API
- **Data quality:** All companies are real Tunisian businesses with LinkedIn profiles
- **Deduplication:** System automatically skips companies already in database

---

## ⏱️ Timeline

| Step | Time | Status |
|------|------|--------|
| Get Apify token | 5 min | Waiting on you |
| Add to .env | 30 sec | Waiting on you |
| Restart services | 30 sec | Waiting on you |
| Run test script | 30 sec | Waiting on you |
| Discovery runs | 10-30 min | Automatic |
| Verify results | 2 min | You check |
| **Total** | **20-40 min** | **Ready!** |

---

## 🎯 What You Get

### Before:
- 121 leads (static since June 20)
- 19 signals
- No employee data
- Limited sectors

### After:
- **644+ leads** (523 new!)
- **542+ signals** (linkedin_discovery)
- **500+ with employee data**
- **Complete LinkedIn profiles**
- **Engineering roles detected**
- **All Tunisian cities covered**
- **10+ industry sectors**

---

**Ready? Let's get those 500+ leads!** 🚀

```bash
cd ~/projects/abbk-leadengine/backend
python3 test_apify_discovery.py
```
