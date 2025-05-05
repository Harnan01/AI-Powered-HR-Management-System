from pymongo import MongoClient

# Connect to the MongoDB server
client = MongoClient('localhost', 27017)
db = client['shortlisting_db']

# Get the collection
collection = db['shortlisting_shortlistedcandidate']

# Remove the shortlisted_at column from all documents
collection.update_many(
    {},
    {"$unset": {"shortlisted_at": ""}}
)

# Update the score field type to string
collection.update_many(
    {},
    [
        {"$set": {"score": {"$toString": "$score"}}}
    ]
)

print("shortlisted_at column removed and score field type updated to string.")
