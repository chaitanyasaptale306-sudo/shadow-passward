from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import numpy as np

from database import init_db, SessionLocal, User, SecurityLog
from security import encrypt_embedding, decrypt_embedding, generate_jwt, verify_jwt
from model_engine import GestureEngine
from voice import VoiceEngine
from behaviour import BehavioralTrustEngine

app = Flask(__name__)
CORS(app)

# Initialize Database
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    raw_landmarks = data.get('landmarks')
    raw_audio = data.get('audio_samples')

    if not all([username, email, raw_landmarks, raw_audio]):
        return jsonify({"status": "error", "message": "Missing biometric payload."}), 400

    db = SessionLocal()
    if db.query(User).filter_by(username=username).first():
        db.close()
        return jsonify({"status": "error", "message": "Identity already exists."}), 400

    # Extract Biometric Embeddings
    spatial_feat, vel_feat = GestureEngine.extract_features(raw_landmarks)
    voice_sig, is_live = VoiceEngine.extract_voice_signature(raw_audio)

    if spatial_feat is None or voice_sig is None:
        db.close()
        return jsonify({"status": "error", "message": "Biometric registration failed. Ensure clear motion and audio."}), 422

    # Serialize & Encrypt Biometric Models
    gesture_data = json.dumps({"spatial": spatial_feat.tolist(), "velocity": vel_feat.tolist()})
    voice_data = json.dumps(voice_sig.tolist())

    new_user = User(
        username=username,
        email=email,
        gesture_embedding=encrypt_embedding(gesture_data),
        voice_embedding=encrypt_embedding(voice_data)
    )

    db.add(new_user)
    db.commit()
    db.close()

    return jsonify({"status": "success", "message": f"Shadow profile for [{username}] registered securely."})

@app.route('/api/authenticate', methods=['POST'])
def authenticate():
    data = request.json
    username = data.get('username')
    raw_landmarks = data.get('landmarks')
    raw_audio = data.get('audio_samples')

    db = SessionLocal()
    user = db.query(User).filter_by(username=username).first()

    if not user:
        db.close()
        return jsonify({"status": "error", "message": "Target identity not found."}), 404

    # Decrypt User Biometrics
    stored_gesture = json.loads(decrypt_embedding(user.gesture_embedding))
    stored_voice = json.loads(decrypt_embedding(user.voice_embedding))

    # Calculate Individual Biometric Scores
    gesture_score = GestureEngine.compare_gestures(
        np.array(stored_gesture["spatial"]),
        np.array(stored_gesture["velocity"]),
        raw_landmarks
    )

    voice_score, liveness_passed = VoiceEngine.compare_voice(
        np.array(stored_voice),
        raw_audio
    )

    # Calculate Global Behavioral Trust Score
    trust_score = BehavioralTrustEngine.calculate_trust_score(
        gesture_score, voice_score, liveness_passed
    )

    status = "SUCCESS" if trust_score >= user.trust_threshold else "INTRUSION"

    # Log Security Attempt
    log = SecurityLog(
        username=username,
        trust_score=trust_score,
        status=status,
        gesture_score=gesture_score,
        voice_score=voice_score
    )
    db.add(log)
    db.commit()
    db.close()

    if status == "SUCCESS":
        token = generate_jwt(user.id, user.username)
        return jsonify({
            "status": "authenticated",
            "trust_score": trust_score,
            "gesture_score": round(gesture_score, 1),
            "voice_score": round(voice_score, 1),
            "token": token,
            "message": "Access Granted. Invisible Biometrics Verified."
        })
    else:
        return jsonify({
            "status": "denied",
            "trust_score": trust_score,
            "gesture_score": round(gesture_score, 1),
            "voice_score": round(voice_score, 1),
            "message": "Intrusion Alert: Biometric Match Below Security Threshold!"
        }), 401

@app.route('/api/logs/<username>', methods=['GET'])
def get_logs(username):
    db = SessionLocal()
    logs = db.query(SecurityLog).filter_by(username=username).order_by(SecurityLog.timestamp.desc()).limit(10).all()
    db.close()
    
    return jsonify({
        "logs": [{
            "timestamp": l.timestamp.strftime("%H:%M:%S"),
            "trust_score": l.trust_score,
            "status": l.status,
            "gesture": l.gesture_score,
            "voice": l.voice_score
        } for l in logs]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    