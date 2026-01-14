from flask import Flask, render_template, request, redirect, Response
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET", "POST"])
def home():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            roll TEXT,
            course TEXT
        )
    """)
    conn.commit()

    if request.method == "POST":
        name = request.form["name"]
        roll = request.form["roll"]
        course = request.form["course"]
        cursor.execute(
            "INSERT INTO students (name, roll, course) VALUES (?, ?, ?)",
            (name, roll, course)
        )
        conn.commit()
        return redirect("/")

    query = request.args.get("query", "")
    sort_by = request.args.get("sort_by", "id")
    sort_order = request.args.get("sort_order", "asc")

    if query:
        cursor.execute(f"""
            SELECT * FROM students
            WHERE name LIKE ? OR roll LIKE ?
            ORDER BY {sort_by} {sort_order}
        """, (f"%{query}%", f"%{query}%"))
    else:
        cursor.execute(f"SELECT * FROM students ORDER BY {sort_by} {sort_order}")

    students = cursor.fetchall()
    conn.close()
    total = len(students)
    return render_template("index.html", students=students, query=query, sort_by=sort_by, sort_order=sort_order, total=total)

@app.route("/delete/<int:id>")
def delete_student(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        roll = request.form["roll"]
        course = request.form["course"]
        cursor.execute(
            "UPDATE students SET name=?, roll=?, course=? WHERE id=?",
            (name, roll, course, id)
        )
        conn.commit()
        conn.close()
        return redirect("/")

    cursor.execute("SELECT * FROM students WHERE id = ?", (id,))
    student = cursor.fetchone()
    conn.close()
    return render_template("edit.html", student=student)

@app.route("/export_csv")
def export_csv():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()

    csv_data = "ID,Name,Roll,Course\n"
    for s in students:
        csv_data += f"{s['id']},{s['name']},{s['roll']},{s['course']}\n"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=students.csv"}
    )

if __name__ == "__main__":
    app.run(debug=True)
