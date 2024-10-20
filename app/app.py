from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid
import random
import string
import os
from flask import jsonify
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "ABC"

# MySQL configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "drawit_db"

mysql = MySQL(app)

# Folder to store uploaded drawings
UPLOAD_FOLDER = "static/files_upload/drawings"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# Folder to store uploaded drawings
BOM_UPLOAD_FOLDER = "static/files_upload/bom"
app.config["BOM_UPLOAD_FOLDER"] = BOM_UPLOAD_FOLDER
# Folder to store uploaded drawings
REFERENCE_UPLOAD_FOLDER = "static/files_upload/reference"
app.config["REFERENCE_UPLOAD_FOLDER"] = REFERENCE_UPLOAD_FOLDER

# Flask-Mail configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = "drawit.sidekick@gmail.com"
app.config["MAIL_PASSWORD"] = "izounnemalhaxpvt"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

mail = Mail(app)

semail = "drawit.sidekick@gmail.com"


# Header Remove when in deployment
@app.after_request
def add_header(response):
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response


# Route for the registration page
@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("home/index.html")


# Login Required Function
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "email" not in session:
            flash("You need to be logged in to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


# Route for the registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        idnum = request.form["idnum"]
        designation = request.form["designation"]

        # Check if user already exists
        cursor = mysql.connection.cursor()

        # Check if email already exists
        cursor.execute("SELECT * FROM user WHERE Email = %s", [email])
        email_account = cursor.fetchone()

        if email_account:
            flash("Email already registered!", "text-danger")
            cursor.close()
            return render_template("auth/register.html")

        # Check if idnum already exists
        cursor.execute("SELECT * FROM user WHERE DrafterID = %s", [idnum])
        idnum_account = cursor.fetchone()

        if idnum_account:
            flash("Corporate ID number already exists!", "text-danger")
            cursor.close()
            return render_template("auth/register.html")

        else:
            # Generate OTP
            otp = "".join(random.choices(string.digits, k=6))
            session["otp"] = otp
            session["name"] = name
            session["email"] = email
            session["idnum"] = idnum
            session["designation"] = designation

            # Send OTP via email
            try:
                msg = Message("OTP for Registration", sender=semail, recipients=[email])
                msg.body = f"Your OTP for registration is {otp}"
                mail.send(msg)

                flash("An OTP has been sent to your email.", "text-info")
                return redirect(url_for("verify_otp"))
            except Exception as e:
                flash(f"Error sending email: {str(e)}", "text-danger")

    return render_template("auth/register.html")


# Route for OTP verification page
@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        otp = request.form["otp"]

        if otp == session.get("otp"):
            name = session.get("name")
            email = session.get("email")
            idnum = session.get("idnum")
            designation = session.get("designation")

            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO user (Name, Email, DrafterID, Designation, DateCreated) VALUES (%s, %s, %s, %s, NOW())",
                (name, email, idnum, designation),
            )
            mysql.connection.commit()
            cursor.close()

            session.pop("otp", None)
            session.pop("name", None)
            session.pop("email", None)
            session.pop("idnum", None)
            session.pop("designation", None)

            flash("Registration successful!", "success")
            return redirect(url_for("login"))
        else:
            flash("Invalid OTP. Please try again.", "danger")

    return render_template("auth/verify_otp.html")


# Route for the login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]

        # Check if user exists
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE Email = %s", [email])
        account = cursor.fetchone()

        if account:
            # Generate OTP
            otp = "".join(random.choices(string.digits, k=6))
            session["otp"] = otp
            session["email"] = email

            # Send OTP via email
            try:
                msg = Message("OTP for Login", sender=semail, recipients=[email])
                msg.body = f"Your OTP for login is {otp}"
                mail.send(msg)

                flash(f"An OTP has been sent to your email: <strong style='color: black;'>{session['email']}</strong> .", "text-info")
                return redirect(url_for("verify_login_otp"))
            except Exception as e:
                flash(f"Error sending email: {str(e)}", "text-danger")
        else:
            flash("Email not registered!", "text-danger")

    return render_template("auth/login.html")


