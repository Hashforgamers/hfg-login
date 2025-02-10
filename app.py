# run.py

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5055, debug=True)  # Specify port=5050
