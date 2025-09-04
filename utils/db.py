from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import settings

# Establece la conexion con la bd
engine = create_engine(settings.DB_URL)
# Crear fabricador de sesiones con la siguiente configuracion
# Autocommit false: No hace commit automaticamente
# Autoflush false: No sicroniza
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crea una clase base que usaremos para definir nuestras tablas
Base = declarative_base()

# Función para obtener conexiones
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()