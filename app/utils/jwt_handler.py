import jwt
from jwt import InvalidTokenError, DecodeError
from app.config import Config

'''
Name: create_access_token 
Usage: This function is used to create access token for user auth
Params: jwt_payload (which is a dict with userId and email)
Return: encoded token str
'''
def create_access_token(jwt_payload: dict):
    try:
        encoded_jwt = jwt.encode(jwt_payload, Config.SECRET_KEY, algorithm="HS256")
        return encoded_jwt
    except Exception as exception:
        return {"message": "Error generating access token"}

'''
Name: decode_access_token 
Usage: This function is used to decode access token for extracting userId and email
Params: token str
Return: jwt_payload (which is a dict with userId and email)
'''
def decode_access_token(token: str):
    try:
        decoded_jwt_to_payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        return decoded_jwt_to_payload
    except InvalidTokenError:
        return {"message": "JWT is invalid"}
    except DecodeError:
        return {"message": "Error decoding the token"}
    except Exception as exception:
        return {"message": f"Some error occured: {exception}"}
