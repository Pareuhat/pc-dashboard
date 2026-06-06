from flask import Flask, render_template, request, redirect, url_for, session
import psutil
import socket
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "pareuhat_dashboard"

PASSWORD = "1234"

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        if request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))

        return render_template("login.html", error=True)

    return render_template("login.html", error=False)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
def dashboard():

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent

    # ✅ FIX: ใช้ "/" แทน C:\ (รองรับ Render Linux)
    disk = psutil.disk_usage("/")
    disk_percent = disk.percent
    disk_free = round(disk.free / (1024**3), 1)

    hostname = socket.gethostname()

    try:
        ip_address = socket.gethostbyname(hostname)
    except:
        ip_address = "Unknown"

    boot_time = psutil.boot_time()
    uptime_seconds = int(datetime.now().timestamp() - boot_time)

    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60

    uptime = f"{hours}h {minutes}m {seconds}s"

    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%d/%m/%Y")

    return render_template(
        "index.html",
        cpu=cpu,
        ram=ram,
        disk_percent=disk_percent,
        disk_free=disk_free,
        hostname=hostname,
        ip_address=ip_address,
        uptime=uptime,
        current_time=current_time,
        current_date=current_date
    )


@app.route("/restart")
def restart():

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    os.system("shutdown /r /t 0")
    return "Restarting..."


@app.route("/shutdown")
def shutdown():

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    os.system("shutdown /s /t 0")
    return "Shutting down..."


# ✅ FIX: สำหรับ Cloud ใช้แบบนี้ (ไม่ debug)
if __name__ == "__main__":
    app.run(host="0.0.0.0")