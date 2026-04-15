from models.contact_agent import recuperer_agent_par_intention

def get_agent():
    """
    Aujourd'hui DB
    Demain API mobile
    """

    agent = recuperer_agent_par_intention(1)

    if not agent:
        return None

    return {
        "whatsapp": agent["whatsapp"],
        "telephone": agent["telephone"],
        "email": agent["email"]
    }