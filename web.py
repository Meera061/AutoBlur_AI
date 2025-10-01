from flask import Flask, request, send_from_directory, render_template, render_template_string
import cv2
import os
import pytesseract
import spacy
from werkzeug.utils import secure_filename
import re
import uuid
import json
import sqlite3

# ---------- CONFIG ----------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
nlp = spacy.load("en_core_web_sm")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
DB_FILE = "database.db"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---------- DB ----------
def init_db():
    """Initialize database for contact form"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()


# ---------- HELPERS ----------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def digits_in_text(s):
    return "".join(ch for ch in s if ch.isdigit())


def detect_sensitive_regions(image_path, min_conf=30):
    """Default Mode: Auto-detect sensitive info"""
    image = cv2.imread(image_path)
    if image is None:
        return []
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    data = pytesseract.image_to_data(rgb, output_type=pytesseract.Output.DICT)
    n = len(data["text"])
    regions = []
    for i in range(n):
        text = data["text"][i].strip()
        if not text:
            continue
        try:
            conf = float(data.get("conf", [])[i])
        except:
            conf = -1
        if conf < min_conf:
            continue
        text_norm = text.lower().strip()

        sensitive_keywords = ["transaction id", "reference id", "order id", "amount", "email", "phone", "contact"]
        if any(k in text_norm for k in sensitive_keywords):
            x = int(data["left"][i]); y = int(data["top"][i])
            w = int(data["width"][i]); h = int(data["height"][i])
            regions.append({"x": x, "y": y, "w": w, "h": h, "text": text, "index": i})
            continue

        digits = digits_in_text(text_norm)
        if len(digits) >= 4:
            x = int(data["left"][i]); y = int(data["top"][i])
            w = int(data["width"][i]); h = int(data["height"][i])
            regions.append({"x": x, "y": y, "w": w, "h": h, "text": text, "index": i})
    return regions


def create_blurred_patches(image_path, regions, uid_prefix):
    img = cv2.imread(image_path)
    h_img, w_img = img.shape[:2]
    patches = []
    pad = 6
    for idx, r in enumerate(regions):
        x1 = max(0, int(r["x"] - pad)); y1 = max(0, int(r["y"] - pad))
        x2 = min(w_img, int(r["x"] + r["w"] + pad)); y2 = min(h_img, int(r["y"] + r["h"] + pad))
        roi = img[y1:y2, x1:x2]
        if roi.size == 0: continue
        kx = 31 if min(roi.shape[:2]) < 70 else 71
        if kx % 2 == 0: kx += 1
        blurred = cv2.GaussianBlur(roi, (kx, kx), 0)
        patch_name = f"{uid_prefix}patch{idx}.png"
        patch_path = os.path.join(app.config["UPLOAD_FOLDER"], patch_name)
        cv2.imwrite(patch_path, blurred)
        patches.append({"file": patch_name, "x": x1, "y": y1,
                        "w": x2 - x1, "h": y2 - y1, "idx": idx, "index": r["index"]})
    return patches


def apply_blur_to_base(image_path, regions, out_path, blur_indices=None):
    img = cv2.imread(image_path)
    if img is None: return False
    h_img, w_img = img.shape[:2]
    pad = 6
    blur_indices = blur_indices or []
    for r in regions:
        if blur_indices and r["index"] not in blur_indices:
            continue
        x1 = max(0, int(r["x"] - pad)); y1 = max(0, int(r["y"] - pad))
        x2 = min(w_img, int(r["x"] + r["w"] + pad)); y2 = min(h_img, int(r["y"] + r["h"] + pad))
        roi = img[y1:y2, x1:x2]
        if roi.size == 0: continue
        kx = 31 if min(roi.shape[:2]) < 70 else 71
        if kx % 2 == 0: kx += 1
        blurred = cv2.GaussianBlur(roi, (kx, kx), 0)
        img[y1:y2, x1:x2] = blurred
    cv2.imwrite(out_path, img)
    return True


# ---------- ROUTES ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/features")
def features():
    return render_template("features.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)", (name, email, message))
        conn.commit()
        conn.close()
        return "<h3>✅ Message Saved. Thank you!</h3><a href='/'>Back Home</a>"
    return render_template("contact.html")


@app.route("/default", methods=["GET", "POST"])
def default_mode():
    if request.method == "POST":
        f = request.files.get("file")
        if not f or not allowed_file(f.filename):
            return "No valid file uploaded", 400
        fname = secure_filename(f.filename)
        uid = uuid.uuid4().hex[:8]
        saved_name = f"{uid}_{fname}"
        path = os.path.join(app.config["UPLOAD_FOLDER"], saved_name)
        f.save(path)
        regions = detect_sensitive_regions(path)
        out_name = f"blurred_{saved_name}"
        out_path = os.path.join(app.config["UPLOAD_FOLDER"], out_name)
        ok = apply_blur_to_base(path, regions, out_path)
        return render_template("default.html", out_name=out_name) if ok else "Error", 500
    return render_template("default.html", out_name=None)


@app.route("/custom", methods=["GET", "POST"])
def custom_mode():
    if request.method == "POST":
        f = request.files.get("file")
        if not f or not allowed_file(f.filename):
            return "No valid file uploaded", 400
        fname = secure_filename(f.filename)
        uid = uuid.uuid4().hex[:8]
        saved_name = f"{uid}_{fname}"
        path = os.path.join(app.config["UPLOAD_FOLDER"], saved_name)
        f.save(path)

        image = cv2.imread(path)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        data = pytesseract.image_to_data(rgb, output_type=pytesseract.Output.DICT)
        n = len(data["text"])
        regions = []
        for i in range(n):
            text = data["text"][i].strip()
            if not text:
                continue
            try:
                conf = float(data.get("conf", [])[i])
            except:
                conf = -1
            if conf < 30:
                continue
            x = int(data["left"][i]); y = int(data["top"][i])
            w = int(data["width"][i]); h = int(data["height"][i])
            regions.append({"x": x, "y": y, "w": w, "h": h, "text": text, "index": i})

        patches = create_blurred_patches(path, regions, uid_prefix=uid)

        regions_file = os.path.join(app.config["UPLOAD_FOLDER"], f"{uid}_regions.json")
        with open(regions_file, "w") as fjson:
            json.dump({"regions": regions, "image": saved_name}, fjson)

        return render_template("custom.html", orig=saved_name, patches=patches, uid=uid)
    return render_template("custom.html", orig=None, patches=None, uid=None)


@app.route("/custom/download", methods=["POST"])
def custom_download():
    uid = request.form.get("uid")
    indices_json = request.form.get("blurred_indices")
    if not uid or not indices_json:
        return "Missing data", 400
    try:
        blurred_indices = json.loads(indices_json)
    except:
        return "Invalid data", 400

    regions_file = os.path.join(app.config["UPLOAD_FOLDER"], f"{uid}_regions.json")
    if not os.path.exists(regions_file):
        return "Session expired", 400

    with open(regions_file, "r") as fjson:
        data = json.load(fjson)
    regions = data["regions"]
    image_name = data["image"]

    image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_name)
    out_name = f"final_{uid}_{image_name}"
    out_path = os.path.join(app.config["UPLOAD_FOLDER"], out_name)

    if not apply_blur_to_base(image_path, regions, out_path, blur_indices=blurred_indices):
        return "Error", 500

    return send_from_directory(app.config["UPLOAD_FOLDER"], out_name, as_attachment=True)


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ---------- MAIN ----------
if __name__ == "__main__":
    if not os.path.exists(DB_FILE):
        init_db()
    else:
        try:
            init_db()
        except:
            os.remove(DB_FILE)
            init_db()
    app.run(debug=True)
