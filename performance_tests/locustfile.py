from locust import HttpUser, task, between

class WebUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def get_all_products(self):
        self.client.get("/products")

    @task
    def get_products_by_criteria(self):
        self.client.get("/products?priceMin=0&category=Jewellery&search=s&maxRating=4&size=XL&size=M&minRating=0&priceMax=2000000&ageGender=Babies")

    @task
    def get_all_categories(self):
        self.client.get("/categories")

    @task
    def get_all_reviews(self):
        self.client.get("/reviews")