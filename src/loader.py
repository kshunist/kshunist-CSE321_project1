import csv

def load_data(csv_path):
    records = []
    key_to_rid = {}

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for rid, row in enumerate(reader):
            student_id = int(row["Student ID"])

            record = {
                "student_id": student_id,
                "name": row["Name"],
                "gender": row["Gender"],
                "gpa": float(row["GPA"]),
                "height": float(row["Height"]),
                "weight": float(row["Weight"]),
            }

            records.append(record)
            key_to_rid[student_id] = rid

    return records, key_to_rid