from flask import Flask, jsonify, request

app = Flask(__name__)

# صفحة رئيسية
@app.route('/')
def home():
    return jsonify({"message": "API يعمل بنجاح!"})

# مثال endpoint لإرسال بيانات
@app.route('/echo', methods=['POST'])
def echo():
    data = request.json
    return jsonify({"you_sent": data})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)