from sec_downloader import Downloader
from sec_downloader.types import RequestedFilings
import dateparser

# Initialize the downloader with your company name and email
_dl = Downloader("MyCompanyName", "email@example.com")

def _metadata_to_dict(metadata):
    print(metadata)
    return {
            'url': metadata.primary_doc_url,
            'cik': metadata.cik,
            'form_type': metadata.form_type,
            'filing_date': metadata.filing_date,
            'company_name': metadata.company_name
            }

def _request_single_form_type(ticker, form_type):
    try:
        metadatas = _dl.get_filing_metadatas(RequestedFilings(ticker_or_cik=ticker, form_type=form_type, limit=10000 ))
        return list(map(_metadata_to_dict, metadatas))
    except:
        print(f"There was an error getting filings for the ticker {ticker}")

def _request_all_form_types(ticker):
    result = []
    form_types = [
        'NO ACT', 'SC 13G/A', 'S-8', '8-K', 'CERT', 'CERTNYS', 'FWP', '25-NSE',
        '424B2', 'CORRESP', 'DEFA14A', 'S-8 POS', 'DEF 14A', 'IRANNOTICE', '144',
        'PX14A6G', '10-K', 'PRE 14A', '8-K/A', 'PX14A6N', '10-Q', 'UPLOAD',
        '8-A12B', 'DFAN14A', 'SD', 'SC 13G', '25', 'S-3ASR'
    ]
    # form_types = [
    #     "10-K",
    #     "10-Q",
    #     # "8-K",
    #     # "Proxy Statement (DEF 14A)",
    #     # "Form 4",
    #     # "S-1",
    #     # "S-3",
    #     # "Form 3",
    #     # "Form 13D/13G"
    # ]
    for form_type in form_types:
        filings = _request_single_form_type(ticker, form_type)
        print(filings)
        if filings:
            result += filings
    return sorted(result, key=lambda filing: dateparser.parse(filing["filing_date"]), reverse=True)



def request_recent_filings(ticker, form_type="All"):
    if form_type == "All":
        return _request_all_form_types(ticker)
    return _request_single_form_type(ticker, form_type)


def download_sec_html(url):
    html = _dl.download_filing(url=url).decode()
    return html

if __name__ == '__main__':
    print(download_sec_html("abc123"))
