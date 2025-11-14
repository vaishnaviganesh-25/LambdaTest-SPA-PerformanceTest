import json
import html
from datetime import datetime, timezone


def get_score_color_hex(score):
    """
    Returns a hex color code based on the score.
    (90+ = green, 50-89 = amber, <50 = red)
    Matches the red from load_test_report.html
    """
    if score >= 90:
        return '#10b981'  # Tailwind Green-500
    if score >= 50:
        return '#f59e0b'  # Tailwind Amber-500
    return '#EF4444'  # Red-500 (from sample)


def get_score_color_text(score):
    """
    Returns Tailwind CSS text color classes based on the score.
    """
    if score >= 90:
        return 'text-green-600'
    if score >= 50:
        return 'text-amber-600'
    return 'text-red-600'


def get_score_color_border(score):
    """
    Returns Tailwind CSS border color classes for summary boxes.
    """
    if score >= 90:
        return 'border-green-500'
    if score >= 50:
        return 'border-amber-500'
    return 'border-red-500'


def get_status_badge(score):
    """
    Returns a full Tailwind CSS class string for a status badge.
    Uses red for < 50, amber for 50-89, green for 90+
    Matches colors from performance_and_ui_report.html
    """
    if score >= 90:
        return 'px-3 py-1 text-xs rounded-full bg-green-100 text-green-700 font-medium'
    if score >= 50:
        return 'px-3 py-1 text-xs rounded-full bg-amber-100 text-amber-700 font-medium'
    return 'px-3 py-1 text-xs rounded-full bg-red-100 text-red-700 font-medium'


def get_status_label(score):
    """
    Returns a simple PASS, WARN, or FAIL label.
    """
    if score >= 90:
        return 'PASS'
    if score >= 50:
        return 'WARN'
    return 'FAIL'


def extract_report_data(data):
    """
    Extracts and processes all necessary data from the raw JSON report.
    """
    try:
        # Get top-level Lighthouse objects
        lh_categories = data.get('lighthouse', {}).get('categories', {})
        lh_audits = data.get('lighthouse', {}).get('audits', {})

        # --- 1. Get Summary Info ---
        page_url = 'Unknown URL'
        # Try to find a reliable URL from one of the audits
        if 'server-response-time' in lh_audits and lh_audits['server-response-time'].get('details', {}).get('items',
                                                                                                            []):
            page_url = lh_audits['server-response-time']['details']['items'][0].get('url', 'Unknown URL')

        raw_time = data.get('mergedAt', '2025-01-01T00:00:00.000Z')

        # Parse the ISO 8601 timestamp and format it
        exec_time = datetime.fromisoformat(raw_time.replace('Z', '+00:00'))
        formatted_time = exec_time.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

        # --- 2. Get All Category Scores ---
        perf_score_raw = lh_categories.get('performance', {}).get('score', 0)
        a11y_score_raw = lh_categories.get('accessibility', {}).get('score', 0)
        bestp_score_raw = lh_categories.get('best-practices', {}).get('score', 0)
        seo_score_raw = lh_categories.get('seo', {}).get('score', 0)

        # Store scores as 0-100 integers
        scores = {
            'accessibility': round((a11y_score_raw or 0) * 100),
            'best_practices': round((bestp_score_raw or 0) * 100),
            'seo': round((seo_score_raw or 0) * 100),
        }

        # --- 3. Calculate Performance Metrics Breakdown ---
        performance_metrics = []
        weighting_scheme = []
        metric_ids = set()

        # Get all audit IDs that belong to the performance category
        perf_audit_refs = lh_categories.get('performance', {}).get('auditRefs', [])
        performance_audit_ids = {ref['id'] for ref in perf_audit_refs}

        # Filter for just the audits that have weight (i.e., the main metrics)
        weighted_audits = [ref for ref in perf_audit_refs if ref.get('weight', 0) > 0]

        total_contribution = 0

        for ref in weighted_audits:
            audit_id = ref['id']
            weight = ref['weight']  # This is the percentage (e.g., 10, 25)
            audit = lh_audits.get(audit_id, {})

            score = audit.get('score', 0) or 0  # This is 0-1

            # Lighthouse score contribution is (score * weight)
            contribution = score * weight
            total_contribution += contribution

            metric_ids.add(audit_id)  # Keep track of main metrics

            performance_metrics.append({
                'title': audit.get('title', audit_id),
                'display_value': audit.get('displayValue', 'N/A'),
                'score': score,  # Score is 0-1
                'weight': weight,  # Weight is a percentage (e.g., 10, 25, 30)
                'contribution': contribution,
            })

            weighting_scheme.append({
                'title': audit.get('title', audit_id),
                'weight': int(weight),
            })

        # The final score is the sum of weighted contributions, rounded.
        total_score = round(total_contribution)
        scores['performance'] = total_score

        # --- 4. Find Diagnostic Errors (PERFORMANCE ONLY) ---
        # This section finds failing audits that are part of the 'performance'
        # category but are *not* the main weighted metrics.
        diagnostics = []
        for audit_id, audit in lh_audits.items():
            score = audit.get('score')

            # Check if it's a failing audit (score < 0.9, and not null)
            # AND it's a performance audit
            # AND it's NOT one of the main weighted metrics (we already show those)
            if (score is not None and
                    score < 0.9 and  # Fails if score is not 1 (or 0.9 for some)
                    audit_id in performance_audit_ids and
                    audit_id not in metric_ids):

                details_text = audit.get('displayValue', '')
                if not details_text:
                    if 'items' in audit.get('details', {}):
                        item_count = len(audit['details']['items'])
                        details_text = f"{item_count} items found"
                    else:
                        # Fallback to description, remove markdown links
                        details_text = audit.get('description', 'No details').split('[Learn more]')[0].strip()

                # Sanitize HTML in details
                details_text = html.escape(details_text)

                diagnostics.append({
                    'title': audit.get('title', audit_id),
                    'score': score,  # Score is 0-1
                    'status_label': get_status_label(score * 100),
                    'details_text': details_text,
                })

        return {
            'page_url': page_url,
            'execution_time': formatted_time,
            'scores': scores,
            'metrics': performance_metrics,
            'total_score': total_score,
            'diagnostics': diagnostics,
            'weighting_scheme': weighting_scheme
        }
    except Exception as e:
        print(f"Error processing JSON data: {e}")
        return None


