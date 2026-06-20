import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();

  const apiCalls = [];

  page.on('request', req => {
    if (req.url().includes('/api/')) {
      apiCalls.push({ method: req.method(), url: req.url() });
    }
  });

  page.on('response', async res => {
    if (res.url().includes('/api/')) {
      const status = res.status();
      let body = '';
      try {
        body = await res.text();
      } catch(e) {}

      console.log(`\nAPI Call: ${res.request().method()} ${res.url()}`);
      console.log(`Status: ${status}`);
      console.log(`Response: ${body.substring(0, 200)}`);
    }
  });

  await page.goto('http://localhost:5173');
  await page.waitForTimeout(1000);

  await page.fill('input[type="email"]', 'admin@abbk.tn');
  await page.fill('input[type="password"]', 'admin123');
  await page.click('button[type="submit"]');

  await page.waitForTimeout(3000);

  console.log('\n=== Summary ===');
  console.log(`Total API calls: ${apiCalls.length}`);
  apiCalls.forEach(call => console.log(`  ${call.method} ${call.url}`));

  await browser.close();
})();
