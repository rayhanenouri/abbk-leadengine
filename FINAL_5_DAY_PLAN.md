# Final 5-Day Delivery Plan — June 26-30, 2026

**Current Date**: June 24, 2026  
**Final Delivery**: June 30, 2026  
**Demo with Manager**: June 20 (already passed - need to show working product)

---

## ✅ What's DONE (80% Complete)

### M1: Foundation — 100% ✅
- Docker Compose (7 services)
- PostgreSQL database + 5 tables
- JWT authentication + RBAC
- FastAPI backend running
- React frontend running

### M2: Scraping — 95% ✅
- **NEW**: AI-powered universal scraper (Playwright + Claude API)
- 34 verified data sources integrated
- Celery tasks for automated scraping
- API endpoints ready
- **Waiting**: Docker build to complete (5 more minutes)

### M3: Scoring Engine — 100% ✅
- Rule-based weighted scoring per ABBK product
- Claude API signal extraction
- 121 leads scored (2,541 scores total)
- Hot lead detection algorithm
- Score recalculation working

### M4: Dashboard — 100% ✅
- Professional B2B frontend redesign
- Modern sidebar navigation
- Lead cards with scores
- Lead detail page with multi-product scoring
- Mobile-responsive
- 10+ pages built (Analytics, Live Signals, etc.)

---

## 🔥 What Needs To Be Done (Next 5 Days)

### Day 1: June 25 (Tomorrow) — DATA + APIFY
**Goal**: Get real production data into the system

**Morning (3 hours)**:
1. ✅ Docker build finishes → restart containers
2. Test universal scraper on 2-3 URLs manually
3. If working → trigger all 34 sources
4. Monitor scraping → should get 100-300 new leads

**Afternoon (3 hours)**:
1. Call ABBK manager → get Apify payment approved
2. Get APIFY_API_TOKEN
3. Run Apify LinkedIn scraper
4. Discover 50-100 Tunisia engineering companies
5. Merge Apify data with scraped data

**Evening (2 hours)**:
1. Run scoring on all new leads
2. Verify scores make sense
3. Check frontend displays correctly
4. Fix any bugs found

**Target**: 200-400 total leads by end of day

---

### Day 2: June 26 — QUALITY + TESTING
**Goal**: Make sure everything works perfectly

**Morning (3 hours)**:
1. Review all leads in database
2. Delete any junk/duplicate data
3. Verify company websites are real
4. Check that signals make sense
5. Ensure scores are reasonable

**Afternoon (3 hours)**:
1. Test all frontend pages
2. Test mobile responsiveness (manager uses phone!)
3. Fix any UI bugs
4. Test scoring engine with edge cases
5. Verify notifications work

**Evening (2 hours)**:
1. Write test scenarios for demo
2. Identify best 10-20 leads to show manager
3. Prepare talking points
4. Test full user journey (login → view leads → see scores → understand why)

**Target**: Zero critical bugs, demo-ready

---

### Day 3: June 27 — POLISH + PERFORMANCE
**Goal**: Make it fast and beautiful

**Morning (3 hours)**:
1. Optimize database queries (add indexes if needed)
2. Test with 500+ leads (performance)
3. Fix any slow pages
4. Add loading states where needed

**Afternoon (3 hours)**:
1. Final UI polish
   - Fix alignment issues
   - Consistent spacing
   - Professional color scheme
   - ABBK logo placement
2. Mobile testing (CRITICAL - manager uses phone)
3. Cross-browser testing

**Evening (2 hours)**:
1. Documentation:
   - User guide for ABBK manager
   - How to interpret scores
   - What each signal means
   - How to export leads
2. Screenshots for presentation

**Target**: Production-quality polish

---

### Day 4: June 28 — DEPLOYMENT + BACKUP
**Goal**: Deploy to Hetzner VPS + have backup plan

