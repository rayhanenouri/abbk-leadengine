import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });

  const page = await context.newPage();

  console.log('Navigating to login page...');
  await page.goto('http://localhost:5173');

  // Wait for login page
  await page.waitForSelector('input[type="email"]', { timeout: 10000 });
  console.log('Login page loaded');

  // Take screenshot of login
  await page.screenshot({ path: '/tmp/abbk_login.png', fullPage: true });
  console.log('Screenshot saved: /tmp/abbk_login.png');

  // Login
  await page.fill('input[type="email"]', 'admin@abbk.tn');
  await page.fill('input[type="password"]', 'admin123');
  await page.click('button[type="submit"]');

  console.log('Logging in...');

  // Wait for dashboard to load
  await page.waitForSelector('text=ABBK LeadEngine', { timeout: 10000 });
  await page.waitForSelector('text=Total Leads', { timeout: 10000 });
  console.log('Dashboard loaded');

  // Wait a bit for data to load
  await page.waitForTimeout(2000);

  // Take screenshot of dashboard
  await page.screenshot({ path: '/tmp/abbk_dashboard.png', fullPage: true });
  console.log('Screenshot saved: /tmp/abbk_dashboard.png');

  // Check for errors
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });

  // Get some stats from the page
  const totalLeads = await page.locator('text=Total Leads').locator('..').locator('div').first().textContent();
  console.log(`Total Leads: ${totalLeads}`);

  if (errors.length > 0) {
    console.log('\n⚠️  Console errors:');
    errors.forEach(err => console.log(`  - ${err}`));
  } else {
    console.log('\n✅ No console errors');
  }

  await browser.close();
  console.log('\n✅ Dashboard test complete!');
})();
