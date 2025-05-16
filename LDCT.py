import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Use DATABASE_URL from environment (Heroku sets this for Postgres)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///survey_data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model
class SurveyResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    smoking = db.Column(db.Integer)
    years_smoking = db.Column(db.Integer)
    secondhand_smoke = db.Column(db.Integer)
    pm25 = db.Column(db.Integer)
    chronic_cough = db.Column(db.Integer)
    shortness_of_breath = db.Column(db.Integer)
    wheezing = db.Column(db.Integer)
    lung_disease_history = db.Column(db.Integer)
    family_cancer_history = db.Column(db.Integer)
    total_score = db.Column(db.Integer)
    risk_level = db.Column(db.String(20))
    recommendation = db.Column(db.Text)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

@app.route("/", methods=["GET", "POST"])
def survey():
    if request.method == "POST":
        answers = {
            "smoking": int(request.form.get("smoking", 0)),
            "years_smoking": int(request.form.get("years_smoking", 0)),
            "secondhand_smoke": int(request.form.get("secondhand_smoke", 0)),
            "pm25": int(request.form.get("pm25", 0)),
            "chronic_cough": int(request.form.get("chronic_cough", 0)),
            "shortness_of_breath": int(request.form.get("shortness_of_breath", 0)),
            "wheezing": int(request.form.get("wheezing", 0)),
            "lung_disease_history": int(request.form.get("lung_disease_history", 0)),
            "family_cancer_history": int(request.form.get("family_cancer_history", 0))
        }
        total_score = sum(answers.values())

        if total_score <= 6:
            risk_level = "ความเสี่ยงต่ำ"
            recommendation = "แนะนำให้ติดตามด้วยตรวจสุขภาพประจำปีทั่วไป"
        elif 7 <= total_score <= 12:
            risk_level = "ความเสี่ยงปานกลาง"
            recommendation = "ควรตรวจ CT Chest Low Dose หรือพบแพทย์เพื่อวางแผนดูแลต่อเนื่อง"
        else:
            risk_level = "ความเสี่ยงสูง"
            recommendation = "ควรพบแพทย์เฉพาะทางโรคปอดทันที และตรวจ CT Chest Low dose"

        if "name" in request.form and "email" in request.form:
            contact_info = {
                "name": request.form.get("name", ""),
                "email": request.form.get("email", "")
            }
            record = SurveyResult(
                smoking=answers["smoking"],
                years_smoking=answers["years_smoking"],
                secondhand_smoke=answers["secondhand_smoke"],
                pm25=answers["pm25"],
                chronic_cough=answers["chronic_cough"],
                shortness_of_breath=answers["shortness_of_breath"],
                wheezing=answers["wheezing"],
                lung_disease_history=answers["lung_disease_history"],
                family_cancer_history=answers["family_cancer_history"],
                total_score=total_score,
                risk_level=risk_level,
                recommendation=recommendation,
                name=contact_info["name"],
                email=contact_info["email"]
            )
            db.session.add(record)
            db.session.commit()
            return render_template(
                "result.html",
                total_score=total_score,
                answers=answers,
                risk_level=risk_level,
                recommendation=recommendation,
                contact_info=contact_info
            )

        return render_template(
            "result.html",
            total_score=total_score,
            answers=answers,
            risk_level=risk_level,
            recommendation=recommendation,
            contact_info=None
        )

    return render_template("survey.html", total_score=None)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=False, host="0.0.0.0", port=5000)
