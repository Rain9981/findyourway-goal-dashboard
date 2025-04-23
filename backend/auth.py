def check_login(username, password):
    users = {
        "basic": {"password": "basic123", "role": "Basic"},
        "elite": {"password": "elite123", "role": "Elite"},
        "premium": {"password": "premium123", "role": "Premium"},
        "admin": {"password": "FindYourWayNMC520", "role": "Admin"}
    }
    return username in users and users[username]["password"] == password

def get_user_role(username):
    users = {
        "basic": {"password": "basic123", "role": "Basic"},
        "elite": {"password": "elite123", "role": "Elite"},
        "premium": {"password": "premium123", "role": "Premium"},
        "admin": {"password": "FindYourWayNMC520", "role": "Admin"}
    }
    return users[username]["role"]
