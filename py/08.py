import turtle
screen=turtle.Screen()
screen.setup(width=600,height=600)
def duobian(n):
    for i in range(n):
        turtle.forward(100)
        turtle.left(360/n)
turtle.shape("turtle")
turtle.penup()
turtle.goto(-50,-150)
turtle.pendown()
duobian(6)
turtle.hideturtle()
turtle.done()