from .key_auth import user_auth_google, user_auth
from bms.web_manager.dbmanager import Users, gen_random_psw
from bms.web_manager import db
from ..web_manager.roles import Roles


class Manager():

    @staticmethod    
    def check_login_type(user_info, source):
        if source == 'google':
            resp, user = user_auth_google({'email' : user_info}, source)
        elif source == 'keycloak':
            resp, user = user_auth(user_info['email'], user_info['password'], source)
        if resp == 200:
            u = Users.query.filter_by(email=user['email']).first()
            if u:
                return True, u
            else:
                user = Users(email=user['email'], 
                             username=user['username'], 
                             password=gen_random_psw(), 
                             source=user['source'],
                             role_id=Roles.query.filter_by(name=user['group']).first().id)
                db.session.add(user)
                db.session.commit()
                return True, user
        return False, user 