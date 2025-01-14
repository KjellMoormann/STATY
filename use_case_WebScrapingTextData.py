####################
# IMPORT LIBRARIES #
####################

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import functions as fc
import os
import PyPDF2
import requests
import streamlit.components.v1 as components
import yfinance as yf
import datetime
from wordcloud import WordCloud
import bs4
from bs4 import BeautifulSoup
from langdetect import detect

import mediawiki
import re
import base64
from io import BytesIO
from sklearn.feature_extraction.text import CountVectorizer
from difflib import SequenceMatcher
import nltk
nltk.download('punkt')
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sentence_transformers import SentenceTransformer
from streamlit_js_eval import streamlit_js_eval
#----------------------------------------------------------------------------------------------

def app():

    # Clear cache
    #st.runtime.legacy_caching.clear_cache()

    # Hide traceback in error messages (comment out for de-bugging)
    #sys.tracebacklimit = 0

    # workaround for Firefox bug- hide the scrollbar while keeping the scrolling functionality
    st.markdown("""
        <style>
        .ReactVirtualized__Grid::-webkit-scrollbar {
        display: none;
        }

        .ReactVirtualized__Grid {
        -ms-overflow-style: none;  /* IE and Edge */
        scrollbar-width: none;  /* Firefox */
        }
        </style>
        """, unsafe_allow_html=True)
    #-------------------------------------------------------------------------
    # RESET INPUT
    
    #Session state
    if 'key' not in st.session_state:
        st.session_state['key'] = 0
    if 'sentiment' not in st.session_state:    
        st.session_state['sentiment']=None

    reset_clicked = st.sidebar.button("Reset all your input")
    if reset_clicked:
        #st.session_state['key'] = st.session_state['key'] + 1
        streamlit_js_eval(js_expressions="parent.window.location.reload()")
        st.runtime.legacy_caching.clear_cache()
    st.sidebar.markdown("")

    def in_wid_change():        
        st.session_state['stock_df']=None
        st.session_state['add_stock_df']=None
        st.session_state['sentiment']=None
   
    #------------------------------------------------------------------------------------------
    # SETTINGS

    settings_expander=st.sidebar.expander('Settings')
    with settings_expander:
        st.caption("**Precision**")
        user_precision=int(st.number_input('Number of digits after the decimal point',min_value=0,max_value=10,step=1,value=4))
        #st.caption("**Help**")
        #sett_hints = st.checkbox('Show learning hints', value=False)
        st.caption("**Appearance**")
        sett_wide_mode = st.checkbox('Wide mode', value=False)
        sett_theme = st.selectbox('Theme', ["Light", "Dark"])
        #sett_info = st.checkbox('Show methods info', value=False)
        #sett_prec = st.number_input('Set the number of diggits for the output', min_value=0, max_value=8, value=2)
    st.sidebar.markdown("")
    st.sidebar.markdown("")

    # Check if wide mode
    if sett_wide_mode:
        fc.wide_mode_func()

    # Check theme
    if sett_theme == "Dark":
        fc.theme_func_dark()
    if sett_theme == "Light":
        fc.theme_func_light()
    fc.theme_func_dl_button()

    def cc():
        st.runtime.legacy_caching.clear_cache()
        st.session_state['load_data_button'] = None
    def tx_sum_change():
            st.session_state['run_text_summary'] = None  
    #++++++++++++++++++++++++++++++++++++++++++++
    # Text Mining and web-scraping
    #++++++++++++++++++++++++++++++++++++++++++++
    
    basic_text="Let STATY do text/web processing for you and start exploring your data stories right below... "
    
    st.header('**Web scraping and text data**')
    tw_meth = ['Text analysis',
                'Text summarization',                  
                'Wikipedia-based search',
                'PLOS ONE paper access and summarization',
                'Stock data access via yfinance'] #  'Yahoo Finance data analysis','Stock data analysis']
    tw_classifier = st.selectbox('What analysis would you like to perform?', list('-')+tw_meth, on_change=cc)
    data_read_check=None

    if tw_classifier in tw_meth:
        st.markdown("")
        st.markdown("")
        st.header('**'+tw_classifier+'**')
        st.markdown(basic_text)

    #------------------------------------------------------------
    # Wiki-based search
    # -----------------------------------------------------------        
    if tw_classifier=='Wikipedia-based search': 
        
        # Clear cache
        st.runtime.legacy_caching.clear_cache()      
        wiki_model=SentenceTransformer('all-MiniLM-L12-v2')
        st.write("")
        lang_opt={'English':'en','Cebuano':'ceb','German':'de','Swedish':'sv','French':'fr','Dutch':'nl','Russian':'ru','Spanish':'es','Italian':'it','Egyptian Arabic':'arz','Polish':'pl','Japanese':'ja','Chinese':'zh','Vietnamese':'vi','Waray':'war','Ukrainian':'uk','Arabic':'ar','Portuguese':'pt','Persian':'fa','Catalan':'ca','Serbian':'sr','Indonesian':'id','Korean':'ko','Norwegian (Bokmål)':'no','Chechen':'ce','Finnish':'fi','Turkish':'tr','Hungarian':'hu','Czech':'cs','Tatar':'tt','Serbo-Croatian':'sh','Romanian':'ro','Southern Min':'zh-min-nan','Basque':'eu','Malay':'ms','Esperanto':'eo','Hebrew':'he','Armenian':'hy','Danish':'da','Bulgarian':'bg','Welsh':'cy','Slovak':'sk','South Azerbaijani':'azb','Estonian':'et','Kazakh':'kk','Belarusian':'be','Simple English':'simple','Minangkabau':'min','Uzbek':'uz','Greek':'el','Croatian':'hr','Lithuanian':'lt','Galician':'gl','Azerbaijani':'az','Urdu':'ur','Slovene':'sl','Georgian':'ka','Norwegian (Nynorsk)':'nn','Hindi':'hi','Thai':'th','Tamil':'ta','Latin':'la','Bengali':'bn','Macedonian':'mk','Asturian':'ast','Cantonese':'zh-yue','Latvian':'lv','Tajik':'tg','Afrikaans':'af','Burmese':'my','Malagasy':'mg','Bosnian':'bs','Marathi':'mr','Occitan':'oc','Albanian':'sq','Low German':'nds','Malayalam':'ml','Belarusian (Taraškievica)':'be-tarask','Kyrgyz':'ky','Telugu':'te','Breton':'br','Swahili':'sw','Ladin':'lld','Newar':'new','Javanese':'jv','Venetian':'vec','Haitian Creole':'ht','Piedmontese':'pms','Western Punjabi':'pnb','Bashkir':'ba','Luxembourgish':'lb','Sundanese':'su','Kurdish (Kurmanji)':'ku','Irish':'ga','Lombard':'lmo','Silesian':'szl','Icelandic':'is','Chuvash':'cv','West Frisian':'fy','Kurdish (Sorani)':'ckb','Tagalog':'tl','Aragonese':'an','Wu Chinese':'wuu','Zaza':'diq','Punjabi':'pa','Scots':'sco','Ido':'io','Volapük':'vo','Yoruba':'yo','Nepali':'ne','Gujarati':'gu','Alemannic German':'als','Kannada':'kn','Interlingua':'ia','Bavarian':'bar','Kotava':'avk','Sicilian':'scn','Bishnupriya Manipuri':'bpy','Quechua (Southern Quechua)':'qu','Crimean Tatar':'crh','Mongolian':'mn','Navajo':'nv','Hausa':'ha','Mingrelian':'xmf','Sinhala':'si','Balinese':'ban','Samogitian':'bat-smg','Pashto':'ps','North Frisian':'frr','Ossetian':'os','Odia':'or','Yakut':'sah','Scottish Gaelic':'gd','Buginese':'bug','Eastern Min':'cdo','Yiddish':'yi','Ilocano':'ilo','Sindhi':'sd','Amharic':'am','Neapolitan':'nap','Limburgish':'li','Gorontalo':'gor','Upper Sorbian':'hsb','Faroese':'fo','Banyumasan':'map-bms','Maithili':'mai','Mazanderani':'mzn','Igbo':'ig','Central Bikol':'bcl','Emilian-Romagnol':'eml','Acehnese':'ace','Shan':'shn','Classical Chinese':'zh-classical','Sanskrit':'sa','Walloon':'wa','Interlingue':'ie','Ligurian':'lij','Assamese':'as','Zulu':'zu','Meadow Mari':'mhr','Western Armenian':'hyw','Hill Mari':'mrj','Fiji Hindi':'hif','Shona':'sn','Banjarese':'bjn','Meitei':'mni','Hakka Chinese':'hak','Khmer':'km','Tarantino':'roa-tara','Somali':'so','Kapampangan':'pam','Rusyn':'rue','Northern Sotho':'nso','Bihari (Bhojpuri)':'bh','Tumbuka':'tum','Santali':'sat','Northern Sámi':'se','Maori':'mi','Erzya':'myv','West Flemish':'vls','Dutch Low Saxon':'nds-nl','Nahuatl':'nah','Sardinian':'sc','Cornish':'kw','Veps':'vep','Kabyle':'kab','Turkmen':'tk','Gan Chinese':'gan','Corsican':'co','Gilaki':'glk','Dagbani':'dag','Moroccan Arabic':'ary','Võro':'fiu-vro','Lhasa Tibetan':'bo','Abkhaz':'ab','Manx':'gv','Franco-Provençal':'frp','Saraiki':'skr','Zeelandic':'zea','Uyghur':'ug','Komi':'kv','Picard':'pcd','Udmurt':'udm','Kashubian':'csb','Maltese':'mt','Guarani':'gn','Aymara':'ay','Inari Sámi':'smn','Norman':'nrm','Lezgian':'lez','Lingua Franca Nova':'lfn','Saterland Frisian':'stq','Livvi-Karelian':'olo','Lao':'lo','Kinyarwanda':'rw','Mirandese':'mwl','Old English':'ang','Friulian':'fur','Romansh':'rm','Judaeo-Spanish':'lad','Konkani (Goan Konkani)':'gom','Pangasinan':'pag','Permyak':'koi','Tuvan':'tyv','Extremaduran':'ext','Lower Sorbian':'dsb','Avar':'av','Doteli':'dty','Lingala':'ln','Chavacano (Zamboanga)':'cbk-zam','Karakalpak':'kaa','Papiamento':'pap','Maldivian':'dv','Ripuarian':'ksh','Gagauz':'gag','Buryat (Russia Buriat)':'bxr','Palatine German':'pfl','Kashmiri':'ks','Twi':'tw','Moksha':'mdf','Pali':'pi','Sakizaya':'szy','Hawaiian':'haw','Awadhi':'awa','Atayal':'tay','Zhuang (Standard Zhuang)':'za','PaO':'blk','Ingush':'inh','Karachay-Balkar':'krc','Kalmyk Oirat':'xal','Pennsylvania Dutch':'pdc','Atikamekw':'atj','Tongan':'to','Aramaic (Syriac)':'arc','Tulu':'tcy','Luganda':'lg','Mon':'mnw','Kabiye':'kbp','Jamaican Patois':'jam','Nauruan':'na','Wolof':'wo','Kabardian':'kbd','Nias':'nia','Novial':'nov','Kikuyu':'ki','NKo':'nqo','Bislama':'bi','Tok Pisin':'tpi','Tetum':'tet','Shilha':'shi','Lojban':'jbo','Aromanian':'roa-rup','Fijian':'fj','Lak':'lbe','Kongo (Kituba)':'kg','Xhosa':'xh','Tahitian':'ty','Old Church Slavonic':'cu','Oromo':'om','Gun':'guw','Seediq':'trv','Sranan Tongo':'srn','Samoan':'sm','French Guianese Creole':'gcr','Southern Altai':'alt','Cherokee':'chr','Latgalian':'ltg','Tswana':'tn','Chewa':'ny','Sotho':'st','Madurese':'mad','Norfuk':'pih','Gothic':'got','Amis':'ami','Romani (Vlax Romani)':'rmy','Bambara':'bm','Ewe':'ee','Venda':'ve','Tsonga':'ts','Fula':'ff','Cheyenne':'chy','Swazi':'ss','Kirundi':'rn','Tyap':'kcg','Akan':'ak','Inuktitut':'iu','Chamorro':'ch','Iñupiaq':'ik','Pontic Greek':'pnt','Adyghe':'ady','Nigerian Pidgin':'pcm','Paiwan':'pwn','Sango':'sg','Dinka':'din','Tigrinya':'ti','Greenlandic':'kl','Dzongkha':'dz','Cree':'cr'}
        
        user_query = st.text_input(label='Please enter your question here:',value="What is data science")
        lang_spec=st.checkbox('Specify Wikipedia language?', value=True)
        if lang_spec:
            lang_var_name=st.selectbox('Please specify the language',lang_opt,index=0)
            lang_var=lang_opt[lang_var_name]           
        else:
            lang_var=None    
        
        
        st.write("")
        run_models = st.button("Press to start data processing...")    
        if run_models:    
                      
            if user_query !='':
                st.subheader('Your answer could be here...')                 
                user_language=detect(user_query) if lang_var is None else lang_var                      
                
                # clean user query
                user_query = re.sub(r'[^\w\s]', '', user_query)                            
                
                wiki = mediawiki.MediaWiki(lang=user_language)
                results = wiki.search(user_query)
                                
                if len(results) > 0:

                    # Get and write sentence or a paragraph that is the best match to a user query                    
                    (bestmatch_index, text)=fc.get_topic_index(user_query, wiki_model, results,user_language)
                    st.write(text)
                    
                    # page with highest cosine similarity
                    best_match = results[bestmatch_index]                  
                    p = wiki.page(best_match)     
                    if len(text)<200: st.write(p.summary)                    
                    st.subheader('Web page preview:')
                    st.text("")
                    components.iframe(p.url,width=None,height=900,scrolling=True)
                else:
                    st.write("No information could be found on your query")
            
    
    
    #------------------------------------------------------------
    # Text summarization
    # -----------------------------------------------------------  
    if tw_classifier=='Text summarization': 
                   
        # Clear cache
        #st.runtime.legacy_caching.clear_cache()
        if fc.is_localhost(): 
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            t5_model = AutoModelForSeq2SeqLM.from_pretrained('t5-base')
            t5_tokenizer = AutoTokenizer.from_pretrained('t5-base')  
        run_text_OK = False

        #specify data source        
        text_source=st.radio('Select data source for text analysis',['text input','PDF or Word document'],index=1)  

        if text_source=='text input':
            user_text=st.text_area('Please enter or copy your text here', value='STATY  \n\n STATY is growing out of the effort to bring more data insights to university education across all disciplines of the natural and social sciences. It is motivated by the belief that fostering data literacy, creativity and critical thinking are more effective towards innovation, than bringing endless units of introduction to programming to students who find learning programming an overwhelming task. By providing easy access to the methods of classical statistics and machine learning, STATY’s approach is to inspire students to explore issues they are studying in the curriculum directly on real data, practice interpreting the results and check the source code to see how it is done or to improve the code. STATY can be used in the process of teaching and learning data science, demonstrations of theoretical concepts across various disciplines, active learning, promotion of teamwork, research and beyond.', height=600 )
                        
            st.write("")
            if len(user_text)>0:  
                run_text_OK = True 

        elif text_source=="PDF or Word document":           
            #upload a document
            uploaded_file = st.file_uploader("Upload your document ", type=["pdf","docx", "doc"])
            if uploaded_file==None:
                st.info("Default file is a pdf of a Wikipedia article on data science (English)")    
            
            if uploaded_file is None:
                pdf_reader = PyPDF2.PdfReader("default data/Data_science.pdf")
                user_text=fc.pdf_read(pdf_reader)
                run_text_OK = True                
            else:
                #read pdf or a Word document
                (run_text_OK,user_text)=fc.read_pdf_word(uploaded_file) 
       
        
        # Summarization settings and processing  
        if run_text_OK == True: 
            
            # check the number of sentences in the text:
            no_sentences=len(nltk.sent_tokenize(user_text))

            #specify methods for extractive summarization      
            extr_methods = st.multiselect("Extractive summarization methods ", ["Luhn",  "Edmunson", "LSA",  "LexRank", "TextRank", "SumBasic","KL-Sum"], ["LSA","SumBasic"], on_change=tx_sum_change)
            extr_length=st.number_input('Specify the extractive summary length (no. sentences in the summary)',min_value=1, max_value=no_sentences,value=min(5,no_sentences))
            
            #detect language           
            user_language=detect(user_text)

            if user_language not in ["en", "de"]:
                st.error("We recommend using texts written in either English or German - although sumy and T5 can perform text summarization in multiple languages, their performance may vary depending on the language and the specific summarization task. To perform text summarization in a specific language, you would need to fine-tune the model on a summarization dataset in that language.")
              
            else: 
                st.write("")
                run_text_summary = st.button("Press to start text summarization...")
                
                if run_text_summary:  
                    sum_bar = st.progress(0.0)
                    progress = 0
                    progress_len=len(extr_methods)+2


                    #Abstractive summary T5-base
                    progress += 1 # mask the slow process
                    sum_bar.progress(progress/progress_len)
                    if fc.is_localhost(): 
                        t5_summary=fc.t5_summary(user_text,t5_model,t5_tokenizer) 
                        st.subheader("Abstractive summarization")                 
                        T5_output = st.expander("T5-base", expanded = False)
                        with T5_output:
                            st.write("**Abstractive summarization using Google's [T5](https://huggingface.co/t5-base)**")
                            st.write(t5_summary)
                    
                    progress += 1
                    sum_bar.progress(progress/progress_len)

                    #Extractive Summary
                    st.subheader("Extractive summarization")    
                    if "LSA" in extr_methods:
                        summy_summary=fc.sumy_summary(user_text,"LSA", extr_length,user_language)
                        progress += 1
                        sum_bar.progress(progress/progress_len)
                        LSA_output = st.expander("LSA", expanded = False)
                        with LSA_output:
                             #provide the output
                            st.write("**Extractive summarization using LSA within [sumy](https://pypi.org/project/sumy/)**")
                            st.write(summy_summary)
                        
                    if "LexRank" in extr_methods:
                        summy_summary=fc.sumy_summary(user_text,"LexRank", extr_length,user_language)
                        progress += 1
                        sum_bar.progress(progress/progress_len)
                        LexRank_output = st.expander("LexRank", expanded = False)
                        with LexRank_output:
                             #provide the output
                            st.write("**Extractive summarization using LexRank within [sumy](https://pypi.org/project/sumy/)**")
                            st.write(summy_summary)

                    if "Edmunson" in extr_methods:
                        summy_summary=fc.sumy_summary(user_text,"Edmunson", extr_length,user_language)
                        progress += 1
                        sum_bar.progress(progress/progress_len)
                        Edmunson_output = st.expander("Edmunson", expanded = False)
                        with Edmunson_output:
                            #provide the output
                            st.write("**Extractive summarization using Edmunson within [sumy](https://pypi.org/project/sumy/)**")
                            st.write(summy_summary)
                    if "Luhn" in extr_methods:
                        summy_summary=fc.sumy_summary(user_text,"Luhn", extr_length,user_language)
                        progress += 1
                        sum_bar.progress(progress/progress_len)
                        Luhn_output = st.expander("Luhn", expanded = False)
                        with Luhn_output:
                            #provide the output
                            st.write("**Extractive summarization using Luhn within [sumy](https://pypi.org/project/sumy/)**")
                            st.write(summy_summary)   
                    if "TextRank" in extr_methods:
                        summy_summary=fc.sumy_summary(user_text,"TextRank", extr_length,user_language)
                        progress += 1
                        sum_bar.progress(progress/progress_len)
                        TextRank_output = st.expander("TextRank", expanded = False)
                        with TextRank_output:
                            #provide the output
                            st.write("**Extractive summarization using TextRank within [sumy](https://pypi.org/project/sumy/)**")
                            st.write(summy_summary)
                    if "SumBasic" in extr_methods:
                        summy_summary=fc.sumy_summary(user_text,"SumBasic", extr_length,user_language)
                        progress += 1
                        sum_bar.progress(progress/progress_len)
                        SumBasic_output = st.expander("SumBasic", expanded = False)
                        with SumBasic_output:
                             #provide the output
                            st.write("**Extractive summarization using SumBasic within [sumy](https://pypi.org/project/sumy/)**")
                            st.write(summy_summary) 
                    if "KL-Sum" in extr_methods:
                        summy_summary=fc.sumy_summary(user_text,"KL-Sum", extr_length,user_language)
                        progress += 1
                        sum_bar.progress(progress/progress_len)
                        KLSum_output = st.expander("KL-Sum", expanded = False)
                        with KLSum_output:
                            #provide the output
                            st.write("**Extractive summarization using KL-Sum within [sumy](https://pypi.org/project/sumy/)**")
                            st.write(summy_summary)


                    
                    st.success('Text summarization completed!')
    #---------------------------------------------
    #  PLOS ONE paper access and summarization
    #---------------------------------------------  
    if tw_classifier=='PLOS ONE paper access and summarization':             
        # Clear cache
        st.runtime.legacy_caching.clear_cache() 
        if fc.is_localhost(): 
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            t5_model = AutoModelForSeq2SeqLM.from_pretrained('t5-base')
            t5_tokenizer = AutoTokenizer.from_pretrained('t5-base') 
        run_paper_summary=[]
        #set the url of a plos paper
        paper_url = st.text_input("What paper should I summarize for you?","https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0040530")
        
        st.text("")
        if paper_url !='':
            run_paper_summary = st.button("Press to start text processing...")
                   
        if run_paper_summary:
            # Make a request to the URL of the selected paper 
            paper=requests.get(paper_url)
            #st.write('Status code:', paper.status_code)
            
            # status bar
            st.info("Paper summarization progress")
            ra_bar = st.progress(0.0)
            progress = 0

            if paper.status_code != 200:
                st.write('Status code:', paper.status_code)
                raise Exception('Failed to fetch web page ')
            else:
                # Parse the HTML of the selected paper using BeautifulSoup                   
                response = requests.get(paper_url)

                # Parse the HTML of the webpage
                soup = BeautifulSoup(response.text, 'html.parser')
                        
                # Find the element containing the abstract
                abstract_element = soup.find(class_='abstract-content')

                # Find the element containing the full text of the paper
                paper_text_element = soup.find(id='artText')

                # Extract the text of the paper
                paper_text = paper_text_element.text

                st.subheader('Abstract:')                
                st.write(abstract_element.text)                
                progress += 1
                ra_bar.progress(progress/3)

                summy_summary=fc.sumy_htmlsummary(paper_text,paper_url)
                progress += 1
                ra_bar.progress(progress/3)

                if fc.is_localhost(): 
                    t5_summary=fc.t5_summary(paper_text,t5_model,t5_tokenizer) 
                progress += 1
                ra_bar.progress(progress/3)
                st.success('Paper summarization completed!')

                #provide the output
                st.subheader("Extractive summarization using [sumy](https://pypi.org/project/sumy/)")
                st.write(summy_summary)
                if fc.is_localhost(): 
                    st.subheader("Abstractive summarization using Google's [T5](https://huggingface.co/t5-base)")
                    st.write(t5_summary)
                
                   
