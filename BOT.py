#Google API 設定ファイル
from __future__ import print_function
import datetime #時刻を扱う
import os.path #パスを扱う
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import sys

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

#Serviceの変数を設定
def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    #このPythonファイルと同一のファイル内にtoken.jsonファイルを設置すること
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    #token.jsonが存在しない時、同一ファイル内にあるcredentials.jsonからtoken.jsonファイルを自動で生成する
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    #Google API の呼び出し
    service = build('calendar', 'v3', credentials=creds)
    #GoogleAPIの時間設定はUTC + Zで設定する
    #'Z'は時差を表す。Zはタイムゾーンの設定によって自動的に決まる。日本は+9
    now = datetime.datetime.utcnow()
    now_add = now + datetime.timedelta(hours=2) #範囲を2時間に設定
    now_utc = now.isoformat() + 'Z'
    now_add_utc = now_add.isoformat() + 'Z'

    #データを収集する対象時間の範囲を設定する　timeMin ~ timeMax　maxResults= 最大取得予定　orderBy= 昇順
    #ココでは現在時刻～＋２時間を範囲にしている
    events_result = service.events().list(calendarId='primary', timeMin=now_utc, timeMax=now_add_utc, maxResults=20, singleEvents=True, orderBy='startTime').execute()

    #カレンダーからイベントの結果を収集してリストにして格納
    events = events_result.get('items', [])
    #print(events)
    #イベントがない場合,プログラムを終了
    if not events:
        print('No upcoming events found.')
        sys.exit()
    
    #イベントがある場合
    #リストの新規作成
    events_list = []
    for event in events:
        #print(event['summary'], event['location'], event['description'], event['start'], event['end'])
        #一時イベントリストの中に、{[summa],[date],[description],[location]}の順番で格納する
        #日時データは 曜日　HH:mm(start) ~ HH:mm(end) データに変換し[hours]に格納する
        #event['']
　　　　#一時リストの初期化
        event_list = []
        
        #タイトルデータの抽出
        summary = event['summary']
        event_list.append(summary)
        
        #日付データの抽出　（if データが無い場合は空データを格納）
        #type(string)：2021-11-26T21:30:00+09:00 JST + 時差（UTC ９時間）
        if not 'dateTime' in event['start']:
            day = event['start']['date']
            day = day[5:]
            day = day.replace('-','月')
            dt_str = day+'日' 
            event_list.append(dt_str)
        else:
            start = event['start']['dateTime']
            end = event['end']['dateTime']

            start = start.replace(':00+09:00','')
            end = end.replace(':00+09:00','')
            day = start[:10]
            day = day[5:]
            day = day.replace('-','月')
            start = start[11:]
            end = end[11:]
            dt_str = day+'日 '+start+' ~ '+end
            event_list.append(dt_str)
            #OUTPUT 11月28日 09:00 ~ 23:00
        
        #コメントデータ　（if データが無い場合は空データを格納）
        if not 'description' in event:
            event_list.append('')
        else:
            comment = event['description']
            event_list.append(comment)
        
        #ロケーションデータ　（if データが無い場合は空データを格納）
        if not 'location' in event:
            event_list.append('')
        else:
            location = event['location']
            event_list.append(location)
        
        #event_listをevents_listに格納
        events_list.append(event_list)

    #printテスト　格納されているイベントリストを確認します   
    #print(events_list)

    #Twitter API の認証
    import tweepy
    import time

    # 認証に必要なキーとトークン（入力必須）
    API_KEY = ''
    API_SECRET = ''
    ACCESS_TOKEN = ''
    ACCESS_TOKEN_SECRET = ''

    # APIの認証
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    #イベントリストからデータを抽出
    def getTemplate(summary_txt,date_txt,comment_txt,location_txt) :
　　　　#本文を作成します。
        result = f'タイトル：{summary_txt}\n日時：{date_txt}\n\nコメント：{comment_txt}\n\nロケーション：{location_txt}'
        return result

    #ツイート文の作成
    #コメントにヘッダー文を追記します。
    tweet = "Header\n\n"
    n = 0
    for i in events_list:
        tweet += getTemplate(events_list[n][0],events_list[n][1],events_list[n][2],events_list[n][3])
        n += 1
    #コメントにフッター文字を追記します
    tweet += "\n\nFooter"
    #print(tweet)
    try:
        #api.update_status(tweet)
        api.update_status(tweet)
        print('SUCCESSFUL!')
        time.sleep(5)
    except tweepy.error.TweepError as e:
        print(e) 
    

if __name__ == '__main__':
    main()
