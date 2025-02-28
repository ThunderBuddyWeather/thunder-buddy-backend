from flask import Blueprint, jsonify
from ..Controllers.userAccountController import (
    save_user_account,
    get_user_account,
    update_user_account,
    delete_user_account,
)
from ..extensions import caching, limiter

user_account_blueprint = Blueprint('user_account', __name__)

@user_account_blueprint.route('/post', methods=['POST'])
@limiter.limit("5 per minute") 
def create_user_account():  
    return save_user_account() 

@user_account_blueprint.route('/get/<int:user_id>' ,methods=['GET'])
@limiter.limit("10 per minute")
@caching.cached(timeout=60) 
def retrieve_user_account(user1_id, user2_id): 
    return get_user_account(user1_id, user2_id)

@user_account_blueprint.route('/put/<int:user_id>', methods=['PUT'])
@limiter.limit("10 per minute")
def update_user_account_route(user1_id, user2_id):  
    return update_user_account(user1_id, user2_id)

@user_account_blueprint.route('/delete/<int:user_id>', methods=['DELETE'])
@limiter.limit("10 per minute")
def delete_user_account_route(user1_id, user2_id): 
    return delete_user_account(user1_id, user2_id)
