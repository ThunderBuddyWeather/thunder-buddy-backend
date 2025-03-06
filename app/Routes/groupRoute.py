from flask import Blueprint, jsonify
from ..Controllers.groupController import (
    save_group,
    get_group,
    update_group,
    delete_group,
)
from ..extensions import caching, limiter

group_blueprint = Blueprint('group', __name__)

@group_blueprint.route('/post', methods=['POST'])
@limiter.limit("5 per minute") 
def create_group():  
    return save_group() 

@group_blueprint.route('/get/group_id', methods=['GET'])
@limiter.limit("10 per minute")
@caching.cached(timeout=60) 
def retrieve_group(group_id): 
    return get_group(group_id)

@group_blueprint.route('/put/group_id', methods=['PUT'])
@limiter.limit("10 per minute")
def update_group_route(group_id):  
    return update_group(group_id)

@group_blueprint.route('/delete/group_id', methods=['DELETE'])
@limiter.limit("10 per minute")
def delete_group_route(group_id): 
    return delete_group(group_id)
