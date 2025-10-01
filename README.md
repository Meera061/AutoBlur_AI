# AutoBlur_AI
🖼️ Auto Blur AI

Auto Blur AI is a Flask-based web application that automatically detects and blurs sensitive information in images and documents.
It supports Default Mode (automatic blur) and Custom Mode (manual selection of blur areas).

🚀 Features

Default Mode → Upload a file, and sensitive data (like phone numbers, OTPs, transaction IDs, tracking IDs, and amounts) are blurred automatically.

Custom Mode → Upload a file and interactively choose which detected regions to blur.

Supports images (JPG, PNG, JPEG, etc.) and documents (PDF, DOCX, PPTX).

Uses OCR (Tesseract) + NLP (spaCy) to detect sensitive text accurately.

Clean and modern UI with interactive blur toggling.

📂 Project Structure
AutoBlurAI/
│
├── static/                # Static assets (images, CSS, JS)
│   ├── uploads/           # Uploaded files
│   └── processed/         # Blurred/processed outputs
│
├── templates/             # HTML templates
│   ├── index.html         # Homepage (Default & Custom blur options)
│   ├── custom.html        # Custom blur page
│   ├── default.html       # Default blur result page
│   └── thankyou.html      # Thank you / Success page
│
├── web.py                 # Flask backend
├── requirements.txt       # Dependencies
└── README.md              # Project documentation

⚙️ Installation
1️⃣ Clone the repo
git clone https://github.com/your-username/autoblur-ai.git
cd autoblur-ai

2️⃣ Create a virtual environment
python -m venv venv
source venv/bin/activate   # On Mac/Linux
venv\Scripts\activate      # On Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Install Tesseract OCR

Windows: Download from Tesseract OCR

Linux (Ubuntu):

sudo apt-get install tesseract-ocr


Mac:

brew install tesseract

▶️ Run the App
python web.py


Then open in browser:
👉 http://127.0.0.1:5000

🛠️ Tech Stack

Flask – Web framework

OpenCV – Image processing

Tesseract OCR – Text extraction

spaCy NLP – Detecting sensitive info

SQLite – Session/data storage

📸 Screenshots

(Add screenshots of your app here)

🙌 Contribution


Pull requests are welcome!
For major changes, please open an issue first to discuss what you’d like to change.

📜 License

This project is licensed under the MIT License.

<img width="1889" height="903" alt="1 (2)" src="https://github.com/user-attachments/assets/f93af4a4-c46e-4ef1-8748-4d000e6e62a1" />
<img width="1887" height="930" alt="2 (2)" src="https://github.com/user-attachments/assets/262f3016-7036-41a7-a2b6-0b8c70ea2aee" />
<img width="1873" height="912" alt="3 (2)" src="https://github.com/user-attachments/assets/938d3e90-138f-483d-bcf2-8fb2ef46c809" />
<img width="1740" height="917" alt="4 (2)" src="https://github.com/user-attachments/assets/c38d84a9-7459-44f1-96c4-5c89f1bd04e0" />
<img width="1888" height="930" alt="5 (2)" src="https://github.com/user-attachments/assets/054cda06-1486-444b-a6e7-ff2c287ae70d" />
<img width="1902" height="923" alt="6 (2)" src="https://github.com/user-attachments/assets/ccd8c611-ce7a-4dce-ab7f-4cec31f5591e" />
