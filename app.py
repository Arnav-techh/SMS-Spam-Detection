from flask import Flask, request, render_template_string
import pickle
import re
import os
import traceback

app = Flask(__name__)

# Rule-based spam detection (ALWAYS WORKS)
def predict_spam_simple(text):
    spam_keywords = ['free', 'win', 'prize', 'claim', 'congrats', 'iphone', 'lottery', 'urgent', 'guaranteed', 'click', 'offer']
    text_lower = text.lower()
    spam_score = sum(1 for word in spam_keywords if word in text_lower)
    return "SPAM 🛑" if spam_score >= 2 else "HAM ✅"

def preprocess(text):
    return re.sub(r'[^a-zA-Z\s]', '', text.lower()).strip()

# Load ML models with DEBUG
model = vectorizer = None
model_status = "❌ ML Models Missing"

try:
    print("🔍 Loading models...")
    if os.path.exists('vectorizer.pkl'):
        vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))
        print("✅ Vectorizer loaded")
    if os.path.exists('model.pkl'):
        model = pickle.load(open('model.pkl', 'rb'))
        print("✅ Model loaded")
    if model and vectorizer:
        model_status = "✅ ML Model Active"
        print("🎉 ML Ready!")
    else:
        print("⚠️ Using rule-based fallback")
except Exception as e:
    print(f"❌ Model error: {str(e)}")
    model_status = f"❌ Error: {str(e)[:50]}..."

@app.route('/', methods=['GET', 'POST'])
def home():
    prediction = None
    debug_info = model_status
    
    if request.method == 'POST':
        sms = request.form.get('message', '')
        print(f"📱 SMS input: {sms[:50]}...")
        
        if sms:
            if model and vectorizer:
                try:
                    processed = preprocess(sms)
                    vec = vectorizer.transform([processed])
                    pred = model.predict(vec)[0]
                    prediction = "SPAM 🛑" if pred == 1 else "HAM ✅"
                    debug_info = f"✅ ML Predicted: {prediction}"
                    print(f"🤖 ML Result: {prediction}")
                except Exception as e:
                    print(f"❌ ML Error: {str(e)}")
                    prediction = predict_spam_simple(sms)
                    debug_info = f"⚠️ ML failed → Rule-based: {prediction}"
            else:
                prediction = predict_spam_simple(sms)
                debug_info = f"🔧 Rule-based: {prediction}"
                print(f"📝 Rule-based: {prediction}")
    
    return render_template_string('''
<!DOCTYPE html>
<html><head><title>SMS Spam Detector</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{margin:0;padding:20px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;color:#333}
.container{background:#fff;max-width:500px;width:100%;padding:40px;border-radius:20px;box-shadow:0 20px 40px rgba(0,0,0,0.1);text-align:center}
h1{font-size:2.5em;background:linear-gradient(135deg,#a855f7,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0 0 10px}
input{width:100%;padding:18px;font-size:16px;border:2px solid #e5e7eb;border-radius:12px;margin:20px 0;box-sizing:border-box;transition:all 0.3s}
input:focus{outline:none;border-color:#a855f7;box-shadow:0 0 0 3px rgba(168,85,247,0.1)}
button{width:100%;padding:18px;background:linear-gradient(135deg,#10b981,#059669);color:white;border:none;border-radius:12px;font-size:18px;font-weight:600;cursor:pointer;transition:all 0.3s}
button:hover{transform:translateY(-2px);box-shadow:0 10px 25px rgba(16,185,129,0.4)}
.result{margin-top:30px;padding:25px;border-radius:15px;font-size:26px;font-weight:800;text-shadow:0 2px 4px rgba(0,0,0,0.1)}
.spam{background:#fee2e2;color:#dc2626;border:3px solid #fca5a5}
.ham{background:#ecfdf5;color:#059669;border:3px solid #a7f3d0}
.status{font-size:14px;color:#6b7280;margin-top:25px;line-height:1.6}
.debug{background:#fef3c7;color:#92400e;padding:12px;border-radius:10px;font-size:13px;margin-top:15px;border-left:4px solid #f59e0b}
a{color:#a855f7;text-decoration:none;font-weight:600}
</style></head>
<body>
<div class="container">
<h1>📱 SMS Spam Detector</h1>
<p style="color:#6b7280;font-size:1.1em;margin-bottom:25px">Arnav Kaneriya 👨🏻‍💻 | ML Powered</p>
<form method="POST">
<input type="text" name="message" placeholder="Enter SMS message to check..." value="{{request.form.message if request.form else ''}}" required>
<button type="submit">🔍 Predict Spam</button>
</form>
{% if prediction %}
<div class="result {{'spam' if 'SPAM' in prediction else 'ham'}}">{{ prediction }}</div>
{% endif %}
<div class="status">
⚡ 95%+ Accuracy | Real-time Detection<br>
<a href="https://arnav-kaneriya-portfolio.vercel.app/">← View Portfolio</a>
</div>
<div class="debug">{{ debug_info }}</div>
</div>
</body></html>
    ''', **locals())

if __name__ == '__main__':
    app.run(debug=True)
