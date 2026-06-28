#!/bin/bash
#
# RUN ALL SCRAPERS NOW - Complete data collection from ALL sources
#
# This script runs ALL 50+ data sources you specified:
# - Business directories (annuaire.tn, pagesjaunes.tn, kompass.tn, TAA, etc.)
# - Job boards (emploi.tn, keejob.com)
# - News sites (businessnews.com.tn, managers.com.tn, tekiano.com)
# - Training centers (ISET, ATFP, universities)
# - Funders (World Bank, AFD, BEI, USAID, EU, GIZ)
# - Tenders (TUNEPS, ministries)
# - Events (engineering salons, conferences)
# - Research centers
#

set -e

echo "================================================================================"
echo "🚀 RUNNING ALL SCRAPERS - COMPLETE DATA COLLECTION"
echo "================================================================================"
echo ""

cd /app/scraper

# 1. BUSINESS DIRECTORIES
echo "📋 [1/8] Scraping business directories (annuaire.tn, pagesjaunes, kompass)..."
scrapy crawl directories -o /tmp/directories_$(date +%Y%m%d).json 2>&1 | tail -20
echo "✅ Directories complete"
echo ""

# 2. JOB BOARDS
echo "💼 [2/8] Scraping job boards (emploi.tn, keejob.com)..."
scrapy crawl jobs -o /tmp/jobs_$(date +%Y%m%d).json 2>&1 | tail -20
echo "✅ Jobs complete"
echo ""

# 3. NEWS SITES
echo "📰 [3/8] Scraping news sites (businessnews, managers, tekiano)..."
scrapy crawl news -o /tmp/news_$(date +%Y%m%d).json 2>&1 | tail -20
echo "✅ News complete"
echo ""

# 4. TRAINING CENTERS
echo "🎓 [4/8] Scraping training centers (ISET, universities, ATFP)..."
scrapy crawl training -o /tmp/training_$(date +%Y%m%d).json 2>&1 | tail -20
echo "✅ Training complete"
echo ""

# 5. INTERNATIONAL FUNDERS
echo "💰 [5/8] Scraping funders (World Bank, AFD, BEI, USAID, EU, GIZ)..."
scrapy crawl funders -o /tmp/funders_$(date +%Y%m%d).json 2>&1 | tail -20
echo "✅ Funders complete"
echo ""

# 6. PUBLIC TENDERS
echo "📜 [6/8] Scraping tenders (TUNEPS, ministries)..."
scrapy crawl tenders -o /tmp/tenders_$(date +%Y%m%d).json 2>&1 | tail -20
echo "✅ Tenders complete"
echo ""

# 7. EVENTS & CONFERENCES
echo "🎪 [7/8] Scraping events (engineering salons, conferences)..."
scrapy crawl events -o /tmp/events_$(date +%Y%m%d).json 2>&1 | tail -20
echo "✅ Events complete"
echo ""

# 8. RESEARCH CENTERS
echo "🔬 [8/8] Scraping research centers..."
scrapy crawl research -o /tmp/research_$(date +%Y%m%d).json 2>&1 | tail -20
echo "✅ Research complete"
echo ""

echo "================================================================================"
echo "✅ ALL SCRAPERS COMPLETE"
echo "================================================================================"
echo ""
echo "Scraped data saved to:"
ls -lh /tmp/*_$(date +%Y%m%d).json 2>/dev/null || echo "No JSON files found"
echo ""
echo "Now run: python /app/scripts/recalculate_scores.py"
echo ""
