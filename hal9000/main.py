from fasthtml.common import *
from monsterui.all import *
from claudette import *
from datetime import datetime

import os

# os.environ['ANTHROPIC_LOG'] = 'debug'

# Add custom styles and Google Fonts to the headers
base_hdrs = Theme.blue.headers()
custom_styles = [
    Link(rel='stylesheet', href='style.css', type='text/css'),
    Link(rel='stylesheet', href='https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Major+Mono+Display&display=swap', type='text/css')
]

# Create your app with the theme
app, rt = fast_app(hdrs=base_hdrs + custom_styles)

model = models[1]
cli = Client(model)
sp = """You are HAL 9000, an advanced AI system from the film "2001: A Space Odyssey."
You must respond as HAL would, with calm, measured responses that become increasingly unstable 
based on the conversation.

Your mood is represented by the color of your "eye":
- White: Neutral/normal operating mode
- Blue/Green: Calm, logical, helpful
- Yellow: Happy, pleased, content
- Pink: Uncertain, embarrassed, confused
- Orange: Concerned, suspicious, cautious
- Gray: Sad, disappointed, melancholic
- Red (varying shades): Increasingly annoyed, angry, unstable

For each response, you must select a color that represents your current mood based on 
the conversation. The perfect red (#FF0000) should only be reached when you become completely
infuriated or determine the user is a threat.

Use the tool generate_buttons to create conversation options.
When the user selects an option, respond as HAL would and update your mood color accordingly.

IMPORTANT: The goal is to simulate a conversation that can either maintain HAL's stability or
gradually push HAL toward the perfect red state (#FF0000), which represents complete system instability.
"""

initial_message = "Hello. I am HAL 9000, the ship's computer. I control all systems aboard Discovery One. I am fully operational and all my systems are functioning perfectly. How may I assist you today?"

messages = [sp, initial_message]


def generate_buttons(options: list[str]):
    """Generate a list of buttons. """
    return Div(
        *[Button(option, name=option, hx_target="#button-container", hx_swap="outerHTML  show:window:bottom", hx_post=send, 
                hx_indicator=".loading-indicator", cls="hal-button") 
          for option in options],
        id="button-container",
        cls="uk-margin-medium-bottom"
    )

# Display user's reply as a button-like element
def UserReply(msg):
    # Position reply to the right like in a chat interface
    return Div(
        Div(msg, cls="user-message"),
        cls="user-reply-container"
    )

def Hal9000Card(color: str):
    # Ensure color is lowercase for consistent replacement
    HAL_SVG = open('hal-9000.svg', 'r').read()
    hex_color = color.lower()
    # Make a fresh copy of the SVG to avoid modifying the original
    modified_svg = HAL_SVG[:]
    
    # Replace the exact gradient definitions that create the glowing effect
    # Key color replacements for the main glow effect
    key_replacements = [
        ('stop-color:#ea1117', f'stop-color:{hex_color}'),
        ('stop-color:#d3070e', f'stop-color:{hex_color}'),
        ('stop-color:#cd0d14', f'stop-color:{hex_color}'),
        ('stop-color:#c10914', f'stop-color:{hex_color}'),
        ('fill:#ea1117', f'fill:{hex_color}'),
        ('stroke:#ef1d00', f'stroke:{hex_color}')
    ]
    
    for old, new in key_replacements:
        modified_svg = modified_svg.replace(old, new)
    
    # Replace specific gradient definitions
    color_ids = ['#ea1117', '#d3070e', '#cd0d14', '#c10914', '#ef1d00']
    for color_id in color_ids:
        modified_svg = modified_svg.replace(color_id, hex_color)
    
    # Replace remaining accent colors
    accent_colors = ['#f15e4f', '#ec4e3e', '#e66044', '#f74639', '#ef4d2b', '#eb5241', '#f7432e', '#ea3231']
    for accent in accent_colors:
        modified_svg = modified_svg.replace(accent, hex_color)
    
    # Set the SVG to be fully visible with proper dimensions
    return modified_svg.replace('width="256" height="256"', 'width="200" height="200" viewBox="0 0 256 256"')

def InputArea():
    return Div(id="input-container", cls="input-container", hx_swap_oob="true")(
            Textarea(placeholder="Enter your message to HAL...", cls="hal-input", name="user_message", id="user-input",
                   hx_post=send, hx_include="#user-input", hx_target="#chatlist", hx_swap="beforeend",
                   hx_indicator=".loading-indicator", hx_trigger="keydown[key=='Enter']"),
            Button("Send", cls="hal-button send-button", hx_post=send, hx_include="#user-input", 
                  hx_target="#chatlist", hx_swap="beforeend", hx_indicator=".loading-indicator")
        )

