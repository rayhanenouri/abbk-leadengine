# ABBK LeadEngine — Demo Script for ABBK Manager
**Date:** June 20, 2026  
**Presenter:** Rayhane Nouri  
**Audience:** ABBK Business Manager

---

## DEMO OVERVIEW (30 seconds)
"This platform automatically finds and scores companies in Tunisia and North Africa that are ready to buy SOLIDWORKS licenses or training from ABBK. Instead of manually searching and cold calling, you now see exactly who to call today and what to offer them."

---

## LIVE DEMO (5 minutes)

### 1. Login (30 seconds)
**Open:** http://localhost:5173  
**Credentials:**
- Email: `admin@abbk.tn`
- Password: `admin123`

**Say:** "The platform is secure with role-based access. Managers like you see all leads and scores. Sales reps only see their assigned leads."

### 2. Dashboard Overview (1 minute)
**Point to stats bar:**
- Total Leads: 10 companies currently tracked
- High Priority: 8 leads (score 70+) — call these first
- Medium Priority: 2 leads (score 50+) — warm leads

**Say:** "The dashboard ranks every company automatically. Green badges = high priority = call today. Orange = medium priority = follow up next week."

### 3. Top Lead Example — BET-SCET (2 minutes)
**Point to first card:**
- Company: Bureau d'Études Technique BET-SCET
- Score: 95/100
- Sector: Engineering Consulting
- City: Tunis

**Read the reasoning:**
"HIGH PRIORITY - Score: 95/100. Sector 'Engineering Consulting' highly relevant. Located in Tunis. Has website - established company. Phone available. 🔥 Hiring engineers NOW - hot lead! Good fit for SOLIDWORKS Essential Training."

**Say:** "This is your best lead today. They are hiring mechanical engineers RIGHT NOW — that's a buying signal. Engineering consulting firms need SOLIDWORKS daily. Offer them training first since they have new hires to onboard."

### 4. Second Lead — Groupe Chimique Tunisien (1 minute)
**Point to second card:**
- Company: Groupe Chimique Tunisien
- Score: 95/100
- Sector: Chemical Manufacturing
- City: Gabès
- Best Service: SOLIDWORKS Standard

**Say:** "Chemical manufacturers need CAD for equipment design and pipe systems. Large national company, also hiring engineers. Perfect for SOLIDWORKS Standard license."

### 5. Filtering (30 seconds)
**Change filter to "70+ (High Priority)"**

**Say:** "You can filter to see only high priority leads when you're ready to call. Or set it to 'All Leads' to see everyone including research-stage companies."

---

## KEY FEATURES TO HIGHLIGHT

### ✅ What Works Right Now (Demo Day - June 20)
1. **Automated Lead Discovery:**
   - Scraped 29 Tunisian companies from business directories
   - More sources coming: job boards, news, LinkedIn, training centers

2. **Smart Scoring System:**
   - Every company gets a score 0-100 for each ABBK product
   - 14 different scores per lead (SOLIDWORKS, training programs, Abaqus, etc.)
   - Dashboard shows the BEST opportunity per company

3. **Buying Signals Detected:**
   - 🔥 Hiring engineers NOW — hottest signal
   - Engineering sector match (manufacturing, consulting, R&D)
   - Location in Tunis (easier to visit)
   - Established companies with websites and phone numbers

4. **Mobile Responsive:**
   - You can check this dashboard on your phone
   - See top leads while traveling

### 🚀 Coming in Next 10 Days (June 30 Delivery)
1. **More Data Sources:**
   - Job boards (emploi.tn, keejob.com) — who is hiring CAD engineers
   - Business news — who just got funding or won international contracts
   - LinkedIn — company size and employee roles
   - Ministry of Industry — public tenders requiring licensed software

2. **Advanced Signals:**
   - Multinational clients — forced to use licensed software
   - International audit pressure — cannot use cracked versions
   - Funding from bailleurs de fonds — projects requiring compliance
   - SOLIDWORKS logo detected on website — already using it

3. **Action Tracking:**
   - Mark leads as "called", "interested", "quoted", "converted"
   - Track which offers you sent to each company
   - Reminder system for follow-ups

4. **Production Deployment:**
   - Hosted on Hetzner VPS — accessible from anywhere
   - Daily automatic scraping — new leads appear every morning
   - Email alerts for high-priority signals

