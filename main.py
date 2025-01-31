from fasthtml.common import *
from claudette import *
import asyncio
from monsterui.all import *

# Create your app with the theme
hdrs = Theme.blue.headers()
app, rt = fast_app(hdrs=hdrs, exts='ws')


# Set up a chat model client and list of messages (https://claudette.answer.ai/)
cli = AsyncClient(models[-1])
sp = """You are a helpful and concise assistant."""
messages = [
    {"role": "assistant", "content": "Hi! How can I help you today? 🚀"},
    {"role": "user", "content": "Can you help me with MonsterUI?"}
]

def UsrMsg(txt, content_id): 
    return Div(Div(txt, id=content_id,cls='whitespace-pre-wrap'), cls='max-w-[70%] ml-auto rounded-3xl bg-[#f4f4f4] px-5 py-2.5 rounded-tr-lg')

def AIMsg(txt, content_id): 
    avatar = Div(UkIcon('bot', height=24, width=24), cls='h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center')
    return Div(Div(avatar, Div(txt, cls='whitespace-pre-wrap ml-3'), cls='flex items-start'), id=content_id, cls='max-w-[70%] rounded-3xl px-5 py-2.5 rounded-tr-lg')

def ChatMessage(msg_idx, **kwargs):
    """Unified interface for chat messages"""
    msg = messages[msg_idx]
    content_id = f"chat-content-{msg_idx}"
    return (UsrMsg(msg['content'], content_id) if msg['role'] == 'user' 
            else AIMsg(msg['content'], content_id))

Input = Form(
    Div(
        TextArea(placeholder='Message assistant', 
                cls='resize-none border-none outline-none bg-transparent w-full shadow-none ring-0 focus:ring-0 focus:outline-none hover:shadow-none text-lg'),
        DivFullySpaced(
            DivHStacked(
                UkIconLink('paperclip', height=24, width=24, cls='hover:opacity-70'),
                UkIconLink('mic', height=24, width=24, cls='hover:opacity-70')
            ),
            Button(UkIcon('arrow-right', height=24, width=24), 
                  cls='bg-black text-white rounded-full hover:opacity-70 h-8 w-8 transform -rotate-90'),
            cls='px-3'
        )
    ), cls='p-2 bg-[#f4f4f4] rounded-3xl')

def chat_layout():
    return Container(
        Div(
            *[ChatMessage(msg_idx) for msg_idx, msg in enumerate(messages)],
            cls='space-y-2'
        ),
        Input,
        cls='space-y-4'
    )
# The main screen
@app.route("/")
def get():
    return chat_layout()




serve()