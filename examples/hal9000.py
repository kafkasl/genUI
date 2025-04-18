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

# Read the HAL9000 SVG file
# with open('hal-9000.svg', 'r') as file:
#     HAL_SVG = file.read()

def generate_buttons(options: list[str]):
    """Generate a list of buttons. """
    return Div(
        *[Button(option, name=option, hx_target="#button-container", hx_swap="outerHTML",hx_post=send, cls="uk-button uk-button-default uk-margin-small-right") 
          for option in options],
        id="button-container",
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
            H4(f"HAL's mood.", cls="uk-text-center uk-margin-small-top"),
            # Message
            Div(description, cls="uk-text-center uk-text-small"),
            cls="uk-card-body"
        ),
        id="color-card",
        cls="uk-card uk-card-default uk-border-rounded uk-box-shadow-small uk-margin-auto"
    )

def HalMessage(response_text: str):
    return Div(
        Div(
            Div("HAL 9000", cls="uk-text-bold uk-text-small uk-text-muted uk-margin-small-bottom"),
            Div(response_text, cls="uk-text-left"),
            cls="uk-card uk-card-default uk-card-body uk-padding-small"
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
    _, _, color_component = ColorCard(color, mood_description)
    
    # Generate new buttons
    new_buttons = generate_buttons(options)
    
    return response_text, color_component, new_buttons

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
    _, _, color_component = ColorCard("white", "HAL is operating within normal parameters")

    # Create a two-column layout with chat on left and color card on right
    page = Div(cls="uk-container")(
        Div(cls="uk-grid uk-grid-medium uk-margin-top", attrs={"uk-grid": ""})(
            # Left column: Chat
            Div(cls="uk-width-2-3@m")(
                Card(id="chatlist", cls="chat-box h-full overflow-y-auto px-4")(
                    HalMessage(initial_message),
                    buttons)
            ),
            # Right column: Color Display (sticky position)
            Div(cls="uk-width-1-3@m")(
                Div(id="color-display", cls="uk-position-sticky", style="top: 20px;")(
                    color_component
                )
            )
        )
    )
    return Titled('Don\'t Anger HAL', page, cls=ContainerT.lg)

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
    r = cli.structured(messages, tools=[generate_hal_response])
    response_text, color_component, new_buttons = r[0]

    messages.append(response_text)
    
    # Return the user's reply, buttons from Claude, and out-of-band color update
    return (
        UserReply(user_choice), 
        HalMessage(response_text),
        Div(
            new_buttons,
            id="button-container"
        ),
        Div(id="color-display",
             cls="uk-position-sticky",
             style="top: 20px;", hx_swap_oob="true")(color_component)
    )

serve(reload=True)
