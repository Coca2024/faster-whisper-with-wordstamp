import gradio as gr
from gradio_components import gr_components as gc

with gr.Blocks() as UI:
    gc.gr_components()
UI.launch(debug=True,inbrowser=True)