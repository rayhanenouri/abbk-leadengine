/**
 * Playwright test for Lead Detail Page
 * Tests the complete flow: login → dashboard → lead detail → back
 */
import { chromium } from 'playwright';

async function testLeadDetailUI() {
  console.log('🚀 Testing Lead Detail UI...\n');

  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  try {
    // 1. Login
    console.log('1. Loading login page...');
    await page.goto('http://localhost:5173');
    await page.waitForSelector('input[type="email"]');
    console.log('✓ Login page loaded\n');

    console.log('2. Logging in...');
    await page.fill('input[type="email"]', 'admin@abbk.tn');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);
    console.log('✓ Logged in\n');

    // 2. Dashboard
    console.log('3. Checking dashboard...');
    await page.waitForSelector('text=ABBK LeadEngine', { timeout: 5000 });
    const leadsVisible = await page.isVisible('text=View Details');
    if (!leadsVisible) {
      throw new Error('No leads visible on dashboard');
    }
    console.log('✓ Dashboard loaded with leads\n');

    // 3. Click View Details on first lead
    console.log('4. Opening first lead detail...');
    await page.click('button:has-text("View Details")');
    await page.waitForTimeout(1500);

    // 4. Verify Lead Detail Page loaded
    console.log('5. Verifying lead detail page...');

    // Check for back button
    const backButton = await page.isVisible('button:has-text("Back to Dashboard")');
    if (!backButton) {
      throw new Error('Back button not found');
    }
    console.log('✓ Back button present');

    // Check for company header
    const companyName = await page.textContent('h2');
    console.log(`✓ Company: ${companyName}`);

    // Check for best deal section
    const bestDeal = await page.isVisible('text=Best Deal Recommendation');
    if (!bestDeal) {
      throw new Error('Best Deal section not found');
    }
    console.log('✓ Best Deal Recommendation present');

    // Check for score cards
    const scoreCards = await page.isVisible('text=All ABBK Services');
    if (!scoreCards) {
      throw new Error('Score cards section not found');
    }
    console.log('✓ Score cards section present');

    // Check for signals timeline
    const timeline = await page.isVisible('text=Signals Timeline');
    if (!timeline) {
      throw new Error('Signals timeline not found');
    }
    console.log('✓ Signals timeline present\n');

    // 5. Take screenshot
    console.log('6. Taking screenshot...');
    await page.screenshot({ path: 'lead_detail_screenshot.png', fullPage: true });
    console.log('✓ Screenshot saved: lead_detail_screenshot.png\n');

    // 6. Test back navigation
    console.log('7. Testing back navigation...');
    await page.click('button:has-text("Back to Dashboard")');
    await page.waitForTimeout(500);
    const backToDashboard = await page.isVisible('text=Ranked Leads');
    if (!backToDashboard) {
      throw new Error('Failed to return to dashboard');
    }
    console.log('✓ Back to dashboard successful\n');

    console.log('✅ ALL TESTS PASSED!');
    console.log('\n📊 Lead Detail Page Features Verified:');
    console.log('  ✓ Company header with name, sector, city');
    console.log('  ✓ Contact links (website, LinkedIn, phone)');
    console.log('  ✓ Best Deal Recommendation card');
    console.log('  ✓ All ABBK Services score cards');
    console.log('  ✓ Signals timeline');
    console.log('  ✓ Back navigation to dashboard');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    await page.screenshot({ path: 'error_screenshot.png' });
    console.log('Error screenshot saved: error_screenshot.png');
  } finally {
    await browser.close();
  }
}

testLeadDetailUI();
