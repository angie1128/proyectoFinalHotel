from app import create_app
from dotenv import load_dotenv
import os

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8086)))
    

load_dotenv()  # carga las variables del archivo .env
db_url = os.getenv("DATABASE_URL")
print("DB URL:", db_url)  # opcional para verificar

