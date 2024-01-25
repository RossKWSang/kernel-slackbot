import pandas as pd

class OutputRestaurant:
    def __init__(self, restaurant_info):
        self.name = restaurant_info[0]
        self.dist = restaurant_info[1]
        self.category = restaurant_info[2]
        self.menu = restaurant_info[3]
        self.average_price = restaurant_info[4]
        self.upvote_score = restaurant_info[5]
        self.downvote_score = restaurant_info[6]

    def __str__(self):
        return f"\"{self.name}\"을 추천드립니다. 거리{self.dist}km에 있는 {self.category}식당이고 " \
               f"\n점심으로 {self.menu}이(가) 먹을만 합니다. " \
               f"\n평균 가격은 1인당 {self.average_price}입니다." \
               f"\n추천개수: {int(self.upvote_score)}" \
               f"\n비추개수: {self.downvote_score}\n"


class Recommendation:
    def __init__(self, raw_data):
        self.data_frame = pd.DataFrame(raw_data, columns=["가게명", "거리", "카테고리", "메뉴", "평균가격", "별점", "리뷰개수"])
        self.data_frame["거리"] = self.data_frame["거리"].astype(float)
        self.data_frame["평균가격"] = self.data_frame["평균가격"].astype(int)
        self.data_frame["별점"] = self.data_frame["별점"].astype(float)

    def get_random(self, num_rest=1):
        return self.data_frame.sample(num_rest)

    def get_categorized_restaurant(self, category, num_rest=1):
        if category not in ["한식", "일식", "중식", "양식", "동남아식"]:
            raise ValueError("카테고리는 '한식', '일식', '중식', '양식', '동남아식' 중에서 선택되어야 합니다.")
        return self.data_frame[self.data_frame["카테고리"] == category].sample(num_rest)

    def get_close_restaurant(self, min_dist, num_rest=1):
        if not isinstance(min_dist, (int, float)):
            raise TypeError("거리는 숫자형 이어야 함니다.")
        return self.data_frame[self.data_frame["거리"] < min_dist].sample(num_rest)

