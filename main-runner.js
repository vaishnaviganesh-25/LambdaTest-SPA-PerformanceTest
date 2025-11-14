import dotenv from "dotenv";
dotenv.config();
console.log("DEBUG process.env.PAGE =", process.env.PAGE);

import { runLoginTest } from "./test-login-lambdatest.js";
import { runHomeTest } from "./test-home-lambdatest.js";
import { runLighthouse } from "./lighthouse-runner.js";
import { mergeReports } from "./merge-reports.js";

const PAGE = process.env.PAGE;

console.log(`🚀 Starting Execution for PAGE=${PAGE}`);

async function main() {
    let seleniumResult = null;
    let lighthouseJson = null;

    // -----------------------------
    // 1️⃣ Run Selenium for this page
    // -----------------------------
    if (PAGE === "login") {
        seleniumResult = await runLoginTest();
    } else if (PAGE === "home") {
        seleniumResult = await runHomeTest();
    } else {
        console.log("❌ Invalid PAGE value. Must be login or home.");
        return;
    }

    // -------------------------------------
    // 2️⃣ Run Lighthouse for this same page
    // -------------------------------------
    lighthouseJson = await runLighthouse(PAGE);

    // -----------------------------------------------------
    // 3️⃣ Merge Selenium + Lighthouse into final JSON report
    // -----------------------------------------------------
    console.log(`🔄 Merging reports for: ${PAGE}`);
    mergeReports(PAGE, seleniumResult, lighthouseJson);
}

main();
