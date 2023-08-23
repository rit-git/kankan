import streamlit as st
import requests

def search_hotel():
    response = requests.post(
        'http://localhost:21345/api/search',
        json={
            'tdfk': st.session_state['tdfk'],
            'query': st.session_state['query']
        }
    )
    if response.status_code == 200:
        response = response.json()
        st.session_state['result'] = '***  {}   ***'.format(response['result'])

def update_state(key):
    st.session_state[key] = st.session_state[key]

def main():
    st.set_page_config(
        page_title='Kankan',
        layout='wide',
    )
    st.title('KanKan：観光スポット検索エンジン')

    st.selectbox('都道府県',('日本全国', '東京都', '大阪府', '長野県', '沖縄県'), key='tdfk', on_change=update_state, args=('tdfk',))
    st.text_input('検索クエリ', 'デートに最適', key='query', on_change=update_state, args=('query',))
    st.button('検索', on_click=search_hotel)
    st.text_area('検索結果', '', key='result', on_change=update_state, args=('result',))

if __name__ == '__main__':
    main()