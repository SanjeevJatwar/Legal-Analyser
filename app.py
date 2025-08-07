from flask import Flask, request, jsonify
from retrieval_model import get_insurance_answer

app = Flask(_name_)

@app.route("/api/v1/hackrx/run", methods=["POST"])
def hackrx_webhook():
    try:
        data = request.get_json()
        query = data.get("query", "")
        result = get_insurance_answer(query)
        return jsonify({
            "status": "success",
            "result": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if _name_ == "_main_":