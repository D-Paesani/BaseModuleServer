from bms.web_manager import create_app, dbmanager

app = create_app()

@app.before_first_request
def before_first_request():
    dbmanager.is_db_created()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
    
