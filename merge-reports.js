import fs from "fs";

export function mergeReports(page, seleniumResult, lighthouseJson) {
  const final = {
    page: page || "unknown",
    mergedAt: new Date().toISOString(),
    selenium: seleniumResult || { status: "missing" },
    lighthouse: lighthouseJson || { note: "Lighthouse report missing" }
  };

  // -------------------------------
  // ⭐ THRESHOLD CHECK EXAMPLE ⭐
  // -------------------------------
  // Example: Fail job if Lighthouse Performance < 80
  const performanceScore = final?.lighthouse?.categories?.performance?.score;

  if (performanceScore !== undefined) {
    const perfPercent = performanceScore * 100;
    const threshold = 80;

    if (perfPercent < threshold) {
      console.error(`❌ Performance score too low: ${perfPercent} < ${threshold}`);
      process.exit(1);   // ← FAIL THE JOB
    } else {
      console.log(`✔ Performance score OK: ${perfPercent} ≥ ${threshold}`);
    }
  }
  // -------------------------------

  const outDir = "lighthouse";
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir);

  const outputPath = `${outDir}/merged-report.json`;
  fs.writeFileSync(outputPath, JSON.stringify(final, null, 2));

  console.log(`✓ Combined report saved → ${outputPath}`);
}
