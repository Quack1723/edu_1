import numpy as np
import random
import streamlit as st
from pathlib import Path
import json
import os
import time
import requests
from tqdm import tqdm
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import pandas as pd

def get_lat_lon_from_address(address_l):
    """
    address_lにlistの形で住所を入れてあげると、latlonsという入れ子上のリストで緯度経度のリストを返す関数。
    >>>>get_lat_lon_from_address(['東京都文京区本郷7-3-1','東京都文京区湯島３丁目３０−１'])
    [['35.712056', '139.762775'], ['35.707771', '139.768205']]
    """
    url = 'http://www.geocoding.jp/api/'
    latlons = []
    for address in tqdm(address_l):
        payload = {"v": 1.1, 'q': address}
        r = requests.get(url, params=payload)
        ret = BeautifulSoup(r.content,'lxml')
        if ret.find('error'):
            raise ValueError(f"Invalid address submitted. {address}")
        else:
            lat = ret.find('lat').string
            lon = ret.find('lng').string
            latlons.append([lat,lon])
            time.sleep(10)
    return latlons


def make_dic(sample_lat, sample_w):
    dic_lat = {}
    dic_w = {}
    for i in range(len(sample_lat)):
        dic_lat[i] = sample_lat[i][0]
        dic_w[i] = sample_w[i]

    return dic_lat, dic_w

def get_integral_value_combination(dic_w, target):
    def a(idx, l, r, I, j, t):
        if t == sum(l):
            r.append(l)
            j.append(I)
        elif t < sum(l):
            return
        for u in range(idx, len(dic_w)):
            a((u + 1), l + [dic_w[u]], r, I+[u], j, t)
        return r,j
    return a(0, [], [], [], [], target)


def make_P_list(Index, dic_lat, W_choice, S, G):
    P = []
    P_W = []
    for pat in range(len(Index)):
        D2 = {}
        W2 = {}
        for i in range(len(Index[pat]) + 2):
            if i == 0:
                D2[i] = S
                W2[i] = 0
            elif i == len(Index[pat]) + 1:
                D2[i] = G
                W2[i] = 0
            else:
                D2[i] = dic_lat[Index[pat][i - 1]]
                W2[i] = W_choice[pat][i - 1]
        P.append(D2)
        P_W.append(W2)

    return P, P_W

def main():
    # タイトル
    st.title('段ボールEats')
    # 回収して欲しい側
    st.markdown('** 回収をお願いする方はこちらに登録 **')

    cliant_db_path = f"cliant_db.json"
    if os.path.exists(cliant_db_path) and os.stat(cliant_db_path).st_size != 0:
        json_open = open(cliant_db_path, 'r')
        d = json.load(json_open)
    else:
        d = {'name': [], 'lat': [], 'lon': [], 'how_many': []}
    name = st.text_input(label='登録名')
    address = st.text_input(label='住所', value='')

    how_many = st.number_input(label='段ボールの量', value=0)
    if st.button('登録'):
        if address == '':
            st.error('登録内容を入力してください')
        else:
            address = get_lat_lon_from_address([address])
            insert_json(d, name, address[0], how_many)
            # d['name'].append(name)
            # d['lat'].append(get_lat_lon_from_address([address])[0][0])
            # d['lon'].append(get_lat_lon_from_address([address])[0][1])
            # d['how_many'].append(how_many)
            st.success('Done!')
        df = pd.DataFrame(d)
        st.dataframe(df)
    json.dump(d, open(cliant_db_path, "w"))

    """
    # 回収する側
    st.markdown('** 回収してくれる方はこちらで検索 **')
    # サンプル用の緯度経度データを作成する

    # ------------------------画面作成------------------------

    st.title("最短経路")  # タイトル

    target = st.slider("運びたい段ボールの個数",
                       value=10, min_value=10, max_value=40)  # スライダーをつける

    start = '35.6809591,139.7673068'
    goal = '35.6616778,139.7703389'

    sample_lat = [['35.6786944,139.7745278'],
                  ['35.6816778,139.7703389'],
                  ['35.6742222,139.7718056'],
                  ['35.67425,139.7743333'],
                  ['35.6715,139.7691389'],
                  ['35.6781444,139.7693167'],
                  ['35.6859722,139.7747778'],
                  ['35.6823069,139.7797439'],
                  ['35.6841944,139.7784444'],
                  ['35.6708056,139.7771944']]

    sample_w = []
    for i in range(len(sample_lat)):
        sample_w.append(random.randint(1, 20))

    locat = test(sample_lat, sample_w, target, start, goal)

    locations = []
    for i in locat:
        locate = i[0].split(',')
        loc1 = float(locate[0])
        loc2 = float(locate[1])
        locations.append([loc1, loc2])

    df = pd.DataFrame({
        'count': [random.randint(1, 5) for _ in range(len(locations))],
        'latitude': [lat for (lat, lon) in locations],
        'longitude': [lon for (lat, lon) in locations]
    })

    # データを地図に渡す関数を作成する
    def AreaMarker(df, map):
        for index, row in df.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=7,
                color='#0000FF',
                fill_color='#0000FF'
            ).add_to(map)

            points = [(a, b) for a, b in zip(df['latitude'].tolist(), df['longitude'].tolist())]
            folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(map)

    # st.subheader("運びたい段ボール{:,}個".format(weight))
    map = folium.Map(location=[35.6809591, 139.7673068], zoom_start=14)  # 地図の初期設定
    AreaMarker(df, map)  # データを地図渡す
    folium.Marker(location=[35.6786944, 139.7745278]).add_to(map)
    folium.Marker(location=[35.6742222, 139.7718056]).add_to(map)
    folium.Marker(location=[35.67425, 139.7743333]).add_to(map)
    folium.Marker(location=[35.6781444, 139.7693167]).add_to(map)
    folium.Marker(location=[35.6841944, 139.7784444]).add_to(map)
    folium.Marker(location=[35.6708056, 139.7771944]).add_to(map)
    folium.Marker(location=[35.6823069, 139.7797439]).add_to(map)
    folium.Marker(location=[35.6816778, 139.7703389]).add_to(map)
    folium.Marker(location=[35.6859722, 139.7747778]).add_to(map)
    folium_static(map)  # 地図情報を表示
    """

if __name__ == '__main__':
    main()
