require('dotenv').config();
const fs = require('fs');

// Determine which page is being tested: default to 'login'
const PAGE = process.env.PAGE || "login";

// Set input file paths based on PAGE, but keep the combined report's path fixed
let seleniumReportFile, lighthouseReportFile, combinedReportFile;

if (PAGE === 'home') {
  seleniumReportFile = 'lambdatest-report-home.json';
  lighthouseReportFile = 'lighthouse/lh-report-home.json';
} else {
  seleniumReportFile = 'lambdatest-report-login.json';
  lighthouseReportFile = 'lighthouse/lh-report-login.json';
}

combinedReportFile = 'lighthouse/combined-report.json'; // <-- always this file

// Read JSON reports
const lighthouseReport = JSON.parse(fs.readFileSync(lighthouseReportFile, 'utf8'));
const lambdaTestReport = JSON.parse(fs.readFileSync(seleniumReportFile, 'utf8'));

// Attach LambdaTest checks to Lighthouse report
lighthouseReport.lambdatestChecks = lambdaTestReport;

// Score calculation (for fields that are boolean)
const keysToCheck = Object.keys(lambdaTestReport).filter(
  key => typeof lambdaTestReport[key] === 'boolean'
);
const allPassed = keysToCheck.every(key => lambdaTestReport[key] === true);
lighthouseReport.lambdatestScore = allPassed ? 1 : 0;
lighthouseReport.lambdatestPassed = allPassed;
lighthouseReport.lambdatestFailedChecks = keysToCheck.filter(
  key => lambdaTestReport[key] !== true
);

// Write combined report to the fixed path for all runs
fs.writeFileSync(combinedReportFile, JSON.stringify(lighthouseReport, null, 2));
console.log(`✅ Combined report generated: ${combinedReportFile}`);