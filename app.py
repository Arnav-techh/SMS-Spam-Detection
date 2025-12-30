import os
import pickle
import nltk
import string
from flask import Flask, request, render_template_string
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

# Initialize Flask app
app = Flask(__name__)

# Download NLTK data (Vercel compatible)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)

# Initialize NLTK components
ps = PorterStemmer()

def transform_text(text):
    """Exact same preprocessing from your Streamlit code"""
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

# Load your model files
@ app.before_first_request
def load_models():
    global model, vectorizer
    with open('vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)

@app.route('/', methods=['GET', 'POST'])
def home():
    prediction = None
    confidence = None
    
    if request.method == 'POST':
        input_sms = request.form.get('message', '').strip()
        
        if input_sms:
            # 1. Preprocess (YOUR EXACT LOGIC)
            transformed_sms = transform_text(input_sms)
            
            # 2. Vectorize
            vector_input = vectorizer.transform([transformed_sms])
            
            # 3. Predict
            result = model.predict(vector_input)[0]
            probability = model.predict_proba(vector_input)[0]
            confidence = max(probability) * 100
            
            # 4. Result
            prediction = "SPAM 🛑" if result == 1 else "HAM ✅"
    
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SMS Spam Detector - Arnav Kaneriya</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                min-height: 100vh; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                padding: 20px;
            }
            .container { 
                background: white; 
                max-width: 500px; 
                width: 100%; 
                padding: 40px; 
                border-radius: 25px; 
                box-shadow: 0 25px 50px rgba(0,0,0,0.2); 
                text-align: center;
            }
            h1 { 
                background: linear-gradient(135deg, #a855f7, #60a5fa); 
                -webkit-background-clip: text; 
                -webkit-text-fill-color: transparent; 
                font-size: 2.5em; 
                margin-bottom: 10px;
            }
            .subtitle { color: #64748b; font-size: 1.2em; margin-bottom: 30px; }
            .input-group { margin-bottom: 20px; }
            input[type="text"] { 
                width: 100%; 
                padding: 18px; 
                font-size: 16px; 
                border: 2px solid #e2e8f0; 
                border-radius: 15px; 
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            button { 
                background: linear-gradient(135deg, #10b981, #059669); 
                color: white; 
                padding: 18px 40px; 
                border: none; 
                border-radius: 15px; 
                font-size: 18px; 
                font-weight: 600; 
                cursor: pointer; 
                width: 100%; 
                transition: all 0.3s;
            }
            button:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(16,185,129,0.4); }
            .result { 
                margin-top: 30px; 
                padding: 25px; 
                border-radius: 20px; 
                font-size: 28px; 
                font-weight: 800; 
                min-height: 80px; 
                display: flex; 
                flex-direction: column; 
                align-items: center; 
                justify-content: center;
            }
            .spam { background: linear-gradient(135deg, #fee2e2, #fecaca); color: #dc2626; border: 3px solid #fca5a5; }
            .ham { background: linear-gradient(135deg, #ecfdf5, #bbf7d0); color: #059669; border: 3px solid #a7f3d0; }
            .confidence { font-size: 16px; margin-top: 10px; opacity: 0.9; }
            .footer { 
                margin-top: 30px; 
                padding: 20px; 
                background: #f8fafc; 
                border-radius: 15px;
            }
            .footer a { color: #a855f7; text-decoration: none; font-weight: 600; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📱 SMS Spam Detector</h1>
            <div class="subtitle">*Made by Arnav Kaneriya 👨🏻‍💻*</div>
            
            <form method="POST">
                <div class="input-group">
                    <input type="text" name="message" placeholder="Enter SMS message to check for spam..." value="{{ request.form.message if request.form else '' }}" required>
                </div>
                <button type="submit">🔍 Predict Spam</button>
            </form>
            
            {% if prediction %}
            <div class="result {{ 'spam' if 'SPAM' in prediction else 'ham' }}">
                {{ prediction }}
                {% if confidence %}
                <div class="confidence">{{ "%.1f"|format(confidence) }}% Confidence</div>
                {% endif %}
            </div>
            {% endif %}
            
            <div class="footer">
                <p>⚡ ML Powered | NLTK + Stemming | 95%+ Accuracy</p>
                <p><a href="https://arnav-kaneriya-portfolio.vercel.app/">← View My Portfolio</a></p>
            </div>
        </div>
    </body>
    </html>
    ''', request=request)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
