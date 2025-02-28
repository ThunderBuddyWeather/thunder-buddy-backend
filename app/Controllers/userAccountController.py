from flask import jsonify, request
from ..extensions import db
from werkzeug.security import generate_password_hash
from ..Models.userAccountModel import UserAccount 

def save_user_account():
    data = request.get_json()
    required_fields = [
        'user_username', 'user_password', 'user_name', 'user_email', 
        'user_phone', 'user_address', 'user_location', 
        'user_weather', 'user_profile_picture'
    ]

    if not data or not all(field in data for field in required_fields):
        return jsonify({"message": "Invalid input"}), 400

    new_account = UserAccount(
        user_username=data['user_username'],
        user_password=generate_password_hash(data['user_password']),  
        user_name=data['user_name'],
        user_email=data['user_email'],
        user_phone=data['user_phone'],
        user_address=data['user_address'],
        user_location=data['user_location'],
        user_weather=data['user_weather'],
        user_profile_picture=data['user_profile_picture']
    )
    
    db.session.add(new_account)
    db.session.commit()
    return jsonify({"message": "User account saved"}), 201


def get_user_account(user_id):  
    account = UserAccount.query.filter_by(UserAccount.user_id==user_id).first()  
    if account is None:
        return jsonify({"message": "User account not found"}), 404

    return jsonify({
        'user_id': account.user_id,
        'user_username': account.user_username,
        'user_name': account.user_name,
        'user_email': account.user_email,
        'user_phone': account.user_phone,
        'user_address': account.user_address,
        'user_location': account.user_location,
        'user_weather': account.user_weather,
        'user_profile_picture': account.user_profile_picture,
        'user_time_created': account.user_time_created.strftime('%Y-%m-%d %H:%M:%S')
    }), 200


def update_user_account(user_id): 
    account = UserAccount.query.filter_by(UserAccount.user_id==user_id).first()  
    if account is None: 
        return jsonify({"message": "User account not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid input"}), 400

    if 'user_username' in data:
        account.user_username = data['user_username']
    if 'user_password' in data:
        account.user_password = generate_password_hash(data['user_password']) 
    if 'user_name' in data:
        account.user_name = data['user_name']
    if 'user_email' in data:
        account.user_email = data['user_email']
    if 'user_phone' in data:
        account.user_phone = data['user_phone']
    if 'user_address' in data:
        account.user_address = data['user_address']
    if 'user_location' in data:
        account.user_location = data['user_location']
    if 'user_weather' in data:
        account.user_weather = data['user_weather']
    if 'user_profile_picture' in data:
        account.user_profile_picture = data['user_profile_picture']

    db.session.commit()
    return jsonify({"message": "User account updated"}), 200


def delete_user_account(user_id):  
    account = UserAccount.query.filter_by(UserAccount.user_id==user_id).first()  
    if account is None:
        return jsonify({"message": "User account not found"}), 404

    db.session.delete(account)
    db.session.commit()
    return jsonify({"message": "User account deleted"}), 200
