import shutil as sh

def archive(filename : str):
    sh.make_archive(f'./uploads/{filename}.parse', 'zip', f'./uploads/{filename}.parse')
    sh.move(f'./uploads/{filename}.parse.zip', f'./uploads/{filename}.parse/archive.zip')
