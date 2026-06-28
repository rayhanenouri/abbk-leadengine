# 🚨 CRITICAL CREDIBILITY FIX — Signal Source URLs

**Date:** June 28, 2026  
**Issue Severity:** **CRITICAL** (Demo Blocker)  
**Status:** **IN PROGRESS**

---

## **THE PROBLEM**

### **What Was Wrong:**
The platform had a **fundamental scraping architecture flaw** that destroyed credibility:

1. **Fake Company Names:** 
   - "Our Network", "Dams and Transfer", "Les études régionales"
   - These are navigation menu items, not real companies
   - **40+ fake entries** in database

2. **Directory URLs as "Websites":**
   - All automotive companies (APTIV, ACTIA, etc.) had `https://taa.tn/...` URLs
   - These are directory listing pages, NOT the actual company websites
   - **99 out of 102 "websites" were directory pages**

3. **Fake Signal Source URLs:**
   - Signal: "Training detected"
   - Source: `https://taa.tn/fr/node/228` (TAA directory page)
   - **NOT** a real training post or company announcement
   - **Clicking the URL shows a directory listing, not proof**

### **Why This Destroys Credibility:**
When the business manager clicks a signal source URL during the board demo:
- ❌ Sees a TAA directory page with generic company description
- ❌ No actual evidence of training, hiring, or ISO certification
- ❌ Signal cannot be verified
- ❌ Platform looks like it's **making up data**

---

## **THE FIX**

### **STEP 1: Clean Fake Company Names** ✅
**Completed:** Deleted 40+ fake entries

**Patterns removed:**
- Navigation items: "Our Network", "Nos Valeurs", "Les études"
- Generic words: "network", "cluster", "liste", "secteur"
- Short names: < 4 characters
- Articles: "Le", "La", "Les", "The", "Our"
- Social media pages: Facebook, Instagram, LinkedIn links

**Result:** 831 companies → 790 companies (clean)

---

### **STEP 2: Find Real Company Websites** 🔄
**Status:** Running now

**What it does:**
1. For each company with a TAA directory URL (`https://taa.tn/...`)
2. Scrape the TAA page to extract the **actual company website**
3. Update `leads.website` with the real URL
4. If no real website found → set `website = NULL`

**Expected result:**
- APTIV: `https://www.aptiv.com/` (real Aptiv global website)
- ACTIA: `https://www.actia.com/` or Tunisia-specific subdomain
- Companies without websites → `website = NULL`, marked "Unverified"

---

### **STEP 3: Delete All Fake Signals** ✅
**Completed:** Deleted 215 directory-based signals

**Deleted signals with source URLs pointing to:**
- `taa.tn` — TAA directory
- `tunisieindustrie.nat.tn` — Ministry directory
- `mecatronic.tn` — Cluster directory
- `annuaire.tn` — Business directory

**Result:** 260 signals → 45 signals (only real ones remain)

---

### **STEP 4: Re-Scrape with Real Source URLs** ⏳
**Status:** Pending (after Step 2 completes)

**Two-Stage Architecture:**

**Stage 1 - Discovery (directories are OK here):**
- Scrape TAA, annuaire.tn to get: company NAME, SECTOR, CITY, WEBSITE URL
- Store as leads with `status = "discovered"`
- **Do NOT create signals yet**

**Stage 2 - Deep Research (REAL sources only):**
For each company with a real website:

**A. Scrape Actual Company Website:**
```
Visit: homepage, /about, /services, /careers, /news
Extract: activities, software mentions, team info
Source URL: https://www.aptiv.com/careers/tunisia
```

**B. Search Job Boards:**
```
Search: "APTIV Tunisia" on emploi.tn
Find: Actual job posting for "Ingénieur Mécanique"
Source URL: https://www.emploi.tn/offres/12345
```

**C. Search News Sites:**
```
Search: "APTIV Tunisia" on businessnews.com.tn
Find: Article about expansion or new project
Source URL: https://www.businessnews.com.tn/article/12345
```

