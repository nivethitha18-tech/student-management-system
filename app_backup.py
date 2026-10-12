from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)


# Create the student database
def create_database():
    connection = sqlite3.connect("students.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            name TEXT,
            department TEXT,
            year TEXT,
            marks INTEGER
        )
    """)

    connection.commit()
    connection.close()


# Home page
@app.route("/")
def home():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT department) FROM students")
    total_departments = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT year) FROM students")
    total_years = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(marks) FROM students")
    average_marks = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        total_students=total_students,
        total_departments=total_departments,
        total_years=total_years,
        average_marks=round(average_marks, 2) if average_marks is not None else 0
    )


# Add a new student
@app.route("/add-student", methods=["GET", "POST"])
def add_student():

    message = ""

    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()
        name = request.form.get("name", "").strip()
        department = request.form.get("department", "").strip()
        year = request.form.get("year", "").strip()
        marks_text = request.form.get("marks", "").strip()

        # Check for empty fields
        if not student_id or not name or not department or not year or not marks_text:
            message = "Error: All fields are required."

        else:
            # Validate marks
            try:
                marks = float(marks_text)

                if marks < 0 or marks > 100:
                    message = "Error: Marks must be between 0 and 100."

                else:
                    connection = sqlite3.connect("students.db")
                    cursor = connection.cursor()

                    # Check for duplicate Student ID
                    cursor.execute(
                        "SELECT id FROM students WHERE student_id = ?",
                        (student_id,)
                    )
                    existing_student = cursor.fetchone()

                    if existing_student:
                        message = "Error: This Student ID already exists."
                    else:
                        cursor.execute("""
                            INSERT INTO students
                            (student_id, name, department, year, marks)
                            VALUES (?, ?, ?, ?, ?)
                        """, (student_id, name, department, year, marks))

                        connection.commit()
                        message = "Student saved successfully!"

                    connection.close()

            except ValueError:
                message = "Error: Marks must be a valid number."

    return render_template(
    "add_student.html",
    message=message
)

# View all students
@app.route("/students")
def view_students():
    connection = sqlite3.connect("students.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    connection.close()

    return render_template("students.html", students=students)


# Search for a student using Student ID
@app.route("/search", methods=["GET", "POST"])
def search_student():
    results = []
    message = ""

    if request.method == "POST":
        search_query = request.form.get("search_query", "").strip().lower()

        if not search_query:
            message = "Please enter a search term."
        else:
            connection = sqlite3.connect("students.db")
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM students")
            all_students = cursor.fetchall()

            connection.close()

            # Linear search across student details
            for record in all_students:
                student_id = str(record[1]).lower()
                name = str(record[2]).lower()
                department = str(record[3]).lower()
                year = str(record[4]).lower()

                if (
                    search_query in student_id
                    or search_query in name
                    or search_query in department
                    or search_query in year
                ):
                    results.append(record)

            if not results:
                message = "No matching students found."

    return render_template(
        "search_student.html",
        results=results,
        message=message
    )


# Sort students by name from A to Z
@app.route("/sort")
def sort_students():
    connection = sqlite3.connect("students.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    connection.close()

    # Sorting algorithm
    students.sort(key=lambda student: student[2].lower())

    return render_template("students.html", students=students)
    

    # Search for a student using Binary Search
@app.route("/binary-search", methods=["GET", "POST"])
def binary_search_student():
    student = None
    message = ""

    if request.method == "POST":
        search_id = request.form["student_id"].strip()

        connection = sqlite3.connect("students.db")
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM students")
        all_students = cursor.fetchall()

        connection.close()

        # Sort students by Student ID before Binary Search
        all_students.sort(key=lambda record: record[1].lower())

        low = 0
        high = len(all_students) - 1

        while low <= high:
            mid = (low + high) // 2
            current_id = all_students[mid][1].lower()

            if current_id == search_id.lower():
                student = all_students[mid]
                break
            elif current_id < search_id.lower():
                low = mid + 1
            else:
                high = mid - 1

        if student is None:
            message = "Student not found."

    return render_template(
        "binary_search.html",
        student=student,
        message=message
    )



# Display application routes
print(app.url_map)


# Run the application
@app.route("/edit-student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    connection = sqlite3.connect("students.db")
    cursor = connection.cursor()

    if request.method == "POST":
        student_code = request.form["student_id"]
        name = request.form["name"]
        department = request.form["department"]
        year = request.form["year"]
        marks = request.form["marks"]

        cursor.execute(
            """UPDATE students
               SET student_id = ?, name = ?, department = ?, year = ?, marks = ?
               WHERE id = ?""",
            (student_code, name, department, year, marks, student_id)
        )

        connection.commit()
        connection.close()

        return redirect(url_for("view_students"))

    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()
    connection.close()

    if student is None:
        return "Student not found", 404

    return render_template("edit_student.html", student=student)


@app.route("/delete-student/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    connection = sqlite3.connect("students.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))

    connection.commit()
    connection.close()

    return redirect(url_for("view_students"))
if __name__ == "__main__":
    create_database()
    app.run(debug=True)