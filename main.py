from flask import Flask, render_template, jsonify, request
from src.sec_edgar import request_recent_filings

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
    recent_filings = request_recent_filings(company)

    if recent_filings == None:
        return jsonify({"error": "Company not found"}), 404

    return jsonify({"company": company, "filings": recent_filings})

@app.route('/filing_html_link')
def get_filing_html():
    company = request.args.get('company')
    filing_type = request.args.get('filing_type')
    if not all([company, filing_type]):
        return jsonify({"error": "Company and filing_type are required"}), 400
    
    if company not in recent_filings_data or filing_type not in recent_filings_data[company]:
        return jsonify({"error": "Filing not found"}), 404
    
    filing_html_link = get_filing_html_link(company, filing_type)
    return jsonify({"company": company, "filing_type": filing_type, "html_link": filing_html_link})

if __name__ == '__main__':
    app.run(debug=True)