---

## BUSINESS IMPACT

### Current Manual Process:
1. Google "SolidWorks Tunisia" on SolidWorks website
2. See company names — no context
3. Call blindly — most hang up if using cracked version
4. No system to prioritize or track

### New Process with LeadEngine:
1. Open dashboard on phone or computer
2. See ranked list of companies ready to buy
3. Know exactly what to offer and why they will say yes
4. Call only high-priority leads — better conversion rate

### Example Real Lead from Dashboard:
**BET-SCET (95/100):**
- Engineering consulting firm in Tunis
- Hiring engineers RIGHT NOW
- Strategy: Offer SOLIDWORKS Essential Training for new hires first
- Then upsell SOLIDWORKS licenses once they are trained
- DO NOT lead with legal threats — lead with training value

**Groupe Chimique Tunisien (95/100):**
- Large chemical manufacturer
- Hiring engineers
- Strategy: Offer SOLIDWORKS Standard for equipment and piping design
- Mention compliance and international standards

---

## TECHNICAL STACK (for reference)
- Backend: FastAPI Python with PostgreSQL database
- Frontend: React with modern responsive design
- Scraping: Automated scrapers running daily
- Scoring: Rule-based algorithm (upgrading to AI signals soon)
- Hosting: Docker containers, ready for cloud deployment

---

## QUESTIONS TO EXPECT

**Q: How accurate are the scores?**  
A: Right now it's rule-based — sector match + location + hiring signals + company size. It's conservative but accurate. We are adding Claude AI to extract more nuanced signals from company news and job postings.

**Q: Can I add my own companies?**  
A: Yes! There is a CSV import feature. You can upload your existing ABBK database and the system will score them all.

**Q: What about companies using cracked SolidWorks?**  
A: The system detects potential cracked users (has engineers but no license signals). We score them LOWER for direct license sales but HIGHER for training. Strategy: lead with training offer first, then upsell licenses.

**Q: When can we go live?**  
A: Demo MVP is ready today (June 20). Full production version with all scrapers and cloud deployment: June 30.

**Q: How much does this cost ABBK?**  
A: This is a custom-built platform for ABBK. Hosting cost is about $10/month on Hetzner VPS. No per-user fees, no SaaS subscription.

---

## NEXT STEPS AFTER DEMO

1. **Feedback from Manager:**
   - Which features are most important?
   - Any specific data sources you want added?
   - Which ABBK products should we prioritize scoring?

2. **June 21-30 Development:**
   - Add job board scrapers for hiring signals
   - Add business news scrapers for funding and export signals
   - Add LinkedIn connector for company enrichment
   - Deploy to Hetzner VPS for production access

3. **Go Live June 30:**
   - Import ABBK's existing company database
   - Run full scraping on all Tunisian and North African data
   - Train ABBK sales team on platform usage
   - Hand over credentials and documentation

---

## DEMO CREDENTIALS

**Dashboard:** http://localhost:5173  
**Login:** admin@abbk.tn  
**Password:** admin123

**Backend API:** http://localhost:8000  
**API Health Check:** http://localhost:8000/health  
**API Docs:** http://localhost:8000/docs

---

## BACKUP DATA (if demo questions arise)

**Total Companies in Database:** 29  
**Total Scores Calculated:** 406 (29 companies × 14 ABBK services)  
**ABBK Services Scored:**
1. SOLIDWORKS Standard
2. SOLIDWORKS Simulation
3. SOLIDWORKS Flow Simulation
4. SOLIDWORKS Plastics
5. SOLIDWORKS PDM
6. SOLIDWORKS CAM + CAMWorks
7. SOLIDWORKS Electrical
8. SOLIDWORKS Essential Training
9. SOLIDWORKS Professional Training
10. SOLIDWORKS Certification Prep (CSWA/CSWP)
11. Abaqus Training
12. CAMWorks Training
13. 3DEXPERIENCE Training
14. STEM Education Programs

**Top 5 Leads by Score:**
1. Bureau d'Études Technique BET-SCET — 95/100
2. Groupe Chimique Tunisien — 95/100
3. Auto Hall Tunisia — 90/100
4. Telnet Tunisie Sableblastingmac — 80/100
5. Société Tunisie Autoroutes (STA) — 80/100

---

**Good luck with the demo! You are 2 days ahead of schedule and the platform looks professional.**
