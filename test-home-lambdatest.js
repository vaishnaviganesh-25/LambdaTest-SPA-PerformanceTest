require('dotenv').config();
const {Builder, By, until} = require('selenium-webdriver');
const fs = require('fs');

(async function runHomeTest() {
  let capabilities = {
    browserName: 'Chrome',
    browserVersion: 'latest',
    'LT:Options': {
      user: process.env.LT_USERNAME,
      accessKey: process.env.LT_ACCESS_KEY,
      platformName: 'Windows 10',
      build: 'homepage-test-build',
      name: 'Home Page Test'
    }
  };

  let driver = await new Builder()
    .usingServer('https://hub.lambdatest.com/wd/hub')
    .withCapabilities(capabilities)
    .build();

  let results = {
    pageTitle: '',
    bannerPresent: false,
    specialOfferPresent: false,
    timestamp: new Date().toISOString()
  };

  try {
    await driver.get('https://demoqa.com');

    results.pageTitle = await driver.getTitle();

    // Example: Check homepage elements, e.g., banner and special offer
    results.bannerPresent = await driver.findElements(By.css('.banner-image')).then(els => els.length > 0);
    results.specialOfferPresent = await driver.findElements(By.css('.some-special-offer')).then(els => els.length > 0);

    // Save result
    fs.writeFileSync('lambdatest-report-home.json', JSON.stringify(results, null, 2));
    console.log("✅ Home page test results saved: lambdatest-report-home.json");

  } finally {
    await driver.quit();
  }
})();