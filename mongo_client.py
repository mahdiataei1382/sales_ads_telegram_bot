import pymongo


class AdsMongoClient:
    def __init__(
        self,
        host: str,
        port: int,
        db_name: str = "telegram_bot",
        ads_collection_name: str = "ads",
        categories_collection_name: str = "categories",
    ):
        self.client = pymongo.MongoClient(host, port)
        self.db = self.client.get_database(db_name)
        self.ads_collection = self.db.get_collection(ads_collection_name)
        self.categories_collection = self.db.get_collection(categories_collection_name)

    def add_category(self, category: str):
        Category = {"category": category}
        self.categories_collection.insert_one(Category)

    def get_categories(self) -> list:
        categories = []
        results = self.categories_collection.find()
        for result in results :
            category = result["category"]
            categories.append(category)

        return categories

    def add_advertising(
        self, user_id: int, photo_url: str, category: str, description: str
    ):
        ads = {
            "user_id": user_id,
            "description": description,
            "category": category,
            "photo_url": photo_url,
        }
        self.ads_collection.insert_one(ads)

    def delete_advertising(self, user_id: int, doc_id: str):
        ads_want_deleted = {
            "_id": doc_id ,
            "user_id" : user_id
        }
        self.ads_collection.delete_one(ads_want_deleted)
    def get_ads_by_user_id(self, user_id: int):
        users_ads = []
        query = {"user_id":user_id}
        results = self.ads_collection.find(query)
        for result in results :
            ads = {
                "id": str(result["_id"]),
                "photo_url": result["photo_url"],
                "category": result["category"],
                "description": result["description"],

            }
            users_ads.append(ads)
        return  users_ads

    def get_ads_by_category(self, category: str):
        categoies_ads = []
        query = {"category": category}
        results = self.ads_collection.find(query)
        for result in results:
            ads = {
                "id": str(result["_id"]),
                "photo_url": result["photo_url"],
                "category": result["category"],
                "description": result["description"],

            }
            categoies_ads.append(ads)
        return categoies_ads


if __name__ == "__main__":
    ads_mongo_client = AdsMongoClient("localhost", 27017)
    ads_mongo_client.add_category("کالای دیجیتال")
    ads_mongo_client.add_category("خودرو")
    ads_mongo_client.add_category("موبایل")
    ads_mongo_client.add_advertising(123, "url1", "کالای دیجیتال", "لپ تاپ")
    ads_mongo_client.add_advertising(123, "url2", "خودرو", "پراید")
    ads_mongo_client.add_advertising(123, "url3", "موبایل", "آیفون")
    ads_mongo_client.add_advertising(321, "url4", "کالای دیجیتال", "موس")
    ads_mongo_client.add_advertising(321, "url5", "خودرو", "پژو")
    ads_mongo_client.add_advertising(321, "url6", "موبایل", "سامسونگ")

    print("Categories")
    print(ads_mongo_client.get_categories())

    print("User 123 ads")
    print(ads_mongo_client.get_ads_by_user_id(123))

    print("Ads of category کالای دیجیتال")
    print(ads_mongo_client.get_ads_by_category("کالای دیجیتال"))
