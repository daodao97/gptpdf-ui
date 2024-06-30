from gptpdf import parse_pdf
import sys

filepath = sys.argv[1]
api_key = sys.argv[2]
base_url = sys.argv[3]

parse_pdf(filepath, api_key=api_key, base_url=base_url, output_dir=filepath+".parse", verbose=True)