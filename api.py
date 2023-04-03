import streamlit as st
import geocoder
import requests
import pandas as pd
import math
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from PIL import Image

url = 'http://webservice.recruit.co.jp/hotpepper/gourmet/v1/'

st.title('現在地付近のレストランを検索')
st.sidebar.write('## 検索する条件を入力してください')
st.sidebar.write('距離と金額を同時に検索することも可能')
st.sidebar.write('---------------------------------------------')
dis = st.sidebar.text_input('距離（m）※入力してからEnterで検索','0')
max_budget = st.sidebar.text_input('予算（円）※入力してからEnterで検索','0')

if int(dis)==0 and int(max_budget)==0:
    st.write('左の入力欄に検索条件を記入してください。')
    
#距離と金額を確認
if 0<int(dis) and int(max_budget)==0:
    st.write(f'現在地から {dis}'+'m以内のレストランを表示しています')
if 0<int(max_budget) and int(dis)==0:
    st.write(f'{max_budget}'+'円以下のレストランを表示しています')
if 0<int(dis) and 0<int(max_budget):
    st.write(f'{max_budget}'+f'円以下かつ現在地から {dis}'+'m以内のレストランを表示しています')
    
#詳細　Buttonが押された時
def page(i):
    _logo_image = df['photo1'][con]   
    st.image(_logo_image, width=200)   #店舗の写真を表示
    
    col1, col2= st.columns([1,3])
    with col1:
        st.write('###### ・店舗名')
        st.write('')
        st.write('###### ・最寄り駅')
        st.write('')
        st.write('###### ・金額')
        st.write('')
        st.write('###### ・営業時間')
        st.write('')
        st.write('###### ・住所')
    with col2:
        st.write(_name)
        st.write(_access)
        st.write(_budget)
        st.write(_open) 
        st.write(_address)       

        
#現在地の緯度経度を取り出す
g = geocoder.ip('me')
pl = []                
#現在地を取得※微調節
lat_me = g.latlng[0]+0.027568999999999733
lng_me = g.latlng[1]-0.005419999999986658
pl.append(lat_me)    #plに現在地の緯度経度を追加
pl.append(lng_me)

#緯度経度から現在地の住所を取得
loc = Nominatim(user_agent="test1")
getlocation = loc.geocode(pl)
place_here = getlocation.address.split(',')[3] #市町村のみを抽出

##現在地の市町村のレストランを全て抽出##
#100番目までの情報を抽出
start = 1
count = 100
params = {
    'key' : '5246e7438be8d585',
    'keyword': place_here,
    'start':start,
    'count':count,
    'format' : 'json'
}

res1 = requests.get(url,params)
shops = res1.json()['results']['shop']           #100番目までの情報をshopsに追加

#101番目から情報を抽出
start = 1
count = 100                    
avai = int(res1.json()['results']['results_available'])   #市町村のレストラン一覧の数をavaiに追加

for n in range(math.floor(avai/100)):
    x = (n+1)*100+1
    y = (n+1)*100+100
    params = {
    'key' : '5246e7438be8d585',
    'keyword': place_here,
    'start':x,
    'count':count,
    'format' : 'json'
    }
    
    res = requests.get(url,params)
    shop = res.json()['results']['shop']   #101番目以上の情報をshopに追加
    
    shops += shop                          #shopsに101番目以上の情報を追加

    
##必要な情報を抽出##
data = []
#一店舗ずつ取り出し、shopに代入
for shop in shops:
    datum = {
        'name':shop['name'],
        'address':shop['address'],
        'capacity':shop['capacity'],
        'access':shop['access'],
        'urls':shop['urls']['pc'],
        'open':shop['open'],
        'budget':shop['budget']['name'],
        'lat':shop['lat'],
        'lng':shop['lng'],
        'logo_image':shop['logo_image'],
        'photo1':shop['photo']['pc']['l'],
        'photo2':shop['photo']['pc']['m'],
        'photo3':shop['photo']['pc']['s']
        }
     #必要な情報のみを取り出したdatumをdataに追加
    data.append(datum)
    
df = pd.DataFrame(data)    #リスト→DataFrame


##情報を抽出して使いやすい形に変換
distance = []
i = 0
a = 0
for con in range(len(data)):
    _lat = df['lat'][con]
    _lng = df['lng'][con]
    _logo_image = df['logo_image'][con] 
    _name = df['name'][con] 
    _access = df['access'][con]
    _budget = df['budget'][con]
    _open = df['open'][con]
    _address = df['address'][con]
    _photo1 = df['photo1'][con]
    _photo2 = df['photo2'][con]
    _photo3 = df['photo3'][con]
    
    place_me=(lat_me, lng_me)
    place=(_lat, _lng)
    
    distance_m=geodesic(place_me,place).m      #現在地からの距離を測定
    ans = math.floor(distance_m)               #小数点以下切り捨て
    
    #金額の記入がない場合を避ける→0円とする
    if _budget != '':
        upper_budget = int(_budget.split('～')[1].replace('円',''))    #最高金額を抽出
    else:
        lower_budget = 0
        upper_budget = 0
        
    #検索条件判断
    if ((int(max_budget) !=0 and upper_budget <= int(max_budget) and int(dis)==0) #金額のみの検索をする時
        or (ans <= int(dis) and int(max_budget)==0)                               #距離のみの検索をする時
        or ((int(max_budget) !=0 and upper_budget <= int(max_budget)) and (ans <= int(dis)))):#金額と距離の検索をする時
            #店舗ごとに区切りをつける
            st.write('-------------------------------------------------------------------')

            _logo_image = df['logo_image'][con]   
            st.image(_logo_image, width=120)      #ロゴ画像を表示
         
            df1 = pd.DataFrame(
                data={'詳細': [
                df['name'][con], 
                df['access'][con],
                df['budget'][con]
                 ]},
             index=['店舗名', 'アクセス','金額']    #任意の情報を表示
             )

            st.dataframe(df1, width=1000, height=150)
            distance.append(ans)
            #検索にヒットした数を数える
            i += 1
            a = str(i)
            #詳細Button
            if st.button(df['name'][con]+"の詳細を開く"):
                page(i)

#検索ヒット数をsidebarに表示
if int(a) != 0:
    st.sidebar.write(str(a)+'件ヒットしました！')
else:
    #待機
    st.sidebar.write('検索中...')