**Morning (4 hours)**:
1. Prepare Hetzner VPS (if not done)
2. Deploy full stack to production
3. Test production deployment
4. Configure Nginx properly
5. Set up SSL certificate (Let's Encrypt)
6. Test on public URL

**Afternoon (2 hours)**:
1. Set up Celery Beat automation
2. Verify scrapers run on schedule
3. Test scoring auto-recalculation
4. Monitor logs for errors

**Evening (2 hours)**:
1. Backup plan: If Hetzner has issues, run from localhost
2. Test localhost → ngrok → public URL
3. Prepare demo environment (clean data, good examples)
4. Final smoke test

**Target**: Working production deployment OR reliable localhost backup

---

### Day 5: June 29 — FINAL TESTING
**Goal**: Zero surprises on delivery day

**Morning (3 hours)**:
1. Full system test (end-to-end)
2. Test scraping → new leads appear
3. Test scoring → scores update
4. Test frontend → all pages work
5. Test mobile → manager's phone screen size

**Afternoon (3 hours)**:
1. Prepare demo walkthrough
2. Practice explaining:
   - How scoring works
   - Why Lead X is 85/100 (hot lead)
   - Why Lead Y is 30/100 (cold lead)
   - What signals mean
3. Prepare answers to likely questions:
   - "How often does it update?" → Every 6 hours for jobs, daily for directories
   - "Can I export to Excel?" → Yes (build this if not done)
   - "How do I know which company to call first?" → Sorted by score, hot leads on top

**Evening (2 hours)**:
1. Final data refresh (scrape all sources)
2. Recalculate all scores
3. Clean up any bad data
4. Set up demo account with good password
5. Write down credentials

**Target**: 100% confidence for June 30 delivery

---

### Day 6: June 30 — DELIVERY DAY 🎯
**Goal**: Successful handoff to ABBK

**Morning (2 hours)**:
1. Final smoke test
2. Verify all services running
3. Check data is current
4. Prepare laptop/screen for demo

**Midday (2 hours) - DEMO WITH MANAGER**:
1. Show login
2. Show dashboard with real Tunisia companies
3. Show lead detail page
4. Explain scoring system
5. Show mobile version
6. Answer questions
7. Hand over credentials

**Afternoon (2 hours)**:
1. Final documentation delivery
2. Show how to:
   - Add new leads manually
   - Run scrapers
   - Understand reports
3. Provide support contact info

**Evening**:
1. Celebrate! 🎉
2. Monitor for any immediate issues
3. Respond to manager's first questions

**Target**: Happy ABBK manager, successful project delivery

---

## Critical Success Factors

### MUST HAVE for June 30:
1. ✅ 200+ real Tunisia companies in database
2. ✅ Scores calculated for all companies
3. ✅ Scores make business sense (match ABBK priorities)
4. ✅ Frontend loads fast and looks professional
5. ✅ Mobile works perfectly (manager uses phone!)
6. ✅ Manager can log in and see leads immediately
7. ✅ Clear explanation of "why call this company"

### NICE TO HAVE (if time):
- Excel export
- Email notifications
- Advanced filters
- Charts/analytics
- Hetzner deployment (localhost is acceptable)

---

## Current Status Check

**As of June 24, 22:15**:
- ✅ AI-powered universal scraper built
- ✅ All 34 verified sources integrated
- ✅ Celery tasks configured
- ✅ API endpoints ready
- ✅ Frontend professional redesign complete
- ✅ Scoring engine working
- ⏳ Docker build in progress (installing Playwright)
- ⏳ Waiting to test scraper on real URLs
- ⏳ Waiting for Apify token (tomorrow)

**Blockers**: None  
**Risks**: None  
**Confidence**: 95% — on track for successful delivery

---

## What Could Go Wrong + Mitigation

### Risk 1: Scraper doesn't find data
**Mitigation**: 
- Use Apify LinkedIn as primary source (more reliable)
- Manual CSV import of ABBK existing database
- Already have 121 leads - can demo with those

### Risk 2: Hetzner deployment issues
**Mitigation**:
- Use localhost + ngrok for demo
- Deploy to Hetzner AFTER demo if needed
- Manager cares about functionality, not hosting

### Risk 3: Manager doesn't understand scoring
**Mitigation**:
- Prepare clear examples
- Show 3 leads: hot (85+), warm (50-70), cold (<50)
- Explain in business terms, not technical

### Risk 4: Mobile doesn't work well
**Mitigation**:
- Test on actual phone (not just browser dev tools)
- Manager uses phone - this is CRITICAL
- Fix mobile issues FIRST before desktop polish

---

## Daily Checklist Template

**Every morning**:
- [ ] Docker containers running
- [ ] Database accessible
- [ ] Backend health check passes
- [ ] Frontend loads
- [ ] No errors in logs

**Every evening**:
- [ ] Commit code
- [ ] Push to GitHub
- [ ] Update progress notes
- [ ] Plan tomorrow's tasks

---

## Emergency Contacts

**If stuck**:
1. Check CLAUDE.md for project context
2. Check PROGRESS.md for current status
3. Check backend logs: `docker logs abbk_backend`
4. Check worker logs: `docker logs abbk_worker`
5. Check database: `docker compose exec db psql -U abbk_user -d abbk_LeadEngine`

**Questions to ask yourself**:
- Does this help deliver a working product by June 30?
- Would the ABBK manager care about this feature?
- Is this a nice-to-have or must-have?
- Can I do this in 2 hours or less?

If NO to any → deprioritize or skip.

---

## Success Criteria (June 30)

**Manager can**:
- ✅ Log in to the platform
- ✅ See a list of Tunisia companies
- ✅ See which companies to call first (sorted by score)
- ✅ Understand WHY he should call them (signals)
- ✅ Use it on his phone
- ✅ Trust the recommendations

**Technical**:
- ✅ 200+ real leads in database
- ✅ All scores calculated correctly
- ✅ No critical bugs
- ✅ Fast page loads (<2 seconds)
- ✅ Mobile responsive
- ✅ Production-ready code quality

**Outcome**:
✅ ABBK manager uses this daily to identify sales opportunities  
✅ Rayhane Nouri delivers a working AI-powered lead generation platform  
✅ Strong portfolio piece for Dassault Systemes internship application

---

## You Got This! 💪

**5 days is plenty of time.**

You've already built 80% of the system. Now it's about:
1. Getting real data in
2. Making sure it works perfectly
3. Showing it to the manager

Focus on the goal: **ABBK manager can identify which companies to call and why.**

Everything else is secondary.

---

End of FINAL_5_DAY_PLAN.md
