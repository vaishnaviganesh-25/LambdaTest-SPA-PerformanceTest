import { Builder, By, until } from "selenium-webdriver";
import chrome from "selenium-webdriver/chrome.js";


export async function runHomeTest() {
    console.log("🏠 Running Home Selenium Test...");

    const driver = await new Builder()
        .forBrowser("chrome")
        .setChromeOptions(new chrome.Options().addArguments("--headless"))
        .build();

    try {
        await driver.get("https://demoapp-ft6dwhwtc-dev-pranavs-projects.vercel.app/");

        // Home page main heading <h1>Simple FastAPI UI</h1>
        await driver.wait(until.elementLocated(By.xpath("//h1[contains(text(), 'Simple FastAPI UI')]")), 5000);

        console.log("✅ Home Page Validation Passed");

        return { status: "success", page: "home" };

    } catch (error) {
        console.log("❌ Home Test Failed", error);
        return { status: "failed", error: error.message };
    } finally {
        await driver.quit();
    }
}
