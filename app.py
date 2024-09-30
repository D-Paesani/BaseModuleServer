from bms.web_manager import create_app, dbmanager
from bms.controller.jsc import initialize_jsc
import os

print('GET ENV => ',os.getenv('FLASK_CONFIG'))
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.before_first_request
def before_first_request():
    dbmanager.is_db_created()
    initialize_jsc()
    print('Initialize JSC ')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
    
