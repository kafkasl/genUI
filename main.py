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

user_info = {}

def wrap_response(*r):
    return Div(*r, id="chat", hx_swap_oob="beforeend")

def generate_input(label: str, placeholder: str, id: str):
    return LabelInput(label, placeholder, id, hx_post="/chat")

def generate_select(label: str, options: list[str], id: str):
    return Select(label, options, id, hx_post="/chat", hx_trigger="change")

@rt("/chat")
def post(name: str = '', sex: str = '', age: str = ''):
    print(f"name: {name}, sex: {sex}")
    if name:
        user_info['name'] = name
        return wrap_response(P(f"Welcome {name}!"), generate_select("Sex", ["Male", "Female"], "sex"))
    elif sex:
        user_info['sex'] = sex
        return wrap_response(P(f"Good {sex}!"), generate_input("Age", "Your age", "age"))
    elif age:
        user_info['age'] = age
        return wrap_response(P(f"Hello {user_info['name']}! You are a {user_info['sex']} and {user_info['age']} years old."))
    
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
            # Standard select with explicit HTMX attributes
            Label("Test Select", 
                Select(
                    Option("Choose an option", value="", selected=True, disabled=True),
                    Option("Male", value="Male"),
                    Option("Female", value="Female"),
                    name="test_sex",
                    id="test_sex",
                    hx_post="/chat",
                    hx_trigger="change"
                )
            ),
            generate_input('Name', 'Your name', 'name'),
            Div(id="chat"),
            footer=DivLAligned(*[UkIconLink(icon,href=url) for icon,url in socials])))

serve()
