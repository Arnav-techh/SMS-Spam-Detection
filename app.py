import pickle
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import string
from flask import Flask, request, render_template_string

# Download NLTK resources (one time)
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

app = Flask(__name__)
ps = PorterStemmer()

def transform_text(text):
    text = text.lower()
    text = nltk.word_tokenize(text)
    y = []
    for i in text:
        if i.isalnum():
            y.append(i)
    text = y[:]
    y.clear()
    for i in text:
        if i not in stopwords.words('english') and i not in string.punctuation:
            y.append(i)
    text = y[:]
    y.clear()
    for i in text:
        y.append(ps.stem(i))
    return " ".join(y)

# Load model files (tumhare same!)
with open('vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

@app.route('/', methods=['GET', 'POST'])
def home():
    prediction = None
    if request.method == 'POST':
        input_sms = request.form['message']
        transformed_sms = transform_text(input_sms)
        vector_input = vectorizer.transform([transformed_sms])
        result = model.predict(vector_input)[0]
        prediction = "SPAM 🛑" if result == 1 else "HAM ✅"
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>SMS Spam Detector - Arnav Kaneriya</title>
        <style>
            *{margin:0;padding:0;box-sizing:border-box;}
            body{font-family:'Segoe UI',sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;}
            .container{background:white;max-width:500px;width:100%;padding:40px;border-radius:25px;box-shadow:0 25px 50px rgba(0,0,0,0.2);text-align:center;}
            h1{background:linear-gradient(135deg,#a855f7,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:2.5em;margin-bottom:10px;}
            .subtitle{color:#64748b;font-size:1.2em;margin-bottom:30px;}
            input[type="text"]{width:100%;padding:18px;font-size:16px;border:2px solid #e2e8f0;border-radius:15px;margin-bottom:20px;box-shadow:0 5px 15px rgba(0,0,0,0.1);}
            button{background:linear-gradient(135deg,#10b981,#059669);color:white;padding:18px 40px;border:none;border-radius:15px;font-size:18px;font-weight:600;cursor:pointer;width:100%;transition:all 0.3s;}
            button:hover{transform:translateY(-2px);box-shadow:0 10px 25px rgba(16,185,129,0.4);}
            .result{margin-top:30px;padding:25px;border-radius:20px;font-size:28px;font-weight:800;text-align:center;min-height:80px;display:flex;align-items:center;justify-content:center;}
            .spam{background:linear-gradient(135deg,#fee2e2,#fecaca);color:#dc2626;border:3px solid #fca5a5;}
            .ham{background:linear-gradient(135deg,#ecfdf5,#bbf7d0);color:#059669;border:3px solid #a7f3d0;}
            .footer{margin-top:30px;padding:20px;background:#f8fafc;border-radius:15px;}
            .footer a{color:#a855f7;text-decoration:none;font-weight:600;}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📱 SMS Spam Detector</h1>
            <div class="subtitle">*Made by Arnav Kaneriya 👨🏻‍💻*</div>
            
            <form method="POST">
                <input type="text" name="message" placeholder="Enter SMS message to check..." required>
                <button type="submit">🔍 Predict Spam</button>
            </form>
            
            {% if prediction %}
            <div class="result {{ 'spam' if 'SPAM' in prediction else 'ham' }}">
                {{ prediction }}
            </div>
            {% endif %}
            
            <div class="footer">
                <p>⚡ ML Powered | 95%+ Accuracy</p>
                <a href="https://arnav-kaneriya-portfolio.vercel.app/">← View Portfolio</a>
            </div>
        </div>
    </body>
    </html>
    ''', prediction=prediction)

if __name__ == '__main__':
    app.run(debug=True)
