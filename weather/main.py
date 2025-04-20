from fasthtml.common import *
from monsterui.all import *
from claudette import *
from datetime import datetime

# import os
# os.environ['ANTHROPIC_LOG'] = 'debug'

hdrs = Theme.blue.headers()

# Create your app with the theme
app, rt = fast_app(hdrs=hdrs)

model = models[1]

# Define the weather component function with enhanced visuals
def WeatherComponent(location:str, temperature:str, description:str):
    """Generate a clean, minimal weather card like iPhone's weather app.
    Description should be 'sunny', 'cloudy', or 'rainy'."""
    
    # Simple weather icons (minimalist approach)
    weather_icons = {
        "sunny": "https://cdn-icons-png.flaticon.com/512/869/869869.png",  # Simple yellow circle
        "cloudy": "https://cdn-icons-png.flaticon.com/512/414/414825.png", # Simple cloud
        "rainy": "https://cdn-icons-png.flaticon.com/512/3351/3351979.png" # Simple rain
    }
    
    # Get image and determine background color
    desc_lower = description.lower()
    img_url = next((url for condition, url in weather_icons.items() 
                 if condition in desc_lower), weather_icons["sunny"])
    
    # Get current date
    current_date = datetime.now().strftime("%A, %B %d")
    
    return Div(
        # Location name at the top
        H2(location, cls="text-xl font-semibold mb-1"),
        
        # Header with date and condition
        Div(cls="flex justify-between items-center mb-3")(
            P(current_date, cls="text-sm font-medium"),
            P(description.capitalize(), cls="text-sm font-medium")
        ),
        
        # Large temperature and weather icon
        Div(cls="flex items-center")(
            Span(f"{temperature}°", cls="text-7xl font-light mr-4"),
            Img(src=img_url, cls="w-16 h-16")
        ),
        
        # Styling for the entire component
        cls="p-4 bg-sky-500 text-white rounded-lg max-w-xs"
    )

# Chat message component (renders a chat bubble)
def ChatMessage(msg, user):
    bubble_class = "chat-bubble-primary" if user else 'chat-bubble-secondary'
    chat_class = "chat-end" if user else 'chat-start'
    return Div(cls=f"chat {chat_class}")(
               Div('user' if user else 'assistant', cls="chat-header"),
               Div(msg, cls=f"chat-bubble {bubble_class}"),
               Hidden(msg, name="messages")
           )

# The input field for the user message. Also used to clear the
# input field after sending a message via an OOB swap
def ChatInput():
    return Input(name='msg', id='msg-input', placeholder="Type a message",
                 cls="input input-bordered w-full", hx_swap_oob='true')

# The main screen
@app.get
def index():
    page = Form(hx_post=send, hx_target="#chatlist", hx_swap="beforeend")(
           Div(id="chatlist", cls="chat-box h-[73vh] overflow-y-auto"),
               Div(cls="flex space-x-2 w-full")(
                   ChatInput(),
                   Button("Send", cls="btn btn-primary")
               )
           )
    return Titled('Weather Component', page, cls=ContainerT.sm)

# Handle the form submission
@app.post
def send(msg:str, messages:list[str]=None):
    if not messages: messages = []
    messages.append(msg.rstrip())

    cli = Client(model)
    sp="""You are a helpful assistant that invents weather for a specific location. 
                Use the tool WeatherComponent to generate a card for the given location."""
    r = cli.structured([sp, msg], tools=[WeatherComponent])
    return (ChatMessage(msg, True),    # The user's message
            r[0], # The chatbot's response
            ChatInput()) # And clear the input field via an OOB swap

serve()
