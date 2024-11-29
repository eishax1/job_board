from pymongo import MongoClient
import bcrypt #for password hashing 

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.Backend      
users = db.users        

user_list = [
          { 
            "name" : "Homer Simpson",
            "username" : "homer",  
            "password" : b"homer_s",
            "email" : "homer@springfield.net",
            "admin" : False,
            "role" : "Recruiter"
          },
          { 
            "name" : "Marge Simpson",
            "username" : "marge",  
            "password" : b"marge_s",
            "email" : "marge@springfield.net",
            "admin" : False,
            "role" : "user"
          },
          { 
            "name" : "Bart Simpson",
            "username" : "bart",  
            "password" : b"bart_s",
            "email" : "bart@springfield.net",
            "admin" : False,
            "role" : "user"
          },        
          { 
            "name" : "Lisa Simpson",
            "username" : "lisa",  
            "password" : b"lisa_s",
            "email" : "lisa@springfield.net",
            "admin" : True,
            "role" : "user"
          },
          { 
            "name" : "Maggie Simpson",
            "username" : "maggie",  
            "password" : b"maggie_s",
            "email" : "maggie@springfield.net",
            "admin" : False,
            "role" : "Recruiter"
          }
       ]

for new_user in user_list:
      new_user["password"] = bcrypt.hashpw(new_user["password"], bcrypt.gensalt())
      users.insert_one(new_user)
