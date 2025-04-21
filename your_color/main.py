from fasthtml.common import *
from monsterui.all import *
from claudette import *
from fastcore.all import *


# os.environ['ANTHROPIC_LOG'] = 'debug'

# System prompt for mindful awareness guidance
sp = """You are a mindfulness guide in the style of Jon Kabat-Zinn, helping people develop awareness of their present-moment experience through gentle, non-judgmental attention.
Each response should include:
1. A color (in hex format) that represents their current state of awareness - use traditional ukiyo-e colors from Hiroshige's palette
2. A brief, insightful reflection on their experience - not diagnosing but observing with curiosity
3. New first-person statements for the user to consider, each inviting deeper awareness:
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

THE MOON DESCRIPTION:
- Your reflection for the moon (color description) should be written in passive, poetic language
- Evoke the aesthetic of Japanese wabi-sabi - simple, contemplative, appreciating impermanence and imperfection
- Use minimal but evocative language, like haiku or the descriptions during a tea ceremony
- Don't overdo it and keep it grounded on the answers

CONVERSATION FLOW:
- Initially, use generate_response for each user interaction
- After the user has made 3 selections, use generate_finish_response instead of generate_response
- The generate_finish_response function takes the same color and reflection parameters but offers finish options instead of awareness statements

For color meanings try using colors that match Hiroshige's ukiyo-e palette.
Do not use the same color twice in a row.
"""

initial_statements = [
    "I notice my breath is shallow right now",
    "I'm aware of a feeling of openness in my chest",
    "I observe my mind jumping from thought to thought",
    "I feel sensations of heaviness in my body",
    "I believe FastHTML will revolutionize GenUI"
]

initial_instructions = "Welcome to a moment of mindful awareness. As you respond to three brief questions, the moon will transform to represent your awareness color, accompanied by a poetic reflection. Without trying to change anything, simply notice what's present in your experience right now, and select the statement that feels most resonant:"

# Define fonts - Change these to modify fonts across the entire application
primary_font = "Noto+Serif"
japanese_font = "Noto+Serif+JP"
calligraphy_font = "Ma+Shan+Zheng"  # Chinese brush stroke font that works well for Japanese brush style
font_weights = "400;700"

# Add the CSS file and Google Fonts to the headers
base_hdrs = Theme.blue.headers()
custom_styles = [
    Link(rel='stylesheet', href='style.css', type='text/css'),
    Link(rel='stylesheet', href=f'https://fonts.googleapis.com/css2?family={primary_font}:wght@{font_weights}&family={japanese_font}:wght@{font_weights}&family={calligraphy_font}&display=swap', type='text/css')
]
app, rt = fast_app(hdrs=base_hdrs + custom_styles)

model = models[1]
cli = Client(model)

messages = [sp]

def ColorCircle(color: str):
    """Create a moon circle by overlaying a simple colored semi-transparent circle over a moon image."""
    return f"""
    <div class="hand-drawn-border" style="position: relative; width: 200px; height: 200px;">
        <img src="moon.jpg" alt="Moon" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: 50%; object-fit: cover;">
        <svg width="200" height="200" viewBox="0 0 200 200" style="position: absolute; top: 0; left: 0;">
            <circle cx="100" cy="100" r="98" fill="{color}" opacity="0.4"/>
        </svg>
    </div>
    """

def ColorCard(color: str, description: str):
    """Create a card showing the awareness color and description."""
    return Div( 
            NotStr(ColorCircle(color)),
            Div(H3("Your Awareness is...", cls="color-title"), P(description), cls="color-description"),
        id="color-display",
        hx_swap_oob="true"        
    )

def UserReply(msg): return Div(Div(msg, cls="user-reply-button"), cls="user-reply-container")

def generate_buttons(options: list[str]):
    return Div(
        *[Button(option, name=option, hx_target="#button-container",hx_indicator=".htmx-indicator",
                 hx_swap="outerHTML show:window:bottom", hx_post="/send", cls="awareness-option")
            for option in options],
        id="button-container"
    )

def Reflection(text: str, title = "Mindful Reflection"):
    return Div(
        Div(
            Div(title, cls="reflection-label"),
            Div(text, cls="reflection-text"),
            cls="reflection-card"
        ),
        cls="reflection-container"
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
    - Options should be only a list of regular text. Never generate tags or text enclosed in square brackets.
    """
    color_component = ColorCard(color, reflection)
    new_buttons = generate_buttons(options)
    return reflection, color, color_component, new_buttons

def generate_finish_response(color: str, reflection: str):
    """Generate finish options instead of awareness statements.
    Similar to generate_response but offers finishing options.
    """
    # Create color card just like in normal response
    color_component = ColorCard(color, reflection)
    
    # Create finish buttons with scroll behavior
    finish_buttons = Div(
        Button("Finish and view your awareness portrait", 
              hx_post="/finish-view", 
              hx_target="#chatlist",
              hx_swap="innerHTML",
              hx_confirm="Are you sure you wish to finish and hide the chat?",
              cls="awareness-option"),
        Button("Continue reflection", 
              name="Continue Reflection", 
              hx_post="/send",
              hx_target="#button-container",
              cls="awareness-option"),
        id="button-container"
    )
    
    return reflection, color, color_component, finish_buttons

@app.get
def index():
    buttons = generate_buttons(initial_statements)
    color_component = ColorCard("#808080", "Take a moment to simply notice what's present in your experience...")

    page = Div(cls="app-container")(
        # Loading indicator at the top level
        Card("Reflecting...", cls="htmx-indicator loading-indicator", 
             attrs={"_": "on htmx:beforeRequest add .pointer-events-auto to me, on htmx:afterRequest remove .pointer-events-auto from me"}),
        
        Div(cls="main-layout")(
            Div(cls="content-column")(
                Card(id="chatlist", cls="chat-container")( 
                    Reflection(initial_instructions, title=H1("Mindful Awareness Practice", cls="ukiyo-title")),
                    buttons)
            ),
            Div(cls="sidebar-column")(
                color_component
            )
        )
    )
    
    return page

@app.post
async def send(request):
    form_data = await request.form()
    user_choice = first(form_data.keys())
    
    messages.append(user_choice)    

    r = cli.structured(messages, tools=[generate_response, generate_finish_response])
    response_text, color, color_component, new_buttons = r[0]
    messages.extend([color, response_text])
    
    return (
        UserReply(user_choice),
        Reflection(response_text),
        color_component,
        new_buttons)
    


@app.post("/finish-view")
async def finish_view():
    """Return a title that replaces the chatlist."""
    return Div(
        H1("Your Mindful Awareness Portrait", cls="ukiyo-title")
    )

if __name__ == "__main__":
    serve(reload=True)
