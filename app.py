from flask import Flask, render_template, request
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
    return render_template("index.html")


# Add a new student
@app.route("/add-student", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":
        student_id = request.form["student_id"]
        name = request.form["name"]
        department = request.form["department"]
        year = request.form["year"]
        marks = request.form["marks"]

        connection = sqlite3.connect("students.db")
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO students
            (student_id, name, department, year, marks)
            VALUES (?, ?, ?, ?, ?)
        """, (student_id, name, department, year, marks))

        connection.commit()
        connection.close()

        return "Student saved successfully!"

    return render_template("add_student.html")


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
    student = None
    message = ""

    if request.method == "POST":
        search_id = request.form["student_id"].strip()

        connection = sqlite3.connect("students.db")
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM students")
        all_students = cursor.fetchall()

        connection.close()

        # Linear search
        for record in all_students:
            if record[1] == search_id:
                student = record
                break

        if student is None:
            message = "Student not found."

    return render_template(
        "search_student.html",
        student=student,
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
if __name__ == "__main__":
    create_database()
    app.run(debug=True)