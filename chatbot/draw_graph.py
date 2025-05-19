from langchain_core.runnables.graph import MermaidDrawMethod

from chatbot.real_main_agent import graph

image_data = graph.get_graph().draw_mermaid_png()
with open("graph.png", "wb") as f:
    f.write(image_data)
