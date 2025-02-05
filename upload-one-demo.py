from fasthtml.common import *
from pathlib import Path

app, rt = fast_app()

upload_dir = Path("filez")
upload_dir.mkdir(exist_ok=True)

# @rt('/')
# def get():
#     return Titled("File Upload Demo",
#         Article(
#             Form(
#                 Input(type="file", 
#                     name="file",
#                     enctype="multipart/form-data",
#                     cls="hidden",
#                     id="file-input",
#                     hx_post="/upload",
#                     hx_trigger="change from:#file-input",
#                     hx_target="#result-one",
#                     hx_swap="beforeend"),
#                 type='submit'
#               ),
#             Div(id="result-one")
#         )
#     )


@rt('/')
def get():
    return Titled("File Upload Demo",
        Article(
            Form(
                Input(type="file", name="file", id="file-input"),
                hx_post="/upload", hx_encoding="multipart/form-data",
                hx_trigger="change from:#file-input",
                hx_target="#result-one", hx_swap="beforeend"
            ),
            Div(id="result-one")
        )
    )

def FileMetaDataCard(f):I want to modify these examples so we can upload.
    return Article(
        Header(H3(f.filename)),
        Ul(Li("Size: ", f.size), Li("Content Type: ", f.content_type), Li("Headers: ", f.headers))
    )

@rt
async def upload(request):
    form = await request.form()
    f = form['file']
    card = FileMetaDataCard(f)
    filebuffer = await f.read()
    (upload_dir / f.filename).write_bytes(filebuffer)
    return card

serve()