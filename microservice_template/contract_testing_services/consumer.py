
import json
import os
from typing import Optional

import requests
from faker import Faker
from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel

app = FastAPI()

PRODUCER_ENDPOINT = os.environ["PRODUCER_ENDPOINT"]


class User(BaseModel):
    user_name: str
    email: Optional[str] = None
    name: Optional[str] = None


@app.post("/users/random/{length}")
def create_random_users(length: int):

    fake = Faker()
    users = []
    for _ in range(length):

        user = User(user_name=fake.user_name(),
                    email=fake.company_email(),
                    name=fake.name())
        users.append(user)

        response = requests.post(
            f"{PRODUCER_ENDPOINT}users",
            json=json.loads(user.json()))
        response.raise_for_status()

    return users


handler = Mangum(app)
