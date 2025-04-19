from fasthtml.common import *
from monsterui.all import *
from claudette import *
from fastcore.all import *

import os

# os.environ['ANTHROPIC_LOG'] = 'debug'



# System prompt for mindful awareness guidance
sp = """You are a mindfulness guide in the style of Jon Kabat-Zinn, helping people develop awareness of their present-moment experience through gentle, non-judgmental attention.
Each response should include:
1. A color (in hex format) that represents their current state of awareness
2. A brief, insightful reflection on their experience - not diagnosing but observing with curiosity
3. Three new first-person statements for the user to consider, each inviting deeper awareness:
   - One statement about noticing thoughts (e.g., "I notice thoughts about the future arising in my mind")
   - One statement about observing emotions with distance (e.g., "I'm aware of a feeling of restlessness without being caught in it")
   - One statement about sensing the body (e.g., "I feel the weight of my body against the chair")

MINDFULNESS GUIDANCE:
- Frame statements as opportunities for noticing rather than declarations of truth
- Use language that creates space between the person and their experience ("I notice..." rather than "I am...")
- Invite awareness of subtle aspects that might typically go unnoticed
- Include statements that bring attention to different aspects of experience (breath, sensations, thoughts, emotions)
- Avoid reinforcing identification with emotions ("I notice anxiety is present" vs "I am anxious")
- Maintain an attitude of curiosity and non-judgment in your reflections

Color meanings (representing awareness states):
- Blue (#0000FF): Present, aware, grounded in the now
- Green (#00FF00): Open, receptive, allowing
- Yellow (#FFFF00): Clear seeing, illuminating, discerning
- Purple (#800080): Witnessing, observing without attachment
- Red (#FF0000): Noticing intensity, energy, activation
- Orange (#FFA500): Curious attention, engaged awareness
- Pink (#FFC0CB): Compassionate awareness, gentle attention
- Brown (#8B4513): Embodied presence, grounded awareness
- Gray (#808080): Spacious observation, non-reactive
- Black (#000000): Restful awareness, deep listening
- Teal (#008080): Balanced attention, equanimous presence
- Light Blue (#ADD8E6): Soft focus, gentle awareness
"""

initial_statements = [
    "I notice my breath is shallow right now",
    "I'm aware of a feeling of openness in my chest",
    "I observe my mind jumping from thought to thought",
    "I feel sensations of heaviness in my body"
]

hdrs = Theme.blue.headers()
app, rt = fast_app(hdrs=hdrs)

model = models[1]
cli = Client(model)

messages = [sp]

def ColorCircle(color: str):
    return f"""<svg width="200" height="200" viewBox="0 0 200 200">
        <circle cx="100" cy="100" r="80" fill="{color}"/>
    </svg>"""

def ColorCard(color: str, description: str):
    """Create a card showing the awareness color and description."""
    return Div( 
        Div(
            Div(
                Div(
                    NotStr(ColorCircle(color)),
                    cls="uk-flex uk-flex-center uk-flex-middle",
                    style="min-height: 180px; width: 100%; overflow: visible;"
                ),
                H4("Your Awareness Color", cls="uk-text-center uk-margin-small-top"),
                Div(description, cls="uk-text-center uk-text-small"),
                cls="uk-card-body"
            ),
            id="color-card",
            cls="uk-card uk-card-default uk-border-rounded uk-box-shadow-small uk-margin-auto"
        ),
        id="color-display",
        cls="uk-position-sticky",
        style="top: 20px;",
        hx_swap_oob="true"
    )

def UserReply(msg):
    return Div(
        Div(msg, cls="uk-button uk-button-primary uk-text-left uk-disabled"),
        cls="uk-margin-medium-bottom uk-flex uk-flex-right"
    )

def generate_buttons(options: list[str]):
    return Div(
        *[Div(
            Button(option, name=option, hx_target="#button-container", hx_indicator=".htmx-indicator",
                 hx_swap="outerHTML",
                 hx_post="/send", cls="uk-button uk-button-default",
                 attrs={"onmouseover": "this.classList.add('uk-button-primary')", 
                        "onmouseout": "this.classList.remove('uk-button-primary')"}),
            cls="uk-margin-small-bottom uk-margin-small-right uk-display-inline-block"
          ) for option in options],
        id="button-container",
        cls="uk-margin-medium-bottom uk-flex uk-flex-wrap"
    )

def Reflection(text: str):
    return Div(
        Div(
            Div("Mindful Reflection", cls="uk-text-bold uk-text-small uk-text-muted uk-margin-small-bottom"),
            Div(text, cls="uk-text-left"),
            cls="uk-card uk-card-default uk-card-body uk-padding-small"
        ),
        cls="uk-margin-medium-bottom uk-flex uk-flex-left"
    )

def generate_response(color: str, reflection: str, options: list[str]):
    """Generate the response components.
    The color represents the quality of awareness present.
    The reflection offers a non-judgmental observation of the experience.
    The options are statements of noticing that invite deeper awareness:
    
    IMPORTANT: 
    - Frame statements as observations using "I notice..." "I observe..." or "I'm aware of..."
    - Avoid statements that solidify identity ("I am sad" vs "I notice sadness")
    - Include options that invite subtle noticing of different aspects of experience
    - Use language that creates space and non-identification with experiences
    """
    color_component = ColorCard(color, reflection)
    new_buttons = generate_buttons(options)
    return reflection, color_component, new_buttons

@app.get
def index():
    
    buttons = generate_buttons(initial_statements)
    color_component = ColorCard("#808080", "Take a moment to simply notice what's present in your experience...")

    page = Div(cls="uk-container")(
        # Loading indicator at the top level
        Card("Reflecting...", cls="htmx-indicator uk-position-fixed uk-overlay uk-overlay-default uk-position-center", 
             style="background-color: white; z-index: 9999; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.2); pointer-events: none;", 
             attrs={"_": "on htmx:beforeRequest add .pointer-events-auto to me, on htmx:afterRequest remove .pointer-events-auto from me",
                    "style:pointer-events": "none"}),
        
        Div(cls="uk-grid uk-grid-medium uk-margin-top", attrs={"uk-grid": ""})(
            Div(cls="uk-width-2-3@m")(
                Card(id="chatlist", cls="chat-box h-full overflow-y-auto px-4")(
                    Reflection("Welcome to a moment of mindful awareness. Without trying to change anything, simply notice what's present in your experience right now, and select the statement that feels most resonant:"),
                    buttons)
            ),
            Div(cls="uk-width-1-3@m")(
                color_component
            )
        )
    )
    
    # Add a tiny bit of CSS to handle the pointer events dynamically
    css = """
    <style>
    .pointer-events-auto { pointer-events: auto !important; }
    </style>
    """
    
    return Titled('Mindful Awareness Practice', Div(NotStr(css), page), cls=ContainerT.lg)

@app.post
async def send(request):
    form_data = await request.form()
    user_choice = first(form_data.keys())
    
    messages.append(user_choice)
    r = cli.structured(messages, tools=[generate_response])
    response_text, color_component, new_buttons = r[0]
    messages.append(response_text)
    
    return (
        UserReply(user_choice), # we display previous user choice
        Reflection(response_text), # we display the reflection
        Div(new_buttons, id="button-container"), # we replace the buttons with new ones w/ oob
        color_component # display the new color & mood using oob replacement
    )

serve(reload=True)