# Route for OTP verification page for login
@app.route("/verify_login_otp", methods=["GET", "POST"])
def verify_login_otp():
    if request.method == "POST":
        otp = request.form["otp"]

        if otp == session.get("otp"):
            session.pop("otp", None)
            email = session.get("email")

            # Fetch all required fields from the database
            cursor = mysql.connection.cursor()
            cursor.execute(
                "SELECT DrafterID, Name, Email, ProfileImage, Designation FROM user WHERE Email = %s",
                [email],
            )
            account = cursor.fetchone()

            if account:
                # Access each element of the tuple
                employee_id = account[0]
                name = account[1]
                email = account[2]
                profile_image = account[3]
                designation = account[4]

                # Set session variables
                session["employee_id"] = employee_id
                session["name"] = name
                session["email"] = email
                session["profile_image"] = profile_image
                session["designation"] = designation
            else:
                # Set default values if the account is not found
                session["employee_id"] = "N/A"
                session["name"] = "User"
                session["email"] = email
                session["profile_image"] = "default.png"
                session["designation"] = "N/A"

            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid OTP. Please try again.", "danger")

    return render_template("auth/verify_login_otp.html")


# Logout
@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("login"))


# Route for the dashboard (protected page)
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():

    # employee_id = session.get('employee_id')  # Assuming employee_id is stored in session
    employee_id = session.get("employee_id")
    if not employee_id:
        flash("No employee ID found in session.", "warning")
        return redirect(url_for("login"))

    # Fetch data from the drawing table
    cursor = mysql.connection.cursor()
    query = """
    SELECT DrawingID, Title, DrawingNumber, DATE_FORMAT(DateCreated, '%%d-%%m-%%Y') as DateCreated, 
           DATE_FORMAT(ReleaseDate, '%%d-%%m-%%Y') as ReleaseDate 
    FROM drawing 
    WHERE DrafterID = %s
    """
    cursor.execute(query, (employee_id,))
    drawings = cursor.fetchall()
    cursor.close()
    return render_template("dashboard/user.html", drawings=drawings)


# Route for the user (protected page)
@app.route("/user/<user_id>", methods=["GET", "POST"])
@login_required
def user_view(user_id):

    # employee_id = session.get('employee_id')  # Assuming employee_id is stored in session
    employee_id = session.get("employee_id")
    if not employee_id:
        flash("No employee ID found in session.", "warning")
        return redirect(url_for("login"))

    # Fetch data from the drawing table
    cursor = mysql.connection.cursor()
    query = """
    SELECT * 
    FROM user 
    WHERE DrafterID = %s
    """
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    cursor.close()

    # Fetch data from the drawing table
    cursor = mysql.connection.cursor()
    query = """
    SELECT DrawingID, Title, DrawingNumber, DATE_FORMAT(DateCreated, '%%d-%%m-%%Y') as DateCreated, 
           DATE_FORMAT(ReleaseDate, '%%d-%%m-%%Y') as ReleaseDate 
    FROM drawing 
    WHERE DrafterID = %s
    """
    cursor.execute(query, (user_id,))
    drawings = cursor.fetchall()
    cursor.close()
    return render_template("dashboard/user_view.html", drawings=drawings, user=user)


# API for userid fetch from user
@app.route("/get_user_ids", methods=["GET"])
@login_required
def get_user_ids():
    query = request.args.get("query")
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT DrafterID FROM user WHERE DrafterID LIKE %s", (f"%{query}%",)
    )
    user_ids = cursor.fetchall()
    cursor.close()

    # Extract user IDs from tuples
    user_ids = [user_id[0] for user_id in user_ids]

    return jsonify(user_ids)


