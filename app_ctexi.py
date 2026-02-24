from flask import Flask     
from config import Config
from routes.auth_routes import auth_bp
from routes.faq_route import faq_bp


# Creation de l'app
app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(auth_bp)
app.register_blueprint(faq_bp)


if __name__ == "__main__":  
    app.run(debug=True)



