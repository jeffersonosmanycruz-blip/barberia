from flask import Flask, render_template, request
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# 🔒 LICENCIA (1 MES)
fecha_inicio = datetime(2026, 5, 16)
fecha_fin = fecha_inicio + timedelta(days=30)

# ⛔ BLOQUEO SI EXPIRA
if datetime.now() > fecha_fin:
    print("❌ Sistema bloqueado. Contacta al desarrollador.")
    exit()


# 🗄️ BASE DE DATOS
def conectar():
    conn = sqlite3.connect("barberia.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS citas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        fecha_hora TEXT
    )
    """)

    conn.commit()
    return conn, cursor


# 🕒 HORARIOS
horarios = [
    "08:00", "09:00", "10:00",
    "11:00", "12:00",
    "1:00", "2:00", "3:00", "4:00",
    "5:00", "6:00", "7:00", "8:00"
]


@app.route("/", methods=["GET", "POST"])
def index():

    conn, cursor = conectar()
    mensaje = ""

    # 🔥 BORRAR CITAS PASADAS AUTOMÁTICAMENTE
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")

    cursor.execute(
        "DELETE FROM citas WHERE fecha_hora < ?",
        (ahora,)
    )
    conn.commit()

    # ➕ AGENDAR CITA
    if request.method == "POST":

        nombre = request.form["nombre"]
        fecha = request.form["fecha"]
        hora = request.form["hora"]

        # 🔥 UNIR FECHA + HORA
        fecha_hora = f"{fecha} {hora}"

        # ❌ VERIFICAR SI YA EXISTE
        cursor.execute(
            "SELECT * FROM citas WHERE fecha_hora=?",
            (fecha_hora,)
        )

        existe = cursor.fetchone()

        if existe:
            mensaje = "❌ Ese horario ya está ocupado"
        else:
            cursor.execute(
                "INSERT INTO citas (nombre, fecha_hora) VALUES (?, ?)",
                (nombre, fecha_hora)
            )

            conn.commit()
            mensaje = "✔ Cita guardada correctamente"

    # 📋 CITAS
    cursor.execute("SELECT nombre, fecha_hora FROM citas")
    citas = cursor.fetchall()

    # ⛔ OCUPADAS
    cursor.execute("SELECT fecha_hora FROM citas")
    ocupadas = [c[0] for c in cursor.fetchall()]

    return render_template(
        "index.html",
        horarios=horarios,
        citas=citas,
        ocupadas=ocupadas,
        mensaje=mensaje
    )


if __name__ == "__main__":
    app.run(debug=True)