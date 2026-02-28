from locust import HttpUser, task, between
import random

class StudentUser(HttpUser):
    # 模擬學生在選填時的思考時間 (1到3秒)
    wait_time = between(1, 3)
    
    # 假設測試時使用固定的帳號 (為了測試方便)
    def on_start(self):
        """測試開始時先執行登入，取得 token"""
        response = self.client.post("/login", json={
            "student_id": "114001",
            "password": "123456"
        })
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None

    @task(3) # 執行機率較高 (3倍)
    def submit_choice(self):
        """模擬選填志願"""
        if self.token:
            choice = random.choice([1, 2, 3, 4])
            self.client.post("/submit", json={"choice": choice}, headers=self.headers)

    @task(1) # 執行機率較低 (1倍)
    def view_page(self):
        """模擬瀏覽頁面"""
        self.client.get("/")