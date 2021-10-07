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
    ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    headers = {'User-Agent': ua}
    latlons = []
    for address in tqdm(address_l):
        payload = {"v": 1.1, 'q': address}
        html = requests.get(url, params=payload, headers=headers)
        st.markdown(html)
        ret = BeautifulSoup(html.content, 'lxml')
        st.markdown(ret)
        if ret.find('error'):
            raise ValueError(f"Invalid address submitted. {address}")
        else:
            lat = ret.find('lat').string
            lon = ret.find('lng').string
            latlons.append((lat, lon))
            time.sleep(5)
    return latlons


def delete_json(d, index):
    for key in d.keys():
        d[key] = d[key][:index] + d[key][index+1:]
    return d

def insert_json(d, name, address, how_many):
    d['name'].append(name)
    d['lat'].append(address[0])
    d['lon'].append(address[1])
    d['how_many'].append(how_many)
    return d


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


if __name__ == '__main__':
    main()
