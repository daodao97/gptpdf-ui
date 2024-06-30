
from flask import Flask, request, render_template, Response, send_file, send_from_directory
import os
import subprocess
import base64
import markdown
from markupsafe import Markup
from markdown.inlinepatterns import InlineProcessor
from markdown.extensions import Extension
import xml.etree.ElementTree as ElementTree

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html', pdf_files= get_all_pdf_names(UPLOAD_FOLDER))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        # replace whitespace with underscore
        filepath = filepath.replace(' ', '_')
        file.save(filepath)
        return Response(run_gptpdf(filepath), content_type='text/event-stream')
    
@app.route('/files/<path:filename>')
def md_render(filename):
    # 读取 Markdown 文件并转换为 HTML
    file_path = os.path.join(UPLOAD_FOLDER, filename + ".parse", "output.md")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            html_content = markdown.markdown(content, extensions=[ImagePrefixExtension(prefix= "/"+os.path.join(UPLOAD_FOLDER, filename + ".parse"))])
            return render_template('file.html', content=Markup(html_content), filename=filename)
    else:
         if filename.lower().endswith('.png'):
            # 直接发送 PNG 文件
            return send_file(os.path.join(UPLOAD_FOLDER, filename + ".parse", filename), mimetype='image/png')
         else:
            return "File not found", 404

@app.route('/uploads/<path:filename>')
def file_server(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/md/<path:filename>')
def md_format(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename + ".parse", "output.md")
    return send_file(file_path, filename)

def run_gptpdf(filepath):
    process = subprocess.Popen(['python', 'parse_pdf.py', filepath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in iter(process.stdout.readline, b''):
        line_str = line.decode('utf-8')
        if line_str.startswith('![]('):  # ![](1.png)
            image_path = line_str.strip()[4:-1]  # Extract the image path from the line
            full_image_path = os.path.join(filepath + ".parse", image_path)
            if os.path.exists(full_image_path):
                with open(full_image_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    base64_image = f"data:image/png;base64,{encoded_string}"
                    line_str = f"![]({base64_image})"
        yield f'data: {line_str}\n\n'
    process.stdout.close()
    process.wait()

def get_all_pdf_names(directory):
    """
    获取目录下所有的 PDF 文件名称列表
    :param directory: 目标目录
    :return: PDF 文件名称列表
    """
    pdf_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(file)
    return pdf_files

class ImagePrefixExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            'prefix': ['', 'Prefix for image paths']
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        IMAGE_LINK_RE = r'!\[(.*?)\]\((.*?)\)'
        md.inlinePatterns.register(ImagePrefixInlineProcessor(IMAGE_LINK_RE, self.getConfigs()), 'image_prefix', 175)

class ImagePrefixInlineProcessor(InlineProcessor):
    def __init__(self, pattern, config):
        super().__init__(pattern)
        self.config = config

    def handleMatch(self, m, data):
        if m:
            alt = m.group(1)
            src = m.group(2)
            src = self.config['prefix'] + "/" + src
            el = ElementTree.Element("img")
            el.set('src', src)
            el.set('alt', alt)
            return el, m.start(0), m.end(0)
        return None, None, None



if __name__ == '__main__':
    app.run(debug=True)
