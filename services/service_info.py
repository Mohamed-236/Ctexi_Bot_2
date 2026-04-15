from models.service import recuperer_service_par_intention

def get_services():
    services = recuperer_service_par_intention()

    if not services:
        return []

    return services