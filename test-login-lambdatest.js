import { Builder, By, until } from "selenium-webdriver";
import chrome from "selenium-webdriver/chrome.js";

export async function runLoginTest() {
    console.log("🔐 Running Login Selenium Test...");

    const driver = await new Builder()
        .forBrowser("chrome")
        .setChromeOptions(new chrome.Options().addArguments("--headless"))
        .build();

    try {
       /* await driver.get("https://neda-supernormal-domenica.ngrok-free.dev/");
        await driver.findElement(By.css('button[type="Visit Site"]')).click();
        await driver.get("https://neda-supernormal-domenica.ngrok-free.dev/");*/


        await driver.get("https://demoapp-ashen.vercel.app/login");

        // 🔥 Correct selectors based on placeholder
        await driver.findElement(By.css('input[placeholder="Username"]')).sendKeys("admin");
        await driver.findElement(By.css('input[placeholder="Password"]')).sendKeys("password");

        await driver.findElement(By.css('button[type="submit"]')).click();

        // Wait for redirect (home page has title "Simple FastAPI UI")
        await driver.wait(until.elementLocated(By.css("h1")), 5000);

        console.log("✅ Login Test Passed");
        return { status: "success", page: "login" };

    } catch (error) {
        console.log("❌ Login Test Failed", error);
        return { status: "failed", error: error.message };
    } finally {
        await driver.quit();
    }
}
