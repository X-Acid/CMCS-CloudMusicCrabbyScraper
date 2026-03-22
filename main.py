import glob
import json
import os
import sys
import time
from urllib.parse import quote

import requests
import win32api
from cefpython3 import cefpython as cef


SEARCH_COOKIE = {"NMTID": "00OuXADISZEZcV3wE3Bhnrj6-iWv_YAAAF_p4zVZQ"}
SEARCH_ENDPOINT = "https://music.163.com/api/search/pc?s={}&offset=0&limit={}&type=1"
HTML_TEMPLATE = (
    '<html><head></head><body><center>'
    '<img src="{cover}" alt="{title}" width="256" height="256"><br/>'
    '<audio controls><source src="{audio}" type="audio/mpeg"></audio><br/>'
    '<font color="blue"><h2>{title}</h2><h3><br/>'
    '#依赖于网易云音乐API的MP3爬虫#<br/>作者:<a href ="https://github.com/X-Acid">X-Acid<a>'
    '</h3></font><center></body></html>'
)


def get_temp_dir(user):
    return os.path.join('C:\\Users', user, 'AppData', 'Local', 'Temp')


def cleanup_temp_files(temp_dir):
    for path in glob.glob(os.path.join(temp_dir, 'cmcs_*.htm')):
        os.remove(path)


def prompt_continue():
    re = str(input('是否继续搜索(Y/N)：')).strip().lower()
    if re == 'y':
        CMCS(exit=0)
        return 0
    if re == 'n':
        print('感谢您的使用！')
        time.sleep(1.5)
        return 1
    print('错误：请输入Y(是)/N(否)')
    return prompt_continue()


def ensure_network(session):
    try:
        session.get('https://www.baidu.com', timeout=5)
    except Exception:
        print('连接异常，请检查您的网络！')
        time.sleep(3.5)
        exit()


def fetch_songs(session, keyword, limit):
    url = SEARCH_ENDPOINT.format(quote(keyword), limit)
    response = session.get(url, cookies=SEARCH_COOKIE, timeout=10)
    payload = json.loads(response.text, strict=False)
    return payload.get("result", {}).get("songs", [])


def build_song_name(song):
    artists = '/'.join(str(artist["name"]) for artist in song["artists"])
    return f'{song["name"]} - {artists}'


def write_song_preview(temp_dir, index, title, cover, song_id):
    audio = f'http://music.163.com/song/media/outer/url?id={song_id}.mp3'
    path = os.path.join(temp_dir, f'cmcs_{index}.htm')
    with open(path, 'w') as f:
        f.write(HTML_TEMPLATE.format(cover=cover, title=title, audio=audio))


def CMCS(exit=1):
    if exit == 1:
        print('======CMCS BY TUDOOU-ETH======')

    user = str(win32api.GetUserName())
    temp_dir = get_temp_dir(user)
    cleanup_temp_files(temp_dir)

    session = requests.Session()
    ensure_network(session)

    keyword = str(input("输入您想搜索的音乐:"))
    x = input("键入输出结果的条数:")

    try:
        x = int(x)
        if x > 100 or x < 1:
            print("很抱歉，搜索结果条数范围为1~100!")
            time.sleep(4)
            exit()
    except Exception:
        print("操作失败，请输入整数！")
        exit()

    songs = fetch_songs(session, keyword, x)
    nml = []

    if not songs:
        print("很抱歉，未找到相关结果")
        time.sleep(2.5)
        if prompt_continue() == 1:
            exit()
        return

    for i, song in enumerate(songs[:x]):
        name = build_song_name(song)
        nml.append(name)
        if int(song["fee"]) == 1:
            print(f'{i + 1}. {name}(vip单曲暂不支持操作)')
            continue

        write_song_preview(temp_dir, i, name, song["album"]["blurPicUrl"], song["id"])
        print(f'{i + 1}. {name}')

    c = input(f"输入您想操作的结果(1~{len(nml)}):")
    try:
        c = int(c)
        if c <= 0 or c > len(nml):
            print(f"操作失败，请输入1~{len(nml)}之间的整数！")
            if prompt_continue() == 1:
                time.sleep(2)
                exit()
            return

        fpth = os.path.join(temp_dir, f'cmcs_{c - 1}.htm').replace('\\', '/')
        if not os.path.isfile(fpth):
            print("操作失败，暂不支持vip单曲！")
            if prompt_continue() == 1:
                time.sleep(2)
                exit()
            return

        sys.excepthook = cef.ExceptHook
        cef.Initialize()
        cef.CreateBrowserSync(url='file:///' + fpth, window_title="歌曲预览/" + nml[c - 1])
        cef.MessageLoop()
        print("操作成功，感谢您的使用！")
        time.sleep(1.25)
        if prompt_continue() == 1:
            time.sleep(2)
            exit()
    except Exception as exc:
        print(exc)
        if prompt_continue() == 1:
            time.sleep(2)
            exit()


if __name__ == '__main__':
    CMCS()
