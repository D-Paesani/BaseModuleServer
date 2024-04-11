import requests, configparser
from flask_jwt_extended import create_access_token
from datetime import timedelta

cfg=configparser.ConfigParser()
cfg.read('bms/keycloak/cfg.cfg')

URL_TOKEN = cfg['KEYCLOAK']['URL_TOKEN']
URL_USERS = cfg['KEYCLOAK']['URL_USERS']
URL_USER_GROUP = cfg['KEYCLOAK']['URL_USER_GROUP']
URL_LOGOUT_BY_UID = cfg['KEYCLOAK']['URL_LOGOUT_BY_UID']
CLIENT_SECRET = cfg['KEYCLOAK']['USER_CLIENT_SECRET']
CLIENT_ID = cfg['KEYCLOAK']['USER_CLIENT_ID']
USR_ADMIN = cfg['KEYCLOAK']['USR_ADMIN']
PSW_ADMIN = cfg['KEYCLOAK']['PSW_ADMIN']

HEADERS_GET = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer {}'
}

HEADERS_POST = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

DATA_PSW = {
            'client_id': CLIENT_ID,
            'grant_type': 'password',
            'username': '',
            'password': '',
            'client_secret': CLIENT_SECRET
        }

def retrieve_uid(username, access_token_admin):
        query = {          
                    "username": username  
                }
        headers = HEADERS_GET.copy()
        headers['Authorization'] = headers['Authorization'].format(access_token_admin)
        response = requests.get(URL_USERS, headers=headers, params=query, verify=True)
        if response.status_code == 200:
            data = response.json()
            return data[0]['id']
        else:
            print(response.text)

def logout_user(uid):
        access_token_admin = admin_token()
        headers = HEADERS_GET.copy()
        headers['Authorization'] = headers['Authorization'].format(access_token_admin)
        url = URL_LOGOUT_BY_UID.format(uid)
        requests.post(url, headers=headers, verify=True)
        logout_admin(access_token_admin)

def logout_admin(access_token_admin):
        uid = retrieve_uid(USR_ADMIN, access_token_admin)
        headers = HEADERS_GET.copy()
        headers['Authorization'] = headers['Authorization'].format(access_token_admin)
        url = URL_LOGOUT_BY_UID.format(uid)
        requests.post(url, headers=headers, verify=True)
        #loggerAdapter.info('USER LOGGED OUT')

def admin_token():
    DATA_PSW['username'] = USR_ADMIN
    DATA_PSW['password'] = PSW_ADMIN
    response = requests.post(URL_TOKEN, data=DATA_PSW, headers=HEADERS_POST, verify=True)
    data = response.json()
    if response.status_code  == 200:
        access_token_admin = data['access_token']
        return access_token_admin
    else:
        return False

def user_auth_google(query, source):
    user = {}
    access_token_admin = admin_token()
    # query = {
    #             "email": email  
    #         }
    headers = HEADERS_GET.copy()
    headers['Authorization'] = headers['Authorization'].format(access_token_admin)
    response = requests.get(URL_USERS, headers=headers, params=query, verify=False) #recupero i dati dell'account 
    if response.status_code == 200:
        data = response.json()
        user['uid'] = data[0]['id']
        user['username'] = data[0]['username']
        user['enabled'] = data[0]['enabled']
        user['firstName'] = data[0]['firstName']
        user['lastName'] = data[0]['lastName']
        user['email'] = data[0]['email']
        user['source'] = source
        if user['enabled'] == True:
            response = requests.get(URL_USER_GROUP.format(user['uid']), headers=headers, verify=True) #recupero il nome del gruppo d'appartenenza
            if response.status_code == 200:
                data = response.json()
                for li in data: 
                    if li['path'].split('/')[1] == 'dp-bms':
                        user['group'] = li['name']
            logout_admin(access_token_admin)
            return response.status_code, user
        else:
            return response.status_code, 'User Disabled'
    else:
        logout_admin(access_token_admin)
        return response.status_code, 'User Not Found'
     

def user_auth(username, password, source):
    user = {}
    data_psw = DATA_PSW.copy()
    data_psw['username'] = username
    data_psw['password'] = password
    try:
        response = requests.post(URL_TOKEN, data=data_psw, headers=HEADERS_POST, verify=True) #verifico che l'utente esista e che venga rilasciato il token
    except Exception as e:
        return f'{e}', f'{e}'
    if response.status_code == 200:
        access_token_admin = admin_token()
        query = {
                    "email": username  
                }
        headers = HEADERS_GET.copy()
        headers['Authorization'] = headers['Authorization'].format(access_token_admin)
        response = requests.get(URL_USERS, headers=headers, params=query, verify=False) #recupero i dati dell'account 
        if response.status_code == 200:
            data = response.json()
            user['uid'] = data[0]['id']
            user['username'] = data[0]['username']
            user['enabled'] = data[0]['enabled']
            user['firstName'] = data[0]['firstName']
            user['lastName'] = data[0]['lastName']
            user['email'] = data[0]['email']
            user['source'] = source
            if user['enabled'] == True:
                response = requests.get(URL_USER_GROUP.format(user['uid']), headers=headers, verify=True) #recupero il nome del gruppo d'appartenenza
                if response.status_code == 200:
                    data = response.json()
                    for li in data: 
                        if li['path'].split('/')[1] == 'dp-bms':
                            user['group'] = li['name']
                logout_admin(access_token_admin)
                return response.status_code, user
            else:
                return response.status_code, 'User Disabled'
        else:
            logout_admin(access_token_admin)
            return response.status_code, 'Error In Retrieving Data'
    else:
        return response.status_code, f'User Not Found {response.status_code}'


def generate_token(user):
    return create_access_token(identity=[user['user'],user['uid']],
                                expires_delta=timedelta(days=1),
                                additional_claims={'uid':user['uid'],
                                                    'user':user['user'],
                                                    'givenName':user['givenName'],
                                                    'familyName':user['familyName'],
                                                    'email':user['email'],
                                                    'group':user['group'],
                                                    'enabled':user['enabled'],
                                                    'local':user['local']})