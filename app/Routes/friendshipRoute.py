from flask import Blueprint, jsonify
from ..Controllers.friendshipController import (
    save_friendship,
    get_friendship,
    update_friendship,
    delete_friendship,
)
from ..extensions import caching, limiter

friendship_blueprint = Blueprint('friendship', __name__)

@friendship_blueprint.route('/post', methods=['POST'])
@limiter.limit("5 per minute") 
def create_friendship():  
    return save_friendship() 

@friendship_blueprint.route('/get/<int:user1_id>/<int:user2_id>', methods=['GET'])
@limiter.limit("10 per minute")
@caching.cached(timeout=60) 
def retrieve_friendship(user1_id, user2_id): 
    return get_friendship(user1_id, user2_id)

@friendship_blueprint.route('/put/<int:user1_id>/<int:user2_id>', methods=['PUT'])
@limiter.limit("10 per minute")
def update_friendship_route(user1_id, user2_id):  
    return update_friendship(user1_id, user2_id)

@friendship_blueprint.route('/delete/<int:user1_id>/<int:user2_id>', methods=['DELETE'])
@limiter.limit("10 per minute")
def delete_friendship_route(user1_id, user2_id): 
    return delete_friendship(user1_id, user2_id)
