# ABBK LeadEngine - Data Sources Research

## VERIFIED WORKING SOURCES ✅

### News & Business Intelligence
- ✅ **businessnews.com.tn** - Tunisian business news (200 OK)
- ✅ **tekiano.com** - Tech and business news Tunisia (200 OK)
- ⚠️ **managers.com.tn** - Timeout (may work with retry)

### Job Boards
- ✅ **keejob.com** - Job listings Tunisia (200 OK)
- ✅ **linkedin.com/jobs** - LinkedIn jobs (200 OK - via Apify)
- ⚠️ **emploi.tn** - SSL certificate issue (needs different approach)

### Business Directories
- ❌ **annuaire.tn** - DNS failure (domain doesn't exist or geo-restricted)
- ❌ **pagesjaunes.tn** - DNS failure
- ⚠️ **tn.kompass.com** - Bot protection (403 Datadome - needs headers/delays)

## ALTERNATIVE SOURCES TO ADD 🚀

### Government & Official Sources
- **tunisieindustrie.nat.tn** - Ministry of Industry official directory
- **ins.tn** - Institut National de la Statistique (company registry)
- **api.gov.tn** - Tunisia Open Data portal
- **marchespublics.gov.tn** - Public tenders
- **tuneps.tn** - Tunisia Electronic Procurement System

### LinkedIn (via Apify API)
- Company profiles
- Employee counts
- Job postings with filters:
  - Keywords: "ingénieur", "CAD", "SOLIDWORKS", "bureau d'études"
  - Location: Tunisia
  - Industries: Manufacturing, Engineering, Construction

### Social Media & Professional Networks
- **Facebook Business Pages** - company pages with location=Tunisia
- **Google My Business** - Tunisian engineering companies
- **Crunchbase** - Tunisian startups and companies

### Industry-Specific
- **Chambre de Commerce et d'Industrie de Tunis** - Chamber of Commerce
- **UTICA Tunisia** - Employers union
- **CONECT** - Confédération des Entreprises Citoyennes de Tunisie
- **Pôle de Compétitivité Monastir** - Industrial clusters

### Training & Education
- **isetradesdegueniche.rnu.tn** - ISET campuses
- **enit.rnu.tn** - Engineering schools
- **ucar.rnu.tn** - University career centers

### International Funders
- **worldbank.org/tunisia** - World Bank projects
- **afd.fr/tunisia** - French Development Agency
- **eib.org** - European Investment Bank
- **usaid.gov/tunisia** - USAID projects

## SCRAPING STRATEGY 📋

### Tier 1 - Daily (Most Fresh Data)
1. businessnews.com.tn - News signals
2. tekiano.com - Tech news
3. keejob.com - Job postings
4. LinkedIn (via Apify) - Company updates

### Tier 2 - Weekly (Medium Update Frequency)
1. Government directories (tunisieindustrie.nat.tn)
2. Public tenders (marchespublics.gov.tn)
3. Training centers (ISET websites)

### Tier 3 - Monthly (Slow-changing Data)
1. International funders
2. Industry associations
3. Company registries

## NEXT STEPS ✅

1. ✅ Verify Docker network works (DONE - network is fine)
2. ✅ Fix spider URLs to use working sources
3. Add retry logic for timeout sources
4. Add proper headers to bypass bot protection
5. Implement rate limiting (respect robots.txt)
6. Add Apify LinkedIn connector
