from flask import Flask     #
from config import Config
from routes.chatbot_routes import chatbot_bp

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(chatbot_bp)


if __name__ == "__main__":  
    app.run(debug=True)

