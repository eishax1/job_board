from flask import Flask, make_response, jsonify, request, session
import re
import jwt
import bcrypt
from pymongo import MongoClient
from bson.objectid import ObjectId
from decorators.token_utils import create_token
from decorators.admin_or_recruiter import admin_or_recruiter_required

# Import custom decorators
from decorators.admin_decorator import admin_required
from decorators.recruiter import recruiter_required

# App Configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

# MongoDB Setup
client = MongoClient("mongodb://127.0.0.1:27017")
db = client.Backend
job_collection = db.Job_vacancies
users = db.users
blacklist = db.blacklist


#-------------------------------------Authentication routes---------------------------------------------

@app.route('/api/v1.0/login', methods=['GET']) 
def login():
    if 'user_id' in session:
        return make_response(jsonify({'message': 'You are already logged in. Please log out before attempting to log in again.'}), 409)
    
    auth = request.authorization
    if auth:
        user = users.find_one({'username': auth.username})
        if user is not None:
            if bcrypt.checkpw(bytes(auth.password, 'UTF-8'), user["password"]):
            
                token = create_token(user)
                session.clear()
                # Set the session to indicate the user is logged in
                session['user_id'] = str(user['_id'])
                return make_response(jsonify({'message': f'Welcome back, {user["username"]}! You have successfully logged in.', 'token created': token}), 201)
            else:
                return make_response(jsonify({'message': 'Invalid password. Please try again.'}), 401)
        else:
            return make_response(jsonify({'message': 'No user found with this username. Please check and try again.'}), 401)
    
    return make_response(jsonify({'message': 'Authentication is required to access this resource.'}), 401)

@app.route('/api/v1.0/logout', methods=["GET"])
def logout():
    token = request.headers.get('x-access-token')
    if token:
        # Add the token to the blacklist
        blacklist.insert_one({'token': token})
    # Clear the entire session
    session.clear()
    return make_response(jsonify({'message': 'You have successfully logged out. See you next time!'}), 200)

#-----------------------------Job routes-----------------------------------------------------

@app.route("/api/v1.0/jobs", methods=["GET"])
def show_all_vacancies():
    # Set default page number and page size
    page_num, page_size = 1, 10
    
   
    if request.args.get('pn'):
        page_num = int(request.args.get('pn'))
        
    if request.args.get('limit'):
        page_size = int(request.args.get('limit'))
        if page_size > 20:
            return make_response(jsonify({"error": "Invalid value for 'limit'. Please ensure it does not exceed 20."}), 400)
    
    # Calculate the starting point for pagination
    page_start = page_size * (page_num - 1)


    filters = {}
    
    # Get filters from query parameters
    employment_type = request.args.get('employment_type')
    seniority_level = request.args.get('seniority_level')
    
    if employment_type:
        filters['employment_type'] = employment_type
    if seniority_level:
        filters['seniority_level'] = seniority_level

    data_to_return = []
    
    for job in job_collection.find(filters).skip(page_start).limit(page_size):
        job['_id'] = str(job['_id'])
        data_to_return.append(job)
    
    return make_response(jsonify(data_to_return), 200)

@app.route("/api/v1.0/jobs/<string:job_id>", methods=["GET"])
def show_one_vacancy(job_id):
    # Validate that the id is a 24-character hexadecimal string
    if re.fullmatch(r"^[a-fA-F0-9]{24}$", job_id):
        try:
            # Attempt to find the job by its ObjectId
            job = job_collection.find_one({'_id': ObjectId(job_id)})
            
            if job is not None:
                # Convert the ObjectId to a string for JSON serialization
                job['_id'] = str(job['_id'])
                return make_response(jsonify(job), 200)
            else:
                return make_response(jsonify({"error": "The job you requested could not be found. Please check the job ID and try again."}), 404)
    
        except Exception as e:
            return make_response(jsonify({"error": f"An error occurred while retrieving the job: {str(e)}"}), 400)
        
    else:
        return make_response(jsonify({"error": "The job ID format is invalid. Please ensure it is a 24-character hexadecimal string."}), 400)

@app.route("/api/v1.0/jobs", methods=["POST"])
@recruiter_required
def add_job():
    # Retrieve the token from headers and decode it
    token = request.headers['x-access-token']
    decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
    
    # Extract recruiter ID from the decoded token
    recruiter_id = decoded_token['user_id']  
    if "job_title" in request.form and \
       "company_name" in request.form and \
       "job_description" in request.form and \
       "employment_type" in request.form:
        
        new_job = {
            "job_title": request.form["job_title"],
            "company_name": request.form["company_name"],
            "job_description": request.form["job_description"],
            "employment_type": request.form["employment_type"],
            "seniority_level": request.form.get("seniority_level", ""),
            "industries": request.form.getlist("industries"),
            "posted_info": {
                "posted_date": request.form.get("posted_info[posted_date]", ""),
                "num_applicants": int(request.form.get("posted_info[num_applicants]", 0))
            },
            "recruiterId": recruiter_id  # Add recruiter ID to job document
        }

        new_job_id = job_collection.insert_one(new_job).inserted_id
        new_job_link = f"http://localhost:5000/api/v1.0/jobs/{new_job_id}"

        return make_response(jsonify({"message": "New job vacancy created successfully!", "url": new_job_link}), 201)
    
    else:
        return make_response(jsonify({"error": "Some required form data is missing. Please ensure all fields are filled out."}), 400)

