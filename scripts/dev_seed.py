"""
Development Mode Seed Script for Thunder Buddy Backend
Creates 50 default users with 4-10 random friends each from different US ZIP codes
"""

import logging
import os
import random
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from faker import Faker
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.Models.friendshipModel import Friendship
from app.Models.userAccountModel import UserAccount

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Faker for generating realistic data
fake = Faker('en_US')

# Common password for all users
DEFAULT_PASSWORD = "Password123"

# Output file for saving user information
USER_PROPERTIES_FILE = "generated_users.json"

# Sample ZIP codes from major cities across the USA
US_ZIP_CODES = [
    # Northeast
    ('10001', 'New York, NY'), ('02108', 'Boston, MA'), ('19102', 'Philadelphia, PA'),
    ('07302', 'Jersey City, NJ'), ('20001', 'Washington, DC'),
    # Midwest
    ('60601', 'Chicago, IL'), ('48201', 'Detroit, MI'), ('55401', 'Minneapolis, MN'),
    ('63101', 'St. Louis, MO'), ('44113', 'Cleveland, OH'),
    # South
    ('30303', 'Atlanta, GA'), ('33101', 'Miami, FL'), ('75201', 'Dallas, TX'),
    ('77001', 'Houston, TX'), ('37201', 'Nashville, TN'), ('70112', 'New Orleans, LA'),
    # West
    ('90001', 'Los Angeles, CA'), ('94102', 'San Francisco, CA'), ('98101', 'Seattle, WA'),
    ('80202', 'Denver, CO'), ('89101', 'Las Vegas, NV'), ('85001', 'Phoenix, AZ'),
    ('97201', 'Portland, OR'), ('96813', 'Honolulu, HI'),
    # Additional major cities
    ('78701', 'Austin, TX'), ('27601', 'Raleigh, NC'), ('32801', 'Orlando, FL'),
    ('92101', 'San Diego, CA'), ('46201', 'Indianapolis, IN'), ('73102', 'Oklahoma City, OK'),
    ('67202', 'Wichita, KS'), ('83702', 'Boise, ID'), ('59601', 'Helena, MT'),
    ('87501', 'Santa Fe, NM'), ('84101', 'Salt Lake City, UT'), ('99501', 'Anchorage, AK'),
    ('59715', 'Bozeman, MT'), ('50309', 'Des Moines, IA'), ('45202', 'Cincinnati, OH'),
    ('21202', 'Baltimore, MD'), ('23220', 'Richmond, VA'), ('40202', 'Louisville, KY'),
    ('93721', 'Fresno, CA'), ('95814', 'Sacramento, CA'), ('91101', 'Pasadena, CA'),
    ('55401', 'Minneapolis, MN'), ('97204', 'Portland, OR'), ('33131', 'Miami, FL'),
]


def generate_users(count: int = 50) -> List[UserAccount]:
    """Generate a specified number of random users with data from different ZIP codes"""
    logger.info(f"Generating {count} random users...")
    users = []
    used_usernames = set()
    used_emails = set()

    for _ in range(count):
        # Generate unique username and email
        while True:
            username = fake.user_name() + str(random.randint(1, 999))
            email = f"{username}@{fake.domain_name()}"
            if username not in used_usernames and email not in used_emails:
                used_usernames.add(username)
                used_emails.add(email)
                break

        # Get random ZIP code and location
        zip_code, location = random.choice(US_ZIP_CODES)

        # Generate a simple phone number format to avoid DB constraint errors
        phone_number = (
            f"{random.randint(100, 999)}-{random.randint(100, 999)}-"
            f"{random.randint(1000, 9999)}"
        )

        # Create user with generated data - all users use same hashed password
        user = UserAccount(
            user_username=username,
            user_password=generate_password_hash(DEFAULT_PASSWORD),
            user_name=fake.name(),
            user_email=email,
            user_phone=phone_number,
            user_address=f"{fake.street_address()}, {location} {zip_code}",
            user_location=location,
            user_weather="",  # Weather will be determined by the application
            user_profile_picture=(
                f"https://randomuser.me/api/portraits/"
                f"{random.choice(['men', 'women'])}/{random.randint(1, 99)}.jpg"
            )
        )
        users.append(user)

    return users


