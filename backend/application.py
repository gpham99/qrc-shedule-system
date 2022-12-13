from databaseTest import get_roster, get_master_schedule_info, get_disciplines, check_user
import time
from flask import Flask, request, session, redirect, url_for
from cas import CASClient
from flask_cors import CORS
import ast
import os
from models import read_roster
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '.'
ALLOWED_EXTENSIONS = {'xls', 'xlsx', 'xlsm', 'xlsb', 'odf', 'ods', 'odt'}

# print a nice greeting.
def say_hello(username = "Team"):
    return '<p>Hello %s!</p>\n' % username

# some bits of text for the page.
header_text = '''
    <html>\n<head> <title>EB Flask Test</title> </head>\n<body>'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'
sso_link = '<p><a href="/login">Log in using SSO</a></p>'
logout_link = '<p><a href="/cas_logout">Log out of CAS</a></p>'

# EB looks for an 'application' callable by default.
application = Flask(__name__)
CORS(application)
application.secret_key = 'V7nlCN90LPHOTA9PGGyf'
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
cas_client = CASClient(
    version=3,    
    service_url='http://52.12.35.11:8080/',
    server_url='https://cas.coloradocollege.edu/cas/'
)

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_login():
    if 'username' in session:
        in_system, group = check_user(session['username']+"@coloradocollege.edu")
    else:
        in_system, group = False, "Logged out"
    return in_system, group

# add a rule for the index page
@application.route('/')
def index():
    in_system, group = check_login()
    if in_system:
        return 'You are logged in as part of the ' + group + ' ! <a href="/logout">Exit</a>'
    #if 'username' in session:
        # Already logged in
    #    return 'You are logged in. Here you are going to see your schedule. <a href="/logout">Exit</a>'
    elif group == "None":
        return 'You are not authorized to access this site. <a href="/logout">Exit</a>'
    next = request.args.get('next')
    ticket = request.args.get('ticket')

    if not ticket:
        return header_text + say_hello() + footer_text + sso_link
    
    application.logger.debug('ticket: %s', ticket)
    application.logger.debug('next: %s', next)
    user, attributes, pgtiou = cas_client.verify_ticket(ticket)

    application.logger.debug(
        'CAS verify ticket response: user: %s, attributes: %s, pgtiou: %s', user, attributes, pgtiou)

    if not user:
        return 'Failed to verify ticket. <a href="/login">Login</a>'
    else:  # Login successfully, redirect according `next` query parameter.
        session['username'] = user
        session['email'] = attributes['email']
        if not next:
            return redirect(url_for('profile'))
        return redirect(next)

@application.route('/profile')
def profile(method=['GET']):
    application.logger.debug('session when you hit profile: %s', session)
    in_system, group = check_login()
    if in_system:
        return 'Logged in as {}. Your email address is {}. <a href="/logout">Exit</a>'.format(session['username'], session['email'])
    elif group == "None":
        return 'You are not authorized to access this site. <a href="/logout">Exit</a>'
    return 'Login required. <a href="/login">Login</a>', 403

@application.route('/login')
def login():
    application.logger.debug('session when you hit login: %s', session)

    if 'username' in session:
        # Already logged in
        return redirect(url_for('profile'))

    next = request.args.get('next')
    ticket = request.args.get('ticket')

    if not ticket:
        # No ticket, the request come from end user, send to CAS login
        cas_login_url = cas_client.get_login_url()
        application.logger.debug('CAS login URL: %s', cas_login_url)
        return redirect(cas_login_url) # the return of this is /ticket?=...

@application.route('/cas_logout')
def logout():
    redirect_url = url_for('logout_callback', _external=True)
    application.logger.debug('Redirect logout URL %s', redirect_url)
    cas_logout_url = cas_client.get_logout_url(redirect_url)
    application.logger.debug('CAS logout URL: %s', cas_logout_url)
    session.clear()

    return redirect(cas_logout_url)

@application.route('/logout')
def logout_callback():
    session.clear()
    return redirect("https://www.coloradocollege.edu/")
    
@application.route('/api/time')
def get_current_time():
    return {'time': time.time()}

@application.route('/api/login_status')
def get_login_status():
    print("session: ", session)
    if 'username' in session:
        return {"login_status": "1"}
    else:
        return {"login_status": "0"}

@application.route('/api/master_schedule')
def get_master_schedule():
    disciplines = get_disciplines()
    roster = get_roster()
    master_schedule = []
    master_schedule_with_disciplines = {}
    for i in range(20): #TODO: MAGIC CONSTANT
        master_schedule.append(get_master_schedule_info(i))
    shift_num = 0
    for line in master_schedule:
        if line != None:
            for d in range(len(line)):
                email = line[d]
                if email != None:
                    tutor_found = False
                    for tutor_entry in roster:
                        if tutor_entry[0] == email: #find the tutor in the roster
                            tutor_found = True
                            discipline_list = ast.literal_eval(tutor_entry[4])
                            for i in range(len(discipline_list)): 
                                if discipline_list[i] == 'CHMB':
                                    discipline_list[i] = 'CH/MB'
                            output_str = "/".join(discipline_list) + ": " + str(tutor_entry[1])
                            master_schedule_with_disciplines[str(shift_num)+disciplines[d]] = output_str
                    if not tutor_found:
                        print("Warning: One tutor (", email, ") not found in database. Omitting corresponding shift.")
        shift_num += 1
    return master_schedule_with_disciplines

#Page where any individual tutor's schedule is stored: shift number and discipline they signed up for
@application.route('/api/tutor/<username>')
def get_tutor_schedule(username):
    email = username + "@coloradocollege.edu"
    disciplines = get_disciplines()
    master_schedule = []
    tutor_schedule = {}
    for i in range(20): #TODO: MAGIC CONSTANT
        master_schedule.append(get_master_schedule_info(i))
    shift_num = 0
    for line in master_schedule:
        if line != None:
            if email in line:
                index = line.index(email)
                tutor_schedule[shift_num] = disciplines[index]
            else:
                tutor_schedule[shift_num] = None
            shift_num += 1
    return tutor_schedule
    
    
@application.route('/api/upload_roster', methods=['POST'])
def upload_roster():
    # check if the post request has the file part
    if 'filename' not in request.files:
        print('No file part')
        return redirect(request.url)
    file = request.files['filename']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        print('No selected file')
        return "No selected file"
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if 'ROSTER' in application.config:
            os.remove(application.config['ROSTER'])
        file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
        application.config['ROSTER'] = filename
        result = read_roster(filename)
        print(result)
        return result
    return "File format not accepted"""

@application.route('/unauthorized_login')
def unauthorized_login():
    return "You have successfully logged in to Colorado College, but your account is not part of the QRC database. \n Please contact QRC administrators if you believe this is an error. " + logout_link
    

# # run the app.
# if __name__ == "__main__":
#     # Setting debug to True enables debug output. This line should be
#     # removed before deploying a production app.
#     application.debug = True
#     application.run()
