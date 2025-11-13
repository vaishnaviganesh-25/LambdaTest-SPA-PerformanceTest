require('dotenv').config();
const { execSync } = require('child_process');

const page = process.env.PAGE || "login"; // Default to login if not set

if (page === "login") {
  execSync('node test-login-lambdatest.js', { stdio: 'inherit' });
  execSync('npx lighthouse https://demoqa.com/login --output json --output-path=lighthouse/lh-report-login.json', { stdio: 'inherit' });
  execSync('node merge-reports.js', { stdio: 'inherit' });
} else if (page === "home") {
  execSync('node test-home-lambdatest.js', { stdio: 'inherit' });
  execSync('npx lighthouse https://demoqa.com/ --output json --output-path=lighthouse/lh-report-home.json', { stdio: 'inherit' });
  // You may want a merge-reports-home.js or make merge-reports.js smart
  execSync('node merge-reports.js', { stdio: 'inherit' });
} else {
  console.error('Unknown PAGE value: ' + page);
  process.exit(1);
}