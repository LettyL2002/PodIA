import gradio as gr  # type: ignore

# ? Example


def greet(name):
    return "Hello " + name + "!"


demo = gr.Interface(fn=greet, inputs="textbox", outputs="textbox")

if __name__ == "__main__":
    demo.launch()
