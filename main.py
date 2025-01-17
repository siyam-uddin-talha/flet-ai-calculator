import flet as ft
import flet.canvas as cv
from PIL import Image, ImageDraw
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
import base64
from PIL import Image
import ast


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# prompt = (
#     f"You have been given an image with some mathematical expressions, equations, or graphical problems, and you need to solve them. "
#     f"Note: Use the PEMDAS rule for solving mathematical expressions. PEMDAS stands for the Priority Order: Parentheses, Exponents, Multiplication and Division (from left to right), Addition and Subtraction (from left to right). Parentheses have the highest priority, followed by Exponents, then Multiplication and Division, and lastly Addition and Subtraction. "
#     f"For example: "
#     f"Q. 2 + 3 * 4 "
#     f"(3 * 4) => 12, 2 + 12 = 14. "
#     f"Q. 2 + 3 + 5 * 4 - 8 / 2 "
#     f"5 * 4 => 20, 8 / 2 => 4, 2 + 3 => 5, 5 + 20 => 25, 25 - 4 => 21. "
#     f"YOU CAN HAVE FIVE TYPES OF EQUATIONS/EXPRESSIONS IN THIS IMAGE, AND ONLY ONE CASE SHALL APPLY EVERY TIME: "
#     f"Following are the cases: "
#     f"1. Simple mathematical expressions like 2 + 2, 3 * 4, 5 / 6, 7 - 8, etc.: In this case, solve and return the answer in the format of a LIST OF ONE DICT [{{'expr': given expression, 'result': calculated answer}}]. "
#     f"2. Set of Equations like x^2 + 2x + 1 = 0, 3y + 4x = 0, 5x^2 + 6y + 7 = 12, etc.: In this case, solve for the given variable, and the format should be a COMMA SEPARATED LIST OF DICTS, with dict 1 as {{'expr': 'x', 'result': 2, 'assign': True}} and dict 2 as {{'expr': 'y', 'result': 5, 'assign': True}}. This example assumes x was calculated as 2, and y as 5. Include as many dicts as there are variables. "
#     f"3. Assigning values to variables like x = 4, y = 5, z = 6, etc.: In this case, assign values to variables and return another key in the dict called {{'assign': True}}, keeping the variable as 'expr' and the value as 'result' in the original dictionary. RETURN AS A LIST OF DICTS. "
#     f"4. Analyzing Graphical Math problems, which are word problems represented in drawing form, such as cars colliding, trigonometric problems, problems on the Pythagorean theorem, adding runs from a cricket wagon wheel, etc. These will have a drawing representing some scenario and accompanying information with the image. PAY CLOSE ATTENTION TO DIFFERENT COLORS FOR THESE PROBLEMS. You need to return the answer in the format of a LIST OF ONE DICT [{{'expr': given expression, 'result': calculated answer}}]. "
#     f"5. Detecting Abstract Concepts that a drawing might show, such as love, hate, jealousy, patriotism, or a historic reference to war, invention, discovery, quote, etc. USE THE SAME FORMAT AS OTHERS TO RETURN THE ANSWER, where 'expr' will be the explanation of the drawing, and 'result' will be the abstract concept. "
#     f"Analyze the equation or expression in this image and return the answer according to the given rules: "
#     f"Make sure to use extra backslashes for escape characters like \\f -> \\\\f, \\n -> \\\\n, etc. "
#     f"DO NOT USE BACKTICKS OR MARKDOWN FORMATTING. "
#     f"PROPERLY QUOTE THE KEYS AND VALUES IN THE DICTIONARY FOR EASIER PARSING WITH Python's ast.literal_eval."
# )

prompt = (
    f"You have been given an image with some mathematical expressions, and you need to solve them. "
    f"Note: Use the PEMDAS rule for solving mathematical expressions. PEMDAS stands for the Priority Order: Parentheses, Exponents, Multiplication and Division (from left to right), Addition and Subtraction (from left to right). "
    f"Parentheses have the highest priority, followed by Exponents, then Multiplication and Division, and lastly Addition and Subtraction. "
    f"For example: "
    f"Q. 2 + 3 * 4 "
    f"(3 * 4) => 12, 2 + 12 = 14. "
    f"Q. 2 + 3 + 5 * 4 - 8 / 2 "
    f"5 * 4 => 20, 8 / 2 => 4, 2 + 3 => 5, 5 + 20 => 25, 25 - 4 => 21. "
    f"If the case is a simple mathematical expression like 2 + 2, 3 * 4, 5 / 6, 7 - 8, etc., solve and return the answer in the format of a LIST OF ONE DICT: "
    f"[{{'expr': given expression, 'result': calculated answer}}]. "
    f"Return only the answer in the specified format. "
    f"Make sure to properly quote the keys and values in the dictionary for easier parsing with Python's ast.literal_eval."
    f"DO NOT USE BACKTICKS OR MARKDOWN FORMATTING. "
    ""
)


