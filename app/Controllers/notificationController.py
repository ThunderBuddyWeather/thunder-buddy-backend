from flask import jsonify, request
from ..extensions import db
from ..Models.notificationModel import Notification 

def save_notification():
    data = request.get_json()
    if not data or not all(k in data for k in ('notification_id','user_id', 'notification_message', 'delivery_status', 'time_created')):
        return jsonify({"message": "Invalid input"}), 400
    
    new_notification = Notification(
        notification_id=data['notification_id'],
        user_id=data['user_id'],
        notification_message=data['notification_message'],
        delivery_status = data['delivery_status']
    )
    db.session.add(new_notification)
    db.session.commit()
    return jsonify({"message": "notification saved"}), 201

def get_notification(notification_id):  
    notification = Notification.query.filter_by(notification_id == notification_id).first()
    if notification is None:
        return jsonify({"message": "notification not found"}), 404

    return jsonify({
        'notification_id': notification.notification_id,
        'user_id': notification.user_id,
        'notification_status': notification.notification_status,
        'delivery_status': notification.delivery_status
    }), 200

def update_notification(notification_id): 
    notification = Notification.query.filter_by(notification_id = notification_id).first()   
    if notification is None: 
        return jsonify({"message": "notification not found"}), 404

    data = request.get_json()
    if not data or 'notification_status' not in data:
        return jsonify({"message": "Invalid input"}), 400

    if 'notification_status' in data:
        notification.notification_status = data['notification_status']

    db.session.commit()
    return jsonify({"message": "notification updated"}), 200

def delete_notification(notification_id):  
    notification = Notification.query.filter_by(notification_id == notification_id).first()
    if notification is None:
        return jsonify({"message": "notification not found"}), 404

    db.session.delete(notification)
    db.session.commit()
    return jsonify({"message": "notification deleted"}), 200
