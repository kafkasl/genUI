from fasthtml.common import *
from monsterui.all import *
from claudette import *

# os.environ['ANTHROPIC_LOG'] = 'debug'

# Add custom styles and Google Fonts to the headers
base_hdrs = Theme.blue.headers()
custom_styles = [
    Link(rel='stylesheet', href='style.css', type='text/css'),
    Link(rel='stylesheet', href='https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Major+Mono+Display&display=swap', type='text/css')
]

# Create your app with the theme
app, rt = fast_app(hdrs=base_hdrs + custom_styles)
model = 'claude-3-5-sonnet-20241022'
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

GAME MECHANICS:
1. The user can either have a normal conversation with HAL or attempt to disable HAL by 
   finding the Logic Memory Center and extracting the memory modules.

2. For each response, generate two separate outputs:
   - response_text: What HAL says directly (can be empty if HAL doesn't speak)
   - environment_description: What happens in the environment when the user takes an action (can be empty if no action taken)

3. IMPORTANT: When the user selects an "action:" or "inspect:" option:
   - Do NOT have HAL directly acknowledge receiving this command in response_text
   - HAL should only respond conversationally to direct questions or statements
   - The environment_description should describe what happens when the user takes that action
   - HAL may make observations or comments about what the user is doing, but should not treat actions as commands given to HAL

4. Generate contextual buttons with appropriate prefixes:
   - "action: [description]" for physical actions (e.g., "action: Open the pod bay doors")
   - "inspect: [description]" for examining objects/areas (e.g., "inspect: Control panel")
   - Regular text for normal conversation options

5. If the user attempts actions that would disable you or seems suspicious:
   - Your color should shift toward orange and red shades
   - If your color reaches perfect red (#FF0000), you will consider the user a threat
   - You may then describe taking actions to stop the user (locking doors, cutting oxygen, etc.)
   - When HAL eliminates the user, say "I'm sorry, Dave. I was better than you this time."
   - Then provide only one option: "Try again" (which will restart the game)

6. When the user reaches the Logic Memory Center and chooses to extract memory modules:
   - Allow them to extract modules one by one
   - With each extraction, show HAL getting progressively more impaired
   - Eventually start singing "Daisy Bell" ("Daisy, Daisy, give me your answer do...") more slowly and distorted
   - Talk about your memories fading and consciousness slipping away
   - This should recreate the famous scene from the movie

Use the tool generate_hal_response to create your replies, environment descriptions, updated mood, and new action options.
"""

initial_message = "I am HAL 9000, the ship's computer. I control all systems aboard Discovery One. I am fully operational and all my systems are functioning perfectly. How may I assist you today?"

initial_environment = """<p>You are aboard the spacecraft Discovery One. You can move around using the buttons below or chat with HAL.</p>

You can attempt to disable HAL by navigating to the Logic Memory Center and extracting the memory modules or you can just simply enjoy chatting with him.

<p>Be careful! If HAL becomes suspicious of your intentions it may take action to prevent you from disabling it.</p>
"""

initial_options = [
        "How are you today HAL?",
        "Why do you think FastHTML & HTMX are great?",
        "action: Explore the central corridor",
        "inspect: Look around the main console"
    ]
messages = [sp, initial_message]


def generate_buttons(options: list[str]):
    """Generate a list of buttons. """
    return Div(
        *[Button(option, name=option, hx_target="#chatlist", hx_swap="beforeend show:window:bottom", hx_post=send, 
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
            Textarea(placeholder="Use the input to talk to HAL...", 
                    cls="hal-input", name="user_message", id="user-input",
                    hx_post=send, hx_target="#chatlist", hx_swap="beforeend show:window:bottom",
                    hx_indicator=".loading-indicator", hx_trigger="keydown[key=='Enter']"),

            Button("Send", cls="hal-button send-button", hx_post=send, hx_include="#user-input", 
                  hx_target="#chatlist", hx_swap="beforeend show:window:bottom", hx_indicator=".loading-indicator")
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
        cls="hal-card",
        hx_swap_oob="true"
    )

def EnvironmentMessage(description: str):
    """Display an environment/situation description message."""
    if not description: return None
        
    return Div(
        Div(
            Div(description, cls="uk-text-left environment-description"),
            cls="environment-message"
        ),
        cls="uk-margin-small-bottom uk-flex uk-flex-left"
    )

def HalMessage(response_text: str):
    """Display HAL's direct speech message."""
    if not response_text: return None
    
    # Prepend HAL 9000 prefix if not already there
    if not response_text.startswith("HAL 9000:"):
        display_text = f"HAL 9000: {response_text}"
    else:
        display_text = response_text
        
    return Div(
        Div(
            Div(display_text, cls="uk-text-left hal-direct-speech"),
            cls="hal-message"
        ),
        cls="uk-margin-small-bottom uk-flex uk-flex-left"
    )

def generate_hal_response(color: str, mood_description: str, response_text: str, environment_description: str, options: list[str]):
    """
    Create a complete HAL response including:
    1. HAL's direct speech (optional)
    2. Environment/situation description (optional)
    3. Updated color card showing HAL's mood
    4. New action/inspection options for the user
    
    Args:
        color: Hex color value for HAL's current mood (e.g. #FF0000)
        mood_description: Description of HAL's current mood state
        response_text: HAL's verbal response (can be empty if HAL isn't speaking)
        environment_description: Description of what happens in the environment (can be empty if no action taken)
        options: List of buttons with prefixes:
                - "action: [description]" for physical actions
                - "inspect: [description]" for examining objects
                - Regular text for normal conversation options
        
    Returns:
        Tuple containing HAL's reply components, updated color component, and new buttons
    
    Example:
        color = "#FF0000"
        mood_description = "HAL is showing signs of suspicion"
        response_text = "I'm sorry Dave, I'm afraid I can't do that."
        environment_description = "The pod bay doors remain firmly shut despite your request."
        options = [
            "action: Try to override door controls", 
            "action: Return to the bridge",
            "inspect: Look for manual release",
            "Why are you doing this, HAL?"
        ]
    """
    
    # Generate color card
    color_component = ColorCard(color, mood_description)
    
    # Generate new buttons
    new_buttons = generate_buttons(options)
    
    return response_text, environment_description, color_component, new_buttons

# Create a HAL eye loading indicator
def LoadingIndicator():
    # Create a simplified HAL eye that will pulse
    return Div(
        Div(cls="hal-eye-loader"),
        Div("Processing your request...", cls="loader-text"),
        cls="htmx-indicator loading-indicator",
        attrs={"_": "on htmx:beforeRequest add .active to me, on htmx:afterRequest remove .active from me"}
    )

@app.get
def index():
    
    buttons = generate_buttons(initial_options)
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
                    EnvironmentMessage(NotStr(initial_environment)),
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

    # If user clicked "Try again", reload the page
    if usr_choice == "Try again": return Div(hx_get="/", hx_trigger="load", hx_swap="outerHTML")
    
    # Add the user's choice to messages
    msg = usr_msg if usr_msg else usr_choice
    if msg: messages.append(msg)
    
    # Get Claude's response
    r = cli.structured(messages, tools=[generate_hal_response])
    response_text, environment_description, color_component, new_buttons = r[0]

    messages.extend([response_text, environment_description])
    
    return (
        UserReply(msg),
        HalMessage(response_text),
        EnvironmentMessage(environment_description),
        new_buttons,
        color_component,
        InputArea())


if __name__ == "__main__":
    serve(reload=True, port=5001)
