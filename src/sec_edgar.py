from sec_downloader import Downloader
from sec_downloader.types import RequestedFilings
import sec_parser as sp

# Initialize the downloader with your company name and email
_dl = Downloader("MyCompanyName", "email@example.com")

def _metadata_to_dict(metadata):
    return {
            'url': metadata.primary_doc_url,
            'cik': metadata.cik,
            'form_type': metadata.form_type,
            'filing_date': metadata.filing_date
            }

def request_recent_filings(ticker, form_type="10-K"):
    try:
        metadatas = _dl.get_filing_metadatas(RequestedFilings(ticker_or_cik=ticker, form_type=form_type, limit=10000 ))
        return list(map(_metadata_to_dict, metadatas))
    except:
        print(f"There was an error getting filings for the ticker {ticker}")

def download_sec_html(url):
    html = _dl.download_filing(url=url).decode()
    return html

if __name__ == '__main__':
    print(download_sec_html("abc123"))
