from pymongo import MongoClient
import random

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.Backend 
job_collection = db.Job_vacancies

# List of available recruiter IDs
recruiter_ids = ["671db5f71200075571683e44", "671db5f81200075571683e48"]  

# Fetch all records in the jobs collection that lack a recruiterId
jobs_without_recruiter = job_collection.find({"recruiterId": {"$exists": False}})

# Update each record with a randomly chosen recruiterId
for job in jobs_without_recruiter:
    random_recruiter_id = random.choice(recruiter_ids)
    job_collection.update_one(
        {"_id": job["_id"]},
        {"$set": {"recruiterId": random_recruiter_id}}
    )
    print(f"Updated job {"_id"} with recruiterId {random_recruiter_id}")

print("All applicable records updated.")
