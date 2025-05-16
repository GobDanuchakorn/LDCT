import csv
from datetime import datetime
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def survey():
    if request.method == "POST":
        # รับข้อมูลจากฟอร์ม
        answers = {
            "timestamp": datetime.utcnow().isoformat(),
            "smoking": request.form.get("smoking", ""),
            "years_smoking": request.form.get("years_smoking", ""),
            "secondhand_smoke": request.form.get("secondhand_smoke", ""),
            "pm25": request.form.get("pm25", ""),
            "chronic_cough": request.form.get("chronic_cough", ""),
            "shortness_of_breath": request.form.get("shortness_of_breath", ""),
            "wheezing": request.form.get("wheezing", ""),
            "lung_disease_history": request.form.get("lung_disease_history", ""),
            "family_cancer_history": request.form.get("family_cancer_history", ""),
            "name": request.form.get("name", ""),
            "email": request.form.get("email", "")
        }

        # คำนวณคะแนนรวม
        total_score = sum(int(answers[key]) for key in [
            "smoking", "years_smoking", "secondhand_smoke", "pm25",
            "chronic_cough", "shortness_of_breath", "wheezing",
            "lung_disease_history", "family_cancer_history"
        ] if answers[key].isdigit())

        # ประเมินความเสี่ยง
        if total_score <= 6:
            risk_level = "ความเสี่ยงต่ำ"
            recommendation = "แนะนำให้ติดตามด้วยตรวจสุขภาพประจำปีทั่วไป"
        elif 7 <= total_score <= 12:
            risk_level = "ความเสี่ยงปานกลาง"
            recommendation = "ควรตรวจ CT Chest Low Dose หรือพบแพทย์เพื่อวางแผนดูแลต่อเนื่อง"
        else:
            risk_level = "ความเสี่ยงสูง"
            recommendation = "ควรพบแพทย์เฉพาะทางโรคปอดทันที และตรวจ CT Chest Low dose"

        # เพิ่มข้อมูลลง answers
        answers["total_score"] = total_score
        answers["risk_level"] = risk_level
        answers["recommendation"] = recommendation

        # บันทึกข้อมูลลงไฟล์ CSV
        with open("survey_data.csv", mode="a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=list(answers.keys()))
            # เขียน header ถ้าไฟล์ว่าง
            if csvfile.tell() == 0:
                writer.writeheader()
            writer.writerow(answers)

        # ส่งข้อมูลไปแสดงผลหน้า result.html (หรือจะแสดงในหน้านี้เลยก็ได้)
        return render_template(
            "result.html",
            total_score=total_score,
            answers=answers,
            risk_level=risk_level,
            recommendation=recommendation,
            contact_info={"name": answers["name"], "email": answers["email"]}
        )

    # GET: แสดงฟอร์ม
    return render_template("survey.html", total_score=None)

if __name__ == "__main__":
    app.run(debug=True)