# ----------------------------------------------------------------
# Text Mining
#-----------------------------------------------------------------
    if tw_classifier=='Text analysis':

        # Clear cache
        #st.runtime.legacy_caching.clear_cache()
        
        run_text_OK=False
        text_cv = CountVectorizer()
        
        user_color=21  
        def random_color_func(user_col,word=None, font_size=None, position=None,  orientation=None, font_path=None, random_state=None):
            h = int(user_color)
            s = int(100.0 * 255.0 / 255.0)
            l = int(100.0 * float(random_state.randint(60, 120)) / 255.0)
            return "hsl({}, {}%, {}%)".format(h, s, l)    
        
       
        #specify data source        
        word_sl=st.radio('Select data source for text analysis',['text input','PDF or Word document','web page'])  

        if word_sl=='text input':
            user_text=st.text_area('Please enter or copy your text here', value='STATY  \n\n STATY is growing out of the effort to bring more data insights to university education across all disciplines of the natural and social sciences. It is motivated by the belief that fostering data literacy, creativity and critical thinking are more effective towards innovation, than bringing endless units of introduction to programming to students who find learning programming an overwhelming task. By providing easy access to the methods of classical statistics and machine learning, STATY’s approach is to inspire students to explore issues they are studying in the curriculum directly on real data, practice interpreting the results and check the source code to see how it is done or to improve the code. STATY can be used in the process of teaching and learning data science, demonstrations of theoretical concepts across various disciplines, active learning, promotion of teamwork, research and beyond.', height=600 )
            
            st.write("")
            if len(user_text)>0:  
                run_text_OK = True 

        elif word_sl=="PDF or Word document":           
            #upload a document
            uploaded_file = st.file_uploader("Upload your document ", type=["pdf","docx", "doc"])
            if uploaded_file==None:
                st.info("Default file is a pdf of a Wikipedia article on data science (English)")    
            
            if uploaded_file is None:
                pdf_reader = PyPDF2.PdfReader("default data/Data_science.pdf")
                user_text=fc.pdf_read(pdf_reader)
                run_text_OK = True                
            else:
                #read pdf or a Word document
                (run_text_OK,user_text)=fc.read_pdf_word(uploaded_file) 

        elif word_sl=='web page':
            user_path_wp = st.text_input("What web page should I analyse?","https://en.wikipedia.org/wiki/Data_mining")
            st.info("Remark: some pages do not allow automatic reading or previewing!")
            st.write("")

            if user_path_wp !='':
                web_page=requests.get(user_path_wp)
                            
            
                if web_page.status_code != 200:
                    st.write('Status code:', web_page.status_code)
                    raise Exception('Failed to fetch web page ')
                else:
                    # Parse the HTML of the selected paper using BeautifulSoup                   
                    response = requests.get(user_path_wp)

                    # Parse the HTML of the webpage
                    soup = BeautifulSoup(response.text, 'html.parser')
                    user_text=soup.text                  
                    run_text_OK = True
        
        # text processing
        if run_text_OK == True: 

            #detect language           
            user_language=detect(user_text)
           
            # Basic text processing:    
            text_cv_fit=text_cv.fit_transform([user_text])
            wordcount= pd.DataFrame(text_cv_fit.toarray().sum(axis=0), index=text_cv.get_feature_names(),columns=["Word count"])
            word_sorted=wordcount.sort_values(by=["Word count"], ascending=False)
                                         
            st.write("")
            text_prep_options=['lowercase',
                                'remove whitespaces',
                                'remove abbreviations',
                                'remove numbers',
                                'remove urls',
                                'remove html tags', 
                                'remove emails', 
                                'remove symbols']
            text_prep_selection=['remove whitespaces',
                                'remove abbreviations',
                                'remove numbers',
                                'remove urls',
                                'remove html tags', 
                                'remove emails']                    
            text_prep_ops=st.multiselect('Select text pre-processing options',text_prep_options,text_prep_selection)
            number_remove= False # don't remove within cv_text function
                                 
            #Stop words handling:
            stopword_selection=st.selectbox("Select stop word option",["No stop words (use all words)","Select stop words", "Use a built-in list of stop words in German", "Use a built-in list of stop words in English", "Specify stop words"], index=3, key=st.session_state['key'])
            
            if stopword_selection=="No stop words (use all words)":
                word_stopwords=[] 
            elif stopword_selection=="Select stop words":
                word_stopwords=st.multiselect("Select stop words (words to be removed from the text)", word_sorted.index.tolist(),word_sorted.index[1:min(10,len(word_sorted.index))].tolist())
            elif stopword_selection=="Use a built-in list of stop words in German":
                word_stopwords=["a","ab","aber","abermaliges","abermals","abgerufen","abgerufene","abgerufener","abgerufenes","abgesehen","ach","acht","achte","achten","achter","achtes","aehnlich","aehnliche","aehnlichem","aehnlichen","aehnlicher","aehnliches","aehnlichste","aehnlichstem","aehnlichsten","aehnlichster","aehnlichstes","aeusserst","aeusserste","aeusserstem","aeussersten","aeusserster","aeusserstes","ag","ähnlich","ähnliche","ähnlichem","ähnlichen","ähnlicher","ähnliches","ähnlichst","ähnlichste","ähnlichstem","ähnlichsten","ähnlichster","ähnlichstes","alle","allein","alleine","allem","allemal","allen","allenfalls","allenthalben","aller","allerdings","allerlei","alles","allesamt","allg","allg.","allgemein","allgemeine","allgemeinem","allgemeinen","allgemeiner","allgemeines","allgemeinste","allgemeinstem","allgemeinsten","allgemeinster","allgemeinstes","allmählich","allzeit","allzu","als","alsbald","also","am","an","and","andauernd","andauernde","andauerndem","andauernden","andauernder","andauerndes","ander","andere","anderem","anderen","anderenfalls","anderer","andererseits","anderes","anderm","andern","andernfalls","anderr","anders","anderst","anderweitig","anderweitige","anderweitigem","anderweitigen","anderweitiger","anderweitiges","anerkannt","anerkannte","anerkannter","anerkanntes","anfangen","anfing","angefangen","angesetze","angesetzt","angesetzten","angesetzter","ans","anscheinend","ansetzen","ansonst","ansonsten","anstatt","anstelle","arbeiten","au","auch","auf","aufgehört","aufgrund","aufhören","aufhörte","aufzusuchen","augenscheinlich","augenscheinliche","augenscheinlichem","augenscheinlichen","augenscheinlicher","augenscheinliches","augenscheinlichst","augenscheinlichste","augenscheinlichstem","augenscheinlichsten","augenscheinlichster","augenscheinlichstes","aus","ausdrücken","ausdrücklich","ausdrückliche","ausdrücklichem","ausdrücklichen","ausdrücklicher","ausdrückliches","ausdrückt","ausdrückte","ausgenommen","ausgenommene","ausgenommenem","ausgenommenen","ausgenommener","ausgenommenes","ausgerechnet","ausgerechnete","ausgerechnetem","ausgerechneten","ausgerechneter","ausgerechnetes","ausnahmslos","ausnahmslose","ausnahmslosem","ausnahmslosen","ausnahmsloser","ausnahmsloses","außen","außer","ausser","außerdem","ausserdem","außerhalb","äusserst","äusserste","äusserstem","äussersten","äusserster","äusserstes","author","autor","b","baelde","bald","bälde","bearbeite","bearbeiten","bearbeitete","bearbeiteten","bedarf","bedürfen","bedurfte","been","befahl","befiehlt","befiehlte","befohlene","befohlens","befragen","befragte","befragten","befragter","begann","beginnen","begonnen","behalten","behielt","bei","beide","beidem","beiden","beider","beiderlei","beides","beim","beinahe","beisammen","beispiel","beispielsweise","beitragen","beitrugen","bekannt","bekannte","bekannter","bekanntlich","bekanntliche","bekanntlichem","bekanntlichen","bekanntlicher","bekanntliches","bekennen","benutzt","bereits","berichten","berichtet","berichtete","berichteten","besonders","besser","bessere","besserem","besseren","besserer","besseres","bestehen","besteht","besten","bestenfalls","bestimmt","bestimmte","bestimmtem","bestimmten","bestimmter","bestimmtes","beträchtlich","beträchtliche","beträchtlichem","beträchtlichen","beträchtlicher","beträchtliches","betraechtlich","betraechtliche","betraechtlichem","betraechtlichen","betraechtlicher","betraechtliches","betreffend","betreffende","betreffendem","betreffenden","betreffender","betreffendes","bevor","bez","bez.","bezgl","bezgl.","bezueglich","bezüglich","bietet","bin","bis","bisher","bisherige","bisherigem","bisherigen","bisheriger","bisheriges","bislang","bisschen","bist","bitte","bleiben","bleibt","blieb","bloss","böden","boeden","brachte","brachten","brauchen","braucht","bräuchte","bringen","bsp","bsp.","bspw","bspw.","bzw","bzw.","c","ca","ca.","circa","d","d.h","da","dabei","dadurch","dafuer","dafür","dagegen","daher","dahin","dahingehend","dahingehende","dahingehendem","dahingehenden","dahingehender","dahingehendes","dahinter","damalige","damaligem","damaligen","damaliger","damaliges","damals","damit","danach","daneben","dank","danke","danken","dann","dannen","daran","darauf","daraus","darf","darfst","darin","darüber","darüberhinaus","darueber","darueberhinaus","darum","darunter","das","dasein","daselbst","daß","dass","dasselbe","Dat","davon","davor","dazu","dazwischen","dein","deine","deinem","deinen","deiner","deines","dem","dementsprechend","demgegenüber","demgegenueber","demgemaess","demgemäß","demgemäss","demnach","demselben","demzufolge","den","denen","denkbar","denkbare","denkbarem","denkbaren","denkbarer","denkbares","denn","dennoch","denselben","der","derart","derartig","derartige","derartigem","derartigen","derartiger","derem","deren","derer","derjenige","derjenigen","dermaßen","dermassen","derselbe","derselben","derzeit","derzeitig","derzeitige","derzeitigem","derzeitigen","derzeitiges","des","deshalb","desselben","dessen","dessenungeachtet","desto","desungeachtet","deswegen","dich","die","diejenige","diejenigen","dies","diese","dieselbe","dieselben","diesem","diesen","dieser","dieses","diesseitig","diesseitige","diesseitigem","diesseitigen","diesseitiger","diesseitiges","diesseits","dinge","dir","direkt","direkte","direkten","direkter","doch","doppelt","dort","dorther","dorthin","dran","drauf","drei","dreißig","drin","dritte","dritten","dritter","drittes","drüber","drueber","drum","drunter","du","duerfte","duerften","duerftest","duerftet","dunklen","durch","durchaus","durchweg","durchwegs","dürfen","dürft","durfte","dürfte","durften","dürften","durftest","dürftest","durftet","dürftet","e","eben","ebenfalls","ebenso","ect","ect.","ehe","eher","eheste","ehestem","ehesten","ehester","ehestes","ehrlich","ei","ei,","eigen","eigene","eigenem","eigenen","eigener","eigenes","eigenst","eigentlich","eigentliche","eigentlichem","eigentlichen","eigentlicher","eigentliches","ein","einander","einbaün","eine","einem","einen","einer","einerlei","einerseits","eines","einfach","einführen","einführte","einführten","eingesetzt","einig","einige","einigem","einigen","einiger","einigermaßen","einiges","einmal","einmalig","einmalige","einmaligem","einmaligen","einmaliger","einmaliges","eins","einseitig","einseitige","einseitigen","einseitiger","einst","einstmals","einzig","elf","empfunden","en","ende","endlich","entgegen","entlang","entsprechend","entsprechende","entsprechendem","entsprechenden","entsprechender","entsprechendes","entweder","er","ergänze","ergänzen","ergänzte","ergänzten","ergo","erhält","erhalten","erhielt","erhielten","erneut","ernst","eröffne","eröffnen","eröffnet","eröffnete","eröffnetes","erscheinen","erst","erste","erstem","ersten","erster","erstere","ersterem","ersteren","ersterer","ersteres","erstes","es","etc","etc.","etliche","etlichem","etlichen","etlicher","etliches","etwa","etwaige","etwas","euch","euer","eure","eurem","euren","eurer","eures","euretwegen","f","fall","falls","fand","fast","ferner","fertig","finde","finden","findest","findet","folgend","folgende","folgendem","folgenden","folgender","folgendermassen","folgendes","folglich","for","fordern","fordert","forderte","forderten","fort","fortsetzen","fortsetzt","fortsetzte","fortsetzten","fragte","frau","frei","freie","freier","freies","früher","fuer","fuers","fünf","fünfte","fünften","fünfter","fünftes","für","fürs","g","gab","gaenzlich","gaenzliche","gaenzlichem","gaenzlichen","gaenzlicher","gaenzliches","gängig","gängige","gängigen","gängiger","gängiges","ganz","ganze","ganzem","ganzen","ganzer","ganzes","gänzlich","gänzliche","gänzlichem","gänzlichen","gänzlicher","gänzliches","gar","gbr","geb","geben","geblieben","gebracht","gedurft","geehrt","geehrte","geehrten","geehrter","gefallen","gefälligst","gefällt","gefiel","gegeben","gegen","gegenüber","gegenueber","gehabt","gehalten","gehen","geht","gekannt","gekommen","gekonnt","gemacht","gemaess","gemäss","gemeinhin","gemocht","gemusst","genau","genommen","genug","gepriesener","gepriesenes","gerade","gern","gesagt","geschweige","gesehen","gestern","gestrige","getan","geteilt","geteilte","getragen","getrennt","gewesen","gewiss","gewisse","gewissem","gewissen","gewisser","gewissermaßen","gewisses","gewollt","geworden","ggf","ggf.","gib","gibt","gilt","ging","gleich","gleiche","gleichem","gleichen","gleicher","gleiches","gleichsam","gleichste","gleichstem","gleichsten","gleichster","gleichstes","gleichwohl","gleichzeitig","gleichzeitige","gleichzeitigem","gleichzeitigen","gleichzeitiger","gleichzeitiges","glücklicherweise","gluecklicherweise","gmbh","gott","gottseidank","gratulieren","gratuliert","gratulierte","groesstenteils","groß","gross","große","grosse","großen","grossen","großer","grosser","großes","grosses","grösstenteils","gruendlich","gründlich","gut","gute","guten","guter","gutes","h","hab","habe","haben","habt","haette","haeufig","haeufige","haeufigem","haeufigen","haeufiger","haeufigere","haeufigeren","haeufigerer","haeufigeres","halb","hallo","halten","hast","hat","hätt","hatte","hätte","hatten","hätten","hattest","hattet","häufig","häufige","häufigem","häufigen","häufiger","häufigere","häufigeren","häufigerer","häufigeres","heisst","hen","her","heraus","herein","herum","heute","heutige","heutigem","heutigen","heutiger","heutiges","hier","hierbei","hiermit","hiesige","hiesigem","hiesigen","hiesiger","hiesiges","hin","hindurch","hinein","hingegen","hinlanglich","hinlänglich","hinten","hintendran","hinter","hinterher","hinterm","hintern","hinunter","hoch","höchst","höchstens","http","hundert","i","ich","igitt","ihm","ihn","ihnen","ihr","ihre","ihrem","ihren","ihrer","ihres","ihretwegen","ihrige","ihrigen",
                "ihriges","im","immer","immerhin","immerwaehrend","immerwaehrende","immerwaehrendem","immerwaehrenden","immerwaehrender","immerwaehrendes","immerwährend","immerwährende","immerwährendem","immerwährenden","immerwährender","immerwährendes","immerzu","important","in","indem","indessen","Inf.","info","infolge","infolgedessen","information","innen","innerhalb","innerlich","ins","insbesondere","insgeheim","insgeheime","insgeheimer","insgesamt","insgesamte","insgesamter","insofern","inzwischen","irgend","irgendein","irgendeine","irgendeinem","irgendeiner","irgendeines","irgendetwas","irgendjemand","irgendjemandem","irgendwann","irgendwas","irgendwelche","irgendwen","irgendwenn","irgendwer","irgendwie","irgendwo","irgendwohin","ist","j","ja","jaehrig","jaehrige","jaehrigem","jaehrigen","jaehriger","jaehriges","jahr","jahre","jahren","jährig","jährige","jährigem","jährigen","jähriges","je","jede","jedem","jeden","jedenfalls","jeder","jederlei","jedermann","jedermanns","jedes","jedesmal","jedoch","jeglichem","jeglichen","jeglicher","jegliches","jemals","jemand","jemandem","jemanden","jemandes","jene","jenem","jenen","jener","jenes","jenseitig","jenseitigem","jenseitiger","jenseits","jetzt","jung","junge","jungem","jungen","junger","junges","k","kaeumlich","kam","kann","kannst","kaum","käumlich","kein","keine","keinem","keinen","keiner","keinerlei","keines","keineswegs","klar","klare","klaren","klares","klein","kleine","kleinen","kleiner","kleines","koennen","koennt","koennte","koennten","koenntest","koenntet","komme","kommen","kommt","konkret","konkrete","konkreten","konkreter","konkretes","könn","können","könnt","konnte","könnte","konnten","könnten","konntest","könntest","konntet","könntet","kuenftig","kuerzlich","kuerzlichst","künftig","kurz","kürzlich","kürzlichst","l","laengst","lag","lagen","lang","lange","langsam","längst","längstens","lassen","laut","lediglich","leer","legen","legte","legten","leicht","leide","leider","lesen","letze","letzte","letzten","letztendlich","letztens","letztere","letzterem","letzterer","letzteres","letztes","letztlich","lichten","lieber","liegt","liest","links","los","m","mache","machen","machst","macht","machte","machten","mag","magst","mahn","mal","man","manch","manche","manchem","manchen","mancher","mancherlei","mancherorts","manches","manchmal","mann","margin","massgebend","massgebende","massgebendem","massgebenden","massgebender","massgebendes","massgeblich","massgebliche","massgeblichem","massgeblichen","massgeblicher","mehr","mehrere","mehrerer","mehrfach","mehrmalig","mehrmaligem","mehrmaliger","mehrmaliges","mein","meine","meinem","meinen","meiner","meines","meinetwegen","meins","meist","meiste","meisten","meistens","meistenteils","mensch","menschen","meta","mich","mindestens","mir","mit","miteinander","mitgleich","mithin","mitnichten","mittel","mittels","mittelst","mitten","mittig","mitunter","mitwohl","mochte","möchte","mochten","möchten","möchtest","moechte","moeglich","moeglichst","moeglichste","moeglichstem","moeglichsten","moeglichster","mögen","möglich","mögliche","möglichen","möglicher","möglicherweise","möglichst","möglichste","möglichstem","möglichsten","möglichster","mögt","morgen","morgige","muessen","muesst","muesste","muß","muss","müssen","mußt","musst","müßt","müsst","musste","müsste","mussten","müssten","n","na","nach","nachdem","nacher","nachher","nachhinein","nächste","nacht","naechste","naemlich","nahm","nämlich","naturgemaess","naturgemäss","natürlich","ncht","neben","nebenan","nehmen","nein","neu","neue","neuem","neuen","neuer","neuerdings","neuerlich","neuerliche","neuerlichem","neuerlicher","neuerliches","neues","neulich","neun","neunte","neunten","neunter","neuntes","nicht","nichts","nichtsdestotrotz","nichtsdestoweniger","nie","niemals","niemand","niemandem","niemanden","niemandes","nimm","nimmer","nimmt","nirgends","nirgendwo","noch","noetigenfalls","nötigenfalls","nun","nur","nutzen","nutzt","nützt","nutzung","o","ob","oben","ober","oberen","oberer","oberhalb","oberste","obersten","oberster","obgleich","obs","obschon","obwohl","oder","oefter","oefters","off","offen","offenkundig","offenkundige","offenkundigem","offenkundigen","offenkundiger","offenkundiges","offensichtlich","offensichtliche","offensichtlichem","offensichtlichen","offensichtlicher","offensichtliches","oft","öfter","öfters","oftmals","ohne","ohnedies","online","ordnung","p","paar","partout","per","persoenlich","persoenliche","persoenlichem","persoenlicher","persoenliches","persönlich","persönliche","persönlicher","persönliches","pfui","ploetzlich","ploetzliche","ploetzlichem","ploetzlicher","ploetzliches","plötzlich","plötzliche","plötzlichem","plötzlicher","plötzliches","pro","q","quasi","r","reagiere","reagieren","reagiert","reagierte","recht","rechte","rechten","rechter","rechtes","rechts","regelmäßig","reichlich","reichliche","reichlichem","reichlichen","reichlicher","restlos","restlose","restlosem","restlosen","restloser","restloses","richtig","richtiggehend","richtiggehende","richtiggehendem","richtiggehenden","richtiggehender","richtiggehendes","rief","rund","rundheraus","rundum","runter","s","sa","sache","sage","sagen","sagt","sagte","sagten","sagtest","sagtet","sah","samt","sämtliche","sang","sangen","satt","sattsam","schätzen","schätzt","schätzte","schätzten","scheinbar","scheinen","schlecht","schlechter","schlicht","schlichtweg","schließlich","schluss","schlussendlich","schnell","schon","schreibe","schreiben","schreibens","schreiber","schwerlich","schwerliche","schwerlichem","schwerlichen","schwerlicher","schwerliches","schwierig","sechs","sechste","sechsten","sechster","sechstes","sect","sehe","sehen","sehr","sehrwohl","seht","sei","seid","seien","seiest","seiet","sein","seine","seinem","seinen","seiner","seines","seit","seitdem","seite","seiten","seither","selbe","selben","selber","selbst","selbstredend","selbstredende","selbstredendem","selbstredenden","selbstredender","selbstredendes","seltsamerweise","senke","senken","senkt","senkte","senkten","setzen","setzt","setzte","setzten","sich","sicher","sicherlich","sie","sieben","siebente","siebenten","siebenter","siebentes","siebte","siehe","sieht","sind","singen","singt","so","sobald","sodaß","soeben","sofern","sofort","sog","sogar","sogleich","solang","solange","solc","solchen","solch","solche","solchem","solchen","solcher","solches","soll","sollen","sollst","sollt","sollte","sollten","solltest","solltet","somit","sondern","sonst","sonstig","sonstige","sonstigem","sonstiger","sonstwo","sooft","soviel","soweit","sowie","sowieso","sowohl","später","spielen","startet","startete","starteten","startseite","statt","stattdessen","steht","steige","steigen","steigt","stellenweise","stellenweisem","stellenweisen","stets","stieg","stiegen","such","suche","suchen","t","tag","tage","tagen","tages","tat","tät","tatsächlich","tatsächlichen","tatsächlicher","tatsächliches","tatsaechlich","tatsaechlichen","tatsaechlicher","tatsaechliches","tausend","teil","teile","teilen","teilte","teilten","tel","tief","titel","toll","total","trage","tragen","trägt","tritt","trotzdem","trug","tun","tust","tut","txt","u","übel","über","überall","überallhin","überaus","überdies","überhaupt","überll","übermorgen","üblicherweise","übrig","übrigens","ueber","ueberall","ueberallhin","ueberaus","ueberdies","ueberhaupt","uebermorgen","ueblicherweise","uebrig","uebrigens","uhr","um","ums","umso","umstaendehalber","umständehalber","unbedingt","unbedingte","unbedingter","unbedingtes","und","unerhoert","unerhoerte","unerhoertem","unerhoerten","unerhoerter","unerhoertes","unerhört","unerhörte","unerhörtem","unerhörten","unerhörter","unerhörtes","ungefähr","ungemein","ungewoehnlich","ungewoehnliche","ungewoehnlichem","ungewoehnlichen","ungewoehnlicher","ungewoehnliches","ungewöhnlich","ungewöhnliche","ungewöhnlichem","ungewöhnlichen","ungewöhnlicher","ungewöhnliches","ungleich","ungleiche","ungleichem","ungleichen","ungleicher","ungleiches","unmassgeblich","unmassgebliche","unmassgeblichem","unmassgeblichen","unmassgeblicher","unmassgebliches","unmoeglich","unmoegliche","unmoeglichem","unmoeglichen","unmoeglicher","unmoegliches","unmöglich","unmögliche","unmöglichen","unmöglicher","unnötig","uns","unsaeglich","unsaegliche","unsaeglichem","unsaeglichen","unsaeglicher","unsaegliches","unsagbar","unsagbare","unsagbarem","unsagbaren","unsagbarer","unsagbares","unsäglich","unsägliche","unsäglichem","unsäglichen","unsäglicher","unsägliches","unse","unsem","unsen","unser","unsere","unserem","unseren","unserer","unseres","unserm","unses","unsre","unsrem","unsren","unsrer","unsres","unstreitig","unstreitige","unstreitigem","unstreitigen","unstreitiger","unstreitiges","unten","unter","unterbrach","unterbrechen","untere","unterem","unteres","unterhalb","unterste","unterster","unterstes","unwichtig","unzweifelhaft","unzweifelhafte","unzweifelhaftem","unzweifelhaften","unzweifelhafter","unzweifelhaftes","usw","usw.","v","vergangen","vergangene","vergangenen","vergangener","vergangenes","vermag","vermögen","vermutlich","vermutliche","vermutlichem","vermutlichen","vermutlicher","vermutliches","veröffentlichen","veröffentlicher","veröffentlicht","veröffentlichte","veröffentlichten","veröffentlichtes","verrate","verraten","verriet","verrieten","version","versorge","versorgen","versorgt","versorgte","versorgten","versorgtes","viel","viele","vielem","vielen","vieler","vielerlei","vieles","vielleicht","vielmalig","vielmals","vier","vierte","vierten","vierter","viertes","voellig","voellige","voelligem","voelligen","voelliger","voelliges","voelligst","vollends","völlig","völlige","völligem","völligen","völliger","völliges","völligst","vollstaendig","vollstaendige","vollstaendigem","vollstaendigen","vollstaendiger","vollstaendiges","vollständig","vollständige","vollständigem","vollständigen","vollständiger","vollständiges","vom","von","vor","voran","vorbei","vorgestern","vorher","vorherig","vorherige","vorherigem","vorheriger",
                "vorne","vorüber","vorueber","w","wachen","waehrend","waehrenddessen","waere","während","währenddem","währenddessen","wann","war","wär","wäre","waren","wären","warst","wart","warum","was","weder","weg","wegen","weil","weiß","weit","weiter","weitere","weiterem","weiteren","weiterer","weiteres","weiterhin","weitestgehend","weitestgehende","weitestgehendem","weitestgehenden","weitestgehender","weitestgehendes","weitgehend","weitgehende","weitgehendem","weitgehenden","weitgehender","weitgehendes","welche","welchem","welchen","welcher","welches","wem","wen","wenig","wenige","weniger","weniges","wenigstens","wenn","wenngleich","wer","werde","werden","werdet","weshalb","wessen","weswegen","wichtig","wie","wieder","wiederum","wieso","wieviel","wieviele","wievieler","wiewohl","will","willst","wir","wird","wirklich","wirklichem","wirklicher","wirkliches","wirst","wissen","wo","wobei","wodurch","wofuer","wofür","wogegen","woher","wohin","wohingegen","wohl","wohlgemerkt","wohlweislich","wolle","wollen","wollt","wollte","wollten","wolltest","wolltet","womit","womoeglich","womoegliche","womoeglichem","womoeglichen","womoeglicher","womoegliches","womöglich","womögliche","womöglichem","womöglichen","womöglicher","womögliches","woran","woraufhin","woraus","worden","worin","wuerde","wuerden","wuerdest","wuerdet","wurde","würde","wurden","würden","wurdest","würdest","wurdet","würdet","www","x","y","z","z.b","z.B.","zahlreich","zahlreichem","zahlreicher","zB","zb.","zehn","zehnte","zehnten","zehnter","zehntes","zeit","zeitweise","zeitweisem","zeitweisen","zeitweiser","ziehen","zieht","ziemlich","ziemliche","ziemlichem","ziemlichen","ziemlicher","ziemliches","zirka","zog","zogen","zu","zudem","zuerst","zufolge","zugleich","zuletzt","zum","zumal","zumeist","zumindest","zunächst","zunaechst","zur","zurück","zurueck","zusammen","zusehends","zuviel","zuviele","zuvieler","zuweilen","zwanzig","zwar","zwei","zweifelsfrei","zweifelsfreie","zweifelsfreiem","zweifelsfreien","zweifelsfreier","zweifelsfreies","zweite","zweiten","zweiter","zweites","zwischen","zwölf"]
                if st.checkbox('Show built-in list of stop words', value = False): 
                    st.dataframe(pd.DataFrame(word_stopwords,columns=['stop word'])) 
                if st.checkbox('Add additional stop words', value = False): 
                    user_stopwords=st.text_area('Please enter or copy additional stop words here', value='', height=200)
                    if len(user_stopwords)>0:                                        
                        added_stopwords=fc.get_stop_words(user_stopwords)
                        word_stopwords=word_stopwords+added_stopwords
            elif stopword_selection=="Use a built-in list of stop words in English":
                word_stopwords=['a','about','above','after','again','against','ain','all','am','an','and','any','are','aren',"aren't",'as','at','be','because','been','before','being','below','between','both','but','by','can','couldn',"couldn't",'d','did','didn',"didn't",'do','does','doesn',"doesn't",'doing','don',"don't",'down','during','each','few','for','from','further','had','hadn',"hadn't",'has','hasn',"hasn't",'have','haven',"haven't",'having','he','her','here','hers','herself','him','himself','his','how','i','if','in','into','is','isn',"isn't",'it',"it's",'its','itself','just','ll','m','ma','me','mightn',"mightn't",'more','most','mustn',"mustn't",'my','myself','needn',"needn't",'no','nor','not','now','o','of','off','on','once','only','or','other','our','ours','ourselves','out','over','own','re','s','same','shan',"shan't",'she',"she's",'should',"should've",'shouldn',"shouldn't",'so','some','such','t','than','that',"that'll",'the','their','theirs','them','themselves','then','there','these','they','this','those','through','to','too','under','until','up','ve','very','was','wasn',"wasn't",'we','were','weren',"weren't",'what','when','where','which','while','who','whom','why','will','with','won',"won't",'wouldn',"wouldn't",'y','you',"you'd","you'll","you're","you've",'your','yours','yourself','yourselves']
                if st.checkbox('Show built-in list of stop words', value = False): 
                    st.dataframe(pd.DataFrame(word_stopwords,columns=['stop word'])) 
                if st.checkbox('Add additional stop words', value = False): 
                    user_stopwords=st.text_area('Please enter or copy additional stop words here', value='', height=200 )
                    if len(user_stopwords)>0:                                        
                        added_stopwords=fc.get_stop_words(user_stopwords)
                        word_stopwords=word_stopwords+added_stopwords
            elif stopword_selection=="Specify stop words":
                word_stopwords=[]
                user_stopwords=st.text_area('Please enter or copy stop words here', value='', height=200 )
                if len(user_stopwords)>0:                                        
                    word_stopwords=fc.get_stop_words(user_stopwords)
                                        
                st.write("")

            a4,a5=st.columns(2)
            with a4:
                # user specification of words to search
                word_list=pd.DataFrame(columns=word_sorted.index)                
                #words_cleaned=word_list.drop(word_stopwords,axis=1)
                words_cleaned=sorted(list(set(word_list)-set(word_stopwords)))       
                
                find_words=st.multiselect("Search sentences with following words", 
                    words_cleaned)
            with a5:
                #user-specification of n-grams
                user_ngram=st.number_input("Specify the number of words to be extracted (n-grams)", min_value=1, value=2)
            
            if st.checkbox('Show a word count', value = False): 
                st.write(word_sorted)  
            
             
            a4,a5=st.columns(2)
            with a4:
                #WordCloud color specification               
                st.write("")
                draw_WordCloud=st.checkbox("Create a Word Cloud", value=True)  
            
            with a5:    
                if draw_WordCloud==True:              
                    #color options for the WordCloud (user selection)
                    color_options= pd.DataFrame(np.array([[21, 120, 12, 240, 30]]), 
                    columns=['orange', 'green', 'red','blue','brown'])
                    
                    user_color_name=st.selectbox('Select main color of your WordCloud',color_options.columns)
                    user_color=color_options[user_color_name]
            
            
            st.write("")
            st.write("")
            run_text = st.button("Press to start text processing...")
                

            if run_text:
                st.write("")
                st.write("")

                st.info("Text processing progress")
                text_bar = st.progress(0.0)
                progress = 0

                #Text preprocessing
                user_text=fc.text_preprocessing(user_text,text_prep_ops,user_language)
                                
                #---------------------------------------------------------------------------------
                # Basic NLP metrics and visualisations
                #---------------------------------------------------------------------------------
                wfreq_output = st.expander("Basic NLP metrics and visualisations ", expanded = False)
                with wfreq_output:
                    # Word frequency
                    st.subheader('Word count') 
                    
                    #calculate word frequency - stop words exluded:
                    word_sorted=fc.cv_text(user_text, word_stopwords, 1,user_precision,number_remove)
                                                         
                    st.write("")
                    st.write("Number of words: ", word_sorted["Word count"].sum())
                    st.write("Number of sentences", len(re.findall(r"([^.]*\.)" ,user_text)))
                    
                    if len(word_stopwords)>0:
                        st.warning("All analyses are based on text with stop words removed!") 
                    else:
                        st.warning("No stop words are removed from the text!") 

                    
                    st.write(word_sorted.style.format({"Rel. freq.": "{:.2f}"}))
                    
                    a4,a5=st.columns(2)
                    with a4:
                        # relative frequency for the top 10 words
                        txt_bar=word_sorted.head(min(len(word_sorted),10))
                        
                        fig = go.Figure()                
                        fig.add_trace(go.Bar(x=txt_bar["Rel. freq."], y=txt_bar.index, name='',marker_color = 'indianred',opacity=0.5,orientation='h'))
                        fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',})  
                        fig.update_layout(xaxis=dict(title='relative fraction %', titlefont_size=14, tickfont_size=14,),)
                        fig.update_layout(hoverlabel=dict(bgcolor="white",align="left"))
                        fig.update_layout(height=400,width=400)
                        st.plotly_chart(fig, use_container_width=True) 
                        st.info("Top " + str(min(len(word_sorted),10)) + " words relative frequency")  

                    with a5:
                        fig = go.Figure(data=[go.Histogram(x=word_sorted["Word length"], histnorm='probability',marker_color ='steelblue',opacity=0.5)])
                        fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',})  
                        fig.update_layout(xaxis=dict(title='word length', titlefont_size=14, tickfont_size=14,),)
                        fig.update_layout(hoverlabel=dict(bgcolor="white",align="left"))
                        fig.update_layout(height=400,width=400)
                        st.plotly_chart(fig, use_container_width=True)  
                        st.info("Word length distribution")  

                    
                    #word similarity vs. word length & word frequency
                    word_similarity=[]    
                    for word in txt_bar.index:  
                        d=0                         
                        for sword in txt_bar.index:
                            seq = SequenceMatcher(None,word,sword)
                            d = d+(seq.ratio()*100)                                                       
                        word_similarity.append([d])
                    
                    txt_bar["Similarity"]=(np.float_(word_similarity)/len(txt_bar.index)).round(user_precision)

                    a4,a5=st.columns(2)
                    with a4:
                        # bubble chart                    
                        fig = go.Figure(data=[go.Scatter(
                        y=txt_bar.index, x=txt_bar["Rel. freq."], mode='markers',text=txt_bar["Similarity"],
                            marker_size=txt_bar["Similarity"],marker_color='indianred') ])
                        fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',})  
                        fig.update_layout(xaxis=dict(title='relative frequency', titlefont_size=14, tickfont_size=14,),)
                        fig.update_layout(hoverlabel=dict(bgcolor="white",align="left"))
                        fig.update_layout(height=400,width=400)
                        st.plotly_chart(fig, use_container_width=True) 
                        st.info("Bubble size eq. average word similarity across the top " + str(min(len(word_sorted),10)) +" words") 
                    with a5:
                        
                        df_to_plot=word_sorted
                        df_to_plot['word']=word_sorted.index
                        fig = px.scatter(data_frame=df_to_plot, x='Word length', y='Rel. freq.',hover_data=['word','Word length', 'Rel. freq.'], color_discrete_sequence=['steelblue'])
                        fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',}) 
                        fig.update_layout(xaxis=dict(title="word length", titlefont_size=14, tickfont_size=14,),)
                        fig.update_layout(yaxis=dict(title="word frequency", titlefont_size=14, tickfont_size=14,),)
                        fig.update_layout(hoverlabel=dict(bgcolor="white", ))
                        fig.update_layout(height=400,width=400)
                        st.plotly_chart(fig) 
                        st.info("A comparision of frequencies of short and long words")

                    # bigram distribution
                    cv2_output=fc.cv_text(user_text, word_stopwords, 2,user_precision,number_remove)
                                       

                    # trigram distribution
                    cv3_output=fc.cv_text(user_text, word_stopwords, 3,user_precision,number_remove)
                                

                    a4,a5=st.columns(2)
                    with a4:                        
                        txt_bar=cv2_output.head(min(len(cv2_output),10))                        
                        fig = go.Figure()                
                        fig.add_trace(go.Bar(x=txt_bar["Rel. freq."], y=txt_bar.index, name='',marker_color = 'indianred',opacity=0.5,orientation='h'))
                        fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',})  
                        fig.update_layout(xaxis=dict(title='relative fraction %', titlefont_size=14, tickfont_size=14,),)
                        fig.update_layout(hoverlabel=dict(bgcolor="white",align="left"))
                        fig.update_layout(height=400,width=400)
                        st.plotly_chart(fig, use_container_width=True) 
                        st.info("Top " + str(min(len(cv2_output),10)) + " bigrams relative frequency")  
                    
                    with a5:
                        txt_bar=cv3_output.head(10)                        
                        fig = go.Figure()                
                        fig.add_trace(go.Bar(x=txt_bar["Rel. freq."], y=txt_bar.index, name='',marker_color = 'indianred',opacity=0.5,orientation='h'))
                        fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',})  
                        fig.update_layout(xaxis=dict(title='relative fraction %', titlefont_size=14, tickfont_size=14,),)
                        fig.update_layout(hoverlabel=dict(bgcolor="white",align="left"))
                        fig.update_layout(height=400,width=400)
                        st.plotly_chart(fig, use_container_width=True) 
                        st.info("Top " + str(min(len(cv2_output),10)) + " trigrams relative frequency")  
                   
                    # Word Cloud 
                    if draw_WordCloud==True:                    
                        #Draw WordCloud
                        wordcloud = WordCloud(background_color="white",
                            contour_color="white",max_words=100,stopwords=word_stopwords,
                            width=600,height=400,color_func=random_color_func).generate(user_text)  
                        fig_text, ax = plt.subplots()
                        ax=plt.imshow(wordcloud, interpolation='bilinear')
                        plt.axis("off")
                        
                        st.subheader('WordCloud')
                        st.pyplot(fig_text)   
                    
                    progress += 1
                    text_bar.progress(progress/3)

                                        
                     # Download link
                    st.write("")  
                    output = BytesIO()
                    excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
                    word_sorted.to_excel(excel_file, sheet_name="words",index=False) 
                    if len(word_stopwords)>0:
                        pd.DataFrame(word_stopwords,columns=['stop words']).to_excel(excel_file, sheet_name="stop words",index=False)    
                    if len(cv2_output)>0:
                        cv2_output.to_excel(excel_file, sheet_name="bigrams",index=True) 
                    if len(cv3_output)>0:
                        cv3_output.to_excel(excel_file, sheet_name="trigrams",index=True) 
                    excel_file.close()
                    excel_file = output.getvalue()
                    b64 = base64.b64encode(excel_file)
                    dl_file_name = "BasicTextAnalysis.xlsx"
                    st.markdown(
                        f"""
                    <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download basic NLP metrics</a>
                    """,
                    unsafe_allow_html=True)
                    st.write("") 
                
                #---------------------------------------------------------------------------------
                # Sentiment analysis per sentence
                #---------------------------------------------------------------------------------
                    sentences = re.findall(r"([^.]*\.)" ,user_text) 
                    if user_language=="en":
                        sa_table = pd.DataFrame(index = range(0, len(sentences)), columns=["Sentence", "neg","neu","pos","compound"]) 
                        for i in range(0,len(sentences)):    
                            sid = SentimentIntensityAnalyzer()
                            sentence=sentences[i]                      
                            ss = sid.polarity_scores(sentence)                       
                            sa_table.loc[i]["Sentence"]=sentence
                                                      
                            sa_table.loc[i]["neg"]=ss["neg"]
                            sa_table.loc[i]["neu"]=ss["neu"]
                            sa_table.loc[i]["pos"]=ss["pos"]
                            sa_table.loc[i]["compound"]=ss["compound"]
                           
                            st.session_state['sentiment']=sa_table
                        
                    elif user_language=="de": 

                        if fc.is_localhost():                       
                            from germansentiment import SentimentModel
                            sa_table = pd.DataFrame(index = range(0, len(sentences)), columns=["Sentence", "pos","neg","neu"]) 
                            
                            model = SentimentModel() 
                            for i in range(0,len(sentences)):                           
                                sentence=sentences[i] 
                                classes, probs = model.predict_sentiment([sentence], output_probabilities = True)                    
                                sa_table.loc[i]["Sentence"]=sentence
                                sa_table.loc[i]["pos"]=probs[0][0][1]
                                sa_table.loc[i]["neg"]=probs[0][1][1]
                                sa_table.loc[i]["neu"]=probs[0][2][1]
                                st.session_state['sentiment']=sa_table
                             
                if st.session_state['sentiment'] is not None and user_language in ["de", "en"]:
                    sentiment_output = st.expander("Sentiment Analysis", expanded = False)
                    with sentiment_output:
                        if user_language=="de" and fc.is_localhost()==False: 
                            st.info("German sentiment analysis can be performed on localhost:8501 due to file size restrictions on the cloud!")        
                        else:
                            st.subheader('Sentiment Analysis')
                            st.write(sa_table.style.format(precision=user_precision))  
                            # Download link
                            st.write("")  
                            output = BytesIO()
                            excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
                            sa_table.to_excel(excel_file, sheet_name="sentiment",index=True) 
                                                
                            excel_file.close()
                            excel_file = output.getvalue()
                            b64 = base64.b64encode(excel_file)
                            dl_file_name = "SentimentAnalysis.xlsx"
                            st.markdown(
                                f"""
                            <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download sentiment results</a>
                            """,
                            unsafe_allow_html=True)
                            st.write("")            
                #---------------------------------------------------------------------------------
                # Sentences with specific words
                #---------------------------------------------------------------------------------
                if len(find_words)>0:                   
                    # extract all sentences with specific words:                 
                    sentences_list=[]                  
                    sentences = re.findall(r"([^.]*\.)" ,user_text) 
                    
                    for sentence in sentences:
                        if all(word in sentence for word in find_words):                                
                            if len(sentence)<1000: # threshold for to long sentences is 1000 characters
                                sentences_list.append(sentence)
                               
                    if len(sentences_list)>0: 
                        sentences_output = st.expander("Sentences with specific words", expanded = False)
                        with sentences_output:
                            for sentence in sentences_list:
                                st.write(sentence)
                                #st.table(pd.DataFrame({'Sentences':sentences_list}))
                        
                            # Download link
                            st.write("")  
                            output = BytesIO()
                            excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
                            pd.DataFrame({'Sentences':sentences_list}).to_excel(excel_file, sheet_name="Sentences",index=False) 
                            excel_file.close()
                            excel_file = output.getvalue()
                            b64 = base64.b64encode(excel_file)
                            dl_file_name = "Sentences with specific words.xlsx"
                            st.markdown(
                                f"""
                            <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download sentences</a>
                            """,
                            unsafe_allow_html=True)
                            st.write("") 
                                
                progress += 1
                text_bar.progress(progress/3)
                
                
                #---------------------------------------------------------------------------------
                # User specific n-grams
                #---------------------------------------------------------------------------------
                #extract n-grams:
                ngram_list=[]              
                
                text_cv = fc.cv_text(user_text, word_stopwords,user_ngram,user_precision,number_remove)
                
                #CountVectorizer(analyzer='word', stop_words=set(word_stopwords), ngram_range=(user_ngram, user_ngram))
                #text_cv_fit=text_cv.fit_transform([user_text])
                #listToString='. '.join(text_cv.get_feature_names())
                listToString='. '.join(text_cv.index)
                sentences = re.findall(r"([^.]*\.)" ,listToString)  
                            
                for sentence in sentences:
                    if all(word in sentence for word in find_words):  
                        sentence=re.sub('[.]', '', sentence)                                             
                        ngram_list.append(sentence)
                
                if len(ngram_list)>0:
                    ngram_output = st.expander("n-grams", expanded = False)
                    with ngram_output: 
                        st.write("")
                        st.subheader("n-grams")
                        st.write("")
                        
                        for sentence in ngram_list:
                            st.write(sentence)

                        # Download link
                        st.write("")  
                        output = BytesIO()
                        excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
                        pd.DataFrame({'n-gram':ngram_list}).to_excel(excel_file, sheet_name=str(user_ngram) +"-gram",index=False) 
                        excel_file.close()
                        excel_file = output.getvalue()
                        b64 = base64.b64encode(excel_file)
                        dl_file_name = str(user_ngram)+"gram.xlsx"
                        st.markdown(
                            f"""
                        <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download n-grams</a>
                        """,
                        unsafe_allow_html=True)                    
                
                        st.write("") 
                
                progress += 1
                text_bar.progress(progress/3)
                
 
    #---------------------------------------------               
    # Stock data access via yfinance
    #---------------------------------------------    
    if tw_classifier =='Stock data access via yfinance':  

        # Clear cache
        #st.runtime.legacy_caching.clear_cache()

        # dwonload first the list of comanies in the S&P500 and DAX indices
        payload=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        first_table = payload[0]
        df = first_table
        symbols = df['Symbol'].values.tolist()
        company = df['Security'].values.tolist()
        sector = df['GICS Sector'].values.tolist()
        #sectors = set(sectors)

        payload1=pd.read_html('https://en.wikipedia.org/wiki/DAX')
        
        DAXtable = payload1[4]
        df=DAXtable
        DAXsymbols = df['Ticker'].values.tolist()
        DAXSector = df['Prime Standard Sector'].values.tolist()
        DAXcompany= df['Company'].values.tolist()

        #Merge indices data
        symbols_all=symbols+DAXsymbols
        sector_all=sector+DAXSector 
        company_all=company+DAXcompany

        #ticker specification
        st.subheader('Stock data analysis')
        a3, a4 = st.columns(2) 
        with a3:
            first_stock = st.text_input("Enter a stock ticker symbol", "TSLA", on_change=in_wid_change)
            symbols_all=list('-')+symbols_all
            second_stock = st.selectbox('You can add an additional stock for comparision...',symbols_all, on_change=in_wid_change)
        with a4:
            today = datetime.date.today()
            last_year = today - datetime.timedelta(days=365)
            start_date = st.date_input('Select start date', last_year, on_change=in_wid_change)
            end_date = st.date_input('Select end date', today, on_change=in_wid_change)
            if start_date > end_date:
                st.error('ERROR: End date must fall after start date.')     

        st.markdown("")
        add_data_show=st.checkbox("Get additional data (cashflow, balance sheet etc.)", value = False, on_change=in_wid_change)
        if add_data_show:
            st.info("Additional data are frequently not available - yfinance is failing to decrypt Yahoo data response.")
        st.markdown("")
        
       
        dev_expander_perf = st.expander("Stock performance", expanded=True)
        with dev_expander_perf:
            #get data for a selected ticker symbol:
            stock_data = yf.Ticker(first_stock)
            stock_df = stock_data.history(period='1d', start=start_date, end=end_date)
            st.session_state['stock_df']=stock_df

            if second_stock !="-":
                add_stock_data = yf.Ticker(second_stock)
                add_stock_df = add_stock_data.history(period='1d', start=start_date, end=end_date)
                st.session_state['add_stock_df']=add_stock_df

            #print stock values
            if st.checkbox("Show stock data for " + first_stock, value = True): 
                st.write(stock_df)
            
            if second_stock !="-":    
                if st.checkbox("Show stock data for " + second_stock, value = False): 
                    st.write(add_stock_df)
                comparision_check=st.checkbox('Compare '+ first_stock + " & " + second_stock, value = True)
            
            #draw line chart with stock prices
            a5, a6 = st.columns(2) 
            with a5:
                stock_para= st.selectbox('Select ' + first_stock + " info to draw", stock_df.columns)
                if second_stock !="-":   
                    if comparision_check: 
                        st.write('Daily data comparision '+ first_stock + " & " + second_stock)
                        
                        c1=first_stock + " " + stock_para
                        c2=second_stock + " " + stock_para
                        c1_data=stock_df[[stock_para]]
                        c1_data.rename(columns={c1_data.columns[0]: c1 }, inplace = True)
                        c2_data=add_stock_df[[stock_para]]
                        c2_data.rename(columns={c2_data.columns[0]: c2 }, inplace = True)
                        stock_dataToplot=pd.concat([c1_data, c2_data], axis=1)
                        
                        #st.write(stock_dataToplot)
                        st.line_chart(stock_dataToplot)
                    else:
                        st.write(stock_para + " price for " + first_stock + " (daily)")
                        stock_dataToplot=stock_df[stock_para]
                        st.line_chart(stock_dataToplot)   
                else:    
                    st.write(stock_para + " price for " + first_stock + " (daily)")
                    stock_dataToplot=stock_df[stock_para]
                    st.line_chart(stock_dataToplot)

            with a6:
                stock_para2= st.selectbox('Select ' + first_stock + " info to draw", stock_df.columns, index=3)
                if second_stock !="-":   
                    if comparision_check: 
                        st.write('Daily data comparision '+ first_stock + " & " + second_stock)
                        
                        c3=first_stock + " " + stock_para2
                        c4=second_stock + " " + stock_para2
                        c3_data=stock_df[[stock_para2]]
                        c3_data.rename(columns={c3_data.columns[0]: c3 }, inplace = True)
                        c4_data=add_stock_df[[stock_para2]]
                        c4_data.rename(columns={c4_data.columns[0]: c4 }, inplace = True)
                        stock_dataToplot2=pd.concat([c3_data, c4_data], axis=1)
                        
                        #st.write(stock_dataToplot)
                        st.line_chart(stock_dataToplot2)
                    else:
                        st.write(stock_para2 + " price for " + first_stock + " (daily)")
                        stock_dataToplot2=stock_df[stock_para2]
                        st.line_chart(stock_dataToplot2)   
                else:    
                    st.write(stock_para2 + " price for " + first_stock + " (daily)")
                    stock_dataToplot2=stock_df[stock_para2]
                    st.line_chart(stock_dataToplot2)        
        
        # Show additional stock information
        if add_data_show:
            
            dev_expander_cf = st.expander("Cashflow",expanded=False)
            with dev_expander_cf:
                st.subheader(first_stock)
                
                if len(yf.Ticker(first_stock).cashflow)==0:
                    st.info("No data are available!")  
                else:     
                    st.write(yf.Ticker(first_stock).cashflow)                     
                if second_stock !='-':
                    st.subheader(second_stock)
                    if len(yf.Ticker(second_stock).cashflow)==0:
                        st.info("No data are available!")  
                    else: 
                        st.write(yf.Ticker(second_stock).cashflow)

            dev_expander_bs = st.expander("Balance sheet", expanded=False)
            with dev_expander_bs:                
                st.subheader(first_stock)                
                if len(yf.Ticker(first_stock).balance_sheet)==0:
                    st.info("No data are available!")  
                else:                    
                    st.write(yf.Ticker(first_stock).balance_sheet)
               
                if second_stock !='-':
                    st.subheader(second_stock)
                    if len(yf.Ticker(second_stock).balance_sheet)==0:
                        st.info("No data are available!")  
                    else:                    
                        st.write(yf.Ticker(second_stock).balance_sheet)

            dev_expander_fi = st.expander("Other financials",expanded=False)
            with dev_expander_fi:
                st.subheader(first_stock)                
                if len(yf.Ticker(first_stock).financials)==0:
                    st.info("No data are available!")  
                else:
                    st.write(yf.Ticker(first_stock).financials) 
                if second_stock !='-':
                    st.subheader(second_stock)
                    if len(yf.Ticker(second_stock).financials)==0:
                        st.info("No data are available!")  
                    else: 
                        st.write(yf.Ticker(second_stock).financials)   
            
            # set session key for addtional paramaters    
            st.session_state['add_data_show']='add_data_show_key'
     




 
