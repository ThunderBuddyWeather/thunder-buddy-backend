from flask import jsonify, request
from ..extensions import db
from ..Models.groupModel import Group 

def save_group():
    data = request.get_json()
    if not data or not all(k in data for k in ('group_id', 'group_name', 'group_members', 'time_created')):
        return jsonify({"message": "Invalid input"}), 400
    
    new_group = Group(
        group_id=data['group_id'],  
        group_name=data['group_name'],
        group_members=data['group_members']
    )
    db.session.add(new_group)
    db.session.commit()
    return jsonify({"message": "group saved"}), 201

def get_group(group_id):  
    group = Group.query.filter_by(group_id == group_id).first()
    if group is None:
        return jsonify({"message": "group not found"}), 404

    return jsonify({
        'group_id': group.user1_id,
        'group_name': group.group_name,
        'group_members': group.group_members,
        'time_created': group.time_created
    }), 200

def update_group(group_id): 
    group = Group.query.filter_by(group_id == group_id).first()
    if group is None: 
        return jsonify({"message": "group not found"}), 404

    data = request.get_json()
    if not data or 'group_status' not in data:
        return jsonify({"message": "Invalid input"}), 400

    if 'group_status' in data:
        group.group_status = data['group_status']

    db.session.commit()
    return jsonify({"message": "group updated"}), 200

def delete_group(group_id):  
    group = Group.query.filter_by(group_id == group_id).first()
    if group is None:
        return jsonify({"message": "group not found"}), 404

    db.session.delete(group)
    db.session.commit()
    return jsonify({"message": "group deleted"}), 200
