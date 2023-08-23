import streamlit as st
import requests
import json

def kanji2romaji(s):
    if s == '東京都':
        return 'tokyo'
    elif s == '大阪府':
        return 'osaka'
    elif s == '長野県':
        return 'nagano'
    elif s == '沖縄県':
        return 'okinawa'
    else:
        return 'japan'

def json2str(res_dict):
    res_lines = []
    for hotel_info in res_dict['hotel']:
        res_lines.append('*'*40)
        res_lines.append(
            '第{}位：{}。類似度スコア：{}。住所：〒{} {}'.format(
                hotel_info['rank'], hotel_info['kuchikomi'][0]['name'], hotel_info['score'], hotel_info['kuchikomi'][0]['ybn'], hotel_info['kuchikomi'][0]['address']
            )
        )
        res_lines.append('*'*40)
        for kuchikomi in hotel_info['kuchikomi']:
            res_lines.append('【{:.4f}】{}'.format(kuchikomi['score'], kuchikomi['text']))
    return '\n'.join(res_lines)

def search_hotel():
    response = requests.post(
        'http://localhost:21344/api/search',
        json={
            'tdfk': kanji2romaji(st.session_state['tdfk']),
            'query': st.session_state['query']
        }
    )
    if response.status_code == 200:
        st.session_state['result'] = json2str(response.json())

def update_state(key):
    st.session_state[key] = st.session_state[key]

def main():
    st.set_page_config(
        page_title='Kankan',
        layout='wide',
    )
    st.title('KanKan：観光スポット検索エンジン')

    col1, col2 = st.columns([1,5])

    with col1:
        st.selectbox(
            '都道府県',
            ('東京都', '大阪府', '長野県', '沖縄県'), 
            key='tdfk', on_change=update_state, args=('tdfk',)
        )

        st.text_input('検索クエリ', key='query', on_change=update_state, args=('query',))
        st.button('検索', on_click=search_hotel)
    
    with col2:
        st.text_area('検索結果', '', height=600, key='result', on_change=update_state, args=('result',))

if __name__ == '__main__':
    main()