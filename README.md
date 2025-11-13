# LambdaTest + Lighthouse Automated Testing

## Usage

1. Install dependencies:
   ```sh
   npm install
   ```
2. To run Selenium test:
   ```sh
   node test-login-lambdatest.js
   ```
3. To run Lighthouse:
   ```sh
   npx lighthouse <url> --output json --output-path=lighthouse/lh-report-login.json
   ```
4. To merge reports:
   ```sh
   node merge-reports.js
   ```

## Project Layout

- **test-login-lambdatest.js** — Selenium script for LambdaTest
- **lighthouse/** — Folder to save Lighthouse/merged reports
- **merge-reports.js** — Script to merge JSON reports
- **README.md** — This file
