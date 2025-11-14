import fs from "fs";

export function mergeReports(page, seleniumResult, lighthouseJson) {
    const final = {
        page: page || "unknown",
        mergedAt: new Date().toISOString(),
        selenium: seleniumResult || { status: "missing" },
        lighthouse: lighthouseJson || { note: "Lighthouse report missing" }
    };

    const outDir = "lighthouse";
    if (!fs.existsSync(outDir)) fs.mkdirSync(outDir);

    const outputPath = `${outDir}/merged-report-${page}.json`;
    fs.writeFileSync(outputPath, JSON.stringify(final, null, 2));

    console.log(`✅ Combined report saved → ${outputPath}`);
}