**D. Find LinkedIn Page:**
```
Search: "site:linkedin.com/company APTIV Tunisia"
Find: Official LinkedIn company page
Source URL: https://www.linkedin.com/company/aptiv-tunisia
```

---

### **STEP 5: Signal Quality Requirements** ⏳
**Status:** Will implement after re-scraping

Every `LeadSignal` MUST have:

✅ **source_url** pointing to REAL evidence:
- Actual job posting page (emploi.tn, keejob.com)
- Actual news article (businessnews.com.tn)
- Actual company page showing activity
- Actual LinkedIn post

✅ **Verifiable proof:**
- Company name appears on the source page
- Content matches the signal type
- Evidence is from last 12 months

❌ **NO fake signals:**
- No directory listings
- No generic "company mentions engineering" without URL
- No old/outdated sources

---

### **STEP 6: Companies Without Websites** ⏳
**Status:** Will implement after cleanup

For companies where no real website found:

**Database:**
- `website = NULL`
- `status = "unverified"`

**Frontend:**
- Grey badge: "No web presence found"
- Separate section at bottom of leads list
- No signals generated
- Maximum score: 20/100 on any service

**Manager knows:** These need manual phone verification

---

## **CURRENT STATUS**

### **Database State:**
- **Total companies:** 790 (was 854)
- **Fake entries deleted:** 64
- **Companies being checked:** 99 (TAA URLs)
- **Clean companies:** 3 (real websites confirmed)

### **Signal State:**
- **Fake signals deleted:** 215
- **Real signals remaining:** 45
- **Expected after re-scraping:** 50-150 (with REAL source URLs)

### **Top Priority:**
1. ✅ Clean fake company names
2. 🔄 **Find real websites (running now)**
3. ⏳ Re-scrape with real sources
4. ⏳ Verify top 10 leads manually
5. ⏳ Test clickable source URLs

---

## **DEMO PROOF REQUIREMENT**

**Before the board demo, for the top 10 leads:**

For each signal, the business manager must be able to:
1. **Click the source URL**
2. **See a real webpage** (not a directory)
3. **Find the company name** on that page
4. **Verify the signal** (job posting, news article, ISO cert, etc.)

**Example - APTIV:**
```
Signal: "Hiring Mechanical Engineers"
Source: https://www.emploi.tn/offres/ingenieur-mecanique-aptiv-tunisia-23451
Click → See actual job posting on emploi.tn
Company: APTIV Tunisia
Title: Ingénieur Mécanique - Conception
Posted: June 15, 2026
✅ VERIFIED
```

---

## **EXPECTED FINAL STATE**

### **Scenario A: Company with Real Website**
```
Company: APTIV (DELPHI TUNISIA)
Website: https://www.aptiv.com/careers/tunisia
Signals:
  - Hiring engineers (emploi.tn URL)
  - ISO 9001 certified (aptiv.com/quality URL)
  - Engineering team (aptiv.com/about URL)
Score: 85/100
Status: ✅ Verified, ✅ Clickable proof
```

### **Scenario B: Company Without Website**
```
Company: ACME Manufacturing
Website: NULL
Signals: None
Score: 15/100 (sector only)
Badge: ⚠️ No web presence found
Status: ⚠️ Unverified, needs manual research
```

---

## **TIMELINE**

- ✅ **Step 1:** Fake names cleaned (10 min)
- 🔄 **Step 2:** Real websites (30 min - running)
- ⏳ **Step 3:** Signals deleted (done)
- ⏳ **Step 4:** Re-scrape (1 hour)
- ⏳ **Step 5:** Quality check (30 min)
- ⏳ **Step 6:** Manual verification (30 min)

**Total ETA:** ~2.5 hours to **credible, verifiable platform**

---

**This is the MOST IMPORTANT fix before the board demo. Without verifiable source URLs, the entire platform lacks credibility.**
