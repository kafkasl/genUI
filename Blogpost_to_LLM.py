from fastcore.utils import *
import fastcore.all as fc, re, math, itertools, functools, numpy as np, types, typing, dataclasses, matplotlib.pyplot as plt, collections, regex
from fastcore.xtras import dict2obj
from regex import search
from collections import Counter
from collections.abc import Iterable
np.set_printoptions(linewidth=150, suppress=True)
plt.rcParams['figure.dpi'] = 50
from httpx import get as xget
import yaml
from datetime import datetime
from monsterui.all import *
from fasthtml.common import *

def parse_post(url):
    text = xget(url).text
    parts = text.split('---\n')
    meta = yaml.safe_load(parts[1])
    return dict2obj({
        'title': meta['title'],
        'content': parts[2].strip(),
        'original_url': meta.get('original'),
        'images': meta.get('images', []),
        'created_at': datetime.now().isoformat()
    })

links = L("https://raw.githubusercontent.com/kafkasl/medium2md/refs/heads/main/posts/building-apps-no-one-needs-dogfooding-hammers-and-over-engineering.md", 
"https://raw.githubusercontent.com/kafkasl/medium2md/refs/heads/main/posts/from-text-to-actions-llms-as-the-new-software-consumers.md", 
"https://raw.githubusercontent.com/kafkasl/medium2md/refs/heads/main/posts/how-i-validated-a-gmail-ai-assistant-in-under-a-week-with-chatgpt.md",
"https://raw.githubusercontent.com/kafkasl/medium2md/refs/heads/main/posts/why-give-ai-agents-access-to-money.md")

posts = links.map(parse_post)




import apsw, apsw.bestpractice  
apsw.bestpractice.apply(apsw.bestpractice.recommended)
dbpath = Path('data')  
dbpath.mkdir(exist_ok=True)  
db_fname = dbpath / 'blog.db'
db = apsw.Connection(str(db_fname))  
c = db.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    original_url TEXT,
    created_at TEXT,
    embedding BLOB,
    images TEXT  -- We'll store as JSON array
)''')

def list_posts(db):
    return L(db.cursor().execute('SELECT id, title FROM posts ORDER BY id'))

list_posts(db)

def get_post(db, id):
    cur = db.cursor()
    sql = 'SELECT * FROM posts WHERE id = ?'
    row = cur.execute(sql, (id,)).fetchone()
    if not row: return None
    cols = [d[0] for d in cur.description]
    return dict2obj(dict(zip(cols, row)))

get_post(db, 1).keys()

from monsterui.all import *

def BlogPost(post):
    return Article(
        ArticleTitle(post.title),
        ArticleMeta(
            DivHStacked(UkIcon('calendar', height=16, cls='mr-2 inline'), 
                post.created_at.split('T')[0])
        ),
        Container(render_md(post.content.splitlines()[1:]))
    )

# Test it with one post
# show(BlogPost(get_post(db, 1)))

from fastcore.utils import *
import fastcore.all as fc, re, math, itertools, functools, types, typing, dataclasses, collections, regex
import numpy as np, matplotlib.pyplot as plt, google.generativeai as genai

def array(x): return x if isinstance(x, np.ndarray) else np.array(list(x) if isinstance(x, Iterable) else x)
def cos_sim(a, b): return (a@b)/(np.linalg.norm(a)*np.linalg.norm(b))

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
def get_emb(txt):
    res = genai.embed_content(model="models/text-embedding-004", content=txt)
    return array(res['embedding'])

get_emb(posts[0].content)[:20]

def delete_posts():
    c.execute('DELETE FROM posts')
    print(f"Posts in DB: {list_posts(db)}")
#delete_posts()

def insert_post(db, post):
    sql = '''INSERT INTO posts (title, content, original_url, created_at, images, embedding)
             VALUES (?, ?, ?, ?, ?, ?)'''
    emb = get_emb(post.content)
    db.cursor().execute(sql, (
        post.title,
        post.content,
        post.original_url,
        post.created_at,
        json.dumps(list(post.images)),
        emb
    ))

# Insert all posts with embeddings
for p in posts: insert_post(db, p)

def get_post(db, id):
    cur = db.cursor()
    sql = 'SELECT * FROM posts WHERE id = ?'
    row = cur.execute(sql, (id,)).fetchone()
    if not row: return None
    cols = [d[0] for d in cur.description]
    d = dict(zip(cols, row))
    if d['embedding'] is not None: d['embedding'] = np.frombuffer(d['embedding'])
    return dict2obj(d)

def sims(query, db, n=4):
    qemb = get_emb(query)
    res = [(id, title, cos_sim(qemb, np.frombuffer(emb))) for id, title, _, _, _, emb, _ in 
           db.execute('select * from posts').fetchall()]
    return L(sorted(res, key=itemgetter(2), reverse=True)[:n])
def get_post_content(
    id: int    # The ID of the post to retrieve
) -> str:     # The post's content
    "Get the full content of a post by ID"
    post = get_post(db, id)
    return post.content if post else None

def render_post(
    id: int    # The ID of the post to render
) -> str:     # The rendered markdown
    "Render a post's content as markdown"
    post = get_post(db, id)
    return render_md(post.content) if post else None

# Update search_posts to include ID
def search_posts(
    query: str,  # The search query to find similar posts
    n: int = 4   # Number of results to return
) -> list:       # List of (id, title, similarity) tuples
    "Search posts by semantic similarity to the query"
    results = sims(query, db, n)
    return [(id, title, f"{score:.2f}") for id, title, score in results]

# Update the system prompt to be more comprehensive
sp = """You are a helpful assistant that can search through blog posts. 
When showing search results, format them as a markdown list with scores.
When asked about specific posts, you can retrieve and discuss their content.
You can also render posts in markdown format when asked to show them."""

chat = Chat(model, sp=sp, tools=[search_posts, get_post_content, render_post])


def list_all_posts(
) -> list:    # List of (id, title) tuples
    "List all available blog posts"
    return L(db.cursor().execute('SELECT id, title FROM posts ORDER BY id')).map(tuple)

# Update chat with the new tool
sp = """You are a helpful assistant that managing Pol personal blog."""

chat = Chat(model, sp=sp, tools=[search_posts, get_post_content, render_post, list_all_posts])

# Test it
chat.toolloop("List all available blog posts")

from functools import partial

def render_post(id: int) -> str:
    "Get post content as HTML string"
    post = get_post(db, id)
    if not post: return ""
    return str(Div(
        H1(post.title),
        Div(render_md(post.content)),
        cls='blog-post'
    ))

async def render_post_to_ws(id: int, send) -> str:
    "Render post directly to websocket"
    await send(render_post(id), hx_swap_oob='beforeend', id="chatlist")
    return "Post rendered successfully"

@app.ws('/wscon')
async def submit(msg: str, images: List[str] = [], send = None):
    # Create the tool with send bound to it
    render_tool = partial(render_post_to_ws, send=send)
    chat = Chat(model, sp=sp, tools=[search_posts, get_post_content, render_tool, list_all_posts])
    # ... rest of handler
