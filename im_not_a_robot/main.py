from flask import Flask, render_template, request

app = Flask(__name__)

listOfAIs = [
    "gpt-2", "gpt-3", "gpt-3.5", "gpt-4", "gpt2", "gpt3", "gpt3.5", "gpt4" "gpt4o", "llama3.1405b", "llama38b", "claude3.5sonnet", "claude3haiku", "gemini1.5pro", "mistral7b"
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/processing", methods=["POST"])
def processing():    
    form = request.form
    joke, name, color = form["joke"], form["name"], form["color"]
    
    if joke == "yes" and name.strip().lower() not in listOfAIs and color != "none":
        return render_template("human.html")
    else:
        return render_template("robot.html")

app.run(host="0.0.0.0", port=81, debug=True)