@app.route("/api/v1.0/jobs/<string:job_id>", methods=["PUT"])
@recruiter_required
def edit_job(job_id, user_id):
    if not re.fullmatch(r"^[a-fA-F0-9]{24}$", job_id):
        return make_response(jsonify({"error": "The job ID format is invalid. Please provide a valid job ID."}), 400)

    # Retrieve the job from the database
    job = job_collection.find_one({"_id": ObjectId(job_id)})

    # Check if the job exists
    if not job:
        return make_response(jsonify({"error": "The job you are trying to edit does not exist."}), 404)
    
    # Check if the current user is the job owner
    if job['recruiterId'] != user_id:  
        return make_response(jsonify({"error": "You are not authorized to edit this job."}), 403)

    # Check if required fields are in the request form
    if "job_title" in request.form and \
       "company_name" in request.form and \
       "job_description" in request.form and \
       "employment_type" in request.form:
        
        update_data = {
            "$set": {
                "job_title": request.form["job_title"],
                "company_name": request.form["company_name"],
                "job_description": request.form["job_description"],
                "employment_type": request.form["employment_type"],
                "seniority_level": request.form.get("seniority_level", ""),
                "industries": request.form.getlist("industries"), 
                "posted_info": {
                    "posted_date": request.form.get("posted_info[posted_date]", ""),
                    "num_applicants": int(request.form.get("posted_info[num_applicants]", 0))
                }
            }
        }

        # Update the job in the database
        job_collection.update_one({"_id": ObjectId(job_id)}, update_data)

        return make_response(jsonify({"message": "Job vacancy updated successfully!"}), 200)
    
    return make_response(jsonify({"error": "Some required form data is missing. Please ensure all fields are filled out."}), 400)

@app.route("/api/v1.0/jobs/<string:job_id>", methods=["DELETE"])
@admin_or_recruiter_required
def delete_job(job_id, user_id):
    if not re.fullmatch(r"^[a-fA-F0-9]{24}$", job_id):
        return make_response(jsonify({"error": "The job ID format is invalid. Please provide a valid job ID."}), 400)


    job = job_collection.find_one({"_id": ObjectId(job_id)})
    if not job:
        return make_response(jsonify({"error": "The job you are trying to delete does not exist."}), 404)


    if job['recruiterId'] != user_id:
        return make_response(jsonify({"error": "You are not authorized to delete this job."}), 403)

    # Proceed to delete the job from the database
    job_collection.delete_one({"_id": ObjectId(job_id)})
    return make_response(jsonify({"message": "Job vacancy deleted successfully!"}), 200)

  #---------------------------- Analytics Routes---------------------------------------------------
    
@app.route("/api/v1.0/jobs/analytics", methods=["GET"])
@admin_or_recruiter_required
def job_analytics():
    """
    An endpoint to provide analytics on job postings, such as average number of applicants.
    """
    #Get seniority filter from query params
    seniority = request.args.get('seniority')  
    
    #Calculate average number of applicants per job
    pipeline = [
        {
            '$match': {
                'seniority_level': seniority  #Filter by seniority if provided
            } if seniority else {}
        },
        {
            '$group': {
                '_id': "$seniority_level",  #Group by seniority_level
                'average_applicants': {'$avg': "$posted_info.num_applicants"}
            }
        },
        {
            '$project': {
                'seniority': '$_id',  
                'average_applicants': 1,  
                '_id': 0  
            }
        }
    ]
    # Execute the aggregation
    result = list(job_collection.aggregate(pipeline))
    
    # Prepare the analytics data
    analytics_data = result[0] if result else {"average_applicants": 0}

    return make_response(jsonify(analytics_data), 200)

@app.route("/api/v1.0/jobs/distinct/<string:field_name>", methods=["GET"])
@admin_required
def get_distinct_values(field_name):
    try:
        # Retrieve distinct values for the specified field
        distinct_values = job_collection.distinct(field_name)

        # Return the distinct values as a JSON response
        return make_response(jsonify({"Comapanies registered on the portal": distinct_values}), 200)

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)
    

    #---------------------------------------------- Admin Routes----------------------------------------------

@app.route('/api/v1.0/admin/users', methods=['GET'])
@admin_required
def view_all_users():
    all_users = []
    for user in users.find():
        user['_id'] = str(user['_id'])  
        del user['password']  #Exclude password from response for security
        all_users.append(user)
    return make_response(jsonify(all_users), 200)


@app.route('/api/v1.0/admin/users/<string:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    result = users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 1:
        return make_response(jsonify({"message": "User account deleted successfully"}), 200)
    return make_response(jsonify({"error": "User not found"}), 404)

if __name__ == '__main__':
    app.run(debug=True)

