import datetime
import time
import json
from geopy.geocoders import Nominatim

TINDER_URL = "https://api.gotinder.com"
geolocator = Nominatim(user_agent="auto-tinder")
PROF_FILE = "./images/unclassified/profiles.txt"
headers = {
    'app_version': '11.12.0',
    'platform': 'ios',
    "content-type": "application/json",
    "User-agent": "Tinder/7.5.3 (iPhone; iOS 10.3.2; Scale/2.00)",
    "Accept": "application/json",
    "X-Auth-Token": "YOUR TOKEN HERE"
}

def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)

class Person(object):

    def __init__(self, data, api):
        self._api = api

        self.id = data["_id"]
        self.name = data.get("name", "Unknown")

        self.bio = data.get("bio", "")
        self.distance = data.get("distance_mi", 0) / 1.60934

        self.birth_date = datetime.datetime.strptime(data["birth_date"], '%Y-%m-%dT%H:%M:%S.%fZ') if data.get(
            "birth_date", False) else None
        self.gender = ["Male", "Female", "Unknown"][data.get("gender", 2)]

        self.images = list(map(lambda photo: photo["url"], data.get("photos", [])))

        self.jobs = list(
            map(lambda job: {"title": job.get("title", {}).get("name"), "company": job.get("company", {}).get("name")}, data.get("jobs", [])))
        self.schools = list(map(lambda school: school["name"], data.get("schools", [])))

        if data.get("pos", False):
            self.location = geolocator.reverse(f'{data["pos"]["lat"]}, {data["pos"]["lon"]}')


    def __repr__(self):
        return f"{self.id}  -  {self.name} - {self.bio} - ({self.birth_date.strftime('%d.%m.%Y')})"


    def like(self):
        return self._api.like(self.id)

    def dislike(self):
        return self._api.dislike(self.id)

import requests

TINDER_URL = "https://api.gotinder.com"

class tinderAPI():

    def __init__(self, token):
        self._token = token

    def profile(self):
        data = requests.get(TINDER_URL + "/v2/profile?include=account%2Cuser", headers={"X-Auth-Token": self._token}).json()
        return Profile(data["data"], self)

    def matches(self, limit=10):
        data = requests.get(TINDER_URL + f"/v2/matches?count={limit}", headers={"X-Auth-Token": self._token}).json()
        return list(map(lambda match: Person(match["person"], self), data["data"]["matches"]))

    def like(self, user_id):
        data = requests.get(TINDER_URL + f"/like/{user_id}", headers={"X-Auth-Token": self._token}).json()
        return {
            "is_match": data["match"],
            "liked_remaining": data["likes_remaining"]
        }

    def dislike(self, user_id):
        requests.get(TINDER_URL + f"/pass/{user_id}", headers={"X-Auth-Token": self._token}).json()
        return True

    def nearby_persons(self):
        data = requests.get(TINDER_URL + "/v2/recs/core", headers={"X-Auth-Token": self._token}).json()
        return list(map(lambda user: Person(user["user"], self), data["data"]["results"]))

    def get_self(self):
        try:
            data = requests.get(TINDER_URL + '/profile', headers={"X-Auth-Token": self._token}).json()
            print(data["bio"])
            return data
        except requests.exceptions.RequestException as e:
            print("Something went wrong. Could not get your data:", e)

    def change_preferences(self, **kwargs):
        try:
            print(json.dumps(kwargs))
            data = requests.post(TINDER_URL + '/profile', headers=headers, data=json.dumps(kwargs))
            print(data)
            return data.json()
        except requests.exceptions.RequestException as e:
            print("Something went wrong. Could not change your preferences:", e)


if __name__ == "__main__":
    token = headers["X-Auth-Token"]
    api = tinderAPI(token)
    person = api.get_self()
    from datetime import datetime

    
    starttime=time.time()
    while True:
        now = datetime.now()
        current_time = now.strftime("%I:%M %p")
        bio_str = "It's " 
        bio_str += current_time
        bio_str += " and you're on Tinder instead of being with me? \n \n appreciates spicy noodles, good music, and computers. \n Instagram: max_in_situ"
        d = api.change_preferences(bio = bio_str)
        time.sleep(60.0 - ((time.time() - starttime) % 60.0))

    # api.edit_profile_bio("Likes spicy noodles and good music.")
    # while True:
    #     persons = api.nearby_persons()
    #     for person in persons:
    #         print(person)
    #         # person.like()
