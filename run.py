import os
from flask import Flask
from app.webhook import webhook_bp

app = Flask(__name__)
app.register_blueprint(webhook_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=os.getenv("DEBUG", "False") == "True")