from tkinter import *
from tkinter.ttk import *
from pgvocalizer import vocalize_plan
from pgvocalizer.connection import get_query_plan
import pyttsx


class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()

    def init_window(self):    
        self.master.title("QEP Vocalizer")
        self.pack(fill=BOTH, expand=1)

        self.label_query = Label(self, text="Input Query: ")
        self.label_query.grid(row=0, column=0, padx=5, pady=10)

        self.entry_query = Text(self, width=130, height=10)
        self.entry_query.grid(row=0, column=1, padx=5, pady=10, sticky=EW)

        self.submitButton1 = Button(self, text="Get query execution plan", command=self.get_qep)
        self.submitButton1.grid(row=0, column=2, padx=5, pady=10)

        self.label_qep_result = Label(self, text="Query Execution Plan Result: ")
        self.label_qep_result.grid(row=1, column=0, padx=5, pady=10)

        self.text_qep_result = Text(self, width=130, height=10)
        self.text_qep_result.grid(row=1, column=1, pady=10)

        self.label_qep = Label(self, text="Input Query Execution Plan: ")
        self.label_qep.grid(row=2, column=0, padx=5, pady=10)

        self.entry_qep = Text(self, width=130, height=10)
        self.entry_qep.grid(row=2, column=1, padx=5, pady=10, sticky=EW)

        self.submitButton2 = Button(self, text="Get text description of your query plan", command=self.get_nl)
        self.submitButton2.grid(row=2, column=2, padx=5, pady=10)

        self.label_nl_result = Label(self, text="Text description result: ")
        self.label_nl_result.grid(row=3, column=0, padx=5, pady=10)

        self.text_nl_result = Text(self, width=130, height=10)
        self.text_nl_result.grid(row=3, column=1, pady=10)

        self.submitButton2 = Button(self, text="Vocalize the text description", command=self.speak)
        self.submitButton2.grid(row=3, column=2, padx=5, pady=10)

    def get_qep(self):
        query = self.entry_query.get(0.0, END)
        qep = get_query_plan(query)[0]
        self.text_qep_result.delete(0.0, END)
        self.text_qep_result.insert(END, qep)

    def get_nl(self):
        qep = self.entry_qep.get(0.0, END)
        nl = vocalize_plan(qep)
        self.text_nl_result.delete(0.0, END)
        self.text_nl_result.insert(END, nl)

    def speak(self):
        sentences = self.text_nl_result.get(0.0, END)
        engine = pyttsx.init()
        engine.say(sentences)
        engine.runAndWait()


if __name__ == "__main__":
    root = Tk()
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    root.geometry("%dx%d" % (w, h))
    app = Window(root)
    root.mainloop()
