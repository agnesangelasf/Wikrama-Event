from flask import *
from flask_pymongo import *
from datetime import *
from werkzeug.utils import secure_filename
import os
app = Flask(__name__)
app.secret_key = "SECRET_KEY"
wsgi_app = app.wsgi_app

# app.config["MONGO_URI"] = "mongodb+srv://evenuss:arjuna203@cluster0-sxt0m.gcp.mongodb.net/contoso"
app.config["MONGO_URI"] = "mongodb://localhost:27017/eventwk"
mongo = PyMongo(app)

UPLOAD_FOLDER = './static/img'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/index')
def home():
    return 'Ini home!'







@app.route('/', methods=['GET','POST'])
def login():
    if request.form:
        session['username'] = request.form['username']
        password = request.form['password']
        session['login']=False
        user = mongo.db.users.count({'username':session['username'],'password':password})
        val = mongo.db.users.find_one({'username':session['username'],'password':password})
        print(user)
        session['iduser'] = val['_id']
        print(session['iduser'])
        if user > 0 and val['role']=='member':
            session['login'] = True
            return redirect(url_for('memberDashboard'))
        elif user > 0 and val['role']=='admin':
            session['login'] = True
            return redirect(url_for('newEvent'))
        else:
            return render_template('login.html')
    return render_template('login.html')






@app.route('/home', methods=['GET','POST'])
def memberDashboard():
    if session['login'] == True:
        findUsr = mongo.db.users.find_one({'username':session['username']})
        print(findUsr['username'])
        events= mongo.db.events.find({})
        return render_template('user/index.html',event=events)
    elif session['login'] == False:
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))







@app.route('/register', methods=['GET', 'POST'])
def registMember():
    data = request.form
    today = str(date.today())
    allEdt = mongo.db.users.count({})
    aut = allEdt + 1
    autic = 'USR'+str(aut)
    if request.form:
        userid = autic
        name = data['nama']
        email = data['email']
        username = data['username']
        password = data['password']
        noHp = data['nohp']
        jk = data['gender']
        alamat = data['alamat']
        sekolah = data['sekolah']
        role = 'admin'
        newUser = mongo.db.users.insert({
            '_id':userid,
            'foto':'default.jpg',
            'nama':name,
            'email':email,
            'username':username,
            'password':password,
            'noHp':noHp,
            'gender':jk,
            'alamat':alamat,
            'sekolah':sekolah,
            'role':role,
            'verified':False,
            'createdAt':today,
            'updatedAt':today,
            'deleted':False
            })
        if newUser and request.method=='POST':
            return 'Success!'
        else:
            return 'Error!'
    return render_template('register.html')





@app.route('/profile', methods=['GET','POST'])
def profMem():
    return render_template('user/profile.html')
    # prof = mongo.db.users.find({''})








@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('login', False)
   return redirect(url_for('login'))





def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/new/event', methods=['GET', 'POST'])
def newEvent():
    if session['login'] == True:
        events= mongo.db.events.find({})
        data = request.form
        today = str(date.today())
        allEdt = mongo.db.events.count({})
        aut = allEdt + 1
        autic = 'EVNT'+str(aut)
        if request.form:
            eventId = autic
            name = data['eventName']
            if 'image' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['image']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            desc = data['deskripsi']
            ctgr = data['categori']
            prmtr = data['promotor']
            mulai = data['waktuMulai']
            mulaidaftar = data['mulaiDaftar']
            akhir = data['tutupDaftar']
            service = data['service']
            biaya = data['biaya']
            if request.method=='POST':
                NewEvent = mongo.db.events.insert({
                    '_id':eventId,
                    'name':name,
                    'foto':file.filename,
                    'desc':desc,
                    'categori':ctgr,
                    'service':service,
                    'promotor':prmtr,
                    'tanggalMulai':mulai,
                    'openReg':mulaidaftar,
                    'closeReg':akhir,
                    'biaya':biaya,
                    'createdAt':today,
                    'updatedAt':today,
                    'delete':False
                })
                return redirect(url_for('newEvent'))
            else:
                return 'Error 404'
        allEvnt= mongo.db.events.find({})
        return render_template('admin/newEvent.html',event=allEvnt)
    elif session['login'] == False:
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))
    





#
@app.route('/detail/<idevnt>',methods=['POST','GET'])
def detEvnt(idevnt):
    if session['login'] == True:
        evnt = mongo.db.events.find_one({'_id':idevnt})
        return render_template('user/detailEvent.html', event=evnt)
    elif session['login'] == False:
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))
    







#
@app.route('/jadwal/event', methods=['POST','GET'])
def jadEvnt():
    if session['login'] == True:
        jevent= mongo.db.transaction.find({'userid':session['iduser']})
        return render_template('user/jadwalevent.html',data=jevent)
    elif session['login'] == False:
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))
    







@app.route('/delete/event/<_id>/<name>',methods=['GET','DELETE'])
def deletEvnt(_id,name):
    mongo.db.events.remove({'_id':_id,'name':name})
    return redirect(url_for('newEvent'))
    




@app.route('/delete/jadwal/<_id>/<name>',methods=['GET','DELETE'])
def deletJdwl(_id,name):
    mongo.db.transaction.remove({'_id':_id,'eventid':name})
    return redirect(url_for('jadEvnt'))




@app.route('/register/event/<eventid>', methods=['GET','POST'])
def regEvent(eventid):
    allEdt = mongo.db.transaction.count()
    today = str(date.today())
    aut = allEdt + 1
    autic = 'TRC'+str(aut)
    event = mongo.db.events.find_one({'_id':eventid})
    user = mongo.db.users.find_one({'_id':session['iduser']})
    print(user)
    reg = mongo.db.transaction.insert({
        '_id':autic,
        'userid':user['_id'],
        'eventid':eventid,
        'img':event['foto'],
        'namaEvent':event['name'],
        'categori':event['categori'],
        'email':user['email'],
        'nama':user['nama'],
        'sekolah':user['sekolah'],
        'biaya':event['biaya'],
        'lunas':'proses',
        'verified':False,
        'createdAt':today,
        'updatedAt':today,
        'delete':False
    })

    return redirect(url_for('jadEvnt'))








if __name__ == '__main__':
    app.run(debug=True)
