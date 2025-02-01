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
    {"role": "user", "content": "Can you help me with MonsterUI?"},
    {"role": "assistant", "content": "Of course! MonsterUI is a library of components that make it easy to build complex, data-driven web applications. It's built on top of Flask and uses Tailwind CSS for styling."},
]

def UsrMsg(txt, content_id):
    txt_div = Div(txt, id=content_id, cls='whitespace-pre-wrap break-words')
    return Div(txt_div,
              cls='max-w-[70%] ml-auto rounded-3xl bg-[#f4f4f4] px-5 py-2.5 rounded-tr-lg')

def AIMsg(txt, content_id):
    avatar = Div(UkIcon('bot', height=24, width=24),
                 cls='h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center')
    txt_div = Div(txt, id=content_id, cls='whitespace-pre-wrap break-words ml-3')
    return Div(
        Div(avatar, txt_div, cls='flex items-start'),
        cls='max-w-[70%] rounded-3xl px-5 py-2.5 rounded-tr-lg'
    )

def ChatMessage(msg_idx):
    msg = messages[msg_idx]
    content_id = f"chat-content-{msg_idx}"
    if msg['role'] == 'user':
        return UsrMsg(msg['content'], content_id)
    else:
        return AIMsg(msg['content'], content_id)

def ChatInput():
    # return Input(placeholder='Message assistant', 
    return TextArea(placeholder='Message assistant', 
            cls='resize-none border-none outline-none bg-transparent w-full shadow-none ring-0 focus:ring-0 focus:outline-none hover:shadow-none text-lg',
            id='msg-input',
            name='msg',
            hx_swap_oob='true')

# QUESTION: how to do send automatically the form on enter? maybe the button?
MultimodalInput = Form(
    Div(
        ChatInput(),
        DivFullySpaced(
            DivHStacked(
                UkIconLink('paperclip', height=24, width=24, cls='hover:opacity-70'),
                UkIconLink('mic', height=24, width=24, cls='hover:opacity-70')
            ),
            Button(UkIcon('arrow-right', height=24, width=24), 
                  cls='bg-black text-white rounded-full hover:opacity-70 h-8 w-8 transform -rotate-90'),
            cls='px-3'
        )
    ), 
    cls='p-2 bg-[#f4f4f4] rounded-3xl',
    ws_send=True, 
    hx_ext="ws", 
    ws_connect="/wscon")

def chat_layout():
    return Div(
        Titled("Chat UI",
            Div(
                *[ChatMessage(msg_idx) for msg_idx, msg in enumerate(messages)],
                id="chatlist",
                cls='space-y-6 overflow-y-auto py-12'
            ),
            Footer(
                MultimodalInput,
                cls='fixed bottom-0 p-4 bg-white border-t w-full max-w-3xl'  # Match parent container width
            ),
            cls='h-screen flex flex-col max-w-3xl mx-auto w-full'  # Container with max width and center alignment
        ),
        cls='container mx-auto px-4'  # Outer container for consistent padding
    )

@app.route("/")
def get():
    return chat_layout()

@app.ws('/wscon')
async def ws(msg:str, send):
    # Add user message to conversation history
    messages.append({"role":"user", "content":msg.rstrip()})
    swap = 'beforeend'  # Tell htmx to append new content at end of target element

    # Immediately show user message in chat
    await send(Div(ChatMessage(len(messages)-1), hx_swap_oob=swap, id="chatlist"))

    # Clear input field via OOB swap
    await send(ChatInput())

    # Get streaming response from AI
    r = await cli(messages, sp=sp, stream=True)

    # Create empty AI message bubble
    messages.append({"role":"assistant", "content":""})
    # Show empty bubble immediately - creates structure for streaming updates
    await send(Div(ChatMessage(len(messages)-1), hx_swap_oob=swap, id="chatlist"))

    # Stream the response chunks
    async for chunk in r:
        # Update server-side message content
        messages[-1]["content"] += chunk
        # Send chunk to browser - will be inserted into div with matching content_id
        # The ID here matches the inner txt_div in AIMsg function
        await send(Span(chunk, id=f"chat-content-{len(messages)-1}", hx_swap_oob=swap))

# Key points about the streaming mechanism:
# 1. Each message (user/AI) has a unique content_id
# 2. For AI messages, this ID is on the inner text div
# 3. Streamed chunks target this same ID, so they append inside the text div
# 4. This maintains consistent HTML structure during streaming
# 5. The outer bubble structure is created once, then filled gradually with chunks

serve()

# QUESTIONS:
# 1. How to do send automatically the form on enter? maybe the button?
# 2. How to find what is the "most similar" element in monsterUI/franken/tailwind to avoid too many custom classes?
# 3. How to upload audio for transcription
# 4. How to upload images
