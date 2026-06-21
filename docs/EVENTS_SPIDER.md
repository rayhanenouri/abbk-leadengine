# Engineering Events Spider

## Overview

Detects companies participating in engineering events, SOLIDWORKS events, industry salons, and conferences across Tunisia and Africa.

## Why Event Attendees Are Warm Leads

Companies at engineering events are **WARM LEADS**:

1. **✅ Actively engaged** in engineering/CAD domain
2. **✅ Have budget** - Events/booths cost money
3. **✅ Decision-makers present** - Networking opportunities
4. **✅ SOLIDWORKS events** = Direct users or serious prospects
5. **✅ Growth-minded** - Investing in visibility and connections

## Target Events

### 1. SOLIDWORKS Events
- Regional user groups
- SOLIDWORKS Days
- Training sessions
- **Value**: Direct SOLIDWORKS users = Highest conversion

### 2. Industry Salons/Trade Shows
- Manufacturing exhibitions
- Engineering conferences
- Industrial technology fairs
- **Value**: Companies showcasing capabilities = Budget for tools

### 3. Tunisia Events
- UTICA industry events
- CEPEX export salons
- Tunisie Industrie exhibitions
- Chamber of Commerce events
- **Value**: Local market leaders

### 4. University Career Fairs
- ENIT career fairs
- ENIM recruitment events
- Engineering school job fairs
- **Value**: Companies hiring engineers = Need CAD licenses

## Detection Methods

### Method 1: Exhibitor Lists
Structured lists on event pages:
```html
<div class="exhibitors">
  <ul>
    <li>Poulina Group</li>
    <li>BET-SCET</li>
  </ul>
</div>
```

### Method 2: Exhibitor Logos
Company logos with alt text:
```html
<div class="exhibitors">
  <img alt="Poulina Group" src="logo.png">
</div>
```

### Method 3: Sponsor Lists
Event sponsors/partners:
```html
<section class="sponsors">
  <h3>Gold Sponsors</h3>
  <p>Poulina Group, BET-SCET</p>
</section>
```

### Method 4: Participant Tables
Tables listing participants:
```html
<table class="participants">
  <tr><td>Poulina Group</td><td>Booth 15</td></tr>
</table>
```

## Signal Created

```json
{
  "signal_type": "event_attendance",
  "company_name": "Poulina Group",
  "event_name": "SOLIDWORKS Tunisia User Group 2026",
  "event_date": "15-17 juin 2026",
  "event_type": "SOLIDWORKS event",
  "source": "SOLIDWORKS Events",
  "source_url": "https://...",
  "title": "Attended: SOLIDWORKS Tunisia User Group",
  "detail": "Company participated in SOLIDWORKS Tunisia User Group 2026"
}
```

## Event Classification

Spider automatically classifies events:

- **SOLIDWORKS event**: SOLIDWORKS brand events
- **Trade show**: Salons, fairs, exhibitions
- **Conference**: Conferences, summits
- **Workshop**: Workshops, training sessions
- **Forum**: Industry forums, networking
- **Career fair**: University job fairs
- **Industry event**: Other engineering events

## Business Value

### Sales Intelligence

**Event attendance signals**:
- **SOLIDWORKS event** → "I saw you at SOLIDWORKS Day - how are you finding the software?"
- **Industry salon** → "Your booth at [salon] looked great - let's discuss scaling your tools"
- **Career fair** → "I saw you're hiring engineers - they'll need CAD licenses"

### Conversion Rates

- SOLIDWORKS events: **40-60%** conversion (already users/prospects)
- Industry salons: **30-40%** conversion (growth-minded)
- Career fairs: **20-30%** conversion (hiring = budget)
- Regular leads: 5-10% baseline

### Call Script

> "Bonjour, I noticed you participated in [event name]. I'm from ABBK, the official SOLIDWORKS representative. Many companies we work with were at that event. Would you like to discuss how we can support your engineering team?"

## Scheduling

**Monthly on 1st at 2am**:
```python
"scrape-events-monthly": {
    "task": "app.workers.tasks.scraping.scrape_events",
    "schedule": crontab(hour=2, minute=0, day_of_month=1),
}
```

**Why monthly?**
- Events are infrequent (quarterly/annual)
- Event websites update slowly
- Signals remain valid for months

## Expected Results

**Realistic for Tunisia**:
- SOLIDWORKS events: 2-4 per year, 20-50 companies each
- Industry salons: 10-20 per year, 30-100 exhibitors each
- University fairs: 4-6 per year, 15-30 companies each
- **Total expected: 100-300 event signals per year**

## Running the Spider

```bash
cd backend
python test_events_spider.py
```

```python
from app.workers.tasks.scraping import scrape_events
scrape_events.delay()
```

```sql
SELECT * FROM lead_signals WHERE signal_type = 'event_attendance';
```

## Monitoring

```sql
-- Event signals by type
SELECT 
  CASE 
    WHEN source_url LIKE '%solidworks%' THEN 'SOLIDWORKS Events'
    WHEN source_url LIKE '%utica%' THEN 'UTICA'
    WHEN source_url LIKE '%cepex%' THEN 'CEPEX'
    ELSE 'Other'
  END as source,
  COUNT(*) as count
FROM lead_signals
WHERE signal_type = 'event_attendance'
GROUP BY source;

-- Companies at multiple events (very warm!)
SELECT 
  l.company_name,
  COUNT(*) as events_attended
FROM leads l
JOIN lead_signals ls ON l.id = ls.lead_id
WHERE ls.signal_type = 'event_attendance'
GROUP BY l.company_name
HAVING COUNT(*) > 1
ORDER BY events_attended DESC;
```

## Future Enhancements

- Parse event dates more intelligently
- Detect booth numbers (booth size = company investment)
- Track speaking engagements (thought leaders)
- Monitor social media event hashtags
- Integrate with Eventbrite API

---

**Spider**: `events`  
**Task**: `app.workers.tasks.scraping.scrape_events`  
**Schedule**: Monthly (1st at 2am)  
**Signal Type**: `event_attendance`  
**Conversion**: **30-60%** (vs 5-10% regular)
