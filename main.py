import requests
import os
from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request
from src.sec_edgar import request_recent_filings, download_sec_html
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain_text_splitters import CharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain_community.document_transformers import Html2TextTransformer
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_text_splitters import TokenTextSplitter
from bs4 import BeautifulSoup
from langchain.schema.document import Document


app = Flask(__name__)
load_dotenv('.env')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)


# client = OpenAI(api_key=OPENAI_API_KEY)

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


def get_text_chunks_langchain(text):
    text_splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = [Document(page_content=x) for x in text_splitter.split_text(text)]
    # texts = text_splitter.split_text(text)
    return docs

def get_response_from_GPT(message):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ]
    )
    return completion.choices[0].message.content

def get_summary_from_url(url):
    html = download_sec_html(url)
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    docs = get_text_chunks_langchain(text)
   
    # message = "Summarize this and avoid the boiler plate info: " + text
    # response = get_response_from_GPT(message)
    
    # # print(response)
    
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

    #Map
    map_template = """The following is a set of documents
    {docs}
    Based on this list of docs, please summarize these docs and avoid the boiler plate info.
    Helpful Answer:
    """
    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = LLMChain(llm=llm, prompt=map_prompt)

    #Reduce
    reduce_template = """The following is a set of summaries:
    {docs}
    Take these and distill it into a final, consolidated summary of the main themes.
    Helpful Answer:
    """
    reduce_prompt = PromptTemplate.from_template(reduce_template)

    #Run chain
    reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)

    #Takes a list of documents, combines them into a single string, and passes this to an LLMChain
    combine_documents_chain = StuffDocumentsChain(
        llm_chain=reduce_chain, document_variable_name="docs"
    )

    #Combines and iteratively reduces the mapped documents
    reduce_documents_chain = ReduceDocumentsChain(
        combine_documents_chain=combine_documents_chain,
        collapse_documents_chain=combine_documents_chain,
        token_max=4000,
    )

    #Combining documents by mapping a chain over them, then combining results
    map_reduce_chain = MapReduceDocumentsChain(
        llm_chain=map_chain,
        reduce_documents_chain=reduce_documents_chain,
        document_variable_name="docs",
        return_intermediate_steps=False
    )

    # text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    #     chunk_size=1000, chunk_overlap=0
    # )
    # split_docs = text_splitter.split_documents(docs)
    result = map_reduce_chain.invoke(docs)
    summary = result['output_text']
    return summary
    
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
    
@app.route('/get_summary')
def get_summary():
    url = request.args.get('url')
    
    # Make sure that the URL actually goes to sec.gov
    if not url.startswith("https://www.sec.gov/"):
        return jsonify({"error": "Invalid SEC URL"}), 400
    
    try:
        summary = get_summary_from_url(url)
        
        return jsonify(summary), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "error downloading"}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0")
