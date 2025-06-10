import csv
from datetime import datetime
from flask import Flask, render_template, request, url_for, send_file, jsonify
import os

app = Flask(__name__)

# --- Configuration ---
# Use an absolute path for the CSV file to prevent issues on cloud platforms
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(APP_ROOT, "survey_data.csv")

FIELDNAMES = [
    "timestamp", "smoking", "years_smoking", "secondhand_smoke", "pm25",
    "chronic_cough", "shortness_of_breath", "wheezing",
    "lung_disease_history", "family_cancer_history",
    "total_score", "risk_level", "recommendation", "name", "email"
]

# Ensure the CSV file has a header when the app starts
def initialize_csv():
    """Creates the CSV file with a header if it doesn't exist."""
    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            writer.writeheader()

@app.route("/", methods=["GET", "POST"])
def survey():
    """Handles the survey form submission and displays the survey page."""
    if request.method == "POST":
        # Collect answers from the form
        answers = {key: request.form.get(key, "") for key in FIELDNAMES}
        
        # Generate a unique timestamp to identify this specific submission
        timestamp = datetime.utcnow().isoformat(timespec='seconds') + 'Z'
        answers["timestamp"] = timestamp
        
        # Calculate total score
        score_keys = [
            "smoking", "years_smoking", "secondhand_smoke", "pm25",
            "chronic_cough", "shortness_of_breath", "wheezing",
            "lung_disease_history", "family_cancer_history"
        ]
        total_score = sum(int(answers[key] or 0) for key in score_keys)
        answers["total_score"] = total_score

        # Determine risk level and recommendation based on score
        if total_score <= 4:
            risk_level = "ความเสี่ยงต่ำ"
            recommendation = "แนะนำให้ติดตามด้วยตรวจสุขภาพประจำปีทั่วไป"
        elif total_score <= 9:
            risk_level = "ความเสี่ยงปานกลาง"
            recommendation = "ควรตรวจ CT Chest Low Dose หรือพบแพทย์เพื่อวางแผนดูแลต่อเนื่อง"
        else:
            risk_level = "ความเสี่ยงสูง"
            recommendation = "ควรพบแพทย์เฉพาะทางโรคปอดทันที และตรวจ CT Chest Low dose"
            
        answers["risk_level"] = risk_level
        answers["recommendation"] = recommendation

        # Save the initial data (without name/email) to CSV
        with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            writer.writerow(answers)

        # Render the result page, passing the unique timestamp along with other data
        return render_template(
            "result.html",
            timestamp=timestamp,
            total_score=total_score,
            risk_level=risk_level,
            recommendation=recommendation
        )

    # For GET requests, just show the survey page
    return render_template("survey.html")

@app.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name", "")
    email = request.form.get("email", "")

    # อ่านข้อมูลทั้งหมด
    rows = []
    with open(CSV_FILE, mode="r", newline="", encoding="utf-8") as csvfile:
        reader = list(csv.DictReader(csvfile))
        rows = reader

    # อัปเดตแถวล่าสุด
    if rows:
        rows[-1]["name"] = name
        rows[-1]["email"] = email

    # เขียนกลับลงไฟล์
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    return render_template("thankyou.html", name=name)

@app.route("/download")
def download():
    """Allows downloading the survey data CSV file."""
    try:
        return send_file(CSV_FILE, as_attachment=True)
    except FileNotFoundError:
        return "File not found.", 404

if __name__ == "__main__":
    initialize_csv()
    app.run(debug=True)
