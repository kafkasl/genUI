from fasthtml.common import *
from monsterui.all import *
from claudette import *
from datetime import datetime

import os
import re

os.environ['ANTHROPIC_LOG'] = 'debug'

hdrs = Theme.blue.headers()

# Create your app with the theme
app, rt = fast_app(hdrs=hdrs)

model = models[1]
cli = Client(model)
sp="""You are a color-reading assistant that asks questions to help the user choose a color.
The color you choose for the person will represent their personality.
Make interesting questions to keep the user interested and question what is his nature.
Use the tool generate_buttons to generate a list of buttons. 
When the user clicks on a button, the button's value is returned to you as a message.
"""
messages = [sp]

# Read the HAL9000 SVG file
# with open('hal-9000.svg', 'r') as file:
#     HAL_SVG = file.read()

def generate_buttons(options: list[str]):
    """Generate a list of buttons. """
    return Div(
        *[Button(option, name=option, hx_target="#chatlist", hx_swap="beforeend",hx_post=send, cls="uk-button uk-button-default uk-margin-small-right") 
          for option in options],
        cls="uk-margin-medium-bottom"
    )

# Display user's reply as a button-like element
def UserReply(msg):
    # Position reply to the right like in a chat interface
    return Div(
        Div(msg, cls="uk-button uk-button-primary uk-text-left uk-disabled"),
        cls="uk-margin-medium-bottom uk-flex uk-flex-right"
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

def ColorCard(color: str, description: str):
    """
    Create a beautiful HAL 9000 eye card displaying the user's color.
    
    Args:
        color: Hex color value beginning with # (e.g. #ff0000)
        description: Brief description of the color's meaning
    """
   
    modified_svg = Hal9000Card(color)
    
    # Create a card container optimized for the right column layout
    return color, description, Div(
        # Card container with shadow and rounded corners
        Div(
            # HAL 9000 SVG eye with plenty of space
            Div(
                NotStr(modified_svg),
                cls="uk-flex uk-flex-center uk-flex-middle",
                style="min-height: 180px; width: 100%; overflow: visible;"
            ),
            # Color name with the hex color
            H4(f"Your color so far.", cls="uk-text-center uk-margin-small-top"),
            # Message
            Div(description, cls="uk-text-center uk-text-small", style=f"color: {color}"),
            cls="uk-card-body"
        ),
        id="color-card",
        cls="uk-card uk-card-default uk-border-rounded uk-box-shadow-small uk-margin-auto"
    )

# The main screen
@app.get
def index():
    options = ["Let's start! I'm ready to discover my color", "Why not?", "I'd rather not but here we are"]
    buttons = generate_buttons(options)
    _, _, color_component = ColorCard("blue", "blue")

    # Create a two-column layout with chat on left and color card on right
    page = Div(cls="uk-container")(
        Div(cls="uk-grid uk-grid-medium uk-margin-top", attrs={"uk-grid": ""})(
            # Left column: Chat
            Div(cls="uk-width-2-3@m")(
                Div(id="chatlist", cls="chat-box h-[70vh] overflow-y-auto px-4 py-4 uk-card uk-card-default uk-card-body uk-border-rounded")(buttons)
            ),
            # Right column: Color Display (sticky position)
            Div(cls="uk-width-1-3@m")(
                Div(id="color-display", cls="uk-position-sticky", style="top: 20px;")(
                    color_component
                )
            )
        )
    )
    return Titled('What\'s your color?', page, cls=ContainerT.lg)

# Handle the form submission
@app.post
async def send(request):
    form_data = await request.form()
    form_dict = dict(form_data)
    
    # Get the selected option (button clicked)
    user_choice = next(iter(form_dict))
    
    # Add the user's choice to messages
    messages.append(user_choice)
    
    # Get Claude's response for color
    r = cli.structured(messages, tools=[ColorCard])
    color, msg, color_component = r[0]
    messages.append(f'Current color & message: {color} {msg}')
    
    # Get Claude's response for buttons
    r = cli.structured(messages, tools=[generate_buttons])
    
    # Return the user's reply, buttons from Claude, and out-of-band color update
    return (
        UserReply(user_choice), 
        *r[0],
        Div(id="color-display", hx_swap_oob="true")(color_component)
    )

serve()
