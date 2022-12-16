import random
from faker import Faker
from locust import HttpUser, task, between


faker = Faker()


class MonitoraUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        response = self.client.post(
            "/api/auth/", json=dict(username="admin", password="admin")
        )
        if not response.status_code == 200:
            raise ValueError
        data = response.json()
        self.token = data.get("token")
        self.search_texts = []
    
    @task
    def test_search(self):
        search_text = random.choice(self.search_texts)
        self.client.post(
            f"/api/search/{search_text}",
            headers=dict(Authorization=f"Token {self.token}"),
        )
