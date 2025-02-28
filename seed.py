from app.__init__ import create_app
from app.extensions import db
from app.Models.userAccountModel import UserAccount  # Import your models

app = create_app('develop')

with app.app_context():
    # Create test users
    user1 = UserAccount(user_username='johnsmith', user_password='1234', user_name='jsmith',user_email='jsmith@mail.com', user_phone='123-123-1234' ,
                 user_address='123 Main St.', user_location='NYC', user_weather='Sunny', user_profile_picture='photo.url')
    user2 = UserAccount(user_username='dansmith', user_password='5678', user_name='dsmith',user_email='dsmith@mail.com', user_phone='567-567-5678' ,
                 user_address='123 Elm St.', user_location='SF', user_weather='Cloudy', user_profile_picture='photo_2.url')



    # Add to session
    db.session.add_all([user1, user2])

    # Commit changes
    db.session.commit()

    print("Test data inserted successfully!")
