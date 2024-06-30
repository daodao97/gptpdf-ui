# gptpdf ui

[gptpdf](https://github.com/CosmosShadow/gptpdf)

![](preview.png)

## install dependencies

```shell
pip install -r requirements.txt
```

## set openai key

file `parse_pdf.py`

## start serve

```shell
python main.py
```

## routes

- /upload response pdf conent with sse

- /files/<path:filename>  response pdf content with html

- /md/<path:filename>  response pdf content with md