def generate_html_report(data, min_pass_score=90):
    """
    Generates the full HTML report string from the processed data.
    """
    if not data:
        return "<h1>Error generating report.</h1>"

    # --- Helper variables for templating ---
    scores = data['scores']
    perf_score = scores['performance']

    # Use the color logic from the Lighthouse standard (90/50)
    perf_color_text = get_score_color_text(perf_score)

    final_result = "PASS" if perf_score >= min_pass_score else "FAIL"
    # Use red for FAIL as per image_45d246.png
    final_result_color = "text-green-600" if final_result == "PASS" else "text-red-600"

    # --- Dynamic Sections ---

    # 1. Performance Breakdown Table Rows
    metrics_rows_html = ""
    total_weight = 0
    for metric in data['metrics']:
        metric_score_100 = round(metric['score'] * 100)
        color_class = get_score_color_text(metric_score_100)
        weight = metric['weight']
        total_weight += weight
        metrics_rows_html += f"""
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{metric['title']}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{metric['display_value']}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold {color_class}">{metric_score_100}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{weight}%</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{round(metric['contribution'], 1)}</td>
        </tr>
        """

    # Add a total row for the breakdown
    metrics_rows_html += f"""
    <tr class="bg-indigo-50 font-bold">
        <td class="px-6 py-4 whitespace-nowrap text-sm text-indigo-700" colspan="3">FINAL CALCULATED SCORE</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-indigo-700">{total_weight}%</td>
        <td class="px-6 py-4 whitespace-nowrap text-lg {perf_color_text}">{perf_score}</td>
    </tr>
    """

    # 2. Diagnostics Table (Dynamic)
    diagnostics_html = ""
    if data['diagnostics']:
        diagnostics_rows_html = ""
        # Sort diagnostics by score (worst first)
        sorted_diagnostics = sorted(data['diagnostics'], key=lambda x: x['score'])
        for diag in sorted_diagnostics:
            badge_class = get_status_badge(diag['score'] * 100)
            diagnostics_rows_html += f"""
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 text-sm font-medium text-gray-800">{diag['title']}</td>
                <td class="px-6 py-4">
                    <span class="{badge_class}">
                        {diag['status_label']}
                    </span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-600">{diag['details_text']}</td>
            </tr>
            """

        diagnostics_html = f"""
        <section class="mb-12">
            <h2 class="text-2xl font-bold text-gray-700 mb-4 border-b pb-2">Key Performance Diagnostics</h2>
            <p class="text-gray-600 mb-4">
                These audits do not directly contribute to the Performance score but highlight critical opportunities for improvement.
            </p>
            <div class="bg-white rounded-xl shadow-lg overflow-hidden">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-indigo-50">
                        <tr>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Diagnostic Audit
                            </th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Result
                            </th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Details
                            </th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100">
                        {diagnostics_rows_html}
                    </tbody>
                </table>
            </div>
        </section>

        <hr class="my-8 border-gray-200">
        """

    # 3. Weighting Scheme List
    weighting_html = ""
    for item in data['weighting_scheme']:
        weighting_html += f"""
        <li class="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
            <strong class="text-2xl font-bold text-indigo-600 block mb-1">{item['weight']}%</strong>
            <span class="text-gray-700">{item['title']}</span>
        </li>
        """

    # --- Final HTML String ---
    # We use {{...}} to escape curly braces for Chart.js/CSS, and {variable} for Python f-strings
    # Styling is based on the provided HTML report samples
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lighthouse Performance Report</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js"></script>
    <style>
        /* Custom font from load_test_report.html */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
        body {{ font-family: 'Inter', sans-serif; }}

        /* Styles for the main performance doughnut chart */
        .chart-container-main {{
            position: relative;
            width: 200px;
            height: 200px;
        }}
        .chart-score-main {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 3.75rem; /* 60px */
            font-weight: 800;
        }}

        /* Styles for the small doughnut charts */
        .chart-container-sub {{
            position: relative;
            width: 120px; 
            height: 120px;
            margin: 0 auto 10px;
        }}
        .chart-score-sub {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 1.875rem; /* 30px */
            font-weight: 700;
        }}
        .weighting-list {{
            list-style: none;
            padding-left: 0;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
    </style>
</head>
<body class="bg-gray-100 text-gray-800 p-4 sm:p-8">

    <div class="max-w-7xl mx-auto">

        <header class="mb-8 p-6 bg-white shadow-lg rounded-xl border-t-4 border-indigo-600">
            <h1 class="text-3xl font-extrabold text-indigo-700">Lighthouse Performance Report</h1>
            <p class="text-gray-500 mt-1 text-sm">
                <strong>URL Tested:</strong> <a href="{data['page_url']}" target="_blank" class="text-indigo-500 hover:underline">{data['page_url']}</a> <br>
                <strong>Generated on:</strong> {data['execution_time']}
            </p>
        </header>

        <div class="grid grid-cols-1 mb-10">
            <div class="bg-white p-6 rounded-xl shadow-md border-b-4 border-indigo-500">

                <div class="grid grid-cols-1 md:grid-cols-2 gap-0 items-center">

                    <!-- Left Side: Doughnut Chart -->
                    <div class="flex flex-col items-center">
                        <p class="text-sm text-gray-500 font-semibold uppercase tracking-wider mb-2">Performance Quality Index (PQI)</p>
                        <div class="chart-container-main">
                            <canvas id="perfScoreChart"></canvas>
                            <div class="chart-score-main {perf_color_text}">{perf_score}</div>
                        </div>
                    </div>

                    <!-- Right Side: Min Score and Final Result -->
                    <div class="flex flex-col items-center">
                        <div class="text-center mb-6">
                            <p class="text-sm text-gray-500 font-semibold uppercase tracking-wider">Min Score to Pass</p>
                            <p class="text-4xl font-bold text-gray-700 mt-1">{min_pass_score}</p>
                        </div>
                        <div class="text-center">
                            <p class="text-sm text-gray-500 font-semibold uppercase tracking-wider">Final Result</p>
                            <p class="text-4xl font-bold {final_result_color} mt-1">{final_result}</p>
                        </div>
                    </div>

                </div>
            </div>
        </div>

        <section class="mb-12">
            <h2 class="text-2xl font-bold text-gray-700 mb-6 border-b pb-2">Additional Scores</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">

                <div class="bg-white p-6 rounded-xl shadow-lg text-center border-b-4 {get_score_color_border(scores['accessibility'])}">
                    <h3 class="text-lg font-semibold text-gray-600 mb-4">Accessibility</h3>
                    <div class="chart-container-sub">
                        <canvas id="a11yChart"></canvas>
                        <div class="chart-score-sub {get_score_color_text(scores['accessibility'])}">{scores['accessibility']}</div>
                    </div>
                </div>

                <div class="bg-white p-6 rounded-xl shadow-lg text-center border-b-4 {get_score_color_border(scores['best_practices'])}">
                    <h3 class="text-lg font-semibold text-gray-600 mb-4">Best Practices</h3>
                    <div class="chart-container-sub">
                        <canvas id="bestpChart"></canvas>
                        <div class="chart-score-sub {get_score_color_text(scores['best_practices'])}">{scores['best_practices']}</div>
                    </div>
                </div>

                <div class="bg-white p-6 rounded-xl shadow-lg text-center border-b-4 {get_score_color_border(scores['seo'])}">
                    <h3 class="text-lg font-semibold text-gray-600 mb-4">SEO</h3>
                    <div class="chart-container-sub">
                        <canvas id="seoChart"></canvas>
                        <div class="chart-score-sub {get_score_color_text(scores['seo'])}">{scores['seo']}</div>
                    </div>
                </div>
            </div>
        </section>

        <hr class="my-8 border-gray-200">

        <section class="mb-12">
            <h2 class="text-2xl font-bold text-gray-700 mb-6 border-b pb-2">Performance Score Breakdown</h2>
            <p class="text-gray-600 mb-4">
                The final performance score is a weighted average of key user-centric metrics. 
                This table shows how each metric contributed to the final score.
            </p>
            <div class="bg-white rounded-xl shadow-lg overflow-hidden">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-indigo-50">
                        <tr>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Metric
                            </th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Measured Value
                            </th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Score (0-100)
                            </th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Weight
                            </th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Score Contribution
                            </th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100">
                        {metrics_rows_html}
                    </tbody>
                </table>
            </div>
        </section>

        <hr class="my-8 border-gray-200">

        {diagnostics_html}

        <section>
            <h2 class="text-2xl font-bold text-gray-700 mb-6 border-b pb-2">Score Weighting Scheme</h2>
            <p class="text-gray-600 mb-4">This performance score was calculated using the Lighthouse 10 weighting:</p>
            <ul class="weighting-list">
                {weighting_html}
            </ul>
        </section>

    </div>

    <script>
        // --- Chart Helper Function ---
        // This function creates the small doughnut charts
        function createDoughnutChart(chartId, score, scoreColor, cutout = '80%') {{
            const data = {{
                datasets: [{{
                    data: [score, 100 - score],
                    backgroundColor: [scoreColor, '#e9ecef'], // Use light gray for the remainder
                    borderWidth: 0,
                    borderRadius: 5
                }}]
            }};
            const config = {{
                type: 'doughnut',
                data: data,
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: cutout,
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{ enabled: false }}
                    }}
                }}
            }};
            // Check if element exists before creating chart
            const ctx = document.getElementById(chartId);
            if (ctx) {{
                new Chart(ctx.getContext('2d'), config);
            }}
        }}

        // --- Render Charts ---
        // Create the main performance chart
        createDoughnutChart('perfScoreChart', {perf_score}, '{get_score_color_hex(perf_score)}', '85%');

        // Create the smaller charts for the "Additional Scores" section
        createDoughnutChart('a11yChart', {scores['accessibility']}, '{get_score_color_hex(scores['accessibility'])}');
        createDoughnutChart('bestpChart', {scores['best_practices']}, '{get_score_color_hex(scores['best_practices'])}');
        createDoughnutChart('seoChart', {scores['seo']}, '{get_score_color_hex(scores['seo'])}');
    </script>

</body>
</html>
    """
    return html_template


def main():
    # Define input and output file paths
    # Using the specific file name provided by the user
    json_input_file = 'lighthouse/merged-report.json'
    html_output_file = 'lighthouse_performance_dashboard.html'

    # Define the minimum score required to pass
    MIN_PASS_SCORE = 90

    print(f"Loading JSON data from {json_input_file}...")

    # 1. Load data
    try:
        with open(json_input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found at {json_input_file}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_input_file}")
        return

    # 2. Extract and process data
    print("Processing data and calculating scores...")
    report_data = extract_report_data(data)

    if not report_data:
        print("Failed to process report data.")
        return

    # 3. Generate HTML
    print("Generating HTML report...")
    html_content = generate_html_report(report_data, min_pass_score=MIN_PASS_SCORE)

    # 4. Save HTML file
    try:
        with open(html_output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Successfully generated report: {html_output_file}")
    except IOError as e:
        print(f"Error writing HTML file: {e}")


if __name__ == "__main__":
    main()