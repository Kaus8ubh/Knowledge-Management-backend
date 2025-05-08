from fastapi import HTTPException
from app.models import User
from app.dao import user_dao
from app.utils import create_access_token


class AuthService:
  
    def authenticate_user(self, user_data: User):
        '''
        Usage: This function is used to authenticate user by checking existence or creating new if non existing
        Params: user_data: User Model - name str, email EmailStr, picture str, created_at datetime, last_login datetime
        Return: encoded token str
        '''
        try:
            existing_user = user_dao.find_user_by_email(user_data.email)

            if existing_user:
                user_dao.update_existing_user_last_login(user_data.email)
                user_id = str(existing_user["_id"])
                status = "existing"
            
            else:
                user_id = user_dao.create_user(user_data)
                status = "new"
            
            token_payload = {"userId": user_id,"email": user_data.email,"name": user_data.name, "picture": user_data.picture}
            token = create_access_token(token_payload)

            return{"message": f"User {status}", "token": token}
        except Exception as exception:
            print(f"Error in Authenticating {exception}")
            raise HTTPException(status_code=400, detail={"message": "Something went wrong"})
        