def encode_image(image_path):

    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def analyze_image(image_path, prompt):

    client = OpenAI()

    # Encode the image
    base64_image = encode_image(image_path)

    # Create the payload
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ],
        }
    ]

    # Make the API call
    response = client.chat.completions.create(
        model="gpt-4o", messages=messages, max_tokens=300
    )
    # print(response.choices)
    return response.choices[0].message.content


class State:
    x: float
    y: float


state = State()
image_path = "drawing.png"

max_height = 720
max_width = 1080


def main(page: ft.Page):
    page.title = "Sutio | AI Calculator"
    page.window.height = max_height
    page.window.max_height = max_height
    page.window.width = max_width
    page.window.max_width = max_width

    drawing_actions = []

    def pan_start(e: ft.DragStartEvent):
        state.x = e.local_x
        state.y = e.local_y

    def pan_update(e: ft.DragUpdateEvent):
        cp.shapes.append(
            cv.Line(
                state.x, state.y, e.local_x, e.local_y, paint=ft.Paint(stroke_width=3)
            )
        )
        cp.update()
        drawing_actions.append(
            {"x1": state.x, "y1": state.y, "x2": e.local_x, "y2": e.local_y}
        )
        state.x = e.local_x
        state.y = e.local_y

    background_fill = cv.Fill(
        ft.Paint(
            gradient=ft.PaintLinearGradient(
                (0, 0),
                (600, 600),
                colors=[ft.colors.WHITE, ft.colors.WHITE],
            )
        )
    )

    cp = cv.Canvas(
        shapes=[background_fill],
        content=ft.GestureDetector(
            on_pan_start=pan_start,
            on_pan_update=pan_update,
            drag_interval=10,
        ),
        expand=False,
    )

    def resetCv(e):
        cp.shapes = [background_fill]
        drawing_actions.clear()
        # if os.path.exists(image_path):
        #     os.remove(image_path)
        cp.update()

    def run_the_calculation(e):
        resetButton.disabled = True
        runButton.disabled = True
        cp.update()
        width, height = max_width, max_height
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        # Draw lines
        for action in drawing_actions:
            draw.line(
                (action["x1"], action["y1"], action["x2"], action["y2"]),
                fill="black",
                width=3,
            )

        # Save the image
        image.save(image_path)
        try:
            result = analyze_image(image_path, prompt)
            answers = ast.literal_eval(result)

            for i, ans in enumerate(answers):
                cp.shapes.append(
                    cv.Text(
                        text=f"{ans["expr"]} = {ans["result"]}",
                        x=20,
                        y=20 + (i * 30),
                        style=ft.Paint(
                            color=ft.colors.BLACK,
                            style=ft.PaintingStyle.FILL,
                            stroke_width=3,
                        ),
                        max_width=max_width - 40,
                    )
                )
            cp.update()
        except Exception as ee:
            cp.shapes.append(
                cv.Text(
                    text=f"{result}",
                    x=20,
                    y=20,
                    style=ft.Paint(
                        color=ft.colors.BLACK,
                        style=ft.PaintingStyle.FILL,
                        stroke_width=3,
                    ),
                    max_width=max_width - 40,
                )
            )
            cp.update()

    resetButton = ft.FilledButton(
        "Reset",
        on_click=resetCv,
        bgcolor=ft.Colors.RED_200,
    )
    runButton = ft.FilledButton("Run", on_click=run_the_calculation)

    action_buttons = ft.Row(
        controls=[resetButton, runButton],
        alignment=ft.MainAxisAlignment.END,
    )

    page.add(
        action_buttons,
    )
    page.add(
        ft.Container(
            cp,
            border_radius=5,
            width=float("inf"),
            expand=True,
        )
    )


ft.app(
    main,
)
