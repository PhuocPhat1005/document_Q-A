from flask import Flask, request, jsonify
from flask_cors import CORS
from detector import DocumentDetector

app = Flask("Document Q&A Detector")
CORS(app)

document_detector = DocumentDetector(api_key="AIzaSyDcvOAujrOnkbMIIXMdajEeG229xzZL0ds")


@app.route("/get_answer", methods=["POST"])
def get_answer():
    data = request.get_json()
    query = data["query"]
    documents = data["documents"]
    answer = document_detector.get_answer(query=query, documents=documents)
    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
