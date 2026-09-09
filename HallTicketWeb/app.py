from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, make_response
import mysql.connector
from mysql.connector import Error
import bcrypt
import pandas as pd
import io
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'secret_key_never_reveals!!!'  # Change this to a random string

# Database Config
DB_CONFIG = {
    'host': "127.0.0.1",
    'user': "root",
    'password': "0407",  
    'database': "hall_ticket_db_university",  
}

# --- Database Helper ---
def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def query_db(query, args=(), one=False):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(query, args)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database Error: {e}")
        return False

# --- SECURITY: Initialize DB Columns (Runs on Startup) ---
def init_security_features():
    """Ensures the admin_users table has columns for brute force protection."""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # 1. Add failed_attempts column if not exists
        try:
            cur.execute("SELECT failed_attempts FROM admin_users LIMIT 1")
        except Error:
            print("Adding 'failed_attempts' column for security...")
            cur.execute("ALTER TABLE admin_users ADD COLUMN failed_attempts INT DEFAULT 0")
        
        # 2. Add is_locked column if not exists
        try:
            cur.execute("SELECT is_locked FROM admin_users LIMIT 1")
        except Error:
            print("Adding 'is_locked' column for security...")
            cur.execute("ALTER TABLE admin_users ADD COLUMN is_locked TINYINT(1) DEFAULT 0")
            
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Security Initialization Warning: {e}")


def init_sem_exam_fee_table():
    """Ensure sem_exam_fees table exists for semester exam fee rules."""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sem_exam_fees (
              id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
              mode VARCHAR(20) NOT NULL,
              exam_type VARCHAR(50) NOT NULL,
              semester VARCHAR(10) NOT NULL,
              min_backlogs INT NOT NULL DEFAULT 0,
              max_backlogs INT NOT NULL DEFAULT 0,
              amount INT NOT NULL,
              UNIQUE KEY uniq_sem_fee (mode, exam_type, semester, min_backlogs, max_backlogs)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"sem_exam_fees init warning: {e}")


# Run security check and ensure fee rules table exists immediately
init_security_features()
init_sem_exam_fee_table()

# --- Login Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Helper Lists ---
def get_dropdowns():
    depts = [r[0] for r in query_db("SELECT name FROM departments ORDER BY name")]
    sems = [r[0] for r in query_db("SELECT name FROM semesters ORDER BY name")]
    regs = [r[0] for r in query_db("SELECT code FROM regulations ORDER BY code")]
    return depts, sems, regs

