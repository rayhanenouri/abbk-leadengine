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

  // Collect console messages
  const logs = [];
  page.on('console', msg => {
    logs.push(`[${msg.type()}] ${msg.text()}`);
  });

  console.log('Testing API URL configuration...\n');

  // Login
  console.log('1. Navigating to login page...');
  await page.goto('http://localhost:5173');
  await page.waitForSelector('input[type="email"]', { timeout: 10000 });
  console.log('   ✓ Login page loaded\n');

  console.log('2. Attempting login...');
  await page.fill('input[type="email"]', 'admin@abbk.tn');
  await page.fill('input[type="password"]', 'admin123');
  await page.click('button[type="submit"]');

  // Wait a bit for response
  await page.waitForTimeout(3000);

  console.log('3. Console messages:');
  logs.forEach(log => console.log(`   ${log}`));

  // Check if we're still on login page or reached dashboard
  const currentUrl = page.url();
  console.log(`\n4. Current URL: ${currentUrl}`);

  const hasLoginForm = await page.locator('input[type="email"]').count() > 0;
  const hasDashboard = await page.locator('text=ABBK LeadEngine').count() > 0;

  console.log(`   Has login form: ${hasLoginForm}`);
  console.log(`   Has dashboard: ${hasDashboard}`);

  await page.screenshot({ path: '/tmp/abbk_api_test.png', fullPage: true });
  console.log('\nScreenshot: /tmp/abbk_api_test.png');

  await browser.close();
})();
