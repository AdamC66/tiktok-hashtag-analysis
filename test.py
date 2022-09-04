from tkinter import *
import tkinter as tk


window = tk.Tk()
window.geometry("500x300")
window.title("TikTok Hashtag Analyzer")
frame1 = tk.Frame(master=window,height=200)
frame1.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

button = tk.Button(
    master=frame1,
    text="Click me!",
    width=12,
    height=3,
    bg="blue",
    fg="yellow",
)
label = tk.Label(master=frame1, text="Name")
entry = tk.Entry(master=frame1,)
button.pack()
label.pack()
entry.pack()

window.mainloop()