import { Builder, By, until } from "selenium-webdriver";
import chrome from "selenium-webdriver/chrome.js";


export async function runHomeTest() {
    console.log("🏠 Running Home Selenium Test...");

    const driver = await new Builder()
        .forBrowser("chrome")
        .setChromeOptions(new chrome.Options().addArguments("--headless"))
        .build();

    try {
       // await driver.get("https://neda-supernormal-domenica.ngrok-free.dev/");
      //  await driver.findElement(By.xpath('button[contains(text(), 'Visit Site']')).click();
      //  await driver.get("https://neda-supernormal-domenica.ngrok-free.dev/");
           await driver.get("https://demoapp-ashen.vercel.app/");

            // 🔥 Correct selectors based on placeholder
            await driver.findElement(By.css('input[placeholder="Username"]')).sendKeys("admin");
            await driver.findElement(By.css('input[placeholder="Password"]')).sendKeys("password");

            await driver.findElement(By.css('button[type="submit"]')).click();

            // Wait for redirect (home page has title "Simple FastAPI UI")
            await driver.wait(until.elementLocated(By.css("h1")), 5000);

            console.log("✅ Login Test Passed");
        // Home page main heading <h1>Simple FastAPI UI</h1>
        await driver.wait(until.elementLocated(By.xpath("//h1[contains(text(), 'Simple FastAPI UI')]")), 5000);

            console.log("✔ Title found");

            // Expected button labels
            const expectedButtons = ["Root", "Hello", "Data", "Compute", "Items"];

            for (let btnText of expectedButtons) {
              const buttonLocator = By.xpath(`//button[text()='${btnText}']`);

              await driver.wait(
                until.elementLocated(buttonLocator),
                10000,
                `Button "${btnText}" was not found`
              );

              console.log(`✔ Button found: ${btnText}`);
            }

        console.log("✅ Home Page Validation Passed");

        return { status: "success", page: "home" };

    } catch (error) {
        console.log("❌ Home Test Failed", error);
        return { status: "failed", error: error.message };
    } finally {
        await driver.quit();
    }
}
