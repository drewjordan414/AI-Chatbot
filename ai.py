import os
import sys
import openai
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTextEdit, QLineEdit, QLabel, QVBoxLayout

#response from gpt-3
TEMPERATURE = 0.5 #higher temperature will yeild more creative, less acruate responses. Max temp 1.0
MAX_TOKENS = 500 #tokens determine the response output 
FREQUENCY_PENALTY = 0
PRESENCE_PENALTY = 0.6
# limits how many questions we include in the prompt
MAX_CONTEXT_QUESTIONS = 10


def generate_response(instructions, previous_questions_and_answers, new_question):
    """Get a response from ChatCompletion
    Args:
        instructions: The instructions for the chat bot - this determines how it will behave
        previous_questions_and_answers: Chat history
        new_question: The new question to ask the bot
    Returns:
        The response text
    """
    # build the messages
    messages = [
        {"role": "system", "content": instructions},
    ]
    # add the previous questions and answers
    for question, answer in previous_questions_and_answers[-MAX_CONTEXT_QUESTIONS:]:
        messages.append({"role": "user", "content": question})
        messages.append({"role": "assistant", "content": answer})
    # add the new question
    messages.append({"role": "user", "content": new_question})

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        top_p=1,
        frequency_penalty=FREQUENCY_PENALTY,
        presence_penalty=PRESENCE_PENALTY,
    )
    return completion.choices[0].message.content


# create the main window for the program
class MainWindow(QMainWindow):
    def __init__(self, api_key):
        super().__init__()

        self.chat_box = QTextEdit(self)
        self.chat_box.setReadOnly(True)

        self.user_input = QLineEdit(self)
        self.user_input.returnPressed.connect(self.send_message)

        layout = QVBoxLayout()
        layout.addWidget(self.chat_box)
        layout.addWidget(self.user_input)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

        self.api_key_label = QLabel(api_key, self)
        self.api_key_label.setAlignment(Qt.AlignRight)
        self.statusBar().addWidget(self.api_key_label)

    # function for message sending
    def send_message(self):
        user_input = self.user_input.text()
        self.user_input.clear()
        self.chat_box.append("You: " + user_input)

        response_gpt3 = generate_response("User: {}\nAI".format(user_input), [], user_input)
        self.chat_box.append("AI: " + response_gpt3)


# main function
def main():
    api_key = input("Please enter your OpenAI API key: ")
    openai.api_key = api_key

    try:
        openai.api_key = api_key
        openai.Completion.create(engine="davinci", prompt="test", max_tokens=5)
    except Exception as e:
        print("Error: {}".format(str(e)))
        sys.exit(1)
    app = QApplication(sys.argv)
    window = MainWindow(api_key)
    window.setWindowTitle("GPT Chatbot")
    window.resize(640, 480)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


