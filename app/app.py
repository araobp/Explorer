# Reference: https://qiita.com/hiro_hiro_0425/items/e0a7a777f2772c3ac0ec
from flask import Flask
from controller.controller import main

app = Flask(__name__)
app.register_blueprint(main)

if __name__ == "__main__":

    app.run()
