# Training History Detection Spider

## Business Context

### Why Training Signals Matter for ABBK

Companies that invest in employee training are **warm leads** for ABBK's training programs:

1. **Already training-minded**: They value employee development
2. **Budget allocated**: Have training budget approved
3. **Proven ROI**: See value in professional development
4. **Repeat customers**: Companies train multiple employees over time
5. **Upsell opportunity**: Training → software license sales

### ABBK Training Products

This spider helps identify leads for:
- SOLIDWORKS Essential Level 1 training
- SOLIDWORKS professional training
- SOLIDWORKS certification preparation (CSWA, CSWP, CSWPA)
- Abaqus training
- CAMWorks training
- 3DEXPERIENCE training
- STEM Education programs
- Corporate training programs

## What the Spider Does

### Target Sources

1. **ISET Campuses** (12 locations)
   - ISET Sousse
   - ISET Radès
   - ISET Nabeul
   - ISET Kairouan
   - ISET Gabès
   - ISET Bizerte
   - ISET Gafsa
   - ISET Kef
   - ISET Kasserine
   - ISET Médenine
   - ISET Mahdia
   - ISET Sfax

2. **Engineering Schools**
   - ENIM (École Nationale d'Ingénieurs de Monastir)
   - ENIS (École Nationale d'Ingénieurs de Sfax)
   - ENIT (École Nationale d'Ingénieurs de Tunis)

3. **Professional Training Centers**
   - ATFP (Agence Tunisienne de la Formation Professionnelle)
   - TunisieFormation.com
   - Formation.com.tn

### Detection Methods

#### Method 1: Partner Companies
Looks for "Partenaires" or "Entreprises" sections on training center websites.

**Example**: 
```html
<section class="partenaires">
  <h3>Nos Partenaires Entreprises</h3>
  <ul>
    <li>Poulina Group</li>
    <li>BET-SCET</li>
    <li>Groupe Chimique Tunisien</li>
  </ul>
</section>
```

#### Method 2: Partner Logos
Extracts company names from partner logo images.

**Example**:
```html
<div class="partners">
  <img src="poulina-logo.png" alt="Poulina Group">
  <img src="bet-scet-logo.png" alt="BET-SCET">
</div>
```

#### Method 3: Training Program Announcements
Scans training program descriptions for company mentions.

**Example**:
"Formation SOLIDWORKS pour les ingénieurs de **Poulina Group**"

#### Method 4: Testimonials and Case Studies
Extracts company names from success stories.

**Example**:
> "Nous avons formé 15 ingénieurs de **BET-SCET** sur SOLIDWORKS Simulation"

### Training Type Detection

Automatically classifies training based on keywords:

- **CAD/SOLIDWORKS training**: solidworks, catia, cao, cad
- **Simulation training**: simulation, abaqus, ansys
- **Mechanical engineering**: mécanique, mechanical
- **Design/conception**: conception, design
- **Industrial/manufacturing**: industriel, manufacturing
- **Technical training**: (default for engineering-related training)

## Data Structure

### Signal Created

```json
{
  "signal_type": "training_detected",
  "company_name": "Poulina Group",
  "training_type": "CAD/SOLIDWORKS training",
  "source": "ISET Sousse",
  "source_url": "http://www.isetso.rnu.tn/partenaires",
  "title": "Training at ISET Sousse",
  "detail": "Company sent employees to CAD/SOLIDWORKS training at ISET Sousse"
}
```

### Database Storage

Signals stored in `lead_signals` table:
```sql
INSERT INTO lead_signals (
  lead_id,
  signal_type,
  title,
  detail,
  source_url,
  detected_at
) VALUES (
  123,
  'training_detected',
  'Training at ISET Sousse',
  'Company sent employees to CAD/SOLIDWORKS training at ISET Sousse',
  'http://www.isetso.rnu.tn/partenaires',
  '2026-06-21 10:30:00'
);
```

## Company Name Filtering

### What Qualifies as a Company Name

The spider uses intelligent filtering to avoid false positives:

✅ **Accepted**:
- "Poulina Group"
- "BET-SCET"
- "Groupe Chimique Tunisien"
- "STEG" (even though short)

❌ **Rejected**:
- Navigation items ("Accueil", "Contact", "About")
- Common words ("services", "formation", "voir plus")
- URLs ("http://...", "www...")
- Very short strings (< 3 chars)
- Pure lowercase single words

### Company Name Indicators

Automatically accepts text containing:
- "Group" or "Groupe"
- "SARL", "SA"
- "Industries"
- "Engineering"
- "Tunisie" or "Tunisia"

## Scheduling

### Celery Beat Schedule

Runs **weekly on Monday at 1am**:

```python
"scrape-training-weekly": {
    "task": "app.workers.tasks.scraping.scrape_training",
    "schedule": crontab(hour=1, minute=0, day_of_week=1),
    "options": {"queue": "scrapers"},
}
```

### Why Weekly?

Training partnerships change slowly:
- Educational sites update infrequently
- Training programs run on semester/term schedules
- Avoids overloading .rnu.tn educational servers
- Respectful of bandwidth for public institutions

## Running the Spider

### Manual Test

```bash
cd /home/rayhanenouri/projects/abbk-leadengine/backend
python test_training_spider.py
```

### Via Celery Task

```python
from app.workers.tasks.scraping import scrape_training

# Queue the task
scrape_training.delay()
```

### Direct Scrapy Run

```bash
cd /home/rayhanenouri/projects/abbk-leadengine/backend
scrapy crawl training_centers
```

## Expected Results

### Success Criteria

Issue #13 requires: **"At least 5 training signals detected"**

Realistic expectations for Tunisia:
- **ISET campuses**: 3-10 partner companies per campus
- **Engineering schools**: 5-20 industrial partners each
- **ATFP**: 10-50+ corporate training clients
- **Total expected**: 50-200 training signals

### High-Value Signals

Best signals for ABBK:
1. Companies training on **SOLIDWORKS** (direct competitor use)
2. Companies training on **CAD/conception** (potential switchers)
3. Companies training **multiple employees** (large accounts)
4. Companies at **multiple training centers** (serious about development)

## Troubleshooting

### No Results

**Possible causes**:
1. ISET websites may be down (.rnu.tn can be unreliable)
2. Partner pages may not exist or use different structure
3. Companies listed may not match existing leads in database

**Solutions**:
- Check if URLs are accessible: `curl http://www.isetso.rnu.tn`
- Review spider logs for parsing errors
- Verify companies exist in `leads` table (signals only created for existing leads)

### False Positives

If non-company text is being detected:

**Fix**: Update `_looks_like_company()` filter in spider:
```python
excluded_words = [
    'accueil', 'home', 'contact', ...
    # Add more excluded words here
]
```

### Slow Performance

Educational sites (.rnu.tn) can be very slow.

**Current settings**:
```python
DOWNLOAD_DELAY = 3  # 3 second delay
DOWNLOAD_TIMEOUT = 30  # 30 second timeout
CONCURRENT_REQUESTS = 2  # Only 2 parallel requests
```

These are intentionally conservative to:
- Respect public infrastructure
- Avoid being blocked
- Handle slow server responses

## Scoring Impact

### How Training Signals Increase Scores

Training signals boost scores for **ABBK training products**:

```python
# Example scoring weights
training_signal_weights = {
    "SOLIDWORKS Essential Training": +15 points,
    "SOLIDWORKS Professional Training": +12 points,
    "SOLIDWORKS Certification Prep": +10 points,
    "Abaqus Training": +8 points,
    "CAMWorks Training": +8 points,
}
```

### Business Logic

1. Company sent employees to CAD training
2. → They value CAD skills
3. → They'll send more employees
4. → Warm lead for ABBK training programs

## Sales Intelligence

### What the Manager Sees

Lead detail page shows:
```
Poulina Group

Signals:
📚 Training at ISET Sousse
   CAD/SOLIDWORKS training
   Detected: June 21, 2026
   Source: http://www.isetso.rnu.tn/partenaires

📚 Training at ENIM Monastir
   Mechanical engineering training
   Detected: June 15, 2026
```

### Call Script

Manager calling lead:

> "Bonjour, I'm calling from ABBK, the official SOLIDWORKS representative in Tunisia. I noticed your company works with ISET Sousse for CAD training. We offer official SOLIDWORKS certification programs that your engineers would benefit from. Would you be interested in discussing our corporate training packages?"

### Upsell Path

Training signal → Training sales → License sales

1. **First contact**: Sell training program
2. **During training**: Students use SOLIDWORKS
3. **After training**: "Your engineers are now certified, would you like to purchase licenses?"
4. **Follow-up**: PDM, Simulation, CAM add-ons

## Monitoring

### Check Results

```sql
-- Count training signals
SELECT COUNT(*) 
FROM lead_signals 
WHERE signal_type = 'training_detected';

-- Show recent training signals
SELECT 
  l.company_name,
  ls.title,
  ls.detail,
  ls.detected_at
FROM lead_signals ls
JOIN leads l ON ls.lead_id = l.id
WHERE ls.signal_type = 'training_detected'
ORDER BY ls.detected_at DESC
LIMIT 20;

-- Companies with multiple training signals (very warm leads!)
SELECT 
  l.company_name,
  COUNT(*) as training_count
FROM lead_signals ls
JOIN leads l ON ls.lead_id = l.id
WHERE ls.signal_type = 'training_detected'
GROUP BY l.company_name
HAVING COUNT(*) > 1
ORDER BY training_count DESC;
```

### Celery Flower

Monitor task execution:
```
http://localhost:5555/tasks
```

Filter for: `app.workers.tasks.scraping.scrape_training`

## Future Improvements

### Potential Enhancements

1. **Date extraction**: Detect when training occurred
2. **Participant count**: Extract number of employees trained
3. **Training topics**: More granular classification
4. **Certificate verification**: Check if employees completed
5. **Budget detection**: Identify training spending amounts

### Additional Sources

Could add:
- LinkedIn company pages (training announcements)
- Company websites (training/HR sections)
- Professional association member lists
- Chamber of Commerce training programs
- Ministry of Industry training initiatives

## Next Steps

1. ✅ Spider code complete
2. ✅ Celery task added
3. ✅ Celery Beat scheduled
4. ⏳ Run test to verify signals detected
5. ⏳ Check at least 5 signals created (issue #13 requirement)
6. ⏳ Close issue #13

---

**Spider**: `training_centers`
**Task**: `app.workers.tasks.scraping.scrape_training`
**Schedule**: Weekly Monday 1am
**Signal Type**: `training_detected`
**Priority**: IMPORTANT FOR DEMO (training = warm leads)
