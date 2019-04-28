from flask import Flask, render_template
app = Flask(__name__)

posts=[
    {
        'author':"Cory Hl",
        'title': "Blogt Post 1",
        'content': 'Fist'
    }, {
        'author':"123 Hl",
        'title': "Blogt Post 1",
        'content': '123123'
    }

]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html',posts=posts)

@app.route("/about")
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)