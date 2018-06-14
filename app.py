#import neccesary packages
from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy

#configure flask and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://<username>:<password>@localhost/<database name>'
db = SQLAlchemy(app)

#declare models
class doctor(db.Model):
    __tablename__ = 'doctor'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(255))
    reviews = db.relationship('review', backref = 'doctor', lazy = True)

class review(db.Model):
    __tablename__ = 'review'
    id = db.Column('id', db.Integer, primary_key=True)
    doctor_id = db.Column('doctor_id', db.Integer, db.ForeignKey('doctor.id'))
    description = db.Column('description', db.String(255))

#get all doctors and reviews
@app.route("/doctors", methods = ['GET'])
def get_all():


    #get all
    if request.method == 'GET':

        # list variables to hold doctor or reviews b/c jsonify requires list
        doctor_hold = []
        review_hold = []


        #fill variables with information from both tables
        all_doctor = doctor.query.all()
        all_review = review.query.all()

        #length variables
        doclen = len(all_doctor)
        revlen = len(all_review)

        #loop through doctor table
        for index1 in range(0,doclen):

            #get reviews for current doctor in loop
            review_curr = review.query.filter_by(doctor_id = all_doctor[index1].id).all()
            #length variable
            length = len(review_curr)
            #check if reviews exist
            if length > 0:
                #loop through reviews
                for index in range(0,length):
                    #fill hold with reviews in order
                    review_hold.append({'id':review_curr[index].id, 'doctor_id':review_curr[index].doctor_id, 'description':review_curr[index].description})

            #add reviews to doctor hold
            doctor_hold.append({'name':all_doctor[index1].name, 'id':all_doctor[index1].id, 'reviews':review_hold})
            #clear hold for next loop pass
            review_hold = []

        #return all, if empty return 204
        if doctor_hold:
            return jsonify(doctor_hold)
        else:
            return jsonify({'status': 204})



#add doctor
@app.route("/doctors", methods = ['POST'])
def add_doctor():

    #create doctor
    if request.method == 'POST':

        #format request as json
        request_data = request.get_json()

        #verify request contains correct values
        if('doctor' in request_data) & ('name' in request_data['doctor']):
            #get name and create doctor
            name = request_data['doctor']['name']
            doctor_add = doctor(name = name)

            #add doctor to database
            db.session.add(doctor_add)
            db.session.commit()

            #return success
            return jsonify({'status':200})

        else:
            #return failed
            return jsonify({'status':400})

#add review
@app.route("/doctors/<id>/reviews", methods = ['POST'])
def add_review(id):

    #create review
    if request.method == 'POST':

        #format reuqest as json
        request_data = request.get_json()

        #verify request contains correct values
        if('review' in request_data) & ('description' in request_data['review']):
            #get name and create review
            description = request_data['review']['description']
            review_add = review(doctor_id = id, description = description)

            #add review to database
            db.session.add(review_add)
            db.session.commit()

            #return success
            return jsonify({'status':200})

        else:
            #return failed
            return jsonify({'status':400})

#get specific doctor
@app.route("/doctors/<id>", methods = ['GET'])
def get_doctor(id):

    #get doctor from id
    if request.method == 'GET':

        # list variables to hold doctor or reviews b/c jsonify requires list
        doctor_hold = []
        review_hold = []

        #fill variables with query
        doctor_sel = doctor.query.get(id)

        if doctor_sel:
            review_sel = review.query.filter_by(doctor_id = id).all()
            #set length variable
            length = len(review_sel)

            #check for review (must be positive)
            if length > 0:
                #loop through reviews
                for index in range(0,length):
                    #fill hold with reviews in order
                    review_hold.append({'id':review_sel[index].id, 'doctor_id':review_sel[index].doctor_id, 'description':review_sel[index].description})

            #add reviews to doctor hold
            doctor_hold.append({'name':doctor_sel.name, 'id':doctor_sel.id, 'reviews':review_hold})

            #return doctor
            return jsonify(doctor_hold)
        #return 204 if not in table
        else:
            return jsonify({'status':204})

#get review
@app.route("/doctors/<docid>/reviews/<revid>", methods = ['GET'])
def get_review(docid,revid):

    #get review from id
    if request.method == 'GET':

        #list to hold review
        review_hold = []

        #fill variables with query
        doctor_sel = doctor.query.get(docid)
        review_sel = review.query.get(revid)

        if review_sel:

            #fill hold with correct order and child
            review_hold.append({'description': review_sel.description, 'id':review_sel.id, 'doctor_id':review_sel.doctor_id, 'doctor': {'id': doctor_sel.id, 'name':doctor_sel.name}})

            return jsonify(review_hold)

        else:
            return jsonify({'status':204})

#delete specified doctor
@app.route("/doctors/<id>", methods = ['DELETE'])
def delete_doctor(id):

    #get doctor to delete
    if request.method == 'DELETE':

        #fill variables with query
        doctor_sel = doctor.query.get(id)
        review_sel = review.query.filter_by(doctor_id = id).all()
        #length variable
        length = len(review_sel)

        #check if doctor exists
        if doctor_sel:
            #check if there are reviews
            if length > 0:

                #delete each review
                for index in range(0,length):
                    db.session.delete(review_sel[index])

            #delete doctor
            db.session.delete(doctor_sel)
            db.session.commit()

            return jsonify({'status': 200})

        #doctor does not exist
        else:
            return jsonify({'status':400})

#delete specified review
@app.route("/doctors/<docid>/reviews/<revid>", methods = ['DELETE'])
def delete_review(docid,revid):
    #find review
    if request.method == 'DELETE':
        #set using query
        review_sel = review.query.filter_by(doctor_id = docid, id = revid).first()

        #if exists
        if review_sel:
            db.session.delete(review_sel)
            db.session.commit()

            return jsonify({'status':200})

        #if review does not exist
        else:
            return jsonify({'status':400})

#main method, set debug mode, port 5000
if __name__ == "__main__":
    app.run(debug=True, port = 5000)