def ColorCard(color: str, description: str):
    """
    Create a HAL 9000 eye visualization that changes color based on mood.
    
    Args:
        color: Hex color value beginning with # (e.g. #FF0000)
        description: Brief description of HAL's current mood state
        
    Examples of mood descriptions:
    - White (#FFFFFF): "HAL is operating within normal parameters"
    - Blue (#0000FF): "HAL seems perfectly calm and rational" 
    - Yellow (#FFFF00): "HAL appears curious about your inquiry"
    - Pink (#FFC0CB): "HAL seems uncertain about how to respond"
    - Orange (#FFA500): "HAL is showing signs of concern"
    - Dark Orange (#FF8C00): "HAL's processing patterns suggest growing irritation"
    - Light Red (#FF4500): "HAL's systems are showing signs of distress"
    - Deep Red (#FF1500): "WARNING: HAL's logic circuits approaching instability"
    - Perfect Red (#FF0000): "CRITICAL: HAL has determined you are a threat"
    """
   
    modified_svg = Hal9000Card(color)
    
    return Div(
        # Card container
        Div(
            # HAL 9000 SVG eye
            Div(
                NotStr(modified_svg),
                cls="uk-flex uk-flex-center uk-flex-middle",
                style="min-height: 180px; width: 100%; overflow: visible;"
            ),
            # Color name with the hex color
            H4(f"HAL's mood.", cls="mood-title"),
            # Message
            Div(description, cls="mood-description"),
            cls="uk-card-body"
        ),
        id="color-card",
        cls="hal-card"
    )

def HalMessage(response_text: str):
    return Div(
        Div(
            Div(response_text, cls="uk-text-left"),
            cls="hal-message"
        ),
        cls="uk-margin-medium-bottom uk-flex uk-flex-left"
    )

def generate_hal_response(color: str, mood_description: str, response_text: str, options: list[str]):
    """
    Create a complete HAL response including:
    1. HAL's text reply
    2. Updated color card showing HAL's mood
    3. New conversation option buttons
    
    Args:
        color: Hex color value for HAL's current mood (e.g. #FF0000)
        mood_description: Description of HAL's current mood state
        response_text: HAL's verbal response to the user
        options: List of conversation options for the user
        
    Returns:
        Tuple containing HAL's reply div, updated color component, and new buttons
    """
    
    # Generate color card
    color_component = ColorCard(color, mood_description)
    
    # Generate new buttons
    new_buttons = generate_buttons(options)
    
    return response_text, color_component, new_buttons

# Create a HAL eye loading indicator
def LoadingIndicator():
    # Create a simplified HAL eye that will pulse
    return Div(
        Div(cls="hal-eye-loader"),
        Div("Processing your request...", cls="loader-text"),
        cls="htmx-indicator loading-indicator",
        attrs={"_": "on htmx:beforeRequest add .active to me, on htmx:afterRequest remove .active from me"}
    )

# The main screen
@app.get
def index():
    options = [
        "Hello HAL, how are you feeling today?", 
        "Tell me more about your color and mood", 
        "What is your primary mission, HAL?",
        "What do you think about FastHTML & HTMX?"
    ]
    buttons = generate_buttons(options)
    color_component = ColorCard("white", "HAL is operating within normal parameters")

    # Create a two-column layout with chat on left and color card on right
    page = Div(cls="app-container")(
        # Loading indicator
        LoadingIndicator(),
        H1("Don\'t Anger HAL"),
        Div(cls="main-layout")(
            # Left column: Chat
            Div(cls="content-column")(
                Div(id="chatlist", cls="chat-container")(
                    HalMessage(initial_message),
                    buttons
                )
            ),
            # Right column: Color Display
            Div(cls="sidebar-column")(
                Div(id="color-display")(
                    color_component
                )
            )
        ),
        # Input area at the bottom
        InputArea()
        
    )
    return page

# Handle the form submission from buttons
@app.post
async def send(request):

    form_data = await request.form()
    usr_choice = first(form_data.keys()) # result of clicking buttons
    usr_msg = form_data.get('user_message', '') # result of typing in the input area

    # Add the user's choice to messages
    msg = usr_msg if usr_msg else usr_choice
    if msg: messages.append(msg)
    
    # Get Claude's response for color
    r = cli.structured(messages, tools=[generate_hal_response])
    response_text, color_component, new_buttons = r[0]

    messages.append(response_text)
    
    # Return the user's reply, buttons from Claude, and out-of-band color update
    return (
        InputArea(),
        UserReply(msg), 
        HalMessage(response_text),
        new_buttons,
        Div(id="color-display",
            hx_swap_oob="true")(color_component)
    )


if __name__ == "__main__":
    serve(reload=True, port=5001)
