from flask import Flask, request, render_template_string
import pickle
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

app = Flask(__name__)

# Super lightweight preprocessing
def preprocess(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
    return text.strip()

# Load models (lazy load)
model = None
vectorizer = None

def load_models():
    global model, vectorizer
    try:
        vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))
        model = pickle.load(open('model.pkl', 'rb'))
    except:
        pass

@app.route('/', methods=['GET', 'POST'])
def home():
    global model, vectorizer
    if model is None:
        load_models()
    
    prediction = None
    if request.method == 'POST':
        sms = request.form['message']
        processed = preprocess(sms)
        if model and vectorizer:
            vec = vectorizer.transform([processed])
            pred = model.predict(vec)[0]
            prediction = "SPAM 🛑" if pred == 1 else "HAM ✅"
    
    return render_template_string('''
<!DOCTYPE html>
<html><head><title>SMS Spam Detector</title>
<meta name="viewport" content="width=device-width">
<style>body{margin:0;padding:20px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh}
.container{background:#fff;max-width:500px;width:100%;padding:40px;border-radius:20px;box-shadow:0 20px 40px rgba(0,0,0,0.1);text-align:center}
h1{font-size:2.5em;background:linear-gradient(135deg,#a855f7,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0 0 20px}
input{width:100%;padding:15px;font-size:16px;border:2px solid #e5e7eb;border-radius:12px;margin:20px 0;box-sizing:border-box}
button{width:100%;padding:15px;background:linear-gradient(135deg,#10b981,#059669);color:white;border:none;border-radius:12px;font-size:18px;font-weight:600;cursor:pointer;transition:all 0.3s}
button:hover{transform:translateY(-2px);box-shadow:0 10px 25px rgba(16,185,129,0.4)}
.result{margin-top:30px;padding:20px;border-radius:15px;font-size:24px;font-weight:800}
.spam{background:#fee2e2;color:#dc2626;border:2px solid #fca5a5}
.ham{background:#ecfdf5;color:#059669;border:2px solid #a7f3d0}
.footer{margin-top:30px;font-size:14px;color:#6b7280}
a{color:#a855f7;text-decoration:none}</style></head>
<body><div class="container">
<h1>📱 SMS Spam Detector</h1>
<p style="color:#6b7280;font-size:1.1em;margin-bottom:20px">Arnav Kaneriya 👨🏻‍💻 | ML Powered</p>
<form method="POST">
<input type="text" name="message" placeholder="Enter SMS message to check..." required>
<button type="submit">🔍 Predict Spam</button></form>
{% if prediction %}<div class="result {{'spam' if 'SPAM' in prediction else 'ham'}}">{{ prediction }}</div>{% endif %}
<div class="footer">
<p>⚡ 95%+ Accuracy | <a href="https://arnav-kaneriya-portfolio.vercel.app/">Portfolio</a></p>
</div></div></body></html>
    ''', **locals())

if __name__ == '__main__':
    app.run()
