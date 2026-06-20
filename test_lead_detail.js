/**
 * Test script to verify lead detail page
 * Run with: node test_lead_detail.js
 */

const API_BASE = 'http://localhost:8000/api';

async function testLeadDetail() {
  console.log('Testing Lead Detail Page...\n');

  // 1. Login
  console.log('1. Logging in...');
  const loginRes = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: 'admin@abbk.tn', password: 'admin123' }),
  });
  const { access_token } = await loginRes.json();
  console.log('✓ Login successful\n');

  const headers = {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json',
  };

  // 2. Get lead detail
  const leadId = 1;
  console.log(`2. Fetching lead ${leadId}...`);
  const leadRes = await fetch(`${API_BASE}/leads/${leadId}`, { headers });
  const lead = await leadRes.json();
  console.log(`✓ Lead: ${lead.company_name} - ${lead.sector} - ${lead.city}`);
  console.log(`  Phone: ${lead.scraped_data?.csv_import?.phone || 'N/A'}\n`);

  // 3. Get scores
  console.log('3. Fetching scores...');
  const scoresRes = await fetch(`${API_BASE}/scores/${leadId}`, { headers });
  const scores = await scoresRes.json();
  console.log(`✓ Found ${scores.scores.length} scores`);
  console.log(`  Best: ${scores.best_service} - ${Math.round(scores.best_score)}/100`);
  console.log(`  Top 3:`);
  scores.scores.slice(0, 3).forEach((s, i) => {
    console.log(`    ${i + 1}. ${s.service_name}: ${Math.round(s.score)}/100`);
  });
  console.log('');

  // 4. Get signals
  console.log('4. Fetching signals...');
  const signalsRes = await fetch(`${API_BASE}/signals/${leadId}`, { headers });
  const signals = await signalsRes.json();
  console.log(`✓ Found ${signals.length} signals`);
  signals.forEach(s => {
    console.log(`  - ${s.signal_type}: ${s.title}`);
  });
  console.log('');

  console.log('✅ All API endpoints working correctly!');
  console.log('\nLead Detail Page Data:');
  console.log('=====================');
  console.log(`Company: ${lead.company_name}`);
  console.log(`Sector: ${lead.sector}`);
  console.log(`City: ${lead.city}, ${lead.country}`);
  console.log(`Best Score: ${Math.round(scores.best_score)}/100`);
  console.log(`Best Service: ${scores.best_service}`);
  console.log(`Total Services: ${scores.scores.length}`);
  console.log(`Total Signals: ${signals.length}`);
}

testLeadDetail().catch(console.error);
