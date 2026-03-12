from flask import Blueprint, jsonify, request
from token_nize import token_required
from models.contact_agent import recuperer_agent_par_intention



contact_bp = Blueprint("contact", __name__, url_prefix="/api/agent")


# Recuperer un agent dans la bd
@contact_bp.route("/contact-agent", methods=["GET"])

@token_required
def get_agent_contact():
    agent = recuperer_agent_par_intention(1)

    if not agent:
        return jsonify({
            "status": "error",
            "message": "Aucun agent disponible"
        }), 404
    
    return jsonify({
        "status" : "succes",
        "agent" : {
            "whatsapp" : agent["whatsapp"],
            "telephone" : agent["telephone"],
            "email" : agent["email"]
             }
    }),200