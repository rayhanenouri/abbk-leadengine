import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch({
    headless: false,  // Show browser
    args: ['--no-sandbox']
  });

  const page = await browser.newPage();

  // Capture all network requests
  page.on('request', request => {
    console.log(`→ ${request.method()} ${request.url()}`);
  });

  page.on('response', response => {
    console.log(`← ${response.status()} ${response.url()}`);
  });

  page.on('console', msg => console.log(`[CONSOLE ${msg.type()}]`, msg.text()));

  console.log('Opening http://localhost:5173...\n');
  await page.goto('http://localhost:5173');

  await page.waitForTimeout(2000);

  console.log('\nFilling login form...');
  await page.fill('input[type="email"]', 'admin@abbk.tn');
  await page.fill('input[type="password"]', 'admin123');

  console.log('Clicking login...');
  await page.click('button[type="submit"]');

  await page.waitForTimeout(5000);

  console.log('\nKeeping browser open for 30 seconds to inspect...');
  await page.waitForTimeout(30000);

  await browser.close();
})();