# ================= ROUTES =================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Fetch password hash AND security fields
        # Tuple index: 0=hash, 1=failed_attempts, 2=is_locked
        user = query_db("SELECT password_hash, failed_attempts, is_locked FROM admin_users WHERE username = %s", (username,), one=True)
        
        if user:
            password_hash = user[0]
            failed_attempts = user[1]
            is_locked = user[2]

            # 1. CHECK IF LOCKED
            if is_locked == 1:
                flash('Account LOCKED due to multiple failed attempts. Contact another Admin.', 'danger')
                return render_template('login.html')

            # 2. VERIFY PASSWORD
            # Encode password to bytes for bcrypt
            if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                # Success: Reset attempts and log in
                execute_db("UPDATE admin_users SET failed_attempts = 0 WHERE username = %s", (username,))
                session['user'] = username
                return redirect(url_for('dashboard'))
            else:
                # 3. BRUTE FORCE LOGIC: Increment failures
                new_attempts = failed_attempts + 1
                if new_attempts >= 3:
                    execute_db("UPDATE admin_users SET failed_attempts = %s, is_locked = 1 WHERE username = %s", (new_attempts, username))
                    flash('Account LOCKED. Too many failed attempts.', 'danger')
                else:
                    execute_db("UPDATE admin_users SET failed_attempts = %s WHERE username = %s", (new_attempts, username))
                    flash(f'Invalid Credentials. Attempt {new_attempts}/3', 'warning')
        else:
            # Don't reveal if username exists or not
            flash('Invalid Credentials', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    old = request.form['old_password']
    new = request.form['new_password']
    confirm = request.form['confirm_password']
    
    user = query_db("SELECT password_hash FROM admin_users WHERE username = %s", (session['user'],), one=True)
    
    if user and bcrypt.checkpw(old.encode('utf-8'), user[0].encode('utf-8')):
        if new == confirm:
            hashed = bcrypt.hashpw(new.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            execute_db("UPDATE admin_users SET password_hash = %s WHERE username = %s", (hashed, session['user']))
            flash('Password updated successfully', 'success')
        else:
            flash('New passwords do not match', 'danger')
    else:
        flash('Incorrect current password', 'danger')
    return redirect(request.referrer)

@app.route('/')
@login_required
def dashboard():
    counts = {
        'dept': query_db("SELECT COUNT(*) FROM departments", one=True)[0],
        'student': query_db("SELECT COUNT(*) FROM students", one=True)[0],
        'subject': query_db("SELECT COUNT(*) FROM subjects", one=True)[0]
    }
    return render_template('dashboard.html', counts=counts)

# --- DEPARTMENTS ---
@app.route('/departments', methods=['GET', 'POST'])
@login_required
def departments():
    if request.method == 'POST':
        # Add Dept
        if 'add_name' in request.form:
            execute_db("INSERT INTO departments (name) VALUES (%s)", (request.form['add_name'],))
        # Delete Dept
        elif 'delete_id' in request.form:
            execute_db("DELETE FROM departments WHERE id=%s", (request.form['delete_id'],))
        return redirect(url_for('departments'))
    
    data = query_db("SELECT id, name FROM departments ORDER BY name")
    return render_template('departments.html', departments=data)

# --- STUDENTS ---
@app.route('/students', methods=['GET', 'POST'])
@login_required
def students():
    depts, sems, regs = get_dropdowns()
    
    # Handle Updates/Inserts
    if request.method == 'POST':
        if 'import_file' in request.files: # Import CSV
            file = request.files['import_file']
            if file.filename != '':
                try:
                    df = pd.read_csv(file) if file.filename.endswith('.csv') else pd.read_excel(file)
                    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
                    for _, row in df.iterrows():
                        quota = str(row.get("quota_type", "CONVENER")).upper() or "CONVENER"
                        total = row.get("college_fee_total", 0) or 0
                        pending = row.get("college_fee_pending", 0) or 0
                        execute_db(
                            """INSERT INTO students (roll_number, name, father_name, mother_name, dob, gender, mobile, department, regulation, year, semester, section, caste,
                                                       quota_type, college_fee_total, college_fee_pending) 
                                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                                   ON DUPLICATE KEY UPDATE name=VALUES(name), semester=VALUES(semester),
                                       quota_type=VALUES(quota_type), college_fee_total=VALUES(college_fee_total), college_fee_pending=VALUES(college_fee_pending)""",
                            (str(row.get("roll_number", "")), str(row.get("name", "")), str(row.get("father_name", "")), str(row.get("mother_name", "")),
                             str(row.get("dob", "")), str(row.get("gender", "")), str(row.get("mobile", "")),
                             str(row.get("department", "")), str(row.get("regulation", "")), row.get("year", 1),
                             str(row.get("semester", "")), str(row.get("section", "")), str(row.get("caste", "")),
                             quota, total, pending),
                        )
                    flash('Import Successful', 'success')
                except Exception as e:
                    flash(f'Error: {e}', 'danger')

        elif 'delete_roll' in request.form: # Delete
            execute_db("DELETE FROM students WHERE roll_number=%s", (request.form['delete_roll'],))
            
        else: # Add / Edit
            data = (request.form['roll_number'], request.form['name'], request.form['father_name'], request.form['mother_name'], request.form['dob'],
                    request.form['gender'], request.form['mobile'], request.form['department'], request.form['regulation'],
                    request.form['year'], request.form['semester'], request.form['section'], request.form['caste'])
            
            if 'original_roll' in request.form and request.form['original_roll']: # Update
                execute_db("""UPDATE students SET roll_number=%s, name=%s, father_name=%s, mother_name=%s, dob=%s, gender=%s, mobile=%s, 
                              department=%s, regulation=%s, year=%s, semester=%s, section=%s, caste=%s WHERE roll_number=%s""",
                              data + (request.form['original_roll'],))
                flash('Student Updated', 'success')
            else: # Insert
                execute_db("""INSERT INTO students (roll_number, name, father_name, mother_name, dob, gender, mobile, department, regulation, year, semester, section, caste) 
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", data)
                flash('Student Added', 'success')
        return redirect(url_for('students'))

    # Filtering Logic
    query = "SELECT roll_number, name, gender, department, regulation, semester, year, mobile, father_name, mother_name, dob, section, caste FROM students WHERE 1=1"
    params = []
    
    dept_filter = request.args.get('dept')
    sem_filter = request.args.get('sem')
    year_filter = request.args.get('year')
    search = request.args.get('search')
    
    if dept_filter: query += " AND department=%s"; params.append(dept_filter)
    if sem_filter: query += " AND semester=%s"; params.append(sem_filter)
    if year_filter: query += " AND year=%s"; params.append(year_filter)
    if search: query += " AND (name LIKE %s OR roll_number LIKE %s)"; params.extend([f"%{search}%", f"%{search}%"])
    
    students_data = query_db(query, tuple(params))
    years = [1, 2, 3, 4]
    return render_template('students.html', students=students_data, depts=depts, sems=sems, regs=regs, years=years)


@app.route('/students/sample-csv', methods=['GET'])
@login_required
def students_sample_csv():
    """Download a sample CSV template for student import."""
    cols = ['roll_number', 'name', 'father_name', 'mother_name', 'dob', 'gender', 'mobile',
            'department', 'regulation', 'year', 'semester', 'section', 'caste',
            'quota_type', 'college_fee_total', 'college_fee_pending']
    sample = [[
        '24695A4001', 'JOHN DOE', 'FATHER NAME', 'MOTHER NAME', '2005-01-01', 'Male', '9999999999',
        'CSE', 'R20', 1, 'I-I', 'A', 'OC', 'CONVENER', 0, 0
    ]]
    df = pd.DataFrame(sample, columns=cols)
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    resp = make_response(output.getvalue())
    resp.headers['Content-Type'] = 'text/csv'
    resp.headers['Content-Disposition'] = 'attachment; filename=students_sample.csv'
    return resp


@app.route('/attendance/sample-csv', methods=['GET'])
@login_required
def attendance_sample_csv():
    """Download a sample CSV template for attendance import."""
    cols = ['roll_number', 'semester', 'percentage']
    sample = [['24695A4001', 'I-I', 80.0]]
    df = pd.DataFrame(sample, columns=cols)
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    resp = make_response(output.getvalue())
    resp.headers['Content-Type'] = 'text/csv'
    resp.headers['Content-Disposition'] = 'attachment; filename=attendance_sample.csv'
    return resp


@app.route('/fees/sample-csv', methods=['GET'])
@login_required
def fees_sample_csv():
    """Download a sample CSV template for fee details import."""
    cols = ['roll_number', 'quota_type', 'college_fee_total', 'college_fee_pending']
    sample = [['24695A4001', 'CONVENER', 0, 0]]
    df = pd.DataFrame(sample, columns=cols)
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    resp = make_response(output.getvalue())
    resp.headers['Content-Type'] = 'text/csv'
    resp.headers['Content-Disposition'] = 'attachment; filename=fees_sample.csv'
    return resp


@app.route('/backlogs', methods=['GET', 'POST'])
@login_required
def backlogs_home():
    """Entry page from sidebar to manage student backlogs.

    Lets admin enter a roll number (and optional semester) and redirects
    to the detailed backlog editor for that student.
    """
    _, sems, _ = get_dropdowns()

    if request.method == 'POST':
        # CSV / Excel bulk import of backlogs
        if 'import_file' in request.files:
            file = request.files['import_file']
            if file and file.filename:
                try:
                    df = pd.read_csv(file) if file.filename.endswith('.csv') else pd.read_excel(file)
                    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

                    imported = 0
                    skipped = 0
                    errors_list = []

                    for idx, row in df.iterrows():
                        roll = str(row.get('roll_number', '')).strip().upper()
                        dept = str(row.get('department', '')).strip()
                        reg = str(row.get('regulation', '')).strip()
                        sem = str(row.get('semester', '')).strip()
                        code = str(row.get('subject_code', '')).strip()

                        if not roll or not code:
                            skipped += 1
                            errors_list.append(f"Row {idx+2}: Missing roll_number or subject_code")
                            continue

                        # Verify student exists
                        student_check = query_db("SELECT roll_number FROM students WHERE roll_number=%s", (roll,), one=True)
                        if not student_check:
                            skipped += 1
                            errors_list.append(f"Row {idx+2}: Student {roll} not found")
                            continue

                        # Try to resolve subject by full context first
                        subject = None
                        if dept and reg and sem:
                            subject = query_db(
                                "SELECT id FROM subjects WHERE subject_code=%s AND department=%s AND regulation=%s AND semester=%s LIMIT 1",
                                (code, dept, reg, sem),
                                one=True,
                            )

                        # Fallback: match by code only if not found
                        if not subject:
                            subject = query_db(
                                "SELECT id FROM subjects WHERE subject_code=%s LIMIT 1",
                                (code,),
                                one=True,
                            )

                        if not subject:
                            skipped += 1
                            errors_list.append(f"Row {idx+2}: Subject {code} not found")
                            continue

                        ok = execute_db(
                            "INSERT IGNORE INTO student_backlogs (roll_number, subject_id) VALUES (%s, %s)",
                            (roll, subject[0]),
                        )
                        if ok:
                            imported += 1
                        else:
                            skipped += 1

                    msg = f'Backlogs import completed. Added: {imported}, Skipped: {skipped}.'
                    if errors_list:
                        msg += f" First errors: {'; '.join(errors_list[:3])}" + ("..." if len(errors_list) > 3 else "")
                    flash(msg, 'success' if imported > 0 else 'warning')
                except Exception as e:
                    flash(f'Backlogs import error: {e}', 'danger')

            return redirect(url_for('backlogs_home'))

        # Single-student navigation
        roll = request.form.get('roll_number', '').strip().upper()
        sem = request.form.get('semester', '').strip()

        if not roll:
            flash('Please enter a Roll Number.', 'warning')
            return redirect(url_for('backlogs_home'))

        if sem:
            return redirect(url_for('backlogs', roll_number=roll, sem=sem))
        return redirect(url_for('backlogs', roll_number=roll))

    return render_template('backlogs_search.html', sems=sems)


@app.route('/backlogs/sample-csv', methods=['GET'])
@login_required
def backlogs_sample_csv():
    """Download a sample CSV template for backlog import."""
    cols = ['roll_number', 'subject_code', 'department', 'regulation', 'semester']
    sample = [['24695A4001', 'CS101', 'CSE', 'R20', 'I-I']]
    df = pd.DataFrame(sample, columns=cols)
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    resp = make_response(output.getvalue())
    resp.headers['Content-Type'] = 'text/csv'
    resp.headers['Content-Disposition'] = 'attachment; filename=backlogs_sample.csv'
    return resp


@app.route('/backlogs/<roll_number>', methods=['GET', 'POST'])
@login_required
def backlogs(roll_number):
    """Manage backlog subjects for a particular student.

    - Shows current backlogs (joined with subjects table)
    - Allows adding a subject from the curriculum as backlog
    - Allows removing an existing backlog subject
    """
    # Ensure student exists
    student = query_db(
        "SELECT roll_number, name, department, regulation, semester, year FROM students WHERE roll_number=%s",
        (roll_number,), one=True
    )
    if not student:
        flash('Student not found', 'danger')
        return redirect(url_for('students'))

    # Semester context for backlogs (default = student's current semester)
    _, sems, _ = get_dropdowns()
    current_sem = request.args.get('sem') or student[4]

    if request.method == 'POST':
        # Add backlog subject
        if 'add_subject_id' in request.form and request.form['add_subject_id']:
            sid = request.form['add_subject_id']
            execute_db(
                """INSERT IGNORE INTO student_backlogs (roll_number, subject_id)
                    VALUES (%s, %s)""",
                (roll_number, sid),
            )
            flash('Backlog subject added', 'success')

        # Remove backlog subject
        elif 'remove_id' in request.form and request.form['remove_id']:
            bid = request.form['remove_id']
            execute_db(
                "DELETE FROM student_backlogs WHERE id=%s AND roll_number=%s",
                (bid, roll_number),
            )
            flash('Backlog subject removed', 'success')

        return redirect(url_for('backlogs', roll_number=roll_number, sem=current_sem))

    # Current backlog subjects for this student & selected semester
    backlog_rows = query_db(
        """
        SELECT sb.id, s.subject_code, s.subject_name, s.semester, s.department, s.regulation
        FROM student_backlogs sb
        JOIN subjects s ON sb.subject_id = s.id
        WHERE sb.roll_number = %s AND s.semester = %s
        ORDER BY s.semester, s.subject_code
        """,
        (roll_number, current_sem),
    )

    # Available subjects from this student's curriculum to mark as backlog
    dept = student[2]
    reg = student[3]

    # All subjects for this student's department & regulation & selected semester
    all_subjects = query_db(
        """
        SELECT id, subject_code, subject_name, semester
        FROM subjects
        WHERE department=%s AND regulation=%s AND semester=%s
        ORDER BY semester, subject_code
        """,
        (dept, reg, current_sem),
    )

    # Exclude ones already in backlog list when building dropdown
    existing_ids = {row[0] for row in query_db(
        """SELECT subject_id FROM student_backlogs sb
            JOIN subjects s ON sb.subject_id = s.id
            WHERE sb.roll_number=%s AND s.semester=%s""",
        (roll_number, current_sem),
    )}
    available_subjects = [s for s in all_subjects if s[0] not in existing_ids]

    return render_template(
        'backlogs.html',
        student=student,
        backlogs=backlog_rows,
        available_subjects=available_subjects,
        sems=sems,
        current_sem=current_sem,
    )


@app.route('/students/export', methods=['GET'])
@login_required
def export_students():
    # Export students to Excel. Optional dept filter via ?dept=DeptName (empty or missing => all)
    dept = request.args.get('dept')
    query = "SELECT roll_number, name, gender, department, regulation, semester, year, mobile, father_name, mother_name, dob, section, caste FROM students WHERE 1=1"
    params = []
    if dept:
        query += " AND department=%s"
        params.append(dept)

    rows = query_db(query, tuple(params))

    # Column names correspond to SELECT order
    cols = ['roll_number', 'name', 'gender', 'department', 'regulation', 'semester', 'year', 'mobile', 'father_name', 'mother_name', 'dob', 'section', 'caste']
    try:
        df = pd.DataFrame(rows, columns=cols)
    except Exception:
        # If no rows, create empty df with cols
        df = pd.DataFrame(columns=cols)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Students')
    output.seek(0)

    filename = 'students_all.xlsx' if not dept else f"students_{dept.replace(' ', '_')}.xlsx"
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=filename)


@app.route('/subjects/sample-csv', methods=['GET'])
@login_required
def subjects_sample_csv():
    """Download a sample CSV template for subject import."""
    cols = ['department', 'regulation', 'semester', 'subject_code', 'subject_name']
    sample = [['CSE', 'R20', 'I-I', 'CS101', 'PROGRAMMING FOR PROBLEM SOLVING']]
    df = pd.DataFrame(sample, columns=cols)
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    resp = make_response(output.getvalue())
    resp.headers['Content-Type'] = 'text/csv'
    resp.headers['Content-Disposition'] = 'attachment; filename=subjects_sample.csv'
    return resp

# --- SUBJECTS ---
@app.route('/subjects', methods=['GET', 'POST'])
@login_required
def subjects():
    depts, sems, regs = get_dropdowns()
    if request.method == 'POST':
        # --- FIXED CSV IMPORT LOGIC ---
        if 'import_file' in request.files:
            file = request.files['import_file']
            if file.filename != '':
                try:
                    # Read file
                    df = pd.read_csv(file) if file.filename.endswith('.csv') else pd.read_excel(file)
                    # Normalize columns (lowercase, spaces to underscores)
                    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
                    
                    # Iterate and Insert
                    for _, row in df.iterrows():
                        execute_db("""INSERT INTO subjects (department, regulation, semester, subject_code, subject_name) 
                                      VALUES (%s, %s, %s, %s, %s)
                                      ON DUPLICATE KEY UPDATE subject_name=VALUES(subject_name)""",
                                   (str(row.get('department', '')), 
                                    str(row.get('regulation', '')), 
                                    str(row.get('semester', '')), 
                                    str(row.get('subject_code', '')), 
                                    str(row.get('subject_name', ''))))
                    flash('Subjects Imported Successfully', 'success')
                except Exception as e:
                    flash(f'Import Error: {str(e)}', 'danger')
        
        elif 'delete_id' in request.form:
             execute_db("DELETE FROM subjects WHERE id=%s", (request.form['delete_id'],))
        else:
             vals = (request.form['department'], request.form['regulation'], request.form['semester'], 
                     request.form['subject_code'], request.form['subject_name'])
             if 'edit_id' in request.form and request.form['edit_id']:
                 execute_db("UPDATE subjects SET department=%s, regulation=%s, semester=%s, subject_code=%s, subject_name=%s WHERE id=%s", vals + (request.form['edit_id'],))
             else:
                 execute_db("INSERT INTO subjects (department, regulation, semester, subject_code, subject_name) VALUES (%s, %s, %s, %s, %s)", vals)
        return redirect(url_for('subjects'))

    # Filter Logic
    q = "SELECT id, department, regulation, semester, subject_code, subject_name FROM subjects WHERE 1=1"
    p = []
    dept_filter = request.args.get('dept')
    sem_filter = request.args.get('sem')
    year_filter = request.args.get('year')
    search = request.args.get('search')

    if dept_filter:
        q += " AND department=%s"; p.append(dept_filter)
    if sem_filter:
        q += " AND semester=%s"; p.append(sem_filter)

    if year_filter:
        try:
            y = int(year_filter)
            year_sems_map = {
                1: ['I-I', 'I-II'],
                2: ['II-I', 'II-II'],
                3: ['III-I', 'III-II'],
                4: ['IV-I', 'IV-II'],
            }
            sems_for_year = year_sems_map.get(y, [])
            if sems_for_year:
                placeholders = ",".join(["%s"] * len(sems_for_year))
                q += f" AND semester IN ({placeholders})"
                p.extend(sems_for_year)
        except Exception:
            pass

    if search:
        q += " AND (subject_code LIKE %s OR subject_name LIKE %s)"
        p.extend([f"%{search}%", f"%{search}%"])

    subjects_data = query_db(q, tuple(p))
    years = [1, 2, 3, 4]
    return render_template('subjects.html', subjects=subjects_data, depts=depts, sems=sems, regs=regs, years=years)

# --- PROMOTION & DEMOTION ---
@app.route('/promote', methods=['GET', 'POST'])
@login_required
def promote():
    depts, sems, _ = get_dropdowns()
    
    if request.method == 'POST':
        cur = request.form['current_sem']
        dept = request.form['dept']
        action = request.form.get('action', 'promote') # 'promote' or 'demote'
        
        # Standard Semester Order
        order = ['I-I', 'I-II', 'II-I', 'II-II', 'III-I', 'III-II', 'IV-I', 'IV-II']
        
        try:
            idx = order.index(cur)
            target_sem = None
            
            if action == 'promote':
                # Move Forward
                if idx + 1 < len(order):
                    target_sem = order[idx+1]
                else:
                    flash('Cannot promote from Final Semester (IV-II). Students have completed the course.', 'warning')
                    
            elif action == 'demote':
                # Move Backward
                if idx - 1 >= 0:
                    target_sem = order[idx-1]
                else:
                    flash('Cannot demote from First Semester (I-I).', 'warning')
            
            if target_sem:
                # Calculate new Year based on new Semester Index
                target_idx = order.index(target_sem)
                target_year = (target_idx // 2) + 1
                
                # Execute Update
                sql = "UPDATE students SET semester=%s, year=%s WHERE semester=%s"
                params = [target_sem, target_year, cur]
                
                if dept != "ALL":
                    sql += " AND department=%s"
                    params.append(dept)
                    
                execute_db(sql, tuple(params))
                
                flash(f'Successfully {action}d students from {cur} to {target_sem} (Year {target_year})', 'success')
                
        except ValueError:
            flash('Invalid Semester selected', 'danger')
        except Exception as e:
            flash(f'Database Error: {str(e)}', 'danger')
        
    return render_template('promote.html', depts=depts, sems=sems)

# --- MANAGE ADMINS ROUTE ---
@app.route('/manage_admins', methods=['GET', 'POST'])
@login_required
def manage_admins():
    if request.method == 'POST':
        # Create New Admin
        if 'new_username' in request.form:
            u_name = request.form['new_username']
            p_word = request.form['new_password']
            
            # Check if exists
            exists = query_db("SELECT id FROM admin_users WHERE username=%s", (u_name,), one=True)
            if exists:
                flash('Username already exists', 'warning')
            else:
                hashed = bcrypt.hashpw(p_word.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                execute_db("INSERT INTO admin_users (username, password_hash) VALUES (%s, %s)", (u_name, hashed))
                flash(f'Admin {u_name} created successfully', 'success')
        
        # Delete Admin
        elif 'delete_user' in request.form:
            user_to_delete = request.form['delete_user']
            # Prevent deleting yourself
            if user_to_delete == session['user']:
                flash('You cannot delete your own account while logged in.', 'danger')
            else:
                execute_db("DELETE FROM admin_users WHERE username=%s", (user_to_delete,))
                flash('Admin deleted', 'success')

        # Unlock Admin (New Feature)
        elif 'unlock_user' in request.form:
             execute_db("UPDATE admin_users SET failed_attempts = 0, is_locked = 0 WHERE username=%s", (request.form['unlock_user'],))
             flash(f"Admin {request.form['unlock_user']} unlocked.", 'success')
             
        return redirect(url_for('manage_admins'))

    # Get List of Admins with Lock Status
    # Returns tuple list of (username, is_locked)
    # This works with your HTML which expects admins[0] for username and creates dicts if needed.
    # But wait, your HTML uses admin[0]. It might not display the lock status unless we update the HTML too.
    # However, for Python code request, this logic enables the backend to support it.
    
    # We select username AND is_locked status
    admins = query_db("SELECT username, is_locked FROM admin_users")
    
    # IMPORTANT: The HTML template `manage_admins.html` provided in previous turns iterates using `admin[0]` (tuple index).
    # Since `query_db` returns tuples by default in this script, `admins` will be a list of tuples like `('admin', 0)`.
    # `admin[0]` is username. `admin[1]` is is_locked.
    # Ensure your `manage_admins.html` uses `admin[1]` to show lock status if you update it.
    
    return render_template('manage_admins.html', admins=admins)


# --- BACKLOGS REPORT ---
@app.route('/backlogs-report', methods=['GET', 'POST'])
@login_required
def backlogs_report():
    """Report: List all students with backlogs, grouped by semester/department."""
    depts, sems, _ = get_dropdowns()
    
    dept_filter = request.args.get('dept', '')
    sem_filter = request.args.get('sem', '')
    
    query = """
        SELECT DISTINCT st.roll_number, st.name, st.department, st.semester, COUNT(sb.id) as backlog_count
        FROM students st
        LEFT JOIN student_backlogs sb ON st.roll_number = sb.roll_number
        WHERE 1=1
    """
    params = []
    
    if dept_filter:
        query += " AND st.department=%s"
        params.append(dept_filter)
    if sem_filter:
        query += " AND st.semester=%s"
        params.append(sem_filter)
    
    query += " GROUP BY st.roll_number, st.name, st.department, st.semester HAVING backlog_count > 0"
    query += " ORDER BY st.department, st.semester, st.roll_number"
    
    report_data = query_db(query, tuple(params))
    
    total_backlogs = sum(row[4] for row in report_data)
    total_students_with_backlogs = len(report_data)
    
    return render_template(
        'backlogs_report.html',
        report_data=report_data,
        depts=depts,
        sems=sems,
        dept_filter=dept_filter,
        sem_filter=sem_filter,
        total_backlogs=total_backlogs,
        total_students_with_backlogs=total_students_with_backlogs
    )


@app.route('/hallticket-approvals', methods=['GET', 'POST'])
@login_required
def hallticket_approvals():
    """Admin view to approve or reject hallticket payments after checks."""
    if request.method == 'POST':
        # Per-payment approve/reject
        pid = request.form.get('payment_id')
        action = request.form.get('action')
        note = request.form.get('note', '').strip()
        if pid and action in ('approve', 'reject'):
            status = 'approved' if action == 'approve' else 'rejected'
            execute_db(
                """UPDATE payments
                        SET approval_status=%s, approved_at=NOW(), approved_by=%s, approval_note=%s
                      WHERE id=%s""",
                (status, session.get('username', 'admin'), note, pid),
            )
            flash(f'Payment {"approved" if action == "approve" else "rejected"}.', 'success')
            return redirect(url_for('hallticket_approvals'))

        # Bulk approvals
        bulk_action = request.form.get('bulk_action')
        if bulk_action in ('approve_75_fee_clear', 'approve_75'):
            conds = ["p.status='paid'", "p.approval_status='pending'", "a.percentage IS NOT NULL", "a.percentage>=75"]
            if bulk_action == 'approve_75_fee_clear':
                conds.append("(s.college_fee_pending IS NULL OR s.college_fee_pending=0)")
            where_sql = " AND ".join(conds)
            sql = f"""UPDATE payments p
                         JOIN students s ON p.roll_number = s.roll_number
                         LEFT JOIN attendance a ON a.roll_number = p.roll_number AND a.semester = s.semester
                         SET p.approval_status='approved', p.approved_at=NOW(),
                             p.approved_by=%s, p.approval_note=%s
                       WHERE {where_sql}"""
            execute_db(sql, (session.get('username', 'admin'), f'Bulk approval: {bulk_action}'))
            flash('Bulk approval completed.', 'success')
            return redirect(url_for('hallticket_approvals'))

        # Mark college fee as fully paid for a student
        fee_roll = request.form.get('fee_roll')
        if fee_roll:
            execute_db(
                "UPDATE students SET college_fee_pending=0 WHERE roll_number=%s",
                (fee_roll.strip().upper(),),
            )
            flash(f'College fee marked as paid for {fee_roll}.', 'success')
            return redirect(url_for('hallticket_approvals'))

    rows = query_db(
        """
        SELECT p.id, p.roll_number, s.name, s.department, s.semester,
             p.exam_type, p.exam_month, p.exam_year,
             p.amount, p.status, p.approval_status, p.created_at, p.paid_at,
             s.quota_type, s.college_fee_total, s.college_fee_pending,
             a.percentage
         FROM payments p
         LEFT JOIN students s ON p.roll_number = s.roll_number
         LEFT JOIN attendance a ON a.roll_number = p.roll_number AND a.semester = s.semester
        WHERE p.status = 'paid'
        ORDER BY p.created_at DESC
        LIMIT 200
        """
    )

    # Low attendance (<75%) pending records for manual review
    low_attendance = query_db(
        """
        SELECT p.id, p.roll_number, s.name, s.department, s.semester,
               p.exam_type, p.exam_month, p.exam_year,
               p.amount, p.status, p.approval_status, p.created_at, p.paid_at,
               s.quota_type, s.college_fee_total, s.college_fee_pending,
               a.percentage
          FROM payments p
          LEFT JOIN students s ON p.roll_number = s.roll_number
          LEFT JOIN attendance a ON a.roll_number = p.roll_number AND a.semester = s.semester
         WHERE p.status = 'paid'
           AND p.approval_status = 'pending'
           AND a.percentage IS NOT NULL
           AND a.percentage < 75
         ORDER BY p.created_at DESC
         LIMIT 200
        """
    )

    return render_template('hallticket_approvals.html', payments=rows, low_attendance=low_attendance)


@app.route('/attendance', methods=['GET', 'POST'])
@login_required
def attendance_management():
    """Simple attendance management: add or update percentage per student & semester."""
    depts, sems, _ = get_dropdowns()
    if request.method == 'POST':
        # Single-row manual add/update
        roll = request.form.get('roll_number', '').strip().upper()
        sem = request.form.get('semester', '').strip()
        perc = request.form.get('percentage', '').strip()
        try:
            if roll and sem and perc:
                execute_db(
                    """INSERT INTO attendance (roll_number, semester, percentage)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE percentage=VALUES(percentage), updated_at=NOW()""",
                    (roll, sem, perc),
                )
                flash('Attendance updated.', 'success')
            else:
                flash('Please fill Roll, Semester and Percentage.', 'warning')
        except Exception as e:
            flash(f'Attendance update failed: {e}', 'danger')
        return redirect(url_for('attendance_management'))

    # Filters for department / year-wise view
    dept_filter = request.args.get('dept')
    year_filter = request.args.get('year')

    base = """SELECT a.roll_number, s.name, a.semester, a.percentage, a.updated_at, s.department, s.year
               FROM attendance a
               LEFT JOIN students s ON a.roll_number = s.roll_number
               WHERE 1=1"""
    params = []
    if dept_filter:
        base += " AND s.department=%s"
        params.append(dept_filter)
    if year_filter:
        base += " AND s.year=%s"
        params.append(year_filter)

    base += " ORDER BY a.updated_at DESC LIMIT 200"
    rows = query_db(base, tuple(params))
    years = [1, 2, 3, 4]
    return render_template('attendance.html', sems=sems, records=rows, depts=depts, years=years)


@app.route('/fees', methods=['GET', 'POST'])
@login_required
def fee_management():
    """Manage student quota type and college fee totals/pending."""
    student = None
    roll = request.values.get('roll_number', '').strip().upper()

    if request.method == 'POST':
        quota = request.form.get('quota_type') or 'CONVENER'
        total = request.form.get('college_fee_total') or 0
        pending = request.form.get('college_fee_pending') or 0

        try:
            execute_db(
                """UPDATE students
                       SET quota_type=%s, college_fee_total=%s, college_fee_pending=%s
                       WHERE roll_number=%s""",
                (quota, total, pending, roll),
            )
            flash('Fee details updated.', 'success')
        except Exception as e:
            flash(f'Fee update failed: {e}', 'danger')

    if roll:
        student = query_db(
            """SELECT roll_number, name, department, semester, quota_type,
                       college_fee_total, college_fee_pending
                   FROM students WHERE roll_number=%s""",
            (roll,),
            one=True,
        )

    # Department / year wise listing for fee overview
    depts, _, _ = get_dropdowns()
    dept_filter = request.args.get('dept')
    year_filter = request.args.get('year')

    q = """SELECT roll_number, name, department, year, semester, quota_type,
                    college_fee_total, college_fee_pending
             FROM students WHERE 1=1"""
    params = []
    if dept_filter:
        q += " AND department=%s"
        params.append(dept_filter)
    if year_filter:
        q += " AND year=%s"
        params.append(year_filter)

    q += " ORDER BY department, year, roll_number LIMIT 300"
    fee_rows = query_db(q, tuple(params))
    years = [1, 2, 3, 4]

    return render_template('fees.html', student=student, fee_rows=fee_rows, depts=depts, years=years)


@app.route('/exam-fees', methods=['GET', 'POST'])
@login_required
def exam_fee_management():
    """Manage semester exam fee slabs used by student portal payments."""
    message = None

    if request.method == 'POST':
        # Delete rule
        if 'delete_id' in request.form and request.form['delete_id']:
            rid = request.form['delete_id']
            if execute_db("DELETE FROM sem_exam_fees WHERE id=%s", (rid,)):
                flash('Exam fee rule deleted.', 'success')
            else:
                flash('Failed to delete exam fee rule.', 'danger')
            return redirect(url_for('exam_fee_management'))

        mode = (request.form.get('mode') or '').strip()
        exam_type = (request.form.get('exam_type') or '').strip()
        semester = (request.form.get('semester') or '').strip()
        min_backlogs = request.form.get('min_backlogs') or '0'
        max_backlogs = request.form.get('max_backlogs') or '0'
        amount = request.form.get('amount') or '0'

        if not mode or not exam_type or not semester:
            flash('Mode, exam type, and semester are required.', 'danger')
        else:
            try:
                mb = int(min_backlogs)
                xb = int(max_backlogs)
                amt = int(amount)
            except ValueError:
                flash('Backlogs and amount must be integers.', 'danger')
            else:
                ok = execute_db(
                    """INSERT INTO sem_exam_fees (mode, exam_type, semester, min_backlogs, max_backlogs, amount)
                           VALUES (%s, %s, %s, %s, %s, %s)
                           ON DUPLICATE KEY UPDATE amount=VALUES(amount)""",
                    (mode, exam_type, semester, mb, xb, amt),
                )
                if ok:
                    flash('Exam fee rule saved.', 'success')
                else:
                    flash('Failed to save exam fee rule.', 'danger')
        return redirect(url_for('exam_fee_management'))

    # List all configured rules
    rules = query_db(
        """SELECT id, mode, exam_type, semester, min_backlogs, max_backlogs, amount
               FROM sem_exam_fees
               ORDER BY mode, exam_type, semester, min_backlogs"""
    )

    return render_template('exam_fees.html', rules=rules)


@app.route('/attendance/import', methods=['POST'])
@login_required
def attendance_import():
    """Bulk import attendance from CSV/Excel."""
    if 'import_file' not in request.files:
        flash('No file uploaded for attendance import.', 'danger')
        return redirect(url_for('attendance_management'))

    file = request.files['import_file']
    if not file.filename:
        flash('Empty filename.', 'danger')
        return redirect(url_for('attendance_management'))

    try:
        df = pd.read_csv(file) if file.filename.endswith('.csv') else pd.read_excel(file)
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
        count = 0
        for _, row in df.iterrows():
            roll = str(row.get('roll_number', '')).strip().upper()
            sem = str(row.get('semester', '')).strip()
            perc = row.get('percentage')
            if not roll or not sem or perc is None:
                continue
            execute_db(
                """INSERT INTO attendance (roll_number, semester, percentage)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE percentage=VALUES(percentage), updated_at=NOW()""",
                (roll, sem, perc),
            )
            count += 1
        flash(f'Attendance imported for {count} rows.', 'success')
    except Exception as e:
        flash(f'Attendance import failed: {e}', 'danger')

    return redirect(url_for('attendance_management'))


@app.route('/fees/import', methods=['POST'])
@login_required
def fees_import():
    """Bulk import fee details (quota/college fee) from CSV/Excel."""
    if 'import_file' not in request.files:
        flash('No file uploaded for fee import.', 'danger')
        return redirect(url_for('fee_management'))

    file = request.files['import_file']
    if not file.filename:
        flash('Empty filename.', 'danger')
        return redirect(url_for('fee_management'))

    try:
        df = pd.read_csv(file) if file.filename.endswith('.csv') else pd.read_excel(file)
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
        count = 0
        for _, row in df.iterrows():
            roll = str(row.get('roll_number', '')).strip().upper()
            if not roll:
                continue
            quota = str(row.get('quota_type', 'CONVENER')).upper() or 'CONVENER'
            total = row.get('college_fee_total', 0) or 0
            pending = row.get('college_fee_pending', 0) or 0
            execute_db(
                """UPDATE students
                       SET quota_type=%s, college_fee_total=%s, college_fee_pending=%s
                     WHERE roll_number=%s""",
                (quota, total, pending, roll),
            )
            count += 1
        flash(f'Fee details imported for {count} students.', 'success')
    except Exception as e:
        flash(f'Fee import failed: {e}', 'danger')

    return redirect(url_for('fee_management'))


# --- BULK CLEAR BACKLOGS ---
@app.route('/backlogs/bulk-clear', methods=['GET', 'POST'])
@login_required
def bulk_clear_backlogs():
    """Clear backlogs for multiple students by semester and/or roll range."""
    depts, sems, _ = get_dropdowns()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'clear_by_semester':
            dept = request.form.get('department', '').strip()
            sem = request.form.get('semester', '').strip()
            
            if not sem:
                flash('Please select a semester to clear.', 'warning')
            else:
                query = """
                    DELETE sb FROM student_backlogs sb
                    JOIN subjects s ON sb.subject_id = s.id
                    WHERE s.semester=%s
                """
                params = [sem]
                
                if dept and dept != 'ALL':
                    query += " AND s.department=%s"
                    params.append(dept)
                
                execute_db(query, tuple(params))
                flash(f'Cleared all backlogs for {sem}' + (f' in {dept}' if dept and dept != 'ALL' else ''), 'success')
                return redirect(url_for('bulk_clear_backlogs'))
        
        elif action == 'clear_by_roll_range':
            roll_start = request.form.get('roll_start', '').strip().upper()
            roll_end = request.form.get('roll_end', '').strip().upper()
            
            if not roll_start or not roll_end:
                flash('Please enter both start and end roll numbers.', 'warning')
            else:
                execute_db(
                    "DELETE FROM student_backlogs WHERE roll_number >= %s AND roll_number <= %s",
                    (roll_start, roll_end)
                )
                flash(f'Cleared backlogs for roll numbers {roll_start} to {roll_end}', 'success')
                return redirect(url_for('bulk_clear_backlogs'))
    
    return render_template('bulk_clear_backlogs.html', depts=depts, sems=sems)


# --- CSV VALIDATION ENDPOINT ---
@app.route('/validate-csv', methods=['POST'])
@login_required
def validate_csv():
    """Validate CSV for import and return row-level errors/warnings."""
    import json
    
    if 'file' not in request.files:
        return {'error': 'No file provided'}, 400
    
    file = request.files['file']
    import_type = request.form.get('type', 'students')
    
    if not file.filename:
        return {'error': 'Empty filename'}, 400
    
    try:
        df = pd.read_csv(file) if file.filename.endswith('.csv') else pd.read_excel(file)
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
        
        errors = []
        valid_rows = 0
        
        if import_type == 'students':
            required_cols = ['roll_number', 'name', 'department', 'semester']
            for idx, row in df.iterrows():
                row_errors = []
                for col in required_cols:
                    if col not in row or str(row[col]).strip() == '':
                        row_errors.append(f"Missing {col}")
                if row_errors:
                    errors.append({'row': idx+2, 'errors': row_errors})
                else:
                    valid_rows += 1
        
        elif import_type == 'subjects':
            required_cols = ['department', 'regulation', 'semester', 'subject_code', 'subject_name']
            for idx, row in df.iterrows():
                row_errors = []
                for col in required_cols:
                    if col not in row or str(row[col]).strip() == '':
                        row_errors.append(f"Missing {col}")
                if row_errors:
                    errors.append({'row': idx+2, 'errors': row_errors})
                else:
                    valid_rows += 1
        
        elif import_type == 'attendance':
            required_cols = ['roll_number', 'semester', 'percentage']
            for idx, row in df.iterrows():
                row_errors = []
                for col in required_cols:
                    if col not in row or str(row[col]).strip() == '':
                        row_errors.append(f"Missing {col}")
                # basic numeric validation for percentage
                try:
                    perc = float(row.get('percentage', 0))
                    if perc < 0 or perc > 100:
                        row_errors.append('percentage must be between 0 and 100')
                except Exception:
                    row_errors.append('percentage must be numeric')

                roll = str(row.get('roll_number', '')).strip().upper()
                if roll:
                    student = query_db("SELECT roll_number FROM students WHERE roll_number=%s", (roll,), one=True)
                    if not student:
                        row_errors.append(f"Student {roll} not found")

                if row_errors:
                    errors.append({'row': idx+2, 'errors': row_errors})
                else:
                    valid_rows += 1

        elif import_type == 'fees':
            required_cols = ['roll_number']
            for idx, row in df.iterrows():
                row_errors = []
                for col in required_cols:
                    if col not in row or str(row[col]).strip() == '':
                        row_errors.append(f"Missing {col}")

                roll = str(row.get('roll_number', '')).strip().upper()
                if roll:
                    student = query_db("SELECT roll_number FROM students WHERE roll_number=%s", (roll,), one=True)
                    if not student:
                        row_errors.append(f"Student {roll} not found")

                # Optional numeric checks
                for num_col in ['college_fee_total', 'college_fee_pending']:
                    if num_col in row and str(row[num_col]).strip() != '':
                        try:
                            val = float(row[num_col])
                            if val < 0:
                                row_errors.append(f"{num_col} cannot be negative")
                        except Exception:
                            row_errors.append(f"{num_col} must be numeric")

                if row_errors:
                    errors.append({'row': idx+2, 'errors': row_errors})
                else:
                    valid_rows += 1

        elif import_type == 'backlogs':
            required_cols = ['roll_number', 'subject_code']
            for idx, row in df.iterrows():
                row_errors = []
                for col in required_cols:
                    if col not in row or str(row[col]).strip() == '':
                        row_errors.append(f"Missing {col}")
                
                roll = str(row.get('roll_number', '')).strip().upper()
                code = str(row.get('subject_code', '')).strip()
                
                if roll and code:
                    student = query_db("SELECT roll_number FROM students WHERE roll_number=%s", (roll,), one=True)
                    if not student:
                        row_errors.append(f"Student {roll} not found")
                    
                    subject = query_db("SELECT id FROM subjects WHERE subject_code=%s", (code,), one=True)
                    if not subject:
                        row_errors.append(f"Subject {code} not found")
                
                if row_errors:
                    errors.append({'row': idx+2, 'errors': row_errors})
                else:
                    valid_rows += 1
        
        return {
            'valid_rows': valid_rows,
            'total_rows': len(df),
            'errors': errors,
            'has_errors': len(errors) > 0
        }
    
    except Exception as e:
        return {'error': f'File parsing error: {str(e)}'}, 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)