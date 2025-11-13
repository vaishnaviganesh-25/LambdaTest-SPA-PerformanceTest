require('dotenv').config();
const { Builder, By } = require('selenium-webdriver');
const fs = require('fs');

(async function runTest() {
  let capabilities = {
    browserName: 'Chrome',
    browserVersion: 'latest',
    'LT:Options': {
      user: process.env.LT_USERNAME,            // Set via HyperExecute env
      accessKey: process.env.LT_ACCESS_KEY,
      platformName: 'Windows 10',
      build: 'login-test-build',
      name: 'Login Page Test'
    }
  };

  let driver = await new Builder()
    .usingServer('https://hub.lambdatest.com/wd/hub')
    .withCapabilities(capabilities)
    .build();

  const testResults = {};

  try {
    await driver.get('https://demoqa.com/login');
    testResults.username = await driver.findElement(By.id('userName')).isDisplayed();
    testResults.password = await driver.findElement(By.id('password')).isDisplayed();
    testResults.loginButton = await driver.findElement(By.id('login')).isDisplayed();
    testResults.pageTitle = await driver.getTitle();
    testResults.timestamp = new Date().toISOString();
  } catch (err) {
    testResults.error = err.toString();
  } finally {
    await driver.quit();
    fs.writeFileSync('lambdatest-report-login.json', JSON.stringify(testResults, null, 2));
    console.log('Test complete, JSON report written.');
  }
})();