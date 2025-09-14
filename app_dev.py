import streamlit as st
import pandas as pd
import subprocess as sb
import time 
import threading

st.set_page_config(page_title="BVB Stock Predicter", page_icon="📈")

if 'page' not in st.session_state:
    st.session_state.page = 'main'

if 'collect_started' not in st.session_state:
    st.session_state.collect_started = False
if 'predict_started' not in st.session_state:
    st.session_state.predict_started = False
if 'collect_thread' not in st.session_state:
    st.session_state.collect_thread = None
if 'predict_thread' not in st.session_state:
    st.session_state.predict_thread = None

def main_menu():
    st.set_page_config(page_title="BVB Stock Predicter", page_icon="📈")
    st.title('📊 BVB Stock Predicter')
    
    if st.button('Company Predicter'):
        st.session_state.page = 'company_predicter'
        st.rerun()
    elif st.button('Category Predicter'):
        st.session_state.page = 'category_predicter'
        st.rerun()
    elif st.button('🔍 Search Company'):
        st.session_state.page = 'search_company'
        st.rerun()
    elif st.button('Data collector and train'):
        st.session_state.page = 'data_collector'
        st.rerun()

def company_predicter():
    st.title("Company Predicter")
    st.write('Please press the collect button to start scrapping for latest info.')
    if st.button('Predict'):
        st.session_state.page = 'loading_company'
        st.session_state.collect_started = True
        st.rerun()
        return

    if st.button('⬅️ Înapoi', key='back_from_company'):
        st.session_state.page = 'main'
        st.rerun()
        return

def category_predicter():
    st.title("Category Predicter")

    st.write('Please press the collect button to start scrapping for latest info.')
    if st.button('Predict'):
        st.session_state.page = 'loading_category'
        st.session_state.collect_started = True
        st.rerun()
        return
    
    if st.button("⬅️ Înapoi", 'back_from_category'):
        st.session_state.page = 'main'
        st.rerun()
        return
    
def collect_data():
    st.title('Collect Data')

    st.write('If you have a couple of spare minutes, you can help the community by improving out' \
    ' Machine Learning model by training it on the lastest info. Just press the button below and ' \
    'wait for about 1 - 2 minutes. Thank you!')

    if st.button("Collect and train"):
        st.session_state.page = 'collect_and_train'
        st.rerun()

    if st.button("⬅️ Înapoi", 'back_from_collect'):
        st.session_state.page = 'main'
        st.rerun()
        return

def run_collect():
    global script_result_collect
    script_result_collect = sb.run(['python3', 'data_selector.py'], capture_output=True, text=True)

def run_predict_company():
    global script_result_company
    script_result_company = sb.run(['python3', 'predict_companii.py'], capture_output=True, text=True)

def run_category_predict():
    global result
    result = sb.run(['python3', 'predict_categorii.py'], capture_output=True, text=True)

def train_companii():
    global result_companii
    result_companii = sb.run(['python3', 'ml_tmr.py'], capture_output=True, text=True)

def train_category():
    global result_categorii
    result_categorii = sb.run(['python3', 'ml_categoriiV2.py'], capture_output=True, text=True)

def loading_company():
    loading_placeholder = st.empty()
    global script_result_collect
    script_result_collect = None

    thread = threading.Thread(target=run_collect)
    thread.start()

    i = 0
    while thread.is_alive():
        dots = '.' * (i % 4)
        loading_placeholder.header(f'Collecting data{dots}')
        time.sleep(0.5)
        i += 1

    thread.join()   

    loading_placeholder.empty()

    global script_result_company
    script_result_company = None

    thread = threading.Thread(target=run_predict_company)
    thread.start()

    predicting_placeholder = st.empty()
    
    i = 0
    while thread.is_alive():
        dots = '.' * (i % 4)
        predicting_placeholder.header(f'Data collected successfully! Now predicting{dots}')
        time.sleep(0.5)
        i += 1

    thread.join()

    predicting_placeholder.empty()

    success_box = st.empty()
    success_box.success('Done.')
    time.sleep(1.5)
    success_box.empty()

    st.session_state.page = 'view_result_company'
    st.rerun()

def view_result_company():
    st.title("Prediction results")
    categ = ["Energie_si_Utilitati", "Sector_Financiar_si_Investitii", "Industrie_Constructii_si_Materiale",
			 "Servicii_Tehnologie_si_Bunuri_de_Consum"]
    
    with st.expander('Energie si Utilitati'):
        filename = "predictii_" + categ[0] + ".csv"
        df = pd.read_csv(filename, index_col=0)
        df.drop(columns=['Categorie'], inplace=True)
        st.dataframe(df, use_container_width=True, hide_index=True)

    with st.expander('Sector Financiar si Investitii'):
        filename = "predictii_" + categ[1] + ".csv"
        df = pd.read_csv(filename, index_col=0)
        df.drop(columns=['Categorie'], inplace=True)
        st.dataframe(df, use_container_width=True, hide_index=True)

    with st.expander('Industrie, Constructii si Materiale'):
        filename = "predictii_" + categ[2] + ".csv"
        df = pd.read_csv(filename, index_col=0)
        df.drop(columns=['Categorie'], inplace=True)
        st.dataframe(df, use_container_width=True, hide_index=True)

    with st.expander('Servicii, Tehnologie si Bunuri de Consum'):
        filename = "predictii_" + categ[3] + ".csv"
        df = pd.read_csv(filename, index_col=0)
        df.drop(columns=['Categorie'], inplace=True)
        st.dataframe(df, use_container_width=True, hide_index=True)

    if st.button('🏠Home'):
        st.session_state.page = 'main'
        st.rerun()