@app.route("/drawing_upload", methods=["GET", "POST"])
@login_required
def drawing_upload():
    if request.method == "POST":
        # Fetch form data
        drafter_id = session["employee_id"]
        title = request.form.get("title")
        drawing_number = request.form.get("drawing_number")
        client_name = request.form.get("client_name")
        project_location = request.form.get("project_location")
        project_code = request.form.get("project_code")
        feedback_authority_id = request.form.get("feedback_authority_id")
        reference = request.form.get("reference")
        build_of_material = request.form.get("build_of_material")

        # Handle file uploads
        drawing_file = request.files["drawing_location"]
        bom_file = request.files["build_of_material"]
        reference_file = request.files["reference"]

        drawing_path = ""
        bom_path = ""
        reference_path = ""

        if drawing_file:
            drawing_filename = f"{session['employee_id']}_{uuid.uuid4().hex}_{secure_filename(drawing_file.filename)}"
            drawing_path = os.path.join(app.config["UPLOAD_FOLDER"], drawing_filename)
            drawing_file.save(drawing_path)

        if bom_file:
            bom_filename = f"{session['employee_id']}_{uuid.uuid4().hex}_{secure_filename(bom_file.filename)}"
            bom_path = os.path.join(app.config["BOM_UPLOAD_FOLDER"], bom_filename)
            bom_file.save(bom_path)

        if reference_file:
            reference_filename = f"{session['employee_id']}_{uuid.uuid4().hex}_{secure_filename(reference_file.filename)}"
            reference_path = os.path.join(
                app.config["REFERENCE_UPLOAD_FOLDER"], reference_filename
            )
            reference_file.save(reference_path)

            # Store the file path in the database
            cursor = mysql.connection.cursor()
            cursor.execute(
                """
                INSERT INTO drawing (DrafterID, DrawingLocation, Title, DrawingNumber, ClientName, ProjectLocation, ProjectCode, FeedbackAuthorityID, Reference, BuildOfMaterial, DateCreated)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    drafter_id,
                    drawing_path,
                    title,
                    drawing_number,
                    client_name,
                    project_location,
                    project_code,
                    feedback_authority_id,
                    reference_path,
                    bom_path,
                    datetime.now(),
                ),
            )

            mysql.connection.commit()
            cursor.close()

            flash("Drawing successfully uploaded!", "success")

        else:
            flash("Failed to upload drawing.", "danger")

        return redirect(url_for("dashboard"))

    return render_template("dashboard/drawing_upload.html")


@app.route("/drawing_detail/<int:drawing_id>")
@login_required
def drawing_view(drawing_id):

    cursor = mysql.connection.cursor()
    query = """
    SELECT * FROM drawing WHERE DrawingID = %s
    """
    cursor.execute(query, (drawing_id,))
    drawing = cursor.fetchone()
    cursor.close()

    cursor = mysql.connection.cursor()
    query = """
    SELECT * FROM feedback WHERE DrawingID = %s
    """
    cursor.execute(query, (drawing_id,))
    feedback = cursor.fetchall()
    cursor.close()

    cursor = mysql.connection.cursor()
    query = """
    SELECT * FROM releaserevision WHERE DrawingID = %s
    """
    cursor.execute(query, (drawing_id,))
    review = cursor.fetchall()
    cursor.close()

    if drawing is None:
        flash("Drawing not found.", "warning")
        return redirect(url_for("dashboard"))

    return render_template("dashboard/drawing_detail.html", drawing=drawing, feedback=feedback)


@app.route("/drawing_delete/<int:drawing_id>", methods=["GET", "POST"])
@login_required
def drawing_delete(drawing_id):
    if request.method == "POST" and request.form.get("delete") == "DELETE":
        try:
            cursor = mysql.connection.cursor()
            query = """
            DELETE FROM drawing WHERE DrawingID = %s
            """
            cursor.execute(query, (drawing_id,))
            mysql.connection.commit()
            cursor.close()
            flash("Drawing deleted successfully.", "success")
            return redirect(url_for("dashboard"))
        except MySQLdb.Error as e:
            mysql.connection.rollback()
            flash(f"Unable to delete drawing. Error: {str(e)}", "danger")
            return redirect(url_for("dashboard"))
    else:
        flash("Enter DELETE for deleting the drawing correctely. ", "danger")

    return redirect(url_for("dashboard"))


@app.route("/drawing_edit/<int:drawing_id>", methods=["GET", "POST"])
@login_required
def drawing_edit(drawing_id):
    cursor = mysql.connection.cursor()

    if request.method == "POST":
        # Fetch form data
        title = request.form.get("title")
        drawing_number = request.form.get("drawing_number")
        client_name = request.form.get("client_name")
        project_location = request.form.get("project_location")
        project_code = request.form.get("project_code")
        feedback_authority_id = request.form.get("feedback_authority_id")
        reference = request.form.get("reference")
        build_of_material = request.form.get("build_of_material")

        # Handle file uploads and delete old files
        drawing_file = request.files.get("drawing_location")
        bom_file = request.files.get("build_of_material")
        reference_file = request.files.get("reference")

        # Fetch current file paths
        cursor.execute(
            "SELECT DrawingLocation, BuildOfMaterial, Reference FROM drawing WHERE DrawingID=%s",
            (drawing_id,),
        )
        current_files = cursor.fetchone()
        current_drawing_path = current_files[0]
        current_bom_path = current_files[1]
        current_reference_path = current_files[2]

        drawing_path = current_drawing_path
        bom_path = current_bom_path
        reference_path = current_reference_path

        if drawing_file:
            drawing_filename = f"{session['employee_id']}_{uuid.uuid4().hex}_{secure_filename(drawing_file.filename)}"
            drawing_path = os.path.join(app.config["UPLOAD_FOLDER"], drawing_filename)
            drawing_file.save(drawing_path)
            if os.path.exists(current_drawing_path):
                os.remove(current_drawing_path)

        if bom_file:
            bom_filename = f"{session['employee_id']}_{uuid.uuid4().hex}_{secure_filename(bom_file.filename)}"
            bom_path = os.path.join(app.config["BOM_UPLOAD_FOLDER"], bom_filename)
            bom_file.save(bom_path)
            if os.path.exists(current_bom_path):
                os.remove(current_bom_path)

        if reference_file:
            reference_filename = f"{session['employee_id']}_{uuid.uuid4().hex}_{secure_filename(reference_file.filename)}"
            reference_path = os.path.join(
                app.config["REFERENCE_UPLOAD_FOLDER"], reference_filename
            )
            reference_file.save(reference_path)
            if os.path.exists(current_reference_path):
                os.remove(current_reference_path)

        # Update database
        cursor.execute(
            """
            UPDATE drawing
            SET Title=%s, DrawingNumber=%s, ClientName=%s, ProjectLocation=%s, ProjectCode=%s, 
                FeedbackAuthorityID=%s, DrawingLocation=%s, BuildOfMaterial=%s, Reference=%s
            WHERE DrawingID=%s
        """,
            (
                title,
                drawing_number,
                client_name,
                project_location,
                project_code,
                feedback_authority_id,
                drawing_path,
                bom_path,
                reference_path,
                drawing_id,
            ),
        )

        mysql.connection.commit()
        cursor.close()

        flash("Drawing successfully updated!", "success")
        return redirect(url_for("dashboard"))

    # GET request: fetch drawing data to pre-fill the form
    cursor.execute("SELECT * FROM drawing WHERE DrawingID=%s", (drawing_id,))
    drawing = cursor.fetchone()
    cursor.close()

    # Convert tuple to dictionary if necessary
    drawing_dict = {
        "DrawingID": drawing[0],
        "DrawingLocation": drawing[2],
        "Title": drawing[3],
        "DrawingNumber": drawing[4],
        "ClientName": drawing[5],
        "ProjectLocation": drawing[6],
        "ProjectCode": drawing[7],
        "FeedbackAuthorityID": drawing[8],
        "Reference": drawing[13],
        "BuildOfMaterial": drawing[14],
    }

    return render_template("dashboard/drawing_edit.html", drawing=drawing_dict)


@app.route("/feedback_request_add/<int:drawing_id>", methods=["GET", "POST"])
@login_required
def feedback_request_add(drawing_id):

    cursor = mysql.connection.cursor()
    # Fetch drawing data to pre-fill the form
    cursor.execute("SELECT * FROM drawing WHERE DrawingID=%s", (drawing_id,))
    drawing = cursor.fetchone()
    cursor.close()

    user_id = session.get("employee_id")
    authority_id = drawing[8]
    feedback_note = ""
    status = "Pending"
    date_responded = None  # Will be set when feedback is responded to

    cursor = mysql.connection.cursor()
    # Insert data into feedback table
    cursor.execute(
        """
        INSERT INTO feedback (DrawingID, DrafterID, FeedbackAuthorityID, FeedbackNote, status, DateCreated, DateResponded)
        VALUES (%s, %s, %s, %s, %s, NOW(), %s)
    """,
        (drawing_id, user_id, authority_id, feedback_note, status, date_responded),
    )
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for("feedback_request"))


@app.route("/feedback_request")
@login_required
def feedback_request():
    user_id = session.get("employee_id")

    cursor = mysql.connection.cursor()
    # Fetch feedback data for the user
    cursor.execute(
        "SELECT * FROM feedback WHERE DrafterID=%s OR FeedbackAuthorityID=%s ORDER BY DateCreated DESC",
        (user_id, user_id),
    )
    feedback_entries = cursor.fetchall()
    cursor.close()

    if not feedback_entries:
        # Handle the case where no feedback entries are found
        # return "No feedback found", 404
        formatted_feedback_entries = ""
        drawings = ""
        return render_template(
            "dashboard/request_feedback.html",
            feedback=formatted_feedback_entries,
            drawings=drawings,
        )

    # Extract unique DrawingID values from feedback entries
    drawing_ids = {
        entry[1] for entry in feedback_entries
    }  # Assuming DrawingID is the second element in the tuple

    cursor = mysql.connection.cursor()
    # Fetch drawing data for all unique DrawingID values
    format_strings = ",".join(["%s"] * len(drawing_ids))
    cursor.execute(
        f"SELECT * FROM drawing WHERE DrawingID IN ({format_strings})",
        tuple(drawing_ids),
    )
    drawings = cursor.fetchall()
    cursor.close()

    # Format dates in feedback entries
    formatted_feedback_entries = []
    for entry in feedback_entries:
        entry_list = list(entry)
        entry_list[6] = entry_list[6].strftime("%d/%m/%Y") if entry_list[6] else None
        entry_list[7] = entry_list[7].strftime("%d/%m/%Y") if entry_list[7] else None
        formatted_feedback_entries.append(tuple(entry_list))

    return render_template(
        "dashboard/request_feedback.html",
        feedback=formatted_feedback_entries,
        drawings=drawings,
    )


@app.route("/feedback_response/<int:feedback_id>", methods=["GET", "POST"])
@login_required
def feedback_response(feedback_id):
    if request.method == "POST":
        note = request.form["note"]
        status = "Responded"
        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE feedback SET FeedbackNote = %s, status = %s, DateResponded = NOW() WHERE FeedbackID = %s",
            (note, status, feedback_id),
        )
        mysql.connection.commit()
        cursor.close()

        # fetching drawing id from feedback
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT DrawingID FROM feedback WHERE FeedbackID = %s", (feedback_id,)
        )
        drawing_id = cursor.fetchone()[
            0
        ]  # fetchone returns a tuple, so we need the first element
        cursor.close()

        # updating drawing status
        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE drawing SET FeedbackStatus = %s WHERE DrawingID = %s",
            (status, drawing_id),
        )
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for("feedback_request"))

    # Handle the GET request here if necessary, otherwise you can remove this part
    return "Feedback response page"


@app.route('/drawing_release/<int:drawing_id>')
@login_required
def drawing_release(drawing_id):
    # updating drawing status
    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE drawing SET ReleaseDate = NOW() WHERE DrawingID = %s",
        (drawing_id,),
    )
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('drawing_view', drawing_id=drawing_id))

@app.route('/drawins_search')
@login_required
def drawing_search():
    return render_template('dashboard/drawing_find.html')

@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q', '')
    cursor = mysql.connection.cursor()
    
    # Searching based on DrafterID, DrawingNumber, ProjectCode, or AuthorityID
    sql = """
    SELECT DrawingID, Title, DrafterID, DrawingNumber, ProjectCode, FeedbackAuthorityID AS AuthorityID
    FROM drawing
    WHERE Title LIKE %s OR DrafterID LIKE %s OR DrawingNumber LIKE %s OR ProjectCode LIKE %s OR FeedbackAuthorityID LIKE %s
    """
    like_query = f"%{query}%"
    cursor.execute(sql, (like_query, like_query, like_query, like_query, like_query))
    results = cursor.fetchall()
    cursor.close()

    # Process results into a list of dictionaries for JSON response
    processed_results = [
        {
            "DrawingID": row[0],
            "Title": row[1],
            "DrafterID": row[2],
            "DrawingNumber": row[3],
            "ProjectCode": row[4],
            "AuthorityID": row[5]
        }
        for row in results
    ]

    return jsonify({"results": processed_results})

@app.route('/profile_search')
@login_required
def profile_search():
    return render_template('dashboard/profile_find.html')

@app.route('/search_profile', methods=['GET'])
@login_required
def search_proflie():
    query = request.args.get('q', '')
    cursor = mysql.connection.cursor()
    
    # Searching based on DrafterID, DrawingNumber, ProjectCode, or AuthorityID
    sql = """
    SELECT UserID, DrafterID, Name, Email, Designation
    FROM user
    WHERE DrafterID LIKE %s OR Name LIKE %s OR Email LIKE %s OR Designation LIKE %s
    """
    like_query = f"%{query}%"
    cursor.execute(sql, (like_query, like_query, like_query, like_query))
    results = cursor.fetchall()
    cursor.close()

    # Process results into a list of dictionaries for JSON response
    processed_results = [
        {
            "UserID": row[0],
            "DrafterID": row[1],
            "Name": row[2],
            "Email": row[3],
            "Designation": row[4]
        }
        for row in results
    ]

    return jsonify({"results": processed_results})

@app.route('/Worklog')
@login_required
def user_worklog():
    cursor = mysql.connection.cursor()

    # Fetch data from 'drawing' table
    cursor.execute("SELECT * FROM drawing WHERE DrafterID=%s ORDER BY DateCreated DESC",(session['employee_id'],))
    drawings = cursor.fetchall()

    # Fetch data from 'feedback' table
    cursor.execute("SELECT * FROM feedback WHERE DrafterID=%s OR FeedbackAuthorityID=%s ORDER BY DateCreated DESC", (session['employee_id'], session['employee_id']))
    feedbacks = cursor.fetchall()

    # Fetch data from 'releaserevision' table
    cursor.execute("SELECT * FROM releaserevision ORDER BY DateCreated DESC")
    revisions = cursor.fetchall()

    # Fetch data from 'user' table
    cursor.execute("SELECT * FROM user WHERE DrafterID=%s",(session['employee_id'],))
    users = cursor.fetchall()

    # Fetch count of records from 'drawing' table
    cursor.execute("SELECT COUNT(*) FROM drawing WHERE DrafterID=%s", (session['employee_id'],))
    drawing_count = cursor.fetchone()[0]

    # Fetch count of records from 'feedback' table
    cursor.execute("SELECT COUNT(*) FROM feedback WHERE DrafterID=%s OR FeedbackAuthorityID=%s", (session['employee_id'], session['employee_id']))
    feedback_count = cursor.fetchone()[0]


    return render_template('dashboard/user_worklog.html', drawings=drawings, feedbacks=feedbacks, revisions=revisions, users=users, drawing_count=drawing_count, feedback_count=feedback_count)

# Debug route for listing all routes
# @app.route("/routes")
# def list_routes():
#     import urllib

#     output = []
#     for rule in app.url_map.iter_rules():
#         methods = ",".join(rule.methods)
#         line = urllib.parse.unquote(f"{rule.endpoint:50s} {methods:20s} {rule}")
#         output.append(line)
#     return "<br>".join(sorted(output))


if __name__ == "__main__":
    app.run(debug=True)
