#!/usr/bin/env python3
"""
init_db.py
Script seguro para inicializar la base de datos y sincronizar Alembic.

✅ Crea tablas que no existan.
✅ Marca la DB como actual para Alembic.
"""

from app import create_app, db
from flask_migrate import stamp

app = create_app()

with app.app_context():
    # 1️⃣ Crea todas las tablas que aún no existan
    db.create_all()
    print("✅ Tablas creadas o ya existentes (no se borró nada).")

    # 2️⃣ Marca la DB como actual para Alembic
    stamp(revision="head")
    print("✅ Alembic considera que la DB está al día.")

    # 3️⃣ Indicaciones para futuras migraciones
    print("\n⚡ Para futuras migraciones:")
    print("   1. flask db migrate -m 'Mensaje descriptivo de la migración'")
    print("   2. flask db upgrade")
