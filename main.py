import requests
from flask import Flask, render_template, jsonify, request
from src.sec_edgar import request_recent_filings, download_sec_html

app = Flask(__name__)

# Mock data for demonstration purposes
# Replace this with actual data fetching from SEC API
recent_filings_data = {
    "AAPL": ["10-K", "10-Q", "8-K"],
    "GOOGL": ["10-K", "10-Q"],
    "AMZN": ["10-K", "10-Q", "S-1"]
}

# Mock function to get HTML link for a filing
def get_filing_html_link(company, filing_type):
    # Mock link generation, replace this with actual logic
    return f"https://example.com/{company}/{filing_type}.html"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/public/<path:path>')
def serve_static(path):
    return app.send_static_file(path)

@app.route('/recent_filings')
def get_recent_filings():
    company = request.args.get('company')
    filing_type = request.args.get('filing_type')

    if company:
        company = company.upper() # ensure that tickers are upper-case
    else:
        return jsonify({"error": "Missing query param: comany"}), 400

    if not filing_type:
        filing_type = "All"

    recent_filings = request_recent_filings(company, filing_type)

    if recent_filings == None:
        return jsonify({"error": "Company not found"}), 404

    return jsonify({"company": company, "filings": recent_filings})

@app.route('/get_filing_html')
def get_filing_html():
    url = request.args.get('url')

    # Make sure that the URL actually goes to sec.gov
    if not url.startswith("https://www.sec.gov/"):
        return jsonify({"error": "Invalid SEC URL"}), 400

    try:
        html = download_sec_html(url)
        return html
    except:
        print(f'There was an error downloading the SEC HTML for {url}')
        return jsonify({"error": "Invalid SEC URL"}), 404

if __name__ == '__main__':
    app.run(debug=True)
