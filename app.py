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

    # Department chart data
    cursor.execute("""
        SELECT department, COUNT(*) AS student_count
        FROM students
        GROUP BY department
        ORDER BY department
    """)
    department_data = cursor.fetchall()

    # Student marks chart data
    cursor.execute("""
        SELECT name, marks
        FROM students
        ORDER BY name
    """)
    marks_data = cursor.fetchall()

    cursor.execute("SELECT AVG(marks) FROM students")
    average_marks = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        total_students=total_students,
        total_departments=total_departments,
        total_years=total_years,
        department_data=department_data,
                marks_data=marks_data,
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

@app.route("/search", methods=["GET", "POST"])
def search_student():
    search_results = []
    marks_results = []

    search_message = ""
    marks_message = ""

    search_query = ""
    marks_condition = ""
    mark_value = ""
    second_mark = ""

    if request.method == "POST":
        form_type = request.form.get("form_type", "")

        search_query = request.form.get(
            "search_query", ""
        ).strip().lower()

        marks_condition = request.form.get(
            "marks_condition", ""
        ).strip()

        mark_value = request.form.get(
            "mark_value", ""
        ).strip()

        second_mark = request.form.get(
            "second_mark", ""
        ).strip()

        connection = sqlite3.connect("students.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        all_students = cursor.fetchall()
        connection.close()

        # Advanced Student Search
        if form_type == "student_search":
            if not search_query:
                search_message = "Please enter a search term."
            else:
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
                        search_results.append(record)

                if not search_results:
                    search_message = "No matching students found."

        # Marks Filter
        elif form_type == "marks_filter":
            if not marks_condition:
                marks_message = "Please select a marks condition."

            else:
                try:
                    first = None
                    second = None

                    if marks_condition not in ("even", "odd"):
                        first = float(mark_value)

                        if not 0 <= first <= 100:
                            raise ValueError

                    if marks_condition in ("between", "outside"):
                        second = float(second_mark)

                        if not 0 <= second <= 100 or first > second:
                            raise ValueError

                    for record in all_students:
                        try:
                            marks = float(record[5])
                        except (ValueError, TypeError):
                            continue

                        if marks_condition == "equal" and marks == first:
                            marks_results.append(record)
                        elif marks_condition == "not_equal" and marks != first:
                            marks_results.append(record)
                        elif marks_condition == "greater" and marks > first:
                            marks_results.append(record)
                        elif marks_condition == "greater_equal" and marks >= first:
                            marks_results.append(record)
                        elif marks_condition == "less" and marks < first:
                            marks_results.append(record)
                        elif marks_condition == "less_equal" and marks <= first:
                            marks_results.append(record)
                        elif marks_condition == "between" and first <= marks <= second:
                            marks_results.append(record)
                        elif marks_condition == "outside" and not first <= marks <= second:
                            marks_results.append(record)
                        elif marks_condition == "at_least" and marks >= first:
                            marks_results.append(record)
                        elif marks_condition == "at_most" and marks <= first:
                            marks_results.append(record)
                        elif marks_condition == "zero_to" and 0 <= marks <= first:
                            marks_results.append(record)
                        elif marks_condition == "from_to_100" and first <= marks <= 100:
                            marks_results.append(record)
                        elif (
                            marks_condition == "even"
                            and marks.is_integer()
                            and int(marks) % 2 == 0
                        ):
                            marks_results.append(record)
                        elif (
                            marks_condition == "odd"
                            and marks.is_integer()
                            and int(marks) % 2 != 0
                        ):
                            marks_results.append(record)

                except (ValueError, TypeError):
                    marks_message = (
                        "Please enter valid marks between 0 and 100."
                    )

                if not marks_results and not marks_message:
                    marks_message = "No matching students found."

    return render_template(
        "search_student.html",
        search_results=search_results,
        marks_results=marks_results,
        search_message=search_message,
        marks_message=marks_message,
        search_query=search_query,
        marks_condition=marks_condition,
        mark_value=mark_value,
        second_mark=second_mark
    )
# Insertion Sort algorithm
def insertion_sort(students, key_function, reverse=False):
    students = list(students)

    for i in range(1, len(students)):
        current_student = students[i]
        current_key = key_function(current_student)
        j = i - 1

        if reverse:
            while j >= 0 and key_function(students[j]) < current_key:
                students[j + 1] = students[j]
                j -= 1
        else:
            while j >= 0 and key_function(students[j]) > current_key:
                students[j + 1] = students[j]
                j -= 1

        students[j + 1] = current_student

    return students


# Sort students by different fields
@app.route("/sort")
def sort_students():
    sort_by = request.args.get("by", "name")
    order = request.args.get("order", "asc")
    reverse = order == "desc"

    connection = sqlite3.connect("students.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    connection.close()

    # Select the field to sort
    if sort_by == "student_id":
        key_function = lambda student: str(student[1]).strip().lower()
    elif sort_by == "year":
        year_order = {
            "1": 1, "1st year": 1, "first year": 1,
            "2": 2, "2nd year": 2, "second year": 2,
            "3": 3, "3rd year": 3, "third year": 3,
            "4": 4, "4th year": 4, "fourth year": 4,
            "final year": 4
        }
        key_function = lambda student: year_order.get(
            str(student[4]).strip().lower(), 999
        )
    elif sort_by == "department":
        key_function = lambda student: str(student[3]).strip().lower()
    elif sort_by == "marks":
        key_function = lambda student: float(student[5])
    else:
        key_function = lambda student: str(student[2]).strip().lower()

    students = insertion_sort(students, key_function, reverse)

    return render_template(
        "students.html",
        students=students,
        sort_by=sort_by,
        order=order
    )
    

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


# Edit student details with validation
@app.route("/edit-student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    connection = sqlite3.connect("students.db")
    cursor = connection.cursor()

    if request.method == "POST":
        student_code = request.form.get("student_id", "").strip()
        name = request.form.get("name", "").strip()
        department = request.form.get("department", "").strip()
        year = request.form.get("year", "").strip()
        marks_text = request.form.get("marks", "").strip()

        message = ""

        # Check required fields
        if not student_code or not name or not department or not year or not marks_text:
            message = "Error: All fields are required."

        else:
            try:
                marks = float(marks_text)

                if marks < 0 or marks > 100:
                    message = "Error: Marks must be between 0 and 100."

                else:
                    # Prevent duplicate Student IDs
                    cursor.execute(
                        "SELECT id FROM students WHERE student_id = ? AND id != ?",
                        (student_code, student_id)
                    )
                    duplicate = cursor.fetchone()

                    if duplicate:
                        message = "Error: This Student ID already exists."
                    else:
                        cursor.execute(
                            """UPDATE students
                               SET student_id = ?, name = ?, department = ?,
                                   year = ?, marks = ?
                               WHERE id = ?""",
                            (student_code, name, department, year, marks, student_id)
                        )
                        connection.commit()
                        connection.close()
                        return redirect(url_for("view_students"))

            except ValueError:
                message = "Error: Marks must be a valid number."

        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        student = cursor.fetchone()
        connection.close()

        return render_template(
            "edit_student.html",
            student=student,
            message=message
        )

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