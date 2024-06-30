from gptpdf import parse_pdf
import sys

filepath = sys.argv[1]

api_key = 'sk-xxxxxxxxx'
base_url = 'https://api.xxxxxx.com/v1'

parse_pdf(filepath, api_key=api_key, base_url=base_url, output_dir=filepath+".parse", verbose=True)