def loading_category():
    loading_placeholder = st.empty()
    global script_result_collect
    script_result_collect = None

    thread = threading.Thread(target=run_collect)
    thread.start()

    i = 0
    while thread.is_alive():
        dots = '.' * (i % 4)
        loading_placeholder.header(f'Collecting data{dots}')
        time.sleep(0.5)
        i += 1

    thread.join()   

    loading_placeholder.empty()

    thread = threading.Thread(target=run_category_predict)
    thread.start()

    predicting_placeholder = st.empty()
    
    i = 0
    while thread.is_alive():
        dots = '.' * (i % 4)
        predicting_placeholder.header(f'Data collected successfully! Now predicting{dots}')
        time.sleep(0.5)
        i += 1

    thread.join()

    predicting_placeholder.empty()

    success_box = st.empty()
    success_box.success('Done.')
    time.sleep(1.5)
    success_box.empty()

    st.session_state.page = 'view_result_category'
    st.rerun()

def view_result_category():
    df = pd.read_csv('predictii_categorii.csv')
    st.dataframe(df, use_container_width=True, hide_index=True)

    if st.button('🏠Home'):
        st.session_state.page = 'main'
        st.rerun()  

def search_company():
    categ = ["Energie_si_Utilitati", "Sector_Financiar_si_Investitii", "Industrie_Constructii_si_Materiale",
			 "Servicii_Tehnologie_si_Bunuri_de_Consum"]

    st.header('Search Engine')
    user_input = st.text_input('Please write the symbol of the company that is of interest to you:')

    if st.button("🔍 Caută"):   
        user_input_upper = user_input.upper()
        prediction = st.empty()
        error = st.empty()
        found = False

        for i in categ:
            filename = 'predictii_' + str(i) + '.csv'

            df = pd.read_csv(filename)
            
            result = df[df['Simbol'] == user_input_upper]

            if not result.empty:
                prediction.dataframe(result, hide_index=True)
                found = True
        
        if not found:
            st.error('Symbol Not Found')

    if st.button("⬅️ Înapoi", 'back_from_category'):
        st.session_state.page = 'main'
        st.rerun()

def training():
    loading_placeholder = st.empty()
    global script_result_collect
    script_result_collect = None

    thread = threading.Thread(target=run_collect)
    thread.start()

    i = 0
    while thread.is_alive():
        dots = '.' * (i % 4)
        loading_placeholder.header(f'Collecting data{dots}')
        time.sleep(0.5)
        i += 1

    thread.join()   

    loading_placeholder.empty()

    thread = threading.Thread(target=train_companii)
    thread.start()

    tCompanii_placeholder = st.empty()
    
    i = 0
    while thread.is_alive():
        dots = '.' * (i % 4)
        tCompanii_placeholder.header(f'Data collected successfully! Now training model 1{dots}')
        time.sleep(0.5)
        i += 1

    thread.join()

    tCompanii_placeholder.empty()

    thread = threading.Thread(target=train_category)
    thread.start()

    tCategorii_placeholder = st.empty()
    
    i = 0
    while thread.is_alive():
        dots = '.' * (i % 4)
        tCategorii_placeholder.header(f'Model 1 trained! Now training model 2{dots}')
        time.sleep(0.5)
        i += 1

    thread.join()

    tCategorii_placeholder.empty()

    success_box = st.empty()
    success_box.success('Done.')
    time.sleep(1.5)
    success_box.empty()

    st.session_state.page = 'main'
    st.rerun()
                             
def main():
    if st.session_state.page == 'main':
        main_menu()
    elif st.session_state.page == 'company_predicter':
        company_predicter()
    elif st.session_state.page == 'category_predicter':
        category_predicter()
    elif st.session_state.page == 'loading_company':
        loading_company()
    elif st.session_state.page == 'view_result_company':
        view_result_company()
    elif st.session_state.page == 'loading_category':
        loading_category()
    elif st.session_state.page == 'search_company':
        search_company()
    elif st.session_state.page == 'collect_and_train':
        training()
    elif st.session_state.page == 'data_collector':
        collect_data()
    elif st.session_state.page == 'view_result_category':
        view_result_category()

main()
