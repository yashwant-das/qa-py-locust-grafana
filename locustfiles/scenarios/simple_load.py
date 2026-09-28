import random
from locust import HttpUser, task, between

class SimpleUser(HttpUser):
    """
    A simple user class that simulates basic API interactions.
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    @task
    def get_root(self):
        """
        Simulates a GET request to the root endpoint.
        """
        self.client.get("/")

    @task(3)  # This task will be executed 3 times more often
    def get_users(self):
        """
        Simulates a GET request to fetch all users.
        """
        self.client.get("/users")

    @task
    def get_user_by_id(self):
        """
        Simulates a GET request to fetch a specific user by a random ID.
        """
        user_id = random.randint(1, 5)  # The target app seeds users 1-5 at startup
        self.client.get(f"/users/{user_id}", name="/users/[id]")

    @task
    def create_user(self):
        """
        Simulates a POST request to create a new user.
        """
        new_user = {
            "name": f"TestUser_{random.randint(100, 999)}",
            "email": f"test.{random.randint(100, 999)}@example.com"
        }
        self.client.post("/users", json=new_user)
