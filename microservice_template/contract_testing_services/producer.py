
import os
from typing import Optional

from pydantic import BaseModel
from fastapi import FastAPI, Response, status
from mangum import Mangum
from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model

TABLE_NAME = os.environ["TABLE_NAME"]
TABLE_REGION = os.environ["TABLE_REGION"]


class UserModel(Model):
    """
    A DynamoDB User
    """
    class Meta:
        table_name = TABLE_NAME
        region = TABLE_REGION

    user_name = UnicodeAttribute(hash_key=True)
    email = UnicodeAttribute()
    name = UnicodeAttribute()


class User(BaseModel):
    user_name: str
    email: Optional[str] = None
    name: Optional[str] = None


app = FastAPI()


@app.get("/users/{user_name}")
def read_user(user_name: str, response: Response):
    try:
        user = UserModel.get(user_name)
        print(user)

        return User(user_name=user.user_name, email=user.email, name=user.name)
    except UserModel.DoesNotExist:
        print("User does not exist")
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "user not found"}


@app.post("/users")
def create_user(user: User):
    db_user = UserModel(user_name=user.user_name, email=user.email, name=user.name)
    db_user.save()

    return user


handler = Mangum(app)
