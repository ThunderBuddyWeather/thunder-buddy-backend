from flask import Blueprint, jsonify
from ..Controllers.notificationController import (
    save_notification,
    get_notification,
    update_notification,
    delete_notification,
)
from ..extensions import caching, limiter

notification_blueprint = Blueprint('notification', __name__)

@notification_blueprint.route('/post', methods=['POST'])
@limiter.limit("5 per minute") 
def create_notification():  
    return save_notification() 

@notification_blueprint.route('/get/notification_id', methods=['GET'])
@limiter.limit("10 per minute")
@caching.cached(timeout=60) 
def retrieve_notification(notification_id): 
    return get_notification(notification_id)

@notification_blueprint.route('/put/notification_id', methods=['PUT'])
@limiter.limit("10 per minute")
def update_notification_route(notification_id):  
    return update_notification(notification_id)

@notification_blueprint.route('/delete/notification_id', methods=['DELETE'])
@limiter.limit("10 per minute")
def delete_notification_route(notification_id): 
    return delete_notification(notification_id)  
