from fasthtml.common import *
from monsterui.all import *
from claudette import *
import os
os.environ['ANTHROPIC_LOG'] = 'debug'

# Choose a theme color (blue, green, red, etc)
hdrs = Theme.blue.headers()

# Create your app with the theme
app, rt = fast_app(hdrs=hdrs)


model = models[1]

chat = Chat(model, sp="""You are a helpful and concise assistant. You can only get user feedback generating HTML elements in HTMX like this LabelInput("Name", placeholder="Your name", id="name", hx_post="/chat",  hx_target="chat", hx_swap_oob="beforeend") """)


@rt("/chat")
def post(name: str = '', sex: str = ''):
    print(f"name: {name}, sex: {sex}")
    return Div(LabelInput("Sex", placeholder="Your sex", id="sex", hx_post="/chat"), 
               id="chat", hx_swap_oob="beforeend")
    # r = chat(f"I'm {name}")
    # txt = contents(r)
    # print('txt: ', txt)
    # return txt
    # el = P(txt, hx_target="chat", hx_swap_oob="beforeend")
    # print('element: ', el)
    # return el
    # return H1(f"Welcome {name}!", id="title", hx_swap_oob="outerHTML")

@rt
def index():
    socials = (('github','https://github.com/AnswerDotAI/MonsterUI'),
               ('twitter','https://twitter.com/isaac_flath/'),
               ('linkedin','https://www.linkedin.com/in/isaacflath/'))
    return Titled("",
        Card(
            H1("Welcome!", id="title"),
            P("Your first GenUI experience with FastHTML", cls=TextPresets.muted_sm),
            LabelInput("Name", placeholder="Your name", id="name", hx_post="/chat"),
            Div(id="chat"),
            footer=DivLAligned(*[UkIconLink(icon,href=url) for icon,url in socials])))

serve()
