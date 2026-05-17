from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

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

init_db()

# =========================
# HORARIOS
# =========================
horarios = [
    "8:00 AM","9:00 AM","10:00 AM","11:00 AM",
    "1:00 PM","2:00 PM","3:00 PM","4:00 PM",
    "5:00 PM","6:00 PM","7:00 PM","8:00 PM"
]

# =========================
def liberar_citas_pasadas():
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()

    ahora = datetime.now()

    cursor.execute("SELECT id, fecha_hora FROM citas")
    citas = cursor.fetchall()

    for cita in citas:
        try:
            fecha_cita = datetime.strptime(cita[1], "%Y-%m-%d %I:%M %p")
            if fecha_cita < ahora:
                cursor.execute("DELETE FROM citas WHERE id=?", (cita[0],))
        except:
            pass

    conn.commit()
    conn.close()

# =========================
@app.route("/", methods=["GET"])
def index():

    liberar_citas_pasadas()

    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, nombre, fecha_hora FROM citas")
    citas = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        horarios=horarios,
        citas=citas
    )

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

    # evitar doble reserva
    cursor.execute("SELECT * FROM citas WHERE fecha_hora=?", (fecha_hora,))
    existe = cursor.fetchone()

    if existe:
        conn.close()
        return redirect("/")

    cursor.execute("""
        INSERT INTO citas (nombre, telefono, fecha_hora)
        VALUES (?, ?, ?)
    """, (nombre, telefono, fecha_hora))

    conn.commit()
    conn.close()

    return redirect("/")

# =========================
@app.route("/cancelar/<int:id>")
def cancelar(id):

    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM citas WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/")

# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)