def create_friendships(users: List[UserAccount]) -> List[Friendship]:
    """Create random friendships between users, each user having 4-10 friends"""
    logger.info("Creating random friendships between users...")
    friendships = []

    # Create a list of user IDs for reference
    user_ids = [user.user_id for user in users]

    for user in users:
        # Skip if user ID is None (not yet committed to database)
        if user.user_id is None:
            logger.warning("Skipping friendship creation for user with no ID")
            continue

        # Determine number of friends for this user (4-10)
        num_friends = random.randint(4, min(10, len(users) - 1))

        # Get random friends - excluding self
        potential_friend_ids = [uid for uid in user_ids if uid != user.user_id]
        num_friends = min(num_friends, len(potential_friend_ids))

        friend_ids = random.sample(potential_friend_ids, num_friends)

        # Create friendship relationships
        for friend_id in friend_ids:
            # Ensure we don't create duplicate friendships
            if user.user_id < friend_id:  # Only create one direction
                friendship = Friendship(
                    user1_id=user.user_id,
                    user2_id=friend_id,
                    friendship_status=random.choice(['pending', 'accepted'])
                )
                friendships.append(friendship)

    return friendships


def save_users_to_properties_file(users: List[UserAccount]) -> bool:
    """Save the list of users to a JSON file (more compatible with shell scripts)"""
    logger.info(f"Saving {len(users)} users to JSON file: {USER_PROPERTIES_FILE}")

    try:
        import json

        # Create a list of user dictionaries
        user_data = []
        for user in users:
            user_data.append({
                "id": user.user_id,
                "username": user.user_username,
                "name": user.user_name,
                "email": user.user_email,
                "location": user.user_location,
                "password": DEFAULT_PASSWORD
            })

        # Write to JSON file
        with open(USER_PROPERTIES_FILE, 'w') as f:
            json.dump(
                {
                    "metadata": {
                        "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "total_users": len(users),
                        "default_password": DEFAULT_PASSWORD
                    },
                    "users": user_data
                },
                f,
                indent=2
            )

        # Also write a simple text file with usernames and passwords for quick reference
        with open("user_credentials.txt", 'w') as f:
            f.write("# Thunder Buddy Generated User Credentials\n")
            f.write(f"# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("# Format: username,password\n\n")

            for user in users:
                f.write(f"{user.user_username},{DEFAULT_PASSWORD}\n")

        logger.info(f"Successfully saved users to {USER_PROPERTIES_FILE} and user_credentials.txt")
        return True
    except Exception as e:
        logger.error(f"Failed to save users to file: {str(e)}")
        return False


def seed_development_data() -> None:
    """Main function to seed development data"""
    logger.info("Starting development data seeding...")
    app = create_app("development")

    with app.app_context():
        # Check if we already have users (avoid duplicating seed data)
        existing_users = UserAccount.query.count()
        if existing_users >= 50:
            logger.info(f"Database already has {existing_users} users. Skipping seeding.")
            return

        logger.info("Creating users...")
        users = generate_users(50)
        db.session.add_all(users)

        # Commit users to the database to get their IDs before creating friendships
        logger.info("Committing users to database...")
        db.session.commit()

        # Save users to properties file after they've been committed to get their IDs
        save_users_to_properties_file(users)

        logger.info("Creating friendships...")
        friendships = create_friendships(users)
        db.session.add_all(friendships)

        logger.info("Committing friendships to database...")
        db.session.commit()

        logger.info(
            f"Development data seeding completed. Created {len(users)} users and "
            f"{len(friendships)} friendships."
        )


if __name__ == "__main__":
    seed_development_data()
