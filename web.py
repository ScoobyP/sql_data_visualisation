import streamlit as st

st.set_page_config(layout="wide")
st.logo('https://i1.wp.com/bl-i.thgim.com/public/incoming/1ogk5e/article25940328.ece/alternates/FREE_1200/IPL-400x400jpg?strip=all')
st.sidebar.image("https://i1.wp.com/bl-i.thgim.com/public/incoming/1ogk5e/article25940328.ece/alternates/FREE_1200/IPL-400x400jpg?strip=all", width=200)

p1 = st.Page('page1.py', title='Home', icon='🏠')
p2 = st.Page('page2.py', title='Team Stats', icon='🏏')

pg = st.navigation([p1,p2,])
pg.run()
