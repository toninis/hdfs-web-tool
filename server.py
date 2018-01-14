import sys ,os
from  ldap3 import Server , Connection , ALL , NTLM
from hive import hive_connection_lh , hive_connection_md , msisdn_query , parse_data ,get_pretty_print , get_project_data
from flask import Flask , render_template , request ,session , redirect , url_for , escape
from werkzeug import secure_filename
from flask_wtf import Form
from wtforms.fields.html5 import DateField

app = Flask(__name__)
with open('server_key','r') as secret:
    app.secret_key = secret.read()

ldap_server = Server(host='ldap-server', port=389 )

class ExampleForm(Form):
    fdt = DateField('DatePicker', format='%Y-%m-%d')
    tdt = DateField('DatePicker', format='%Y-%m-%d')

@app.route('/')
def index():
    if 'username' in session:
        return render_template('welcome.html')
    return render_template('login.html')

@app.route('/query')
def query():
    if 'username' in session:
        ##### get dynamic schemas
        ( cursor_lh , conn_lh )  = hive_connection_lh(session['username'],session['password'])
        ( cursor_md , conn_md )  = hive_connection_md(session['username'],session['password'])
        schemas = get_project_data(cursor_lh,cursor_md)
        conn_lh.close()
        conn_md.close()
        return render_template('frontend.html', wr_projects = schemas)
    return render_template('login.html')

### login
@app.route('/login',methods=['POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        ### LDAP AUTH section
        try:

            #auth = Connection(ldap_server,'internal\\'+session['username'],session['password'] ,auto_bind=True ,authentication=NTLM)
            #auth.unbind()
            return redirect(url_for('index'))
        except Exception as e:
            session.pop('username', None)
            return redirect(url_for('index'))

### logout
@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   return redirect(url_for('index'))

### report page
@app.route('/report')
def report():
    if 'username' in session:
        ##### get dynamic schemas
        form = ExampleForm()
        ( cursor_lh , conn_lh )  = hive_connection.lh(session['username'],session['password'])
        ( cursor_md , conn_md )  = hive_connection.md(session['username'],session['password'])
        schemas = get_project_data(cursor_lh,cursor_md)
        conn_lh.close()
        conn_md.close()
        return render_template('file.html', wr_projects = schemas , form = form )
    return render_template('login.html')

### report execution
@app.route('/report_excecution', methods=['POST'])
def execute():
    if request.method == 'POST':
        f = request.files['file']
        result = request.form
        fdt = request.form['fdt']
        tdt = request.form['tdt']
        project_details = eval(result['project'])
        project = project_details[0]
        p_data = project_details[1]
        print ('Report will run for project %s from %s to %s ' % (project,fdt , tdt))
        f.save(secure_filename(f.filename))

        return 'file uploaded'

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/result', methods=['POST'])
def results():
    if request.method == 'POST':
        result = request.form
        project_details = eval(result['project'])

        if project_details['dc'] == 'md':
            ( cursor , conn )  = hive_connection_md(session['username'],session['password'])
        elif project_details['dc'] == 'lh':
            ( cursor , conn )  = hive_connection_lh(session['username'],session['password'])

        data = msisdn_query(cursor,result['msisdn'],project_details['schema'])
        p_data = parse_data(data)
        conn.close()
        return render_template('result.html' , result = p_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
