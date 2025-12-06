from flask import Flask, request, jsonify
import os
import pymqi

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "IBM MQ Web Demo is running!", 200

@app.route("/send", methods=["POST"])
def send_message():
    data = request.json
    msg = data.get("message", "")

    mq_host = os.environ["MQ_HOST"]
    mq_port = os.environ["MQ_PORT"]
    mq_channel = os.environ["MQ_CHANNEL"]
    mq_user = os.environ["MQ_USER"]
    mq_password = os.environ["MQ_PASSWORD"]
    mq_qmgr = os.environ["MQ_QMGR"]
    request_q = os.environ["REQUEST_Q"]
    response_q = os.environ["RESPONSE_Q"]

    conn_info = f"{mq_host}({mq_port})"

    try:
        qmgr = pymqi.connect(mq_qmgr, mq_channel, conn_info, mq_user, mq_password)

        req = pymqi.Queue(qmgr, request_q)
        req.put(msg)
        req.close()

        resp = pymqi.Queue(qmgr, response_q)
        try:
            r = resp.get(wait=5000)
        except:
            r = "No response received within 5 seconds."
        resp.close()

        qmgr.disconnect()
        return jsonify({"response": r}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
