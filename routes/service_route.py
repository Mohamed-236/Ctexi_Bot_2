from flask import Blueprint, jsonify, request
from token_nize import token_required
from models.service import recuperer_service_par_intention




service_bp = Blueprint("service", __name__, url_prefix="/api/list")

# ==========================================================
# Récupérer tous les services (liste pour les boutons)
# ==========================================================
@service_bp.route("/service", methods=["GET"])
@token_required
def get_services():
    try:
        services = recuperer_service_par_intention()  # sans id => liste de services
        # Retourner uniquement id et nom
        services_list = [{
            "id_service": s["id_service"], "nom_service": s["nom_service"]} for s in services]


        return jsonify({
            
            "status": "success",
            "services": services_list
              
              })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==========================================================
# Récupérer un service spécifique (détails)
# ==========================================================
@service_bp.route("/service/<int:id_service>", methods=["GET"])
def get_service_details(id_service):
    try:
        services = recuperer_service_par_intention(id_service)  # id donné => détails
        if not services:
            return jsonify({"status": "error", "message": "Service non trouvé"}), 404

        service = services[0]  # récupération du premier élément
        # menu est déjà en JSONB dans Postgres, donc on peut l'envoyer directement
        return jsonify({
            "status": "success",
            "id_service": service["id_service"],
            "nom_service": service["nom_service"],
            "descriptions": service["descriptions"],
            "menu": service["menu"] or []

            
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500