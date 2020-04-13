from PIL import Image, ImageDraw, ImageFont
import requests
from config import *
import json
from io import BytesIO
import datetime


def printJsonPretty(objectJ):
    print(json.dumps(json.loads(objectJ), indent=4))


def getLikes(posts):
    likes = {}
    for post_id in posts:
        response = requests.get(VK_API_URL + 'likes.getList?type=post&owner_id=' + GROUP_ID
                                + '&item_id=' + str(post_id)
                                + '&friend_only=0'
                                + '&count=125'
                                + VK_SUFFIX)
        # print(response.url)
        # парсим json с лайками
        r = json.loads(response.content)['response']
        # print(r)
        for like in range(r['count']):
            id = r['items'][like]
            if id in likes:
                likes[id] += 1
            else:
                likes[id] = 1
    # print(likes)
    return likes


def getPosts(count=MAX_POSTS):
    response = requests.get(VK_API_URL + 'wall.get?owner_id=' + GROUP_ID + '&count=' + str(count) + VK_SUFFIX)
    # printJsonPretty(response.content)
    return json.loads(response.content)['response']


def calculateRating():
    rating = []
    p = getPosts()
    posts = [p['items'][i]['id'] for i in range(p['count'])]
    likes = getLikes(posts)
    for key in likes:
        rating.append((likes[key], key))
    rating = sorted(rating, reverse=True)
    rating = rating[:min(len(rating), MAX_PEOPLES)]
    return rating
    # print(posts)


def getAvatar(url):
    response = requests.get(url)
    return BytesIO(response.content)


def getUsers(ids):
    response = requests.get(VK_API_URL + 'users.get?user_ids=' + ids
                            + '&fields=photo_100,photo_50'
                            + '&name_case=nom'
                            + VK_SUFFIX,
                            headers={'Accept-Language': 'ru,en-us'})
    return json.loads(response.content)['response']


def applyImage(img):
    response = requests.get(VK_API_URL +
                            'photos.getOwnerCoverPhotoUploadServer' +
                            '?group_id=' + GROUP_ID[1:] +
                            '&crop_x=0&crop_y=0' +
                            '&crop_x2=' + str(RESOLUTION[0]) +
                            '&crop_y2=' + str(RESOLUTION[1]) +
                            VK_GROUP_SUFFIX)
    upload_url = json.loads(response.content)['response']['upload_url']
    files = {'photo': img}
    headers = {'Content-type': 'multipart/form-data'}
    response = requests.post(upload_url, files=files)
    r = json.loads(response.content)
    hash = r['hash']
    photo = r['photo']
    # print(hash, photo)
    response = requests.get(VK_API_URL +
                            'photos.saveOwnerCoverPhoto' +
                            '?hash=' + hash +
                            '&photo=' + photo +
                            VK_GROUP_SUFFIX)
    # printJsonPretty(response.content)


def main():
    # print(FONT['path'])
    # считаем рейтинг юзеров, возвращается словарь типа {rating: id, ...}
    rate = calculateRating()
    # приводим к виду 'id,id,id,id,...'
    ids = ','.join([str(i[1]) for i in rate])
    # получаем данные по юзерам, принимаем json
    users = getUsers(ids)
    # подгружаем шрифт
    fnt = ImageFont.truetype(FONT['path'], FONT['size'])
    # вторичный шрифт
    _fnt = ImageFont.truetype(FONT['path'], FONT['size'] + 60)
    # создаём задний фон с заливкой одним цветом
    background = Image.new('RGB', RESOLUTION, BACKGROUND_COLOR)
    drw = ImageDraw.Draw(background)
    drw.text((190, 15), 'Самые активные:', font=fnt, fill=(0, 0, 0))
    # print(users)
    for i, _user in enumerate(users):
        print(_user)
        ava = Image.open(getAvatar(_user['photo_50']), 'r')
        ava = ava.crop((0, 0, 50, 50))
        background.paste(ava, (180, 85 + i * 60))
        # drw.bitmap((200, 90 + i * 60), ava)
        drw.text((240, 75 + i * 60), str(i + 1) + '. ' + str(_user['first_name'] + ' ' + _user['last_name']), font=fnt,
                 fill=(0, 0, 0))
    # background.show()
    # Отрисовка даты
    date = datetime.date.today().strftime('%d.%m.%Y')
    drw.text((1000, 50), date, font=_fnt, fill=(0, 0, 0))

    # Отрисовка времени
    # time = datetime.datetime.now().strftime('%H:%M')
    # drw.text((1000, 220), time, font=fnt, fill=(0,0,0))

    # Линия по центру
    # drw.line((745, 0, 745, 400), fill=(255, 0, 0), width=20)
    # print(background.size)
    background.save('1.png', 'PNG')
    q = open('1.png', 'rb')
    applyImage(q)
    # print(rate)
    # background.show()


if __name__ == '__main__':
    main()
