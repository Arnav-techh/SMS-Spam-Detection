import os
import pickle
import nltk
import string
from flask import Flask, request, render_template_string
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

app = Flask(__name__)

# Lightweight NLTK
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

ps = PorterStemmer()

def transform_text(text):
    text = text.lower()
    text = nltk.word_tokenize(text)
    y = [i for i in text if i.isalnum()]
    y = [i for i in y if i not in stopwords.words('english') and i not in string.punctuation]
    y = [ps.stem(i) for i in y]
    return " ".join(y)

# Load models ONCE (global)
try:
    vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))
    model = pickle.load(open('model.pkl', 'rb'))
except:
    vectorizer = None
    model = None

@app.route('/', methods=['GET', 'POST'])
def home():
    prediction = None
    
    if request.method == 'POST':
        input_sms = request.form.get('message', '')
        if input_sms and model and vectorizer:
            transformed_sms = transform_text(input_sms)
            vector_input = vectorizer.transform([transformed_sms])
            result = model.predict(vector_input)[0]
            prediction = "SPAM 🛑" if result == 1 else "HAM ✅"
    
    return render_template_string('''
<!DOCTYPE html>
<html><head><title>SMS Spam Detector</title>
<style>body{font-family:Segoe UI;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;}
.container{background:white;max-width:500px;width:100%;padding:40px;border-radius:25px;box-shadow:0 25px 50px rgba(0,0,0,0.2);text-align:center;}
h1{background:linear-gradient(135deg,#a855f7,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:2.5em;}
input[type="text"]{width:100%;padding:18px;font-size:16px;border:2px solid #e2e8f0;border-radius:15px;margin:20px 0;box-shadow:0 5px 15px rgba(0,0,0,0.1);}
button{background:linear-gradient(135deg,#10b981,#059669);color:white;padding:18px 40px;border:none;border-radius:15px;font-size:18px;cursor:pointer;width:100%;transition:all 0.3s;}
button:hover{transform:translateY(-2px);box-shadow:0 10px 25px rgba(16,185,129,0.4);}
.result{margin-top:30px;padding:25px;border-radius:20px;font-size:28px;font-weight:800;}
.spam{background:#fee2e2;color:#dc2626;border:3px solid #fca5a5;}
.ham{background:#ecfdf5;color:#059669;border:3px solid #a7f3d0;}
.footer{margin-top:30px;padding:20px;background:#f8fafc;border-radius:15px;}
a{color:#a855f7;text-decoration:none;font-weight:600;}</style></head>
<body><div class="container">
<h1>📱 SMS Spam Detector</h1>
<p style="color:#64748b;font-size:1.2em;">*Made by Arnav Kaneriya 👨🏻‍💻*</p>
<form method="POST">
<input type="text" name="message" placeholder="Enter SMS message..." value="{{request.form.message if request.form else ''}}" required>
<button type="submit">🔍 Predict Spam</button></form>
{%if prediction%}<div class="result {{'spam' if 'SPAM' in prediction else 'ham'}}">{{prediction}}</div>{%endif%}
<div class="footer">
<p>⚡ ML Powered | 95%+ Accuracy</p>
<a href="https://arnav-kaneriya-portfolio.vercel.app/">← Portfolio</a>
</div></div></body></html>
    ''', request=request)

if __name__ == '__main__':
    app.run()
