# Generative UI Demos with FastHTML

This repository contains demos showcasing how to build interactive Generative UI (genUI) applications using FastHTML and Answer.ai libraries.

## What is Generative UI?

Generative UI extends the concept of Generative AI beyond text and images to create dynamic user interfaces. Instead of generating just text in a chat fashion, genUI produces rich components that users can interact with directly.

Today's AI interfaces are predominantly text-based and feel clunky compared to traditional apps. These demos show how we can transition from basic text-based chat into rich interactive experiences with buttons and visual elements - all in less than 150 lines of code using FastHTML and Answer.ai libraries.

## Demos

This repository contains three progressive demos:

1. [**Weather Demo**](https://github.com/kafkasl/genUI/tree/main/weather) - A basic chatbot enhanced with visual weather cards
2. [**Your Color**](https://github.com/kafkasl/genUI/tree/main/your_color) - An interactive mindfulness experience using button-based navigation
3. [**HAL 9000**](https://github.com/kafkasl/genUI/tree/main/hal9000) - A complete interactive experience combining text chat and button navigation

Try the live demos:
- [Weather Demo](https://fasthtml-app-cbd32e55.pla.sh/) 
- [Your Color Mindfulness](https://fasthtml-app-68e1764d.pla.sh/)
- [HAL 9000 Demo](https://fasthtml-app-6e583cfc.pla.sh/)

## Installation

To run these demos locally:

1. Clone this repository:
   ```bash
   git clone https://github.com/kafkasl/genUI.git
   cd genUI
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Navigate to any of the demo directories and run:
   ```bash
   python main.py
   ```

Each demo consists of just three files:
- `main.py` - The application code
- `style.css` - Styling 
- `requirements.txt` - Dependencies

## Key Concepts

These demos showcase several important concepts:

1. **Hypermedia Controls** - Using HTMX to create interactive elements without complex JavaScript
2. **The Feedback Loop** - How user interactions flow back to the LLM, which generates new UI components
3. **Eliminating Contract Coupling** - How the hypermedia approach removes the need for predefined frontend templates
4. **Progressive Enhancement** - From static visual elements to fully interactive experiences

## Article

For a detailed explanation of these concepts and demos, read the full article: [AI is the new UI: Generative UI with FastHTML](https://kafkasl.github.io/genui-post.html)

## Deployment

These demos are deployed using [Plash](https://github.com/AnswerDotAI/plash_cli), a deployment service from Answer.ai.

To deploy your own version:
1. Create a `plash.env` file with your configuration
2. Run `plash_deploy`

## License

[MIT License](LICENSE) 