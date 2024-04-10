from sec_downloader import Downloader
from sec_downloader.types import RequestedFilings
import sec_parser as sp

# Initialize the downloader with your company name and email
_dl = Downloader("MyCompanyName", "email@example.com")

# Utility function to make the example code a bit more compact
def _print_first_n_lines(text: str, *, n: int):
    print("\n".join(text.split("\n")[:n]), "...", sep="\n")

# def get_recent_filings(ticker):
#     html = dl.get_filing_html(ticker=ticker, form="10-Q")
#     elements: list = sp.Edgar10QParser().parse(html)
#
#     output: str = sp.render(elements)
#     _print_first_n_lines(output, n=7)

def _metadata_to_dict(metadata):
    return {
            'url': metadata.primary_doc_url,
            'cik': metadata.cik,
            'form_type': metadata.form_type,
            'filing_date': metadata.filing_date
            }

def request_recent_filings(ticker):
    try:
        metadatas = _dl.get_filing_metadatas(RequestedFilings(ticker_or_cik=ticker, form_type="10-K", limit=5))
        return list(map(_metadata_to_dict, metadatas))
    except:
        print(f"There was an error getting filings for the ticker {ticker}")

if __name__ == '__main__':
    print(request_recent_filings('AAPL'))
    print(request_recent_filings('faketicker'))
