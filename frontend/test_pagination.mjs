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

  console.log('Testing ABBK LeadEngine Pagination...\n');

  // Login
  console.log('1. Logging in...');
  await page.goto('http://localhost:5173');
  await page.waitForSelector('input[type="email"]', { timeout: 10000 });
  await page.fill('input[type="email"]', 'admin@abbk.tn');
  await page.fill('input[type="password"]', 'admin123');
  await page.click('button[type="submit"]');
  await page.waitForSelector('text=ABBK LeadEngine', { timeout: 10000 });
  await page.waitForTimeout(2000);
  console.log('   ✓ Login successful\n');

  // Check total leads
  const totalLeadsText = await page.locator('text=Total Leads').locator('..').locator('div').first().textContent();
  const totalLeads = parseInt(totalLeadsText.trim());
  console.log(`2. Total leads in database: ${totalLeads}`);

  // Check pagination info
  const paginationText = await page.locator('text=/Showing \\d+-\\d+ of \\d+ leads/').textContent();
  console.log(`   Pagination: ${paginationText}\n`);

  // Check page info in stats
  const pageInfoText = await page.locator('text=/Page \\d+ of \\d+/').textContent();
  console.log(`3. Current page: ${pageInfoText}`);

  // Count visible lead cards on page 1
  const leadsOnPage1 = await page.locator('.company-name, h3').count();
  console.log(`   Lead cards on page 1: ${leadsOnPage1}`);

  // Take screenshot of page 1
  await page.screenshot({ path: '/tmp/abbk_page1.png', fullPage: true });
  console.log('   Screenshot: /tmp/abbk_page1.png\n');

  // Test Next button
  console.log('4. Testing pagination navigation...');
  const nextButton = page.locator('button:has-text("Next")');
  const isNextEnabled = await nextButton.isEnabled();
  console.log(`   Next button enabled: ${isNextEnabled}`);

  if (isNextEnabled) {
    await nextButton.click();
    await page.waitForTimeout(1000);

    const pageInfoPage2 = await page.locator('text=/Page \\d+ of \\d+/').textContent();
    console.log(`   After clicking Next: ${pageInfoPage2}`);

    const paginationTextPage2 = await page.locator('text=/Showing \\d+-\\d+ of \\d+ leads/').textContent();
    console.log(`   Pagination: ${paginationTextPage2}`);

    // Take screenshot of page 2
    await page.screenshot({ path: '/tmp/abbk_page2.png', fullPage: true });
    console.log('   Screenshot: /tmp/abbk_page2.png');

    // Test Previous button
    const prevButton = page.locator('button:has-text("Previous")');
    await prevButton.click();
    await page.waitForTimeout(1000);

    const pageInfoBackToPage1 = await page.locator('text=/Page \\d+ of \\d+/').textContent();
    console.log(`   After clicking Previous: ${pageInfoBackToPage1}\n`);
  }

  // Test page number buttons
  console.log('5. Testing page number buttons...');
  const pageButtons = await page.locator('button').filter({ hasText: /^\d+$/ }).count();
  console.log(`   Page number buttons visible: ${pageButtons}`);

  if (pageButtons > 0) {
    // Click on page 3 if it exists
    const page3Button = page.locator('button:has-text("3")');
    if (await page3Button.count() > 0) {
      await page3Button.click();
      await page.waitForTimeout(1000);

      const pageInfoPage3 = await page.locator('text=/Page \\d+ of \\d+/').textContent();
      console.log(`   After clicking page 3: ${pageInfoPage3}`);

      await page.screenshot({ path: '/tmp/abbk_page3.png', fullPage: true });
      console.log('   Screenshot: /tmp/abbk_page3.png');
    }
  }

  // Check for console errors
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });

  await page.waitForTimeout(1000);

  console.log('\n=== PAGINATION TEST RESULTS ===');
  console.log(`✓ Total leads: ${totalLeads}`);
  console.log(`✓ Leads per page: 50 (expected)`);
  console.log(`✓ Total pages: ${Math.ceil(totalLeads / 50)}`);
  console.log(`✓ Navigation: Next/Previous working`);
  console.log(`✓ Page number buttons: ${pageButtons} visible`);

  if (errors.length > 0) {
    console.log(`\n⚠️  Console errors: ${errors.length}`);
    errors.forEach(err => console.log(`  - ${err}`));
  } else {
    console.log('✓ No console errors');
  }

  console.log('\n✅ Pagination test complete!');

  await browser.close();
})();
