from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# =========================
# HORARIOS
# =========================
horarios = [
    "8:00 AM",
    "9:00 AM",
    "10:00 AM",
    "11:00 AM",
    "1:00 PM",
    "2:00 PM",
    "3:00 PM",
    "4:00 PM",
    "5:00 PM",
    "6:00 PM",
    "7:00 PM",
    "8:00 PM"
]

# =========================
# BASE DE DATOS
# =========================
def init_db():
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS citas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        telefono TEXT NOT NULL,
        fecha_hora TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

# =========================
# LIBERAR CITAS PASADAS
# =========================
def liberar_citas_pasadas():
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()

    ahora = datetime.now()

    cursor.execute("SELECT id, fecha_hora FROM citas")
    citas = cursor.fetchall()

    for cita in citas:
        cita_id = cita[0]
        fecha_hora = cita[1]

        try:
            fecha_cita = datetime.strptime(fecha_hora, "%Y-%m-%d %I:%M %p")

            if fecha_cita < ahora:
                cursor.execute("DELETE FROM citas WHERE id = ?", (cita_id,))
        except:
            pass

    conn.commit()
    conn.close()

# =========================
# PAGINA PRINCIPAL
# =========================
@app.route("/", methods=["GET"])
def index():
    liberar_citas_pasadas()

    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()

    cursor.execute("SELECT fecha_hora FROM citas")
    citas_db = cursor.fetchall()

    conn.close()

    citas_ocupadas = [cita[0] for cita in citas_db]

    return render_template(
        "index.html",
        horarios=horarios,
        citas_ocupadas=citas_ocupadas
    )

# =========================
# AGENDAR CITA
# =========================
@app.route("/agendar", methods=["POST"])
def agendar():
    nombre = request.form["nombre"]
    telefono = request.form["telefono"]
    fecha = request.form["fecha"]
    hora = request.form["hora"]

    fecha_hora = f"{fecha} {hora}"

    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO citas (nombre, telefono, fecha_hora)
    VALUES (?, ?, ?)
    """, (nombre, telefono, fecha_hora))

    conn.commit()
    conn.close()

    return redirect("/")

# =========================
# INICIAR APP (RAILWAY OK)
# =========================
if __name__ == "__main__":
    init_db()
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        debug=False
    
    )