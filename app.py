import os
from flask import Flask, jsonify, redirect, request, url_for
from Tools_script.auth import ensure_accounts_file, authenticate, create_account, get_history

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTERFACE_DIR = os.path.join(BASE_DIR, "interface_AI.     IA")

app = Flask(
    __name__,
    static_folder=INTERFACE_DIR,
    static_url_path=""
)

ensure_accounts_file()


@app.route("/")
def root():
    return redirect(url_for("login_page"))


@app.route("/login")
def login_page():
    return app.send_static_file("login.html")


@app.route("/dashboard")
def dashboard_page():
    return app.send_static_file("index.html")


@app.route("/authenticate", methods=["POST"])
def authenticate_route():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400
    if authenticate(email, password):
        return jsonify({"success": True, "message": "Login successful.", "email": email})
    return jsonify({"success": False, "message": "Wrong email or password."}), 401


@app.route("/register", methods=["POST"])
def register_route():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm", "")
    if not email or not password or not confirm:
        return jsonify({"success": False, "message": "All fields are required."}), 400
    if password != confirm:
        return jsonify({"success": False, "message": "Passwords do not match."}), 400
    if create_account(email, password):
        return jsonify({"success": True, "message": "Account created successfully."})
    return jsonify({"success": False, "message": "This email already exists."}), 400


@app.route("/history")
def history_route():
    email = request.args.get("email", "").strip()
    if not email:
        return jsonify({"success": False, "history": []}), 400
    return jsonify({"success": True, "history": get_history(email)})


@app.errorhandler(404)
def not_found(error):
    return app.send_static_file("login.html"), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
