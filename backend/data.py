from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import pandas as pd

app = Flask(__name__)
CORS(app)

user_data_file = 'users.json'
company_questions_file = 'company_questions.csv'
company_questions = pd.read_csv(company_questions_file)


if not os.path.exists(user_data_file):
    with open(user_data_file, 'w') as file:
        json.dump({}, file)

def username_exists(username):
    with open(user_data_file, 'r') as file:
        users = json.load(file)
    return username in users

def get_user_companies(username):
    with open(user_data_file, 'r') as file:
        users = json.load(file)
    return users.get(username, {}).get('companies', {})

def get_completed_questions(username):
    with open(user_data_file, 'r') as file:
        users = json.load(file)
    return users.get(username, {}).get('completed-questions', [])

def register_user(username, company_list):
    if username_exists(username):
        return False
    else:
        with open(user_data_file, 'r+') as file:
            users = json.load(file)
            users[username] = {
                "companies": {company: {"total-questions": 0, "remaining-questions": 0} for company in company_list},
                "completed-questions": []
            }
            
            file.seek(0)
            json.dump(users, file, indent=4)
        return True


def login_user(username):
    return username_exists(username)

# user login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username').strip().lower()

    if login_user(username):
        return jsonify({"message": f"Welcome back, {username}!"}), 200
    else:
        return jsonify({"message": "Username not found. Please register first."}), 404

# user registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username').strip().lower()
    company_list = [company.strip().lower() for company in data.get('companies', [])]

    if register_user(username, company_list):
        return jsonify({"message": f"User '{username}' registered successfully."}), 201
    else:
        return jsonify({"message": "Username already exists. Please choose another username."}), 409

# get common questions
@app.route('/common-questions', methods=['POST'])
def get_common_questions():
    data = request.json
    username = data.get('username').strip().lower()

    if not login_user(username):
        return jsonify({"message": "User not found. Please log in first."}), 404

    company_list = get_user_companies(username)

    # filter data based on user's companies
    filtered_df = company_questions[company_questions['Company'].str.lower().isin(company_list.keys())]
    common_questions_filtered = (
        filtered_df.groupby(['Title', 'Leetcode Question Link'])
        .size()
        .reset_index(name='Count')
        .sort_values(by='Count', ascending=False)
    )

    common_questions_json = common_questions_filtered.head(10).to_json(orient='records')
    common_questions_dict = json.loads(common_questions_json)

    return jsonify(common_questions_dict), 200

@app.route('/complete-question', methods=['POST'])
def complete_question():
    data = request.json
    username = data.get('username').strip().lower()
    question = data.get('question').strip()
    company_name = company_questions.loc[company_questions['Title'] == question, 'Company'].values
    
    with open(user_data_file, 'r+') as file:
        users = json.load(file)
        if question in users[username]["completed-questions"]:
            for company in company_name:
                if company in users[username]["companies"]:
                    users[username]["companies"][company]["remaining-questions"] -= 1
            
            users[username]["completed-questions"].remove(question)

        file.seek(0)
        json.dump(users, file, indent=4)
        file.truncate()

    return jsonify({"message": f"Questions updated successfully for user '{username}'."}), 200

@app.route('/remove-question', methods=['POST'])
def remove_question():
    data = request.json
    username = data.get('username').strip().lower()
    question = data.get('question').strip()
    company_name = company_questions.loc[company_questions['Title'] == question, 'Company'].values
    
    with open(user_data_file, 'r+') as file:
        users = json.load(file)
        # users[username]["completed-questions"].remove(question)

        if question in users[username]["completed-questions"]:
            for company in company_name:
                if company in users[username]["companies"]:
                    users[username]["companies"][company]["remaining-questions"] -= 1
            
            users[username]["completed-questions"].remove(question)

        file.seek(0)
        json.dump(users, file, indent=4)
        file.truncate()
    
    return jsonify({"message": f"Questions updated successfully for user '{username}'."}), 200

# update companies with question counts
@app.route('/update-companies', methods=['POST'])
def update_companies():
    data = request.json
    username = data.get('username').strip().lower()
    new_companies = {company.strip().lower(): {"total-questions": 0, "remaining-questions": 0} for company in data.get('companies', [])}

    for company in new_companies.keys():
        total_questions = company_questions[company_questions['Company'].str.lower() == company].shape[0]
        new_companies[company]["total-questions"] = total_questions
        new_companies[company]["remaining-questions"] = total_questions 
    
    with open(user_data_file, 'r+') as file:
        users = json.load(file)
        users[username]['companies'].update(new_companies)
        file.seek(0)
        json.dump(users, file, indent=4)
        file.truncate()

    return jsonify({"message": f"Companies updated successfully for user '{username}'."}), 200

@app.route('/get-companies', methods=['POST'])
def get_companies():
    data = request.json
    username = data.get('username').strip().lower()
    return jsonify({"companies": get_user_companies(username)}), 200

@app.route('/get-questions', methods=['POST'])
def get_questions():
    data = request.json
    username = data.get('username').strip().lower()
    return jsonify({"completed-questions": get_completed_questions(username)}), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)


# need a way to cross the companies off for a user once they've checked off all the questions for a company

'''
Track user progress: Add a progress section to the users.json file that tracks answered questions per company.
Answering a question: Add a new route to mark a question as answered for a specific company.
Check completion: Add logic to check whether all questions for a company are answered and cross off the company once complete.


/get-finished-companies -> returns list of finished companies
/get-common-questions -> stays
/answer-question -> what runs when checkbox is checked
/unanswer-question -> uncheck checkbox


{
    "user1": {
        "companies" : {
            "microsoft" : {
                "total-questions": 10,
                "remaining-questions": 5,
            },
            "google": {
            }
        },
        "completed-questions": []
    }
}

companies-to-questions = {
    "microsoft" : {
        "questions": []
    },
    "google": {
        "questions": []
    }
}

'''