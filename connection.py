import flet
from flet import (
    Column,
    Container,
    ElevatedButton,
    Page,
    Row,
    Text,
    Colors,
    FilledButton,
)

class CalculatorApp(Container):
    def __init__(self):
        super().__init__()
        self.reset()
        self.result = Text(value="0", color=Colors.WHITE, size=22)
        self.content = self.build()

    def build(self):
        return Container(
            width=325,
            bgcolor=Colors.BLUE_900,
            border_radius=15,
            padding=20,
            content=Column(
                controls=[
                    Row(controls=[self.result], alignment="end"),

                    Row(controls=[
                        ElevatedButton("AC", bgcolor=Colors.YELLOW_400, color=Colors.BLACK, data="AC", on_click=self.on_button_clicked),
                        ElevatedButton("+/-", bgcolor=Colors.YELLOW_400, color=Colors.BLACK, data="+/-", on_click=self.on_button_clicked),
                        ElevatedButton("%", bgcolor=Colors.GREEN_900, color=Colors.WHITE, data="%", on_click=self.on_button_clicked),
                        ElevatedButton("/", bgcolor=Colors.GREEN_900, color=Colors.WHITE, data="/", on_click=self.on_button_clicked),
                    ]),

                    Row(controls=[
                        FilledButton("7", data="7", color=Colors.WHITE, on_click=self.on_button_clicked),
                        FilledButton("8", data="8", color=Colors.WHITE, on_click=self.on_button_clicked),
                        FilledButton("9", data="9", color=Colors.WHITE, on_click=self.on_button_clicked),
                        ElevatedButton("*", bgcolor=Colors.GREEN_900, color=Colors.WHITE, data="*", on_click=self.on_button_clicked),
                    ]),

                    Row(controls=[
                        FilledButton("4", data="4", color=Colors.WHITE, on_click=self.on_button_clicked),
                        FilledButton("5", data="5", color=Colors.WHITE, on_click=self.on_button_clicked),
                        FilledButton("6", data="6", color=Colors.WHITE, on_click=self.on_button_clicked),
                        ElevatedButton("-", bgcolor=Colors.GREEN_900, color=Colors.WHITE, data="-", on_click=self.on_button_clicked),
                    ]),

                    Row(controls=[
                        FilledButton("1", data="1", color=Colors.WHITE, on_click=self.on_button_clicked),
                        FilledButton("2", data="2", color=Colors.WHITE, on_click=self.on_button_clicked),
                        FilledButton("3", data="3", color=Colors.WHITE, on_click=self.on_button_clicked),
                        ElevatedButton("+", bgcolor=Colors.GREEN_900, color=Colors.WHITE, data="+", on_click=self.on_button_clicked),
                    ]),

                    Row(controls=[
                        FilledButton("0", data="0", color=Colors.WHITE, on_click=self.on_button_clicked),
                        FilledButton("00", data="00", color=Colors.WHITE, on_click=self.on_button_clicked),
                        ElevatedButton(".", bgcolor=Colors.AMBER_600, color=Colors.WHITE, data=".", on_click=self.on_button_clicked),
                        ElevatedButton("=", bgcolor=Colors.ORANGE, color=Colors.WHITE, data="=", on_click=self.on_button_clicked),
                    ]),
                ],
            ),
        )

    def on_button_clicked(self, e):
        data = e.control.data

        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"
            self.reset()

        elif data in ("0","1","2","3","4","5","6","7","8","9",".","00"):
            if self.result.value == "0" or self.new_operand:
                self.result.value = data
                self.new_operand = False
            else:
                self.result.value += data

        elif data in ("+","-","*","/"):
            self.result.value = self.calculate(self.operand1, float(self.result.value), self.operator)
            self.operator = data
            self.operand1 = 0 if self.result.value == "Error" else float(self.result.value)
            self.new_operand = True

        elif data == "=":
            self.result.value = self.calculate(self.operand1, float(self.result.value), self.operator)
            self.reset()

        elif data == "%":
            self.result.value = str(float(self.result.value) / 100)
            self.reset()

        elif data == "+/-":
            val = float(self.result.value)
            self.result.value = str(-val if val > 0 else abs(val))

        self.update()

    def calculate(self, a, b, op):
        if op == "+": return self.format(a + b)
        if op == "-": return self.format(a - b)
        if op == "*": return self.format(a * b)
        if op == "/": return "Error" if b == 0 else self.format(a / b)

    def format(self, num):
        return str(int(num)) if num % 1 == 0 else str(num)

    def reset(self):
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True


def myCal(page: Page):
    page.title = "Basic Calculator using Flet"
    page.window_height = 375
    page.window_width = 350
    page.add(CalculatorApp())


flet.app(target=myCal)
