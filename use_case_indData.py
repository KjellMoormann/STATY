#----------------------------------------------------------------------------------------------

####################
# IMPORT LIBRARIES #
####################

import streamlit as st
import pandas as pd
import numpy as np
import plotly as dd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.font_manager
import plotly.graph_objects as go
import functions as fc
import modelling as ml
import os
import altair as alt
import altair 
import itertools
import statsmodels.api as sm
from scipy import stats 
import sys
from streamlit import caching
import SessionState
import platform
import base64
from io import BytesIO

#----------------------------------------------------------------------------------------------

def app():

    # Clear cache
    caching.clear_cache()

    # Hide traceback in error messages (comment out for de-bugging)
    sys.tracebacklimit = 0

    # Show altair tooltip when full screen
    st.markdown('<style>#vg-tooltip-element{z-index: 1000051}</style>',unsafe_allow_html=True)

    #Session state
    session_state = SessionState.get(id = 0)

    #------------------------------------------------------------------------------------------
    
    #++++++++++++++++++++++++++++++++++++++++++++
    # DATA IMPORT

    # File upload section
    df_dec = st.sidebar.radio("Get data", ["Use example dataset", "Upload data"])
    uploaded_data=None
    if df_dec == "Upload data":
        #st.subheader("Upload your data")
        #uploaded_data = st.sidebar.file_uploader("Make sure that dot (.) is a decimal separator!", type=["csv", "txt"])
        separator_expander=st.sidebar.beta_expander('Upload settings')
        with separator_expander:
                      
            a4,a5=st.beta_columns(2)
            with a4:
                dec_sep=a4.selectbox("Decimal sep.",['.',','], key = session_state.id)

            with a5:
                col_sep=a5.selectbox("Column sep.",[';',  ','  , '|', '\s+', '\t','other'], key = session_state.id)
                if col_sep=='other':
                    col_sep=st.text_input('Specify your column separator', key = session_state.id)     

            a4,a5=st.beta_columns(2)  
            with a4:    
                thousands_sep=a4.selectbox("Thousands x sep.",[None,'.', ' ','\s+', 'other'], key = session_state.id)
                if thousands_sep=='other':
                    thousands_sep=st.text_input('Specify your thousands separator', key = session_state.id)  
             
            with a5:    
                encoding_val=a5.selectbox("Encoding",[None,'utf_8','utf_8_sig','utf_16_le','cp1140','cp1250','cp1251','cp1252','cp1253','cp1254','other'], key = session_state.id)
                if encoding_val=='other':
                    encoding_val=st.text_input('Specify your encoding', key = session_state.id)  
        
        # Error handling for separator selection:
        if dec_sep==col_sep: 
            st.sidebar.error("Decimal and column separators cannot be identical!") 
        elif dec_sep==thousands_sep:
            st.sidebar.error("Decimal and thousands separators cannot be identical!") 
        elif  col_sep==thousands_sep:
            st.sidebar.error("Column and thousands separators cannot be identical!")    
        
        uploaded_data = st.sidebar.file_uploader("Default separators: decimal '.'    |     column  ';'", type=["csv", "txt"])
        
        if uploaded_data is not None:
            df = pd.read_csv(uploaded_data, decimal=dec_sep, sep = col_sep,thousands=thousands_sep,encoding=encoding_val, engine='python')
            df_name=os.path.splitext(uploaded_data.name)[0]
            st.sidebar.success('Loading data... done!')
        elif uploaded_data is None:
           df = pd.read_csv("default data/WHR_2021.csv", sep = ";|,|\t",engine='python')
           df_name="WHR_2021" 
    else:
        df = pd.read_csv("default data/WHR_2021.csv", sep = ";|,|\t",engine='python') 
        df_name="WHR_2021" 
    st.sidebar.markdown("")
        
    #Basic data info
    n_rows = df.shape[0]
    n_cols = df.shape[1]  
    # df_name = "WHR_2021"
    # if uploaded_data is not None:
    #     df_name = list(uploaded_data.name.split(".")[:-1])
    #     if len(df_name) > 1:
    #         new_name = ""
    #         for i in range(0, len(df_name)):
    #             if i < len(df_name)-1:
    #                 new_name += df_name[i]+"_"
    #             if i == len(df_name)-1:
    #                 new_name += df_name[i]
    #         df_name = new_name
    #     else:
    #         df_name = df_name[0]

    #++++++++++++++++++++++++++++++++++++++++++++
    # SETTINGS

    settings_expander=st.sidebar.beta_expander('Settings')
    with settings_expander:
        st.caption("**Help**")
        sett_hints = st.checkbox('Show learning hints', value=False)
        st.caption("**Appearance**")
        sett_wide_mode = st.checkbox('Wide mode', value=False)
        sett_theme = st.selectbox('Theme', ["Light", "Dark"])
        #sett_info = st.checkbox('Show methods info', value=False)
        #sett_prec = st.number_input('Set the number of diggits for the output', min_value=0, max_value=8, value=2)
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

    #++++++++++++++++++++++++++++++++++++++++++++
    # RESET INPUT

    reset_clicked = st.sidebar.button("Reset all your input")
    if reset_clicked:
        session_state.id = session_state.id + 1
    st.sidebar.markdown("")

    #------------------------------------------------------------------------------------------

    
    #++++++++++++++++++++++++++++++++++++++++++++
    # DATA EXPLORATION & VISUALIZATION

    st.header("**Multivariate data**")
    st.markdown("Get your data ready for powerfull methods: Artificial Neural Networks, Boosted Regression Trees, Random Forest, Generalized Additive Models, Multiple Linear Regression, and Logistic Regression! Let STATY do data cleaning, variable transformations, visualizations and deliver you the stats you need. Specify your data processing preferences and start exploring your data stories right below... ")
    
    # Check if enough data is available
    if n_rows > 0 and n_cols > 0:
        st.empty()
    else:
        st.error("ERROR: Not enough data!")
        return

    data_empty_container = st.beta_container()
    with data_empty_container:
        st.empty()
        st.empty()
        st.empty()
        st.empty()
        st.empty()
        st.empty()
        st.empty()
        st.empty()
    
    data_exploration_container = st.beta_container()
    with data_exploration_container:

        st.header("**Data exploration **")

        #------------------------------------------------------------------------------------------

        #++++++++++++++++++++++
        # DATA SUMMARY

        # Main panel for data summary (pre)
        #----------------------------------

        dev_expander_dsPre = st.beta_expander("Explore raw data ", expanded = False)
        with dev_expander_dsPre:

            # Default data description:
            if uploaded_data == None:
                if st.checkbox("Show data description", value = False, key = session_state.id):          
                    st.markdown("**Data source:**")
                    st.markdown("The data come from the Gallup World Poll surveys from 2018 to 2020. For more details see the [World Happiness Report 2021] (https://worldhappiness.report/).")
                    st.markdown("**Citation:**")
                    st.markdown("Helliwell, John F., Richard Layard, Jeffrey Sachs, and Jan-Emmanuel De Neve, eds. 2021. World Happiness Report 2021. New York: Sustainable Development Solutions Network.")
                    st.markdown("**Variables in the dataset:**")

                    col1,col2=st.beta_columns(2) 
                    col1.write("Country")
                    col2.write("country name")
                    
                    col1,col2=st.beta_columns(2)
                    col1.write("Year ")
                    col2.write("year ranging from 2005 to 2020")
                    
                    col1,col2=st.beta_columns(2) 
                    col1.write("Ladder")
                    col2.write("happiness  score  or  subjective  well-being with the best possible life being a 10, and the worst possible life being a 0")
                    
                    col1,col2=st.beta_columns(2) 
                    col1.write("Log GDP per capita")
                    col2.write("in purchasing power parity at  constant  2017  international  dollar  prices")
                    
                    col1,col2=st.beta_columns(2) 
                    col1.write("Social support")
                    col2.write("the national average of the binary responses (either 0 or 1) to the question regarding relatives or friends to count on")
                    
                    col1,col2=st.beta_columns(2) 
                    col1.write("Healthy life expectancy at birth")
                    col2.write("based on  the  data  extracted  from  the  World  Health  Organization’s  Global Health Observatory data repository")
                   
                    col1,col2=st.beta_columns(2) 
                    col1.write("Freedom to make life choices")
                    col2.write("national average of responses to the corresponding question")

                    col1,col2=st.beta_columns(2) 
                    col1.write("Generosity")
                    col2.write("residual of regressing national average of response to the question regarding money donations in the past month on GDP per capita")

                    col1,col2=st.beta_columns(2) 
                    col1.write("Perceptions of corruption")
                    col2.write("the national average of the survey responses to the corresponding question")
                    
                    col1,col2=st.beta_columns(2) 
                    col1.write("Positive affect")
                    col2.write("the  average  of  three  positive  affect  measures (happiness,  laugh  and  enjoyment)")
                    
                    col1,col2=st.beta_columns(2)
                    col1.write("Negative affect (worry, sadness and anger)")
                    col2.write("the  average  of  three  negative  affect  measures  (worry, sadness and anger)")

                    st.markdown("")

            # Show raw data & data info
            df_summary = fc.data_summary(df) 
            if st.checkbox("Show raw data ", value = False, key = session_state.id):      
                st.write(df)
                st.write("Data shape: ", n_rows,  " rows and ", n_cols, " columns")
            if df[df.duplicated()].shape[0] > 0 or df.iloc[list(pd.unique(np.where(df.isnull())[0]))].shape[0] > 0:
                check_nasAnddupl=st.checkbox("Show duplicates and NAs info ", value = False, key = session_state.id) 
                if check_nasAnddupl:      
                    if df[df.duplicated()].shape[0] > 0:
                        st.write("Number of duplicates: ", df[df.duplicated()].shape[0])
                        st.write("Duplicate row index: ", ', '.join(map(str,list(df.index[df.duplicated()]))))
                    if df.iloc[list(pd.unique(np.where(df.isnull())[0]))].shape[0] > 0:
                        st.write("Number of rows with NAs: ", df.iloc[list(pd.unique(np.where(df.isnull())[0]))].shape[0])
                        st.write("Rows with NAs: ", ', '.join(map(str,list(pd.unique(np.where(df.isnull())[0])))))
                
            # Show variable info 
            if st.checkbox('Show variable info ', value = False, key = session_state.id): 
                st.write(df_summary["Variable types"])
        
            # Show summary statistics (raw data)
            if st.checkbox('Show summary statistics (raw data) ', value = False, key = session_state.id): 
                st.write(df_summary["ALL"])
                if fc.get_mode(df).loc["n_unique"].any():
                    st.caption("** Mode is not unique.")
                if sett_hints:
                    st.info(str(fc.learning_hints("de_summary_statistics")))
                
            # Download link for exploration statistics
            output = BytesIO()
            excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
            df_summary["Variable types"].to_excel(excel_file, sheet_name="variable_info")
            df_summary["ALL"].to_excel(excel_file, sheet_name="summary_statistics")
            excel_file.save()
            excel_file = output.getvalue()
            b64 = base64.b64encode(excel_file)
            dl_file_name = "Exploration statistics__" + df_name + ".xlsx"
            st.markdown(
                f"""
            <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download exploration statistics</a>
            """,
            unsafe_allow_html=True)

        #++++++++++++++++++++++
        # DATA PROCESSING

        # Settings for data processing
        #-------------------------------------

        #st.subheader("Data processing")
        dev_expander_dm_sb = st.beta_expander("Specify data processing preferences", expanded = False)
        with dev_expander_dm_sb:
            
            n_rows_wNAs = df.iloc[list(pd.unique(np.where(df.isnull())[0]))].shape[0]
            if n_rows_wNAs > 0:
                a1, a2, a3 = st.beta_columns(3)
            else: a1, a2 = st.beta_columns(2)
            
            sb_DM_dImp_num = None 
            sb_DM_dImp_other = None
            if n_rows_wNAs > 0:
                with a1:
                    #--------------------------------------------------------------------------------------
                    # DATA CLEANING

                    st.markdown("**Data cleaning**")

                    # Delete rows
                    sb_DM_delRows = st.multiselect("Select rows to delete ", df.index, key = session_state.id)
                    df = df.loc[~df.index.isin(sb_DM_delRows)]

                    # Delete columns
                    sb_DM_delCols = st.multiselect("Select columns to delete ", df.columns, key = session_state.id)
                    df = df.loc[:,~df.columns.isin(sb_DM_delCols)]

                    # Delete duplicates if any exist
                    if df[df.duplicated()].shape[0] > 0:
                        sb_DM_delDup = st.selectbox("Delete duplicate rows ", ["No", "Yes"], key = session_state.id)
                        if sb_DM_delDup == "Yes":
                            n_rows_dup = df[df.duplicated()].shape[0]
                            df = df.drop_duplicates()
                    elif df[df.duplicated()].shape[0] == 0:   
                        sb_DM_delDup = "No"    
                        
                    # Delete rows with NA if any exist
                    n_rows_wNAs = df.iloc[list(pd.unique(np.where(df.isnull())[0]))].shape[0]
                    if n_rows_wNAs > 0:
                        sb_DM_delRows_wNA = st.selectbox("Delete rows with NAs ", ["No", "Yes"], key = session_state.id)
                        if sb_DM_delRows_wNA == "Yes": 
                            df = df.dropna()
                    elif n_rows_wNAs == 0: 
                        sb_DM_delRows_wNA = "No"   
            
                with a2:
                    #--------------------------------------------------------------------------------------
                    # DATA IMPUTATION

                    # Select data imputation method (only if rows with NA not deleted)
                    if sb_DM_delRows_wNA == "No" and n_rows_wNAs > 0:
                        st.markdown("**Data imputation**")
                        sb_DM_dImp_choice = st.selectbox("Replace entries with NA ", ["No", "Yes"], key = session_state.id)
                        if sb_DM_dImp_choice == "Yes":
                            # Numeric variables
                            sb_DM_dImp_num = st.selectbox("Imputation method for numeric variables ", ["Mean", "Median", "Random value"], key = session_state.id)
                            # Other variables
                            sb_DM_dImp_other = st.selectbox("Imputation method for other variables ", ["Mode", "Random value"], key = session_state.id)
                            df = fc.data_impute(df, sb_DM_dImp_num, sb_DM_dImp_other)
                    else: 
                        st.markdown("**Data imputation**")
                        st.write("")
                        st.info("No NAs in data set!")
                
                with a3:
                    #--------------------------------------------------------------------------------------
                    # DATA TRANSFORMATION

                    st.markdown("**Data transformation**")
                    # Select columns for different transformation types
                    transform_options = df.select_dtypes([np.number]).columns
                    numCat_options = df.columns
                    sb_DM_dTrans_log = st.multiselect("Select columns to transform with log ", transform_options, key = session_state.id)
                    if sb_DM_dTrans_log is not None: 
                        df = fc.var_transform_log(df, sb_DM_dTrans_log)
                    sb_DM_dTrans_sqrt = st.multiselect("Select columns to transform with sqrt ", transform_options, key = session_state.id)
                    if sb_DM_dTrans_sqrt is not None: 
                        df = fc.var_transform_sqrt(df, sb_DM_dTrans_sqrt)
                    sb_DM_dTrans_square = st.multiselect("Select columns for squaring ", transform_options, key = session_state.id)
                    if sb_DM_dTrans_square is not None: 
                        df = fc.var_transform_square(df, sb_DM_dTrans_square)
                    sb_DM_dTrans_stand = st.multiselect("Select columns for standardization ", transform_options, key = session_state.id)
                    if sb_DM_dTrans_stand is not None: 
                        df = fc.var_transform_stand(df, sb_DM_dTrans_stand)
                    sb_DM_dTrans_norm = st.multiselect("Select columns for normalization ", transform_options, key = session_state.id)
                    if sb_DM_dTrans_norm is not None: 
                        df = fc.var_transform_norm(df, sb_DM_dTrans_norm)
                    sb_DM_dTrans_numCat = st.multiselect("Select columns for numeric categorization ", numCat_options, key = session_state.id)
                    if sb_DM_dTrans_numCat:
                        if not df[sb_DM_dTrans_numCat].columns[df[sb_DM_dTrans_numCat].isna().any()].tolist(): 
                            sb_DM_dTrans_numCat_sel = st.multiselect("Select variables for manual categorization ", sb_DM_dTrans_numCat, key = session_state.id)
                            if sb_DM_dTrans_numCat_sel:
                                for var in sb_DM_dTrans_numCat_sel:
                                    if df[var].unique().size > 5: 
                                        st.error("ERROR: Selected variable has too many categories (>5): " + str(var))
                                        return 
                                    else:
                                        manual_cats = pd.DataFrame(index = range(0, df[var].unique().size), columns=["Value", "Cat"])
                                        text = "Category for "
                                        # Save manually selected categories
                                        for i in range(0, df[var].unique().size):
                                            text1 = text + str(var) + ": " + str(sorted(df[var].unique())[i])
                                            man_cat = st.number_input(text1, value = 0,  min_value=0, key = session_state.id)
                                            manual_cats.loc[i]["Value"] = sorted(df[var].unique())[i]
                                            manual_cats.loc[i]["Cat"] = man_cat
                                        
                                        new_var_name = "numCat_" + var
                                        new_var = pd.DataFrame(index = df.index, columns = [new_var_name])
                                        for c in df[var].index:
                                            if pd.isnull(df[var][c]) == True:
                                                new_var.loc[c, new_var_name] = np.nan
                                            elif pd.isnull(df[var][c]) == False:
                                                new_var.loc[c, new_var_name] = int(manual_cats[manual_cats["Value"] == df[var][c]]["Cat"])
                                        df[new_var_name] = new_var.astype('int64')
                                    # Exclude columns with manual categorization from standard categorization
                                    numCat_wo_manCat = [var for var in sb_DM_dTrans_numCat if var not in sb_DM_dTrans_numCat_sel]
                                    df = fc.var_transform_numCat(df, numCat_wo_manCat)
                            else:
                                df = fc.var_transform_numCat(df, sb_DM_dTrans_numCat)
                        else:
                            col_with_na = df[sb_DM_dTrans_numCat].columns[df[sb_DM_dTrans_numCat].isna().any()].tolist()
                            st.error("ERROR: Please select columns without NAs: " + ', '.join(map(str,col_with_na)))
                            return
                    else:
                        sb_DM_dTrans_numCat = None
                    sb_DM_dTrans_mult = st.number_input("Number of variable multiplications ", value = 0, min_value=0, key = session_state.id)
                    if sb_DM_dTrans_mult != 0: 
                        multiplication_pairs = pd.DataFrame(index = range(0, sb_DM_dTrans_mult), columns=["Var1", "Var2"])
                        text = "Multiplication pair"
                        for i in range(0, sb_DM_dTrans_mult):
                            text1 = text + " " + str(i+1)
                            text2 = text + " " + str(i+1) + " "
                            mult_var1 = st.selectbox(text1, transform_options, key = session_state.id)
                            mult_var2 = st.selectbox(text2, transform_options, key = session_state.id)
                            multiplication_pairs.loc[i]["Var1"] = mult_var1
                            multiplication_pairs.loc[i]["Var2"] = mult_var2
                            fc.var_transform_mult(df, mult_var1, mult_var2)
                    sb_DM_dTrans_div = st.number_input("Number of variable divisions ", value = 0, min_value=0, key = session_state.id)
                    if sb_DM_dTrans_div != 0:
                        division_pairs = pd.DataFrame(index = range(0, sb_DM_dTrans_div), columns=["Var1", "Var2"]) 
                        text = "Division pair"
                        for i in range(0, sb_DM_dTrans_div):
                            text1 = text + " " + str(i+1) + " (numerator)"
                            text2 = text + " " + str(i+1) + " (denominator)"
                            div_var1 = st.selectbox(text1, transform_options, key = session_state.id)
                            div_var2 = st.selectbox(text2, transform_options, key = session_state.id)
                            division_pairs.loc[i]["Var1"] = div_var1
                            division_pairs.loc[i]["Var2"] = div_var2
                            fc.var_transform_div(df, div_var1, div_var2)
            else:
                with a1:
                    #--------------------------------------------------------------------------------------
                    # DATA CLEANING

                    st.markdown("**Data cleaning**")

                    # Delete rows
                    sb_DM_delRows = st.multiselect("Select rows to delete ", df.index, key = session_state.id)
                    df = df.loc[~df.index.isin(sb_DM_delRows)]

                    # Delete columns
                    sb_DM_delCols = st.multiselect("Select columns to delete ", df.columns, key = session_state.id)
                    df = df.loc[:,~df.columns.isin(sb_DM_delCols)]

                    # Delete duplicates if any exist
                    if df[df.duplicated()].shape[0] > 0:
                        sb_DM_delDup = st.selectbox("Delete duplicate rows ", ["No", "Yes"], key = session_state.id)
                        if sb_DM_delDup == "Yes":
                            n_rows_dup = df[df.duplicated()].shape[0]
                            df = df.drop_duplicates()
                    elif df[df.duplicated()].shape[0] == 0:   
                        sb_DM_delDup = "No"    
                        
                    # Delete rows with NA if any exist
                    n_rows_wNAs = df.iloc[list(pd.unique(np.where(df.isnull())[0]))].shape[0]
                    if n_rows_wNAs > 0:
                        sb_DM_delRows_wNA = st.selectbox("Delete rows with NAs ", ["No", "Yes"], key = session_state.id)
                        if sb_DM_delRows_wNA == "Yes": 
                            df = df.dropna()
                    elif n_rows_wNAs == 0: 
                        sb_DM_delRows_wNA = "No"   

                        
                with a2:
                    #--------------------------------------------------------------------------------------
                    # DATA TRANSFORMATION

                    st.markdown("**Data transformation**")
                    # Select columns for different transformation types
                    transform_options = df.select_dtypes([np.number]).columns
                    numCat_options = df.columns
                    sb_DM_dTrans_log = st.multiselect("Select columns to transform with log ", transform_options, key = session_state.id)
                    if sb_DM_dTrans_log is not None: 
                        df = fc.var_transform_log(df, sb_DM_dTrans_log)
                    sb_DM_dTrans_sqrt = st.multiselect("Select columns to transform with sqrt ", transform_options, key = session_state.id)
                    if sb_DM_dTrans_sqrt is not None: 
                        df = fc.var_transform_sqrt(df, sb_DM_dTrans_sqrt)
                    sb_DM_dTrans_square = st.multiselect("Select columns for squaring ", transform_options, key = session_state.id)
                    if sb_DM_dTrans_square is not None: 
                        df = fc.var_transform_square(df, sb_DM_dTrans_square)
                    sb_DM_dTrans_stand = st.multiselect("Select columns for standardization ", transform_options, key = session_state.id)
                    if sb_DM_dTrans_stand is not None: 
                        df = fc.var_transform_stand(df, sb_DM_dTrans_stand)
                    sb_DM_dTrans_norm = st.multiselect("Select columns for normalization ", transform_options, key = session_state.id)
                    if sb_DM_dTrans_norm is not None: 
                        df = fc.var_transform_norm(df, sb_DM_dTrans_norm)
                    sb_DM_dTrans_numCat = st.multiselect("Select columns for numeric categorization ", numCat_options, key = session_state.id)
                    if sb_DM_dTrans_numCat:
                        if not df[sb_DM_dTrans_numCat].columns[df[sb_DM_dTrans_numCat].isna().any()].tolist(): 
                            sb_DM_dTrans_numCat_sel = st.multiselect("Select variables for manual categorization ", sb_DM_dTrans_numCat, key = session_state.id)
                            if sb_DM_dTrans_numCat_sel:
                                for var in sb_DM_dTrans_numCat_sel:
                                    if df[var].unique().size > 5: 
                                        st.error("ERROR: Selected variable has too many categories (>5): " + str(var))
                                        return
                                    else:
                                        manual_cats = pd.DataFrame(index = range(0, df[var].unique().size), columns=["Value", "Cat"])
                                        text = "Category for "
                                        # Save manually selected categories
                                        for i in range(0, df[var].unique().size):
                                            text1 = text + str(var) + ": " + str(sorted(df[var].unique())[i])
                                            man_cat = st.number_input(text1, value = 0, min_value=0, key = session_state.id)
                                            manual_cats.loc[i]["Value"] = sorted(df[var].unique())[i]
                                            manual_cats.loc[i]["Cat"] = man_cat
                                        
                                        new_var_name = "numCat_" + var
                                        new_var = pd.DataFrame(index = df.index, columns = [new_var_name])
                                        for c in df[var].index:
                                            if pd.isnull(df[var][c]) == True:
                                                new_var.loc[c, new_var_name] = np.nan
                                            elif pd.isnull(df[var][c]) == False:
                                                new_var.loc[c, new_var_name] = int(manual_cats[manual_cats["Value"] == df[var][c]]["Cat"])
                                        df[new_var_name] = new_var.astype('int64')
                                    # Exclude columns with manual categorization from standard categorization
                                    numCat_wo_manCat = [var for var in sb_DM_dTrans_numCat if var not in sb_DM_dTrans_numCat_sel]
                                    df = fc.var_transform_numCat(df, numCat_wo_manCat)
                            else:
                                df = fc.var_transform_numCat(df, sb_DM_dTrans_numCat)
                        else:
                            col_with_na = df[sb_DM_dTrans_numCat].columns[df[sb_DM_dTrans_numCat].isna().any()].tolist()
                            st.error("ERROR: Please select columns without NAs: " + ', '.join(map(str,col_with_na)))
                            return
                    else:
                        sb_DM_dTrans_numCat = None
                    sb_DM_dTrans_mult = st.number_input("Number of variable multiplications ", value = 0, min_value=0, key = session_state.id)
                    if sb_DM_dTrans_mult != 0: 
                        multiplication_pairs = pd.DataFrame(index = range(0, sb_DM_dTrans_mult), columns=["Var1", "Var2"])
                        text = "Multiplication pair"
                        for i in range(0, sb_DM_dTrans_mult):
                            text1 = text + " " + str(i+1)
                            text2 = text + " " + str(i+1) + " "
                            mult_var1 = st.selectbox(text1, transform_options, key = session_state.id)
                            mult_var2 = st.selectbox(text2, transform_options, key = session_state.id)
                            multiplication_pairs.loc[i]["Var1"] = mult_var1
                            multiplication_pairs.loc[i]["Var2"] = mult_var2
                            fc.var_transform_mult(df, mult_var1, mult_var2)
                    sb_DM_dTrans_div = st.number_input("Number of variable divisions ", value = 0, min_value=0, key = session_state.id)
                    if sb_DM_dTrans_div != 0:
                        division_pairs = pd.DataFrame(index = range(0, sb_DM_dTrans_div), columns=["Var1", "Var2"]) 
                        text = "Division pair"
                        for i in range(0, sb_DM_dTrans_div):
                            text1 = text + " " + str(i+1) + " (numerator)"
                            text2 = text + " " + str(i+1) + " (denominator)"
                            div_var1 = st.selectbox(text1, transform_options, key = session_state.id)
                            div_var2 = st.selectbox(text2, transform_options, key = session_state.id)
                            division_pairs.loc[i]["Var1"] = div_var1
                            division_pairs.loc[i]["Var2"] = div_var2
                            fc.var_transform_div(df, div_var1, div_var2)

            #--------------------------------------------------------------------------------------
            # PROCESSING SUMMARY
            
            if st.checkbox('Show a summary of my data processing preferences ', value = False, key = session_state.id): 
                st.markdown("Summary of data changes:")

                #--------------------------------------------------------------------------------------
                # DATA CLEANING

                # Rows
                if len(sb_DM_delRows) > 1:
                    st.write("-", len(sb_DM_delRows), " rows were manually deleted:", ', '.join(map(str,sb_DM_delRows)))
                elif len(sb_DM_delRows) == 1:
                    st.write("-",len(sb_DM_delRows), " row was manually deleted:", str(sb_DM_delRows[0]))
                elif len(sb_DM_delRows) == 0:
                    st.write("- No row was manually deleted!")
                # Columns
                if len(sb_DM_delCols) > 1:
                    st.write("-", len(sb_DM_delCols), " columns were manually deleted:", ', '.join(sb_DM_delCols))
                elif len(sb_DM_delCols) == 1:
                    st.write("-",len(sb_DM_delCols), " column was manually deleted:", str(sb_DM_delCols[0]))
                elif len(sb_DM_delCols) == 0:
                    st.write("- No column was manually deleted!")
                # Duplicates
                if sb_DM_delDup == "Yes":
                    if n_rows_dup > 1:
                        st.write("-", n_rows_dup, " duplicate rows were deleted!")
                    elif n_rows_dup == 1:
                        st.write("-", n_rows_dup, "duplicate row was deleted!")
                else:
                    st.write("- No duplicate row was deleted!")
                # NAs
                if sb_DM_delRows_wNA == "Yes":
                    if n_rows_wNAs > 1:
                        st.write("-", n_rows_wNAs, "rows with NAs were deleted!")
                    elif n_rows_wNAs == 1:
                        st.write("-", n_rows - n_rows_wNAs, "row with NAs was deleted!")
                else:
                    st.write("- No row with NAs was deleted!")
                
                #--------------------------------------------------------------------------------------
                # DATA IMPUTATION

                if sb_DM_delRows_wNA == "No" and n_rows_wNAs > 0:
                    st.write("- Data imputation method for numeric variables:", sb_DM_dImp_num)
                    st.write("- Data imputation method for other variable types:", sb_DM_dImp_other)

                #--------------------------------------------------------------------------------------
                # DATA TRANSFORMATION

                # log
                if len(sb_DM_dTrans_log) > 1:
                    st.write("-", len(sb_DM_dTrans_log), " columns were log-transformed:", ', '.join(sb_DM_dTrans_log))
                elif len(sb_DM_dTrans_log) == 1:
                    st.write("-",len(sb_DM_dTrans_log), " column was log-transformed:", sb_DM_dTrans_log[0])
                elif len(sb_DM_dTrans_log) == 0:
                    st.write("- No column was log-transformed!")
                # sqrt
                if len(sb_DM_dTrans_sqrt) > 1:
                    st.write("-", len(sb_DM_dTrans_sqrt), " columns were sqrt-transformed:", ', '.join(sb_DM_dTrans_sqrt))
                elif len(sb_DM_dTrans_sqrt) == 1:
                    st.write("-",len(sb_DM_dTrans_sqrt), " column was sqrt-transformed:", sb_DM_dTrans_sqrt[0])
                elif len(sb_DM_dTrans_sqrt) == 0:
                    st.write("- No column was sqrt-transformed!")
                # square
                if len(sb_DM_dTrans_square) > 1:
                    st.write("-", len(sb_DM_dTrans_square), " columns were squared:", ', '.join(sb_DM_dTrans_square))
                elif len(sb_DM_dTrans_square) == 1:
                    st.write("-",len(sb_DM_dTrans_square), " column was squared:", sb_DM_dTrans_square[0])
                elif len(sb_DM_dTrans_square) == 0:
                    st.write("- No column was squared!")
                # standardize
                if len(sb_DM_dTrans_stand) > 1:
                    st.write("-", len(sb_DM_dTrans_stand), " columns were standardized:", ', '.join(sb_DM_dTrans_stand))
                elif len(sb_DM_dTrans_stand) == 1:
                    st.write("-",len(sb_DM_dTrans_stand), " column was standardized:", sb_DM_dTrans_stand[0])
                elif len(sb_DM_dTrans_stand) == 0:
                    st.write("- No column was standardized!")
                # normalize
                if len(sb_DM_dTrans_norm) > 1:
                    st.write("-", len(sb_DM_dTrans_norm), " columns were normalized:", ', '.join(sb_DM_dTrans_norm))
                elif len(sb_DM_dTrans_norm) == 1:
                    st.write("-",len(sb_DM_dTrans_norm), " column was normalized:", sb_DM_dTrans_norm[0])
                elif len(sb_DM_dTrans_norm) == 0:
                    st.write("- No column was normalized!")
                # numeric category
                if df.iloc[list(pd.unique(np.where(df.isnull())[0]))].shape[0] == 0:
                    if len(sb_DM_dTrans_numCat) > 1:
                        st.write("-", len(sb_DM_dTrans_numCat), " columns were transformed to numeric categories:", ', '.join(sb_DM_dTrans_numCat))
                    elif len(sb_DM_dTrans_numCat) == 1:
                        st.write("-",len(sb_DM_dTrans_numCat), " column was transformed to numeric categories:", sb_DM_dTrans_numCat[0])
                    elif len(sb_DM_dTrans_numCat) == 0:
                        st.write("- No column was transformed to numeric categories!")
                # multiplication
                if sb_DM_dTrans_mult != 0:
                    st.write("-", "Number of variable multiplications: ", sb_DM_dTrans_mult)
                elif sb_DM_dTrans_mult == 0:
                    st.write("- No variables were multiplied!")
                # division
                if sb_DM_dTrans_div != 0:
                    st.write("-", "Number of variable divisions: ", sb_DM_dTrans_div)
                elif sb_DM_dTrans_div == 0:
                    st.write("- No variables were divided!")
                st.write("")
                st.write("")
        
        #------------------------------------------------------------------------------------------
        
        #++++++++++++++++++++++
        # UPDATED DATA SUMMARY   

        # Show only if changes were made
        if  any(v for v in [sb_DM_delRows, sb_DM_delCols, sb_DM_dImp_num, sb_DM_dImp_other, sb_DM_dTrans_log, sb_DM_dTrans_sqrt, sb_DM_dTrans_square, sb_DM_dTrans_stand, sb_DM_dTrans_norm, sb_DM_dTrans_numCat ] if v is not None) or sb_DM_delDup == "Yes" or sb_DM_delRows_wNA == "Yes" or sb_DM_dTrans_mult != 0 or sb_DM_dTrans_div != 0:
            dev_expander_dsPost = st.beta_expander("Explore cleaned and transformed data ", expanded = False)
            with dev_expander_dsPost:
                if df.shape[1] > 0 and df.shape[0] > 0:

                    # Show cleaned and transformed data & data info
                    df_summary_post = fc.data_summary(df)
                    if st.checkbox("Show cleaned and transformed data ", value = False, key = session_state.id):  
                        n_rows_post = df.shape[0]
                        n_cols_post = df.shape[1]
                        st.dataframe(df)
                        st.write("Data shape: ", n_rows_post, "rows and ", n_cols_post, "columns")
                    if df[df.duplicated()].shape[0] > 0 or df.iloc[list(pd.unique(np.where(df.isnull())[0]))].shape[0] > 0:
                        check_nasAnddupl2 = st.checkbox("Show duplicates and NAs info (processed) ", value = False, key = session_state.id) 
                        if check_nasAnddupl2:
                            index_c = []
                            for c in df.columns:
                                for r in df.index:
                                    if pd.isnull(df[c][r]):
                                        index_c.append(r)      
                            if df[df.duplicated()].shape[0] > 0:
                                st.write("Number of duplicates: ", df[df.duplicated()].shape[0])
                                st.write("Duplicate row index: ", ', '.join(map(str,list(df.index[df.duplicated()]))))
                            if df.iloc[list(pd.unique(np.where(df.isnull())[0]))].shape[0] > 0:
                                st.write("Number of rows with NAs: ", len(pd.unique(sorted(index_c))))
                                st.write("Rows with NAs: ", ', '.join(map(str,list(pd.unique(sorted(index_c))))))

                    # Show cleaned and transformed variable info
                    if st.checkbox("Show cleaned and transformed variable info ", value = False, key = session_state.id): 
                        st.write(df_summary_post["Variable types"])

                    # Show summary statistics (cleaned and transformed data)
                    if st.checkbox('Show summary statistics (cleaned and transformed data) ', value = False, key = session_state.id):
                        st.write(df_summary_post["ALL"])
                        if fc.get_mode(df).loc["n_unique"].any():
                            st.caption("** Mode is not unique.")
                        if sett_hints:
                            st.info(str(fc.learning_hints("de_summary_statistics")))  
                else: st.error("ERROR: No data available for Data Exploration!") 

                # Download link for cleaned exploration statistics
                output = BytesIO()
                excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
                df.to_excel(excel_file, sheet_name="cleaned_data")
                df_summary_post["Variable types"].to_excel(excel_file, sheet_name="cleaned_variable_info")
                df_summary_post["ALL"].to_excel(excel_file, sheet_name="cleaned_summary_statistics")
                excel_file.save()
                excel_file = output.getvalue()
                b64 = base64.b64encode(excel_file)
                dl_file_name = "Cleaned data and exploration statistics__" + df_name + ".xlsx"
                st.markdown(
                    f"""
                <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download cleaned data and exploration statistics</a>
                """,
                unsafe_allow_html=True)
                st.write("")
            
    #------------------------------------------------------------------------------------------
    
    #++++++++++++++++++++++
    # DATA VISUALIZATION

    data_visualization_container = st.beta_container()
    with data_visualization_container:
        st.write("")
        st.write("")
        st.header("**Data visualization**")

        #st.subheader("Graphical exploration")
        dev_expander_dv = st.beta_expander("Explore visualization types ", expanded = False)
        with dev_expander_dv:
            if df.shape[1] > 0 and df.shape[0] > 0:
            
                st.write('**Variable selection**')
                varl_sel_options = df.columns
                var_sel = st.selectbox('Select variable for visualizations', varl_sel_options, key = session_state.id)

                if df[var_sel].dtypes == "float64" or df[var_sel].dtypes == "float32" or df[var_sel].dtypes == "int64" or df[var_sel].dtypes == "int32":
                    a4, a5 = st.beta_columns(2)
                    with a4:
                        st.write('**Scatterplot**')
                        yy_options = df.columns
                        yy = st.selectbox('Select variable for y-axis', yy_options, key = session_state.id)
                        if df[yy].dtypes == "float64" or df[yy].dtypes == "float32" or df[yy].dtypes == "int64" or df[yy].dtypes == "int32":
                            fig_data = pd.DataFrame()
                            fig_data[yy] = df[yy]
                            fig_data[var_sel] = df[var_sel]
                            fig_data["Index"] = df.index
                            fig = alt.Chart(fig_data).mark_circle().encode(
                                x = alt.X(var_sel, scale = alt.Scale(domain = [min(fig_data[var_sel]), max(fig_data[var_sel])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y(yy, scale = alt.Scale(zero = False), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = [yy, var_sel, "Index"]
                            )
                            st.altair_chart(fig + fig.transform_regression(var_sel, yy).mark_line(size = 2, color = "darkred"), use_container_width=True)
                            if sett_hints:
                                st.info(str(fc.learning_hints("dv_scatterplot")))
                        else: st.error("ERROR: Please select a numeric variable for the y-axis!")   
                    with a5:
                        st.write('**Histogram**')
                        binNo = st.slider("Select maximum number of bins", 5, 100, 25, key = session_state.id)
                        fig2 = alt.Chart(df).mark_bar().encode(
                            x = alt.X(var_sel, title = var_sel + " (binned)", bin = alt.BinParams(maxbins = binNo), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                            y = alt.Y("count()", title = "count of records", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                            tooltip = ["count()", alt.Tooltip(var_sel, bin = alt.BinParams(maxbins = binNo))]
                        )
                        st.altair_chart(fig2, use_container_width=True)
                        if sett_hints:
                            st.info(str(fc.learning_hints("dv_histogram")))

                    a6, a7 = st.beta_columns(2)
                    with a6:
                        st.write('**Boxplot**')
                        # Boxplot
                        boxplot_data = pd.DataFrame()
                        boxplot_data[var_sel] = df[var_sel]
                        boxplot_data["Index"] = df.index
                        boxplot = alt.Chart(boxplot_data).mark_boxplot(size = 100, color = "#1f77b4", median = dict(color = "darkred"),).encode(
                            y = alt.Y(var_sel, scale = alt.Scale(zero = False)),
                            tooltip = [var_sel, "Index"]
                        ).configure_axis(
                            labelFontSize = 11,
                            titleFontSize = 12
                        )
                        st.altair_chart(boxplot, use_container_width=True)
                        if sett_hints:
                            st.info(str(fc.learning_hints("dv_boxplot")))
                    with a7:
                        st.write("**QQ-plot**")
                        var_values = df[var_sel]
                        qqplot_data = pd.DataFrame()
                        qqplot_data[var_sel] = var_values
                        qqplot_data["Index"] = df.index
                        qqplot_data = qqplot_data.sort_values(by = [var_sel])
                        qqplot_data["Theoretical quantiles"] = stats.probplot(var_values, dist="norm")[0][0]
                        qqplot = alt.Chart(qqplot_data).mark_circle(size=20).encode(
                            x = alt.X("Theoretical quantiles", title = "theoretical quantiles", scale = alt.Scale(domain = [min(qqplot_data["Theoretical quantiles"]), max(qqplot_data["Theoretical quantiles"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                            y = alt.Y(var_sel, title = str(var_sel), scale = alt.Scale(zero = False), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                            tooltip = [var_sel, "Theoretical quantiles", "Index"]
                        )
                        st.altair_chart(qqplot + qqplot.transform_regression('Theoretical quantiles', var_sel).mark_line(size = 2, color = "darkred"), use_container_width = True)
                        if sett_hints:
                            st.info(str(fc.learning_hints("dv_qqplot")))
                else: st.error("ERROR: Please select a numeric variable!") 
            else: st.error("ERROR: No data available for Data Visualization!")  

    #------------------------------------------------------------------------------------------

    #++++++++++++++++++++++++++++++++++++++++++++
    # MACHINE LEARNING (PREDICTIVE DATA ANALYSIS)

    st.write("")
    st.write("")
    
    data_machinelearning_container = st.beta_container()
    with data_machinelearning_container:
        st.header("**Multivariate data modelling**")
        st.markdown("Go for creating predictive models of your data using classical and machine learning techniques!  STATY will take care of the modelling for you, so you can put your focus on results interpretation and communication! ")

        ml_settings = st.beta_expander("Specify models ", expanded = False)
        with ml_settings:
            
            # Initial status for running models
            run_models = False
            sb_ML_alg = "NA"
            do_hypTune = "No"
            do_modval = "No"
            do_hypTune_no = "No hyperparameter tuning"
            final_hyPara_values="None"
            model_val_results = None
            model_full_results = None
            gam_finalPara = None
            brt_finalPara = None
            brt_tuning_results = None
            rf_finalPara = None
            rf_tuning_results = None
            ann_finalPara = None
            ann_tuning_results = None
            MLR_cov_type = None
            MLR_model = "OLS"
            LR_cov_type = None

            if df.shape[1] > 0 and df.shape[0] > 0:
                #--------------------------------------------------------------------------------------
                # GENERAL SETTINGS
            
                st.markdown("**Variable selection**")
                
                # Variable categories
                df_summary_model = fc.data_summary(df)
                var_cat = df_summary_model["Variable types"].loc["category"]
                
                # Response variable
                response_var_options = df.columns
                response_var = st.selectbox("Select response variable", response_var_options, key = session_state.id)
                
                # Check if response variable is numeric and has no NAs
                response_var_message_num = False
                response_var_message_na = False
                response_var_message_cat = False

                if var_cat.loc[response_var] == "string/binary" or var_cat.loc[response_var] == "bool/binary":
                    response_var_message_num = "ERROR: Please transform the binary response variable into a numeric binary categorization in data processing preferences!"
                elif var_cat.loc[response_var] == "string/categorical" or var_cat.loc[response_var] == "other" or var_cat.loc[response_var] == "string/single":
                    response_var_message_num = "ERROR: Please select a numeric or binary response variable!"
                # elif np.where(df[response_var].isnull())[0].size > 0:
                #     response_var_message_na = "ERROR: Please select a response variable without NAs or delete/replace rows with NAs in data processing preferences!"
                elif var_cat.loc[response_var] == "categorical":
                    response_var_message_cat = "WARNING: Non-continuous variables are treated as continuous!"
                
                if response_var_message_num != False:
                    st.error(response_var_message_num)
                # if response_var_message_na != False:
                #     st.error(response_var_message_na)
                if response_var_message_cat != False:
                    st.warning(response_var_message_cat)

                # Continue if everything is clean for response variable
                if response_var_message_num == False and response_var_message_na == False:
                    # Select explanatory variables
                    expl_var_options = df.columns
                    expl_var_options = expl_var_options[expl_var_options.isin(df.drop(response_var, axis = 1).columns)]
                    expl_var = st.multiselect("Select explanatory variables", expl_var_options, key = session_state.id)
                    var_list = list([response_var]) + list(expl_var)
                    
                    

                    # Check if explanatory variables are numeric and have no NAs
                    expl_var_message_num = False
                    expl_var_message_na = False
                    if any(a for a in df[expl_var].dtypes if a != "float64" and a != "float32" and a != "int64" and a != "int64"): 
                        expl_var_not_num = df[expl_var].select_dtypes(exclude=["int64", "int32", "float64", "float32"]).columns
                        expl_var_message_num = "ERROR: Please exclude non-numeric variables: " + ', '.join(map(str,list(expl_var_not_num)))
                    # elif np.where(df[expl_var].isnull())[0].size > 0:
                    #     expl_var_with_na = df[expl_var].columns[df[expl_var].isna().any()].tolist()
                    #     expl_var_message_na = "ERROR: Please select variables without NAs or delete/replace rows with NAs in data processing preferences: " + ', '.join(map(str,list(expl_var_with_na)))
                    
                    # Check if NAs are present and delete them automatically (delete before run models button)
                    if np.where(df[var_list].isnull())[0].size > 0:
                        st.warning("WARNING: Your modelling data set includes NAs. Rows with NAs are automatically deleted!")

                    if expl_var_message_num != False:
                        st.error(expl_var_message_num)
                    elif expl_var_message_na != False:
                        st.error(expl_var_message_na)
                    # Continue if everything is clean for explanatory variables and at least one was selected
                    elif expl_var_message_num == False and expl_var_message_na == False and len(expl_var) > 0:
                    
                        #--------------------------------------------------------------------------------------
                        # ALGORITHMS

                        st.markdown("**Specify modelling algorithms**")

                        # Select algorithms based on chosen response variable
                        # Binary (has to be integer or float)
                        if var_cat.loc[response_var] == "binary":
                            algorithms = ["Multiple Linear Regression", "Logistic Regression", "Generalized Additive Models", "Random Forest", "Boosted Regression Trees", "Artificial Neural Networks"]
                            response_var_type = "binary"
                        
                        # Multi-class (has to be integer, currently treated as continuous reposne)
                        elif var_cat.loc[response_var] == "categorical":
                            algorithms = ["Multiple Linear Regression", "Generalized Additive Models", "Random Forest", "Boosted Regression Trees", "Artificial Neural Networks"]
                            response_var_type = "continuous"
                        # Continuous
                        elif var_cat.loc[response_var] == "numeric":
                            algorithms = ["Multiple Linear Regression", "Generalized Additive Models", "Random Forest", "Boosted Regression Trees", "Artificial Neural Networks"]
                            response_var_type = "continuous"

                        alg_list = list(algorithms)
                        sb_ML_alg = st.multiselect("Select modelling techniques", alg_list, alg_list)
                        
                        # MLR + binary info message
                        if any(a for a in sb_ML_alg if a == "Multiple Linear Regression") and response_var_type == "binary":
                            st.warning("WARNING: For Multiple Linear Regression only the full model output will be determined.")

                        # MLR covariance type setting
                        if any(a for a in sb_ML_alg if a == "Multiple Linear Regression"):
                            st.markdown("**Multiple Linear Regression settings**")
                            # MLR_model = st.selectbox("Multiple Linear Regression model", ["OLS", "GLS"])
                            MLR_cov_type = st.selectbox("Multiple Linear Regression covariance type", ["non-robust", "HC0", "HC1", "HC2", "HC3"])

                        # LR covariance type setting
                        if any(a for a in sb_ML_alg if a == "Logistic Regression"):
                            st.markdown("**Logistic Regression settings**")
                            LR_cov_type = st.selectbox("Logistic Regression covariance type", ["non-robust", "HC0"])
                        
                        # Generalized Additive Models settings
                        if any(a for a in sb_ML_alg if a == "Generalized Additive Models"):
                            st.markdown("**Generalized Additive Models settings**")
                            # Generalized Additive Models default settings
                            gam_finalPara = pd.DataFrame(index = ["value"], columns = ["number of splines", "spline order", "lambda"])
                            gam_finalPara["number of splines"] = 20
                            gam_finalPara["spline order"] = 3
                            gam_finalPara["lambda"] = 0.6
                            if st.checkbox("Adjust settings for Generalized Additive Models"):
                                gam_col1, gam_col2, gam_col3 = st.beta_columns(3)
                                gam_nos_values = []
                                gam_so_values = []
                                gam_lam_values = []
                                gam_finalPara = pd.DataFrame(index = ["value"], columns = ["number of splines", "spline order", "lambda"])
                                for gset in range(0,len(expl_var)):
                                    var_name = expl_var[gset]
                                    with gam_col1:
                                        nos = st.number_input("Number of splines (" + var_name + ")", value = 20, min_value=1) 
                                        gam_nos_values.append(nos)
                                    with gam_col2:
                                        so = st.number_input("Spline order (" + var_name + ")", value = 3, min_value=3) 
                                        gam_so_values.append(so)
                                    with gam_col3: 
                                        lam = st.number_input("Lambda (" + var_name + ")", value = 0.6, min_value=0.01) 
                                        gam_lam_values.append(lam) 
                                st.info("Please make sure that the number of splines is greater than the spline order!") 
                                gam_finalPara.at["value", "number of splines"] = gam_nos_values
                                gam_finalPara.at["value","spline order"] = gam_so_values  
                                gam_finalPara.at["value","lambda"] = gam_lam_values                              

                        #--------------------------------------------------------------------------------------
                        # HYPERPARAMETER TUNING SETTINGS
                        
                        if len(sb_ML_alg) >= 1:

                            # Depending on algorithm selection different hyperparameter settings are shown
                            if any(a for a in sb_ML_alg if a == "Random Forest") or any(a for a in sb_ML_alg if a == "Boosted Regression Trees") or any(a for a in sb_ML_alg if a == "Artificial Neural Networks"):
                                # General settings
                                st.markdown("**Hyperparameter-tuning settings**")
                                do_hypTune = st.selectbox("Use hyperparameter-tuning", ["No", "Yes"])
                            
                                # Save hyperparameter values for all algorithms
                                final_hyPara_values = {}
                                hyPara_values = {}
                                
                                # No hyperparameter-tuning
                                if do_hypTune == "No":
                                    do_hypTune_no = "Default hyperparameter values are used!"

                                    # Random Forest default settings
                                    if any(a for a in sb_ML_alg if a == "Random Forest"):
                                        rf_finalPara = pd.DataFrame(index = ["value"], columns = ["number of trees", "maximum tree depth", "maximum number of features", "sample rate"])
                                        rf_finalPara["number of trees"] = [100]
                                        rf_finalPara["maximum tree depth"] = [None]
                                        rf_finalPara["maximum number of features"] = [len(expl_var)]
                                        rf_finalPara["sample rate"] = [0.99]
                                        final_hyPara_values["rf"] = rf_finalPara
                                    # Boosted Regression Trees default settings
                                    if any(a for a in sb_ML_alg if a == "Boosted Regression Trees"):
                                        brt_finalPara = pd.DataFrame(index = ["value"], columns = ["number of trees", "learning rate", "maximum tree depth", "sample rate"])
                                        brt_finalPara["number of trees"] = [100]
                                        brt_finalPara["learning rate"] = [0.1]
                                        brt_finalPara["maximum tree depth"] = [3]
                                        brt_finalPara["sample rate"] = [1]
                                        final_hyPara_values["brt"] = brt_finalPara
                                    # Artificial Neural Networks default settings
                                    if any(a for a in sb_ML_alg if a == "Artificial Neural Networks"):
                                        ann_finalPara = pd.DataFrame(index = ["value"], columns = ["weight optimization solver", "maximum number of iterations", "activation function", "hidden layer sizes", "learning rate", "L² regularization"])#, "learning rate schedule", "momentum", "L² regularization", "epsilon"])
                                        ann_finalPara["weight optimization solver"] = ["adam"]
                                        ann_finalPara["maximum number of iterations"] = [200]
                                        ann_finalPara["activation function"] = ["relu"]
                                        ann_finalPara["hidden layer sizes"] = [(100,)]
                                        ann_finalPara["learning rate"] = [0.001]
                                        #ann_finalPara["learning rate schedule"] = ["constant"]
                                        #ann_finalPara["momentum"] = [0.9]
                                        ann_finalPara["L² regularization"] = [0.0001]
                                        #ann_finalPara["epsilon"] = [1e-8]
                                        final_hyPara_values["ann"] = ann_finalPara

                                # Hyperparameter-tuning 
                                elif do_hypTune == "Yes":
                                    st.warning("WARNING: Hyperparameter-tuning can take a lot of time!")
                                    
                                    # Further general settings
                                    hypTune_method = st.selectbox("Hyperparameter-search method", ["random grid-search", "grid-search", "Bayes optimization", "sequential model-based optimization"])
                                    hypTune_nCV = st.slider("Select number for n-fold cross-validation", 2, 10, 5)

                                    if hypTune_method == "random grid-search" or hypTune_method == "Bayes optimization" or hypTune_method == "sequential model-based optimization":
                                        hypTune_iter = st.slider("Select number of iterations for search", 20, 1000, 20)
                                    else:
                                        hypTune_iter = False

                                    # Random Forest settings
                                    if any(a for a in sb_ML_alg if a == "Random Forest"):
                                        st.markdown("**Random Forest settings**")
                                        rf_tunePara = pd.DataFrame(index = ["min", "max"], columns = ["number of trees", "maximum tree depth", "maximum number of features", "sample rate"])
                                        rf_tunePara["number of trees"] = [50, 500]
                                        rf_tunePara["maximum tree depth"] = [None, None]
                                        rf_tunePara["maximum number of features"] = [1, len(expl_var)]
                                        rf_tunePara["sample rate"] = [0.8, 0.99]
                                        hyPara_values["rf"] = rf_tunePara
                                        if st.checkbox("Adjust settings for Random Forest"):
                                            rf_tunePara["number of trees"] = st.slider("Range for number of trees ", 50, 1000, [50, 500])
                                            if st.checkbox("Maximum tree depth should be not specified", value = True) == False:
                                                rf_tunePara["maximum tree depth"] = st.slider("Range for maximum tree depth ", 1, 50, [2, 10])
                                            else:
                                                rf_tunePara["maximum tree depth"] = [None, None]
                                            rf_tunePara["maximum number of features"] = st.slider("Range for maximum number of features", 1, len(expl_var), [1, len(expl_var)])
                                            rf_tunePara["sample rate"] = st.slider("Range for sample rate ", 0.5, 0.99, [0.8, 0.99])
                                            hyPara_values["rf"] = rf_tunePara

                                    # Boosted Regression Trees settings
                                    if any(a for a in sb_ML_alg if a == "Boosted Regression Trees"):
                                        st.markdown("**Boosted Regression Trees settings**")
                                        brt_tunePara = pd.DataFrame(index = ["min", "max"], columns = ["number of trees", "learning rate", "maximum tree depth", "sample rate"])
                                        brt_tunePara["number of trees"] = [50, 500]
                                        brt_tunePara["learning rate"] = [1, 10]
                                        brt_tunePara["learning rate"] = brt_tunePara["learning rate"]/1000
                                        brt_tunePara["maximum tree depth"] = [2, 10]
                                        brt_tunePara["sample rate"] = [0.8, 1.0]
                                        hyPara_values["brt"] = brt_tunePara
                                        if st.checkbox("Adjust settings for Boosted Regression Trees"):
                                            brt_tunePara["number of trees"] = st.slider("Range for number of trees", 50, 1000, [50, 500])
                                            brt_tunePara["learning rate"] = st.slider("Range for learning rate (scale = 10e-4)", 1, 100, [1, 10]) 
                                            brt_tunePara["learning rate"] = brt_tunePara["learning rate"]/1000
                                            brt_tunePara["maximum tree depth"] = st.slider("Range for maximum tree depth", 1, 30, [2, 10])
                                            brt_tunePara["sample rate"] = st.slider("Range for sample rate", 0.5, 1.0, [0.8, 1.0])
                                            hyPara_values["brt"] = brt_tunePara

                                    # Artificial Neural Networks settings
                                    if any(a for a in sb_ML_alg if a == "Artificial Neural Networks"):
                                        st.markdown("**Artificial Neural Networks settings**")
                                        ann_tunePara = pd.DataFrame(index = ["min", "max"], columns = ["weight optimization solver", "maximum number of iterations", "activation function", "number of hidden layers", "nodes per hidden layer", "learning rate","L² regularization"])# "learning rate schedule", "momentum", "epsilon"])
                                        ann_tunePara["weight optimization solver"] = list([["adam"], "NA"])
                                        ann_tunePara["maximum number of iterations"] = [100, 200]
                                        ann_tunePara["activation function"] = list([["relu"], "NA"])
                                        ann_tunePara["number of hidden layers"] = list([1, "NA"])
                                        ann_tunePara["nodes per hidden layer"] = [50, 100]
                                        ann_tunePara["learning rate"] = [1, 10]
                                        ann_tunePara["learning rate"] = ann_tunePara["learning rate"]/10000
                                        #ann_tunePara["learning rate schedule"] = list([["constant"], "NA"])
                                        #ann_tunePara["momentum"] = [0.85, 0.9]
                                        ann_tunePara["L² regularization"] = [5, 10]
                                        ann_tunePara["L² regularization"] = ann_tunePara["L² regularization"]/100000
                                        #ann_tunePara["epsilon"] = [5, 10]
                                        #ann_tunePara["epsilon"] = ann_tunePara["epsilon"]/1000000000
                                        hyPara_values["ann"] = ann_tunePara
                                        if st.checkbox("Adjust settings for Artificial Neural Networks"):
                                            weight_opt_list = st.multiselect("Weight optimization solver", ["lbfgs", "adam"], ["adam"])
                                            if len(weight_opt_list) == 0:
                                                weight_opt_list = ["adam"]
                                                st.error("Default value used: adam")
                                            ann_tunePara["weight optimization solver"] = list([weight_opt_list, "NA"])
                                            ann_tunePara["maximum number of iterations"] = st.slider("Maximum number of iterations (epochs)", 10, 1000, [100, 200])
                                            act_func_list = st.multiselect("Activation function", ["identity", "logistic", "tanh", "relu"], ["relu"])
                                            if len(act_func_list) == 0:
                                                act_func_list = ["relu"]
                                                st.error("Default value used: relu")
                                            ann_tunePara["activation function"] = list([act_func_list, "NA"])
                                            number_hidden_layers = st.selectbox("Number of hidden layers", [1, 2, 3])
                                            ann_tunePara["number of hidden layers"]  = list([number_hidden_layers, "NA"])
                                            # Cases for hidden layers
                                            if number_hidden_layers == 1:
                                                ann_tunePara["nodes per hidden layer"] = st.slider("Number of nodes in hidden layer", 5, 500, [50, 100])
                                            if number_hidden_layers == 2:
                                                number_nodes1 = st.slider("Number of neurons in first hidden layer", 5, 500, [50, 100])
                                                number_nodes2 = st.slider("Number of neurons in second hidden layer", 5, 500, [50, 100])
                                                min_nodes = list([number_nodes1[0], number_nodes2[0]])
                                                max_nodes = list([number_nodes1[1], number_nodes2[1]])
                                                ann_tunePara["nodes per hidden layer"] = list([min_nodes, max_nodes])
                                            if number_hidden_layers == 3:
                                                number_nodes1 = st.slider("Number of neurons in first hidden layer", 5, 500, [50, 100])
                                                number_nodes2 = st.slider("Number of neurons in second hidden layer", 5, 500, [50, 100])
                                                number_nodes3 = st.slider("Number of neurons in third hidden layer", 5, 500, [50, 100])
                                                min_nodes = list([number_nodes1[0], number_nodes2[0], number_nodes3[0]])
                                                max_nodes = list([number_nodes1[1], number_nodes2[1], number_nodes3[1]])
                                                ann_tunePara["nodes per hidden layer"] = list([min_nodes, max_nodes])
                                            ann_tunePara["learning rate"] = st.slider("Range for learning rate (scale = 10e-5)", 1, 100, [1, 10])
                                            ann_tunePara["learning rate"] = ann_tunePara["learning rate"]/10000
                                            #learn_rate_list = st.multiselect("Learning rate schedule for weight updates", ["constant", "invscaling", "adaptive"], ["constant"])
                                            #ann_tunePara["learning rate schedule"] = list([learn_rate_list, "NA"])
                                            #if any(a for a in weight_opt_list if a == "sgd"):
                                            #    ann_tunePara["momentum"] = st.slider("Momentum for gradient descent update", 0.0, 1.0, [0.85, 0.9]) 
                                            ann_tunePara["L² regularization"] = st.slider("L² regularization parameter (scale = 10e-6)", 0, 100, [5, 10])
                                            ann_tunePara["L² regularization"] = ann_tunePara["L² regularization"]/100000
                                            # if any(a for a in weight_opt_list if a == "adam"):
                                            #     ann_tunePara["epsilon"] = st.slider("Value for numerical stability in adam (scale = 10e-10)", 0, 100, [5, 10])
                                            #     ann_tunePara["epsilon"] = ann_tunePara["epsilon"]/1000000000 
                                            hyPara_values["ann"] = ann_tunePara
                                    
                            #--------------------------------------------------------------------------------------
                            # VALIDATION SETTINGS

                            st.markdown("**Validation settings**")
                            do_modval= st.selectbox("Use model validation", ["No", "Yes"])

                            if do_modval == "Yes":
                                # Select training/ test ratio 
                                train_frac = st.slider("Select training data size", 0.5, 0.95, 0.8)

                                # Select number for validation runs
                                val_runs = st.slider("Select number for validation runs", 5, 100, 10)

                            #--------------------------------------------------------------------------------------
                            # PREDICTION SETTINGS

                            st.markdown("**Model predictions**")
                            do_modprednew = st.selectbox("Use model prediction for new data", ["No", "Yes"])

                            if do_modprednew == "Yes":
                                # Upload new data
                                new_data_pred = st.file_uploader("  ", type=["csv", "txt"])

                                if new_data_pred is not None:

                                    # Read data
                                    if uploaded_data is not None:
                                        df_new = pd.read_csv(new_data_pred, decimal=dec_sep, sep = col_sep,thousands=thousands_sep,encoding=encoding_val, engine='python')
                                    else:
                                        df_new = pd.read_csv(new_data_pred, sep = ";|,|\t",engine='python')
                                    st.success('Loading data... done!')

                                    # Transform columns if any were transformed
                                    # Log-transformation
                                    if sb_DM_dTrans_log is not None:

                                        # List of log-transformed variables that are included as explanatory variables
                                        tv_list = []
                                        for tv in sb_DM_dTrans_log:
                                            if "log_"+tv in expl_var:
                                                tv_list.append(tv)
                                        
                                        # Check if log-transformed explanatory variables are available for transformation in new data columns
                                        tv_list_not_avail = []
                                        if tv_list:
                                            for tv in tv_list:
                                                if tv not in df_new.columns:
                                                    tv_list_not_avail.append(tv)
                                            if tv_list_not_avail:
                                                st.error("ERROR: Some variables are not available for log-transformation in new data: "+ ', '.join(tv_list_not_avail))
                                                return
                                            else:
                                                # Transform data if variables for transformation are all available in new data   
                                                df_new = fc.var_transform_log(df_new, tv_list)

                                    # Sqrt-transformation
                                    if sb_DM_dTrans_sqrt is not None:

                                        # List of sqrt-transformed variables that are included as explanatory variables
                                        tv_list = []
                                        for tv in sb_DM_dTrans_sqrt:
                                            if "sqrt_"+tv in expl_var:
                                                tv_list.append(tv)
                                        
                                        # Check if sqrt-transformed explanatory variables are available for transformation in new data columns
                                        tv_list_not_avail = []
                                        if tv_list:
                                            for tv in tv_list:
                                                if tv not in df_new.columns:
                                                    tv_list_not_avail.append(tv)
                                            if tv_list_not_avail:
                                                st.error("ERROR: Some variables are not available for sqrt-transformation in new data: "+ ', '.join(tv_list_not_avail))
                                                return
                                            else:
                                                # Transform data if variables for transformation are all available in new data   
                                                df_new = fc.var_transform_sqrt(df_new, tv_list)
                                    
                                    # Square-transformation
                                    if sb_DM_dTrans_square is not None:

                                        # List of square-transformed variables that are included as explanatory variables
                                        tv_list = []
                                        for tv in sb_DM_dTrans_square:
                                            if "square_"+tv in expl_var:
                                                tv_list.append(tv)
                                        
                                        # Check if square-transformed explanatory variables are available for transformation in new data columns
                                        tv_list_not_avail = []
                                        if tv_list:
                                            for tv in tv_list:
                                                if tv not in df_new.columns:
                                                    tv_list_not_avail.append(tv)
                                            if tv_list_not_avail:
                                                st.error("ERROR: Some variables are not available for square-transformation in new data: "+ ', '.join(tv_list_not_avail))
                                                return
                                            else:
                                                # Transform data if variables for transformation are all available in new data   
                                                df_new = fc.var_transform_square(df_new, tv_list)

                                    # Standardization
                                    if sb_DM_dTrans_stand is not None:

                                        # List of standardized variables that are included as explanatory variables
                                        tv_list = []
                                        for tv in sb_DM_dTrans_stand:
                                            if "stand_"+tv in expl_var:
                                                tv_list.append(tv) 
                                        
                                        # Check if standardized explanatory variables are available for transformation in new data columns
                                        tv_list_not_avail = []
                                        if tv_list:
                                            for tv in tv_list:
                                                if tv not in df_new.columns:
                                                    tv_list_not_avail.append(tv)
                                            if tv_list_not_avail:
                                                st.error("ERROR: Some variables are not available for standardization in new data: "+ ', '.join(tv_list_not_avail))
                                                return
                                            else:
                                                # Transform data if variables for transformation are all available in new data
                                                # Use mean and standard deviation of original data for standardization
                                                for tv in tv_list:
                                                    if df_new[tv].dtypes == "float64" or df_new[tv].dtypes == "int64" or df_new[tv].dtypes == "float32" or df_new[tv].dtypes == "int32":
                                                        if df[tv].std() != 0:
                                                            new_var_name = "stand_" + tv
                                                            new_var = (df_new[tv] - df[tv].mean())/df[tv].std()
                                                            df_new[new_var_name] = new_var
                                                    else:
                                                        st.error("ERROR: " + str(tv) + " is not numerical and cannot be standardized!")
                                                        return    

                                    # Normalization
                                    if sb_DM_dTrans_norm is not None:

                                        # List of normalized variables that are included as explanatory variables
                                        tv_list = []
                                        for tv in sb_DM_dTrans_norm:
                                            if "norm_"+tv in expl_var:
                                                tv_list.append(tv) 

                                        # Check if normalized explanatory variables are available for transformation in new data columns
                                        tv_list_not_avail = []
                                        if tv_list:
                                            for tv in tv_list:
                                                if tv not in df_new.columns:
                                                    tv_list_not_avail.append(tv)
                                            if tv_list_not_avail:
                                                st.error("ERROR: Some variables are not available for normalization in new data: "+ ', '.join(tv_list_not_avail))
                                                return
                                            else:
                                                # Transform data if variables for transformation are all available in new data 
                                                # Use min and max of original data for normalization
                                                for tv in tv_list:
                                                    if df_new[tv].dtypes == "float64" or df_new[tv].dtypes == "int64" or df_new[tv].dtypes == "float32" or df_new[tv].dtypes == "int32":
                                                        if (df[tv].max()-df[tv].min()) != 0:
                                                            new_var_name = "norm_" + tv
                                                            new_var = (df_new[tv] - df[tv].min())/(df[tv].max()-df[tv].min())
                                                            df_new[new_var_name] = new_var 
                                                    else:
                                                        st.error("ERROR: " + str(tv) + " is not numerical and cannot be normalized!")
                                                        return  
                                    
                                    # Categorization
                                    if sb_DM_dTrans_numCat is not None: 

                                        # List of categorized variables that are included as explanatory variables
                                        tv_list = []
                                        for tv in sb_DM_dTrans_numCat:
                                            if "numCat_"+tv in expl_var:
                                                tv_list.append(tv) 
                                        
                                        # Check if categorized explanatory variables are available for transformation in new data columns
                                        tv_list_not_avail = []
                                        if tv_list:
                                            for tv in tv_list:
                                                if tv not in df_new.columns:
                                                    tv_list_not_avail.append(tv)
                                            if tv_list_not_avail:
                                                st.error("ERROR: Some variables are not available for categorization in new data: "+ ', '.join(tv_list_not_avail))
                                                return
                                            else:
                                                # Transform data if variables for transformation are all available in new data 
                                                # Use same categories as for original data
                                                for tv in tv_list:
                                                    new_var_name = "numCat_" + tv
                                                    new_var = pd.DataFrame(index = df_new.index, columns = [new_var_name])
                                                    for r in df_new.index:
                                                        if df.loc[df[tv] == df_new[tv][r]].empty == False:
                                                            new_var.loc[r, new_var_name] = df["numCat_" + tv][df.loc[df[tv] == df_new[tv][r]].index[0]]
                                                        else:
                                                            st.error("ERROR: Category is missing for the value in row: "+ str(r) + ", variable: " + str(tv))
                                                            return
                                                    df_new[new_var_name] = new_var.astype('int64')
                                    
                                    # Multiplication
                                    if sb_DM_dTrans_mult != 0:

                                        # List of multiplied variables that are included as explanatory variables
                                        tv_list = []
                                        for tv in range(0, sb_DM_dTrans_mult):
                                            mult_name = "mult_" + str(multiplication_pairs.loc[tv]["Var1"]) + "_" + str(multiplication_pairs.loc[tv]["Var2"])
                                            if mult_name in expl_var:
                                                tv_list.append(str(multiplication_pairs.loc[tv]["Var1"]))
                                                tv_list.append(str(multiplication_pairs.loc[tv]["Var2"]))
                                        
                                        # Check if multiplied explanatory variables are available for transformation in new data columns
                                        tv_list_not_avail = []
                                        if tv_list:
                                            for tv in tv_list:
                                                if tv not in df_new.columns:
                                                    tv_list_not_avail.append(tv)
                                            if tv_list_not_avail:
                                                st.error("ERROR: Some variables are not available for multiplication in new data: "+ ', '.join(tv_list_not_avail))
                                                return
                                            else:
                                                # Transform data if variables for transformation are all available in new data 
                                                for var in range(0, sb_DM_dTrans_mult):  
                                                    df_new = fc.var_transform_mult(df_new, multiplication_pairs.loc[var]["Var1"], multiplication_pairs.loc[var]["Var2"])

                                    # Division
                                    if sb_DM_dTrans_div != 0:

                                        # List of divided variables that are included as explanatory variables
                                        tv_list = []
                                        for tv in range(0, sb_DM_dTrans_div):
                                            mult_name = "div_" + str(division_pairs.loc[tv]["Var1"]) + "_" + str(division_pairs.loc[tv]["Var2"])
                                            if mult_name in expl_var:
                                                tv_list.append(str(division_pairs.loc[tv]["Var1"]))
                                                tv_list.append(str(division_pairs.loc[tv]["Var2"]))
                                        
                                        # Check if multiplied explanatory variables are available for transformation in new data columns
                                        tv_list_not_avail = []
                                        if tv_list:
                                            for tv in tv_list:
                                                if tv not in df_new.columns:
                                                    tv_list_not_avail.append(tv)
                                            if tv_list_not_avail:
                                                st.error("ERROR: Some variables are not available for division in new data: "+ ', '.join(tv_list_not_avail))
                                                return
                                            else:
                                                # Transform data if variables for transformation are all available in new data 
                                                for var in range(0, sb_DM_dTrans_div):  
                                                    df_new = fc.var_transform_div(df_new, division_pairs.loc[var]["Var1"], division_pairs.loc[var]["Var2"])
                                    
                                    # Check if explanatory variables are available as columns
                                    expl_list = []
                                    for expl_incl in expl_var:
                                        if expl_incl not in df_new.columns:
                                            expl_list.append(expl_incl)
                                    if expl_list:
                                        st.error("ERROR: Some variables are missing in new data: "+ ', '.join(expl_list))
                                        return
                                    else:
                                        st.info("All variables are available for predictions!")
                                    
                                    # Check if NAs are present and delete them automatically
                                    if df_new.iloc[list(pd.unique(np.where(df_new.isnull())[0]))].shape[0] == 0:
                                        st.empty()
                                    else:
                                        df_new = df_new[expl_var].dropna()
                                        st.warning("WARNING: Your new data set includes NAs. Rows with NAs are automatically deleted!")
                                    df_new = df_new[expl_var]
                                
                            # Modelling data set
                            df = df[var_list]

                            # Check if NAs are present and delete them automatically
                            if np.where(df[var_list].isnull())[0].size > 0:
                                df = df.dropna()
                                    
                            #--------------------------------------------------------------------------------------
                            # SETTINGS SUMMARY
                            
                            st.write("")

                            # Show modelling data
                            if st.checkbox("Show modelling data"):
                                st.write(df)
                                st.write("Data shape: ", df.shape[0],  " rows and ", df.shape[1], " columns")
                                
                                # Download link for modelling data
                                output = BytesIO()
                                excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
                                df.to_excel(excel_file, sheet_name="modelling_data")
                                excel_file.save()
                                excel_file = output.getvalue()
                                b64 = base64.b64encode(excel_file)
                                dl_file_name= "Modelling data__" + df_name + ".xlsx"
                                st.markdown(
                                    f"""
                                <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download modelling data</a>
                                """,
                                unsafe_allow_html=True)
                            st.write("")

                            # Show prediction data
                            if do_modprednew == "Yes":
                                if new_data_pred is not None:
                                    if st.checkbox("Show new data for predictions"):
                                        st.write(df_new)
                                        st.write("Data shape: ", df_new.shape[0],  " rows and ", df_new.shape[1], " columns")

                                        # Download link for forecast data
                                        output = BytesIO()
                                        excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
                                        df_new.to_excel(excel_file, sheet_name="new_data")
                                        excel_file.save()
                                        excel_file = output.getvalue()
                                        b64 = base64.b64encode(excel_file)
                                        dl_file_name= "New data for predictions__" + df_name + ".xlsx"
                                        st.markdown(
                                            f"""
                                        <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download new data for predictions</a>
                                        """,
                                        unsafe_allow_html=True)
                                    st.write("")

                            # Show machine learning summary
                            if st.checkbox('Show a summary of machine learning settings', value = False): 
                                
                                #--------------------------------------------------------------------------------------
                                # ALOGRITHMS
                                
                                st.write("Algorithms summary:")
                                st.write("-",  ', '.join(sb_ML_alg))
                                if any(a for a in sb_ML_alg if a == "Multiple Linear Regression"):
                                    # st.write("- Multiple Linear Regression model: ", MLR_model)
                                    st.write("- Multiple Linear Regression covariance type: ", MLR_cov_type)
                                if any(a for a in sb_ML_alg if a == "Logistic Regression"):
                                    st.write("- Logistic Regression covariance type: ", LR_cov_type)
                                if any(a for a in sb_ML_alg if a == "Generalized Additive Models"):
                                    st.write("- Generalized Additive Models parameters: ")
                                    st.write(gam_finalPara)
                                st.write("")

                                #--------------------------------------------------------------------------------------
                                # SETTINGS

                                # Hyperparameter settings summary
                                if any(a for a in sb_ML_alg if a == "Artificial Neural Networks" or a == "Boosted Regression Trees" or a == "Random Forest"):
                                    st.write("Hyperparameter-tuning settings summary:")
                                    if do_hypTune == "No":
                                        st.write("- ", do_hypTune_no)
                                        st.write("")
                                    if do_hypTune == "Yes":
                                        st.write("- Search method:", hypTune_method)
                                        st.write("- ", hypTune_nCV, "-fold cross-validation")
                                        if hypTune_method == "random grid-search" or hypTune_method == "Bayes optimization" or hypTune_method == "sequential model-based optimization":
                                            st.write("- ", hypTune_iter, "iterations in search")
                                            st.write("")
                                        # Random Forest summary
                                        if any(a for a in sb_ML_alg if a == "Random Forest"):
                                            st.write("Random Forest settings summary:")
                                            st.write(rf_tunePara)
                                        # Boosted Regression Trees summary
                                        if any(a for a in sb_ML_alg if a == "Boosted Regression Trees"):
                                            st.write("Boosted Regression Trees settings summary:")
                                            st.write(brt_tunePara)
                                        # Artificial Neural Networks summary
                                        if any(a for a in sb_ML_alg if a == "Artificial Neural Networks"):
                                            st.write("Artificial Neural Networks settings summary:")
                                            st.write(ann_tunePara)
                                            st.caption("** Learning rate is only used in adam")
                                        st.write("")

                                # General settings summary
                                st.write("General settings summary:")
                                st.write("- Response variable type: ", response_var_type)
                                # Modelling formula
                                if expl_var != False:
                                    st.write("- Modelling formula:", response_var, "~",  ' + '.join(expl_var))
                                if do_modval == "Yes":
                                    # Train/ test ratio
                                    if train_frac != False:
                                        st.write("- Train/ test ratio:", str(round(train_frac*100)), "% / ", str(round(100-train_frac*100)), "%")
                                    # Validation runs
                                    if val_runs != False:
                                        st.write("- Validation runs:", str(val_runs))
                                st.write("")
                                st.write("")
                        
                            #--------------------------------------------------------------------------------------
                            # RUN MODELS

                            # Models are run on button click
                            st.write("")
                            run_models = st.button("Run models")
                            st.write("")
                            
                            if run_models:

                                #Hyperparameter   
                                if do_hypTune == "Yes":

                                    # Tuning
                                    model_tuning_results = ml.model_tuning(df, sb_ML_alg, hypTune_method, hypTune_iter, hypTune_nCV, hyPara_values, response_var_type, response_var, expl_var)
                                
                                    # Save final hyperparameters
                                    # Random Forest
                                    if any(a for a in sb_ML_alg if a == "Random Forest"):
                                        rf_tuning_results = model_tuning_results["rf tuning"]
                                        rf_finalPara = pd.DataFrame(index = ["value"], columns = ["number of trees", "maximum tree depth", "maximum number of features", "sample rate"])
                                        rf_finalPara["number of trees"] = [rf_tuning_results.loc["value"]["number of trees"]]
                                        if [rf_tuning_results.loc["value"]["maximum tree depth"]][0] == "None":
                                            rf_finalPara["maximum tree depth"] = None
                                        else:
                                            rf_finalPara["maximum tree depth"] = [rf_tuning_results.loc["value"]["maximum tree depth"]]
                                        rf_finalPara["maximum number of features"] = [rf_tuning_results.loc["value"]["maximum number of features"]]
                                        rf_finalPara["sample rate"] = [rf_tuning_results.loc["value"]["sample rate"]]
                                        final_hyPara_values["rf"] = rf_finalPara
                                    # Boosted Regression Trees
                                    if any(a for a in sb_ML_alg if a == "Boosted Regression Trees"):
                                        brt_tuning_results = model_tuning_results["brt tuning"]
                                        brt_finalPara = pd.DataFrame(index = ["value"], columns = ["number of trees", "learning rate", "maximum tree depth", "sample rate"])
                                        brt_finalPara["number of trees"] = [brt_tuning_results.loc["value"]["number of trees"]]
                                        brt_finalPara["learning rate"] = [brt_tuning_results.loc["value"]["learning rate"]]
                                        brt_finalPara["maximum tree depth"] = [brt_tuning_results.loc["value"]["maximum tree depth"]]
                                        brt_finalPara["sample rate"] = [brt_tuning_results.loc["value"]["sample rate"]]
                                        final_hyPara_values["brt"] = brt_finalPara
                                    # Artificial Neural Networks
                                    if any(a for a in sb_ML_alg if a == "Artificial Neural Networks"):
                                        ann_tuning_results = model_tuning_results["ann tuning"]
                                        ann_finalPara = pd.DataFrame(index = ["value"], columns = ["weight optimization solver", "maximum number of iterations", "activation function", "hidden layer sizes", "learning rate", "L² regularization"]) #"learning rate schedule", "momentum", "epsilon"])
                                        ann_finalPara["weight optimization solver"] = [ann_tuning_results.loc["value"]["weight optimization solver"]]
                                        ann_finalPara["maximum number of iterations"] = [ann_tuning_results.loc["value"]["maximum number of iterations"]]
                                        ann_finalPara["activation function"] = [ann_tuning_results.loc["value"]["activation function"]]
                                        ann_finalPara["hidden layer sizes"] = [ann_tuning_results.loc["value"]["hidden layer sizes"]]
                                        ann_finalPara["learning rate"] = [ann_tuning_results.loc["value"]["learning rate"]]
                                        #ann_finalPara["learning rate schedule"] = [ann_tuning_results.loc["value"]["learning rate schedule"]]
                                        #ann_finalPara["momentum"] = [ann_tuning_results.loc["value"]["momentum"]]
                                        ann_finalPara["L² regularization"] = [ann_tuning_results.loc["value"]["L² regularization"]]
                                        #ann_finalPara["epsilon"] = [ann_tuning_results.loc["value"]["epsilon"]]
                                        final_hyPara_values["ann"] = ann_finalPara
                                
                                # Model validation
                                if do_modval == "Yes":
                                    model_val_results = ml.model_val(df, sb_ML_alg, MLR_model, train_frac, val_runs, response_var_type, response_var, expl_var, final_hyPara_values, gam_finalPara)
                                
                                # Full model (depending on prediction for new data)
                                if do_modprednew == "Yes":
                                    if new_data_pred is not None:
                                        model_full_results = ml.model_full(df, df_new, sb_ML_alg, MLR_model, MLR_cov_type, LR_cov_type, response_var_type, response_var, expl_var, final_hyPara_values, gam_finalPara)
                                    else:
                                        st.error("ERROR: Please upload new data for additional model predictions or select 'No'!")
                                        return
                                if do_modprednew == "No":
                                    df_new = pd.DataFrame()
                                    model_full_results = ml.model_full(df, df_new, sb_ML_alg, MLR_model, MLR_cov_type, LR_cov_type, response_var_type, response_var, expl_var, final_hyPara_values, gam_finalPara)
                                
                                # Success message
                                st.success('Models run successfully!')
            else: st.error("ERROR: No data available for Modelling!") 

    #++++++++++++++++++++++
    # ML OUTPUT

    # Show only if models were run (no further widgets after run models or the full page reloads)
    if run_models == True:
        st.write("")
        st.write("")
        st.header("**Model outputs**")

        #--------------------------------------------------------------------------------------
        # FULL MODEL OUTPUT

        full_output = st.beta_expander("Full model output", expanded = False)
        with full_output:
            
            if model_full_results is not None:

                st.markdown("**Correlation Matrix & 2D-Histogram**")
                # Define variable selector
                var_sel_cor = alt.selection_single(fields=['variable', 'variable2'], clear=False, 
                                    init={'variable': response_var, 'variable2': response_var})
                # Calculate correlation data
                corr_data = df[[response_var] + expl_var].corr().stack().reset_index().rename(columns={0: "correlation", 'level_0': "variable", 'level_1': "variable2"})
                corr_data["correlation_label"] = corr_data["correlation"].map('{:.2f}'.format)
                # Basic plot
                base = alt.Chart(corr_data).encode(
                    x = alt.X('variable2:O', sort = None, axis = alt.Axis(title = None, labelFontSize = 12)),
                    y = alt.Y('variable:O',  sort = None, axis = alt.Axis(title = None, labelFontSize = 12))
                )
                # Correlation values to insert
                text = base.mark_text().encode(
                    text='correlation_label',
                    color = alt.condition(
                        alt.datum.correlation > 0.5, 
                        alt.value('white'),
                        alt.value('black')
                    )
                )
                # Correlation plot
                corr_plot = base.mark_rect().encode(
                    color = alt.condition(var_sel_cor, alt.value('#86c29c'), 'correlation:Q', legend = alt.Legend(title = "Bravais-Pearson correlation coefficient", orient = "top", gradientLength = 350), scale = alt.Scale(scheme='redblue', reverse = True, domain = [-1,1]))
                ).add_selection(var_sel_cor)
                # Calculate values for 2d histogram
                value_columns = df[[response_var] + expl_var]
                df_2dbinned = pd.concat([fc.compute_2d_histogram(var1, var2, df) for var1 in value_columns for var2 in value_columns])
                # 2d binned histogram plot
                scat_plot = alt.Chart(df_2dbinned).transform_filter(
                    var_sel_cor
                ).mark_rect().encode(
                    alt.X('value2:N', sort = alt.EncodingSortField(field='raw_left_value2'), axis = alt.Axis(title = "Horizontal variable", labelFontSize = 12)), 
                    alt.Y('value:N', axis = alt.Axis(title = "Vertical variable", labelFontSize = 12), sort = alt.EncodingSortField(field='raw_left_value', order = 'descending')),
                    alt.Color('count:Q', scale = alt.Scale(scheme='reds'),  legend = alt.Legend(title = "Count", orient = "top", gradientLength = 350))
                )
                # Combine all plots
                correlation_plot = alt.vconcat((corr_plot + text).properties(width = 400, height = 400), scat_plot.properties(width = 400, height = 400)).resolve_scale(color = 'independent')
                corr_plot1 = (corr_plot + text).properties(width = 400, height = 400)
                correlation_plot = correlation_plot.properties(padding = {"left": 50, "top": 5, "right": 5, "bottom": 50})
                # hist_2d_plot = scat_plot.properties(height = 350)
                if response_var_type == "continuous":
                    st.altair_chart(correlation_plot, use_container_width = True)
                if response_var_type == "binary":
                    st.altair_chart(correlation_plot, use_container_width = True)
                if sett_hints:
                    st.info(str(fc.learning_hints("mod_cor")))
                st.write("")
                
                #-------------------------------------------------------------

                # Continuous response variable
                if response_var_type == "continuous":

                    # MLR specific output
                    if any(a for a in sb_ML_alg if a == "Multiple Linear Regression"):
                        st.markdown("**Multiple Linear Regression**")
                    
                        # Regression information
                        fm_mlr_reg_col1, fm_mlr_reg_col2 = st.beta_columns(2)
                        with fm_mlr_reg_col1:
                            st.write("Regression information:")
                            st.write(model_full_results["MLR information"])
                        # Regression statistics
                        with fm_mlr_reg_col2:
                            st.write("Regression statistics:")
                            st.write(model_full_results["MLR statistics"])
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_MLR_regStat")))
                        st.write("")
                        # Coefficients
                        st.write("Coefficients:")
                        st.write(model_full_results["MLR coefficients"])
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_MLR_coef")))
                        st.write("")
                        # ANOVA
                        st.write("ANOVA:")
                        st.write(model_full_results["MLR ANOVA"])
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_MLR_ANOVA")))
                        st.write("")
                        # Heteroskedasticity tests
                        st.write("Heteroskedasticity tests:")
                        st.write(model_full_results["MLR hetTest"])
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_MLR_hetTest")))
                        st.write("")
                        # Variable importance (via permutation)
                        fm_mlr_reg2_col1, fm_mlr_reg2_col2 = st.beta_columns(2)
                        with fm_mlr_reg2_col1: 
                            st.write("Variable importance (via permutation):")
                            mlr_varImp_table = model_full_results["MLR variable importance"]
                            st.write(mlr_varImp_table)
                            st.write("")
                        with fm_mlr_reg2_col2: 
                            st.write("")
                            st.write("")
                            st.write("")
                            mlr_varImp_plot_data = model_full_results["MLR variable importance"]
                            mlr_varImp_plot_data["Variable"] = mlr_varImp_plot_data.index
                            mlr_varImp = alt.Chart(mlr_varImp_plot_data, height = 200).mark_bar().encode(
                                x = alt.X("mean", title = "variable importance", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Variable", title = None, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), sort = None),
                                tooltip = ["Variable", "mean"]
                            )
                            st.altair_chart(mlr_varImp, use_container_width = True) 
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_MLR_varImp")))
                        st.write("")                        
                        # Graphical output
                        fm_mlr_figs_col1, fm_mlr_figs_col2 = st.beta_columns(2)
                        with fm_mlr_figs_col1:
                            st.write("Observed vs Fitted:")
                            observed_fitted_data = pd.DataFrame()
                            observed_fitted_data["Observed"] = df[response_var]
                            observed_fitted_data["Fitted"] = model_full_results["MLR fitted"]
                            observed_fitted_data["Index"] = df.index
                            observed_fitted = alt.Chart(observed_fitted_data, height = 200).mark_circle(size=20).encode(
                                x = alt.X("Fitted", title = "fitted", scale = alt.Scale(domain = [min(observed_fitted_data["Fitted"]), max(observed_fitted_data["Fitted"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Observed", title = "observed", scale = alt.Scale(zero = False),  axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Observed", "Fitted", "Index"]
                            )
                            observed_fitted_plot = observed_fitted + observed_fitted.transform_regression("Fitted", "Observed").mark_line(size = 2, color = "darkred")
                            st.altair_chart(observed_fitted_plot, use_container_width = True)
                        with fm_mlr_figs_col2:
                            st.write("Residuals vs Fitted:")
                            residuals_fitted_data = pd.DataFrame()
                            residuals_fitted_data["Residuals"] = model_full_results["residuals"]["Multiple Linear Regression"]
                            residuals_fitted_data["Fitted"] = model_full_results["MLR fitted"]
                            residuals_fitted_data["Index"] = df.index
                            residuals_fitted = alt.Chart(residuals_fitted_data, height = 200).mark_circle(size=20).encode(
                                x = alt.X("Fitted", title = "fitted", scale = alt.Scale(domain = [min(residuals_fitted_data["Fitted"]), max(residuals_fitted_data["Fitted"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Residuals", title = "residuals", scale = alt.Scale(zero = False), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Residuals", "Fitted", "Index"]
                            )
                            residuals_fitted_plot = residuals_fitted + residuals_fitted.transform_loess("Fitted", "Residuals", bandwidth = 0.5).mark_line(size = 2, color = "darkred")
                            st.altair_chart(residuals_fitted_plot, use_container_width = True)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_MLR_obsResVsFit")))
                        st.write("")
                        fm_mlr_figs1_col1, fm_mlr_figs1_col2 = st.beta_columns(2)
                        with fm_mlr_figs1_col1:
                            st.write("Normal QQ-plot:")
                            residuals = model_full_results["residuals"]["Multiple Linear Regression"]
                            qq_plot_data = pd.DataFrame()
                            qq_plot_data["StandResiduals"] = (residuals - residuals.mean())/residuals.std()
                            qq_plot_data["Index"] = df.index
                            qq_plot_data = qq_plot_data.sort_values(by = ["StandResiduals"])
                            qq_plot_data["Theoretical quantiles"] = stats.probplot(residuals, dist="norm")[0][0]
                            qq_plot = alt.Chart(qq_plot_data, height = 200).mark_circle(size=20).encode(
                                x = alt.X("Theoretical quantiles", title = "theoretical quantiles", scale = alt.Scale(domain = [min(qq_plot_data["Theoretical quantiles"]), max(qq_plot_data["Theoretical quantiles"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("StandResiduals", title = "stand. residuals", scale = alt.Scale(zero = False), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["StandResiduals", "Theoretical quantiles", "Index"]
                            )
                            line = alt.Chart(
                                pd.DataFrame({"Theoretical quantiles": [min(qq_plot_data["Theoretical quantiles"]), max(qq_plot_data["Theoretical quantiles"])], "StandResiduals": [min(qq_plot_data["Theoretical quantiles"]), max(qq_plot_data["Theoretical quantiles"])]})).mark_line(size = 2, color = "darkred").encode(
                                        alt.X("Theoretical quantiles"),
                                        alt.Y("StandResiduals"),
                            )
                            st.altair_chart(qq_plot + line, use_container_width = True)
                            if sett_hints:
                                st.info(str(fc.learning_hints("mod_md_MLR_qqplot")))
                        with fm_mlr_figs1_col2:
                            st.write("Scale-Location:")
                            scale_location_data = pd.DataFrame()
                            residuals = model_full_results["residuals"]["Multiple Linear Regression"]
                            scale_location_data["SqrtStandResiduals"] = np.sqrt(abs((residuals - residuals.mean())/residuals.std()))
                            scale_location_data["Fitted"] = model_full_results["MLR fitted"]
                            scale_location_data["Index"] = df.index
                            scale_location = alt.Chart(scale_location_data, height = 200).mark_circle(size=20).encode(
                                x = alt.X("Fitted", title = "fitted", scale = alt.Scale(domain = [min(scale_location_data["Fitted"]), max(scale_location_data["Fitted"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("SqrtStandResiduals", title = "sqrt(|stand. residuals|)", scale = alt.Scale(zero = False), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["SqrtStandResiduals", "Fitted", "Index"]
                            )
                            scale_location_plot = scale_location + scale_location.transform_loess("Fitted", "SqrtStandResiduals", bandwidth = 0.5).mark_line(size = 2, color = "darkred")
                            st.altair_chart(scale_location_plot, use_container_width = True)
                            if sett_hints:
                                st.info(str(fc.learning_hints("mod_md_MLR_scaleLoc")))
                        st.write("")
                        fm_mlr_figs2_col1, fm_mlr_figs2_col2 = st.beta_columns(2)
                        with fm_mlr_figs2_col1:
                            st.write("Residuals vs Leverage:")
                            residuals_leverage_data = pd.DataFrame()
                            residuals = model_full_results["residuals"]["Multiple Linear Regression"]
                            residuals_leverage_data["StandResiduals"] = (residuals - residuals.mean())/residuals.std()
                            residuals_leverage_data["Leverage"] = model_full_results["MLR leverage"]
                            residuals_leverage_data["Index"] = df.index
                            residuals_leverage = alt.Chart(residuals_leverage_data, height = 200).mark_circle(size=20).encode(
                                x = alt.X("Leverage", title = "leverage", scale = alt.Scale(domain = [min(residuals_leverage_data["Leverage"]), max(residuals_leverage_data["Leverage"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("StandResiduals", title = "stand. residuals", scale = alt.Scale(zero = False), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["StandResiduals","Leverage", "Index"]
                            )
                            residuals_leverage_plot = residuals_leverage + residuals_leverage.transform_loess("Leverage", "StandResiduals", bandwidth = 0.5).mark_line(size = 2, color = "darkred")
                            st.altair_chart(residuals_leverage_plot, use_container_width = True)
                        with fm_mlr_figs2_col2:
                            st.write("Cook's distance:")
                            cooksD_data = pd.DataFrame()
                            cooksD_data["CooksD"] = model_full_results["MLR Cooks distance"]
                            cooksD_data["Index"] = df.index
                            cooksD = alt.Chart(cooksD_data, height = 200).mark_bar(size = 2).encode(
                                x = alt.X("Index", title = "index", scale = alt.Scale(domain = [-1, max(cooksD_data["Index"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("CooksD", title = "Cook's distance", scale = alt.Scale(zero = False), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["CooksD", "Index"]
                            )
                            st.altair_chart(cooksD, use_container_width = True)  
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_MLR_resVsLev_cooksD")))

                        # Download link for MLR output
                        output = BytesIO()
                        excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
                        model_full_results["MLR information"].to_excel(excel_file, sheet_name="regression_information")
                        model_full_results["MLR statistics"].to_excel(excel_file, sheet_name="regression_statistics")
                        model_full_results["MLR coefficients"].to_excel(excel_file, sheet_name="coefficients")
                        model_full_results["MLR ANOVA"].to_excel(excel_file, sheet_name="ANOVA")
                        model_full_results["MLR hetTest"].to_excel(excel_file, sheet_name="heteroskedasticity_tests")
                        mlr_varImp_table.to_excel(excel_file, sheet_name="variable_importance")
                        excel_file.save()
                        excel_file = output.getvalue()
                        b64 = base64.b64encode(excel_file)
                        dl_file_name= "MLR full model output__" + df_name + ".xlsx"
                        st.markdown(
                            f"""
                        <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download Multiple Linear Regression full model output</a>
                        """,
                        unsafe_allow_html=True)
                        st.write("")

                    # GAM specific output
                    if any(a for a in sb_ML_alg if a == "Generalized Additive Models"):
                        st.markdown("**Generalized Additive Models**")

                        fm_gam_reg_col1, fm_gam_reg_col2 = st.beta_columns(2)
                        # Regression information
                        with fm_gam_reg_col1:
                            st.write("Regression information:")
                            st.write(model_full_results["GAM information"])
                        # Regression statistics
                        with fm_gam_reg_col2:
                            st.write("Regression statistics:")
                            st.write(model_full_results["GAM statistics"])
                        # if sett_hints:
                        #     st.info(str(fc.learning_hints("mod_md_BRT_regStat")))
                        st.write("")
                        # Feature significance
                        st.write("Feature significance:")
                        st.write(model_full_results["GAM feature significance"])
                        # if sett_hints:
                        #     st.info(str(fc.learning_hints("mod_md_MLR_coef")))
                        st.write("")
                        # Variable importance (via permutation)
                        fm_gam_figs1_col1, fm_gam_figs1_col2 = st.beta_columns(2)
                        with fm_gam_figs1_col1:
                            st.write("Variable importance (via permutation):")
                            gam_varImp_table = model_full_results["GAM variable importance"]
                            st.write(gam_varImp_table)
                            st.write("")
                        with fm_gam_figs1_col2:
                            st.write("")
                            st.write("")
                            st.write("")
                            gam_varImp_plot_data = model_full_results["GAM variable importance"]
                            gam_varImp_plot_data["Variable"] = gam_varImp_plot_data.index
                            gam_varImp = alt.Chart(gam_varImp_plot_data, height = 200).mark_bar().encode(
                                x = alt.X("mean", title = "variable importance", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Variable", title = None, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), sort = None),
                                tooltip = ["Variable", "mean"]
                            )
                            st.altair_chart(gam_varImp, use_container_width = True) 
                        st.write("") 
                        # Partial dependence plots
                        st.write("Partial dependence plots:")    
                        fm_gam_figs3_col1, fm_gam_figs3_col2 = st.beta_columns(2)
                        for pd_var in expl_var:
                            pd_data_gam = pd.DataFrame(columns = [pd_var])
                            pd_data_gam[pd_var] = model_full_results["GAM partial dependence"][pd_var]["x_values"]
                            pd_data_gam["Partial dependence"] = model_full_results["GAM partial dependence"][pd_var]["pd_values"]
                            pd_data_gam["Lower 95%"] = model_full_results["GAM partial dependence"][pd_var]["lower_95"]
                            pd_data_gam["Upper 95%"] = model_full_results["GAM partial dependence"][pd_var]["upper_95"]
                            pd_chart_gam = alt.Chart(pd_data_gam, height = 200).mark_line(color = "darkred").encode(
                                x = alt.X(pd_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Partial dependence", title = "partial dependence", scale = alt.Scale(domain = [model_full_results["GAM partial dependence min/max"]["min"].min(), model_full_results["GAM partial dependence min/max"]["max"].max()]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Upper 95%", "Partial dependence", "Lower 95%"] + [pd_var]
                            )
                            pd_data_ticks_gam = pd.DataFrame(columns = [pd_var])
                            pd_data_ticks_gam[pd_var] = df[pd_var]
                            pd_data_ticks_gam["y"] = [model_full_results["GAM partial dependence min/max"]["min"].min()] * df.shape[0]
                            pd_ticks_gam = alt.Chart(pd_data_ticks_gam, height = 200).mark_tick(size = 5, thickness = 1).encode(
                                x = alt.X(pd_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), scale = alt.Scale(domain = [pd_data_ticks_gam[pd_var].min(), pd_data_ticks_gam[pd_var].max()])),
                                y = alt.Y("y", title = "partial dependence", scale = alt.Scale(domain = [model_full_results["GAM partial dependence min/max"]["min"].min(), model_full_results["GAM partial dependence min/max"]["max"].max()]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = [pd_var]
                            )
                            pd_data_gam_lower = pd.DataFrame(columns = [pd_var])
                            pd_data_gam_lower[pd_var] = model_full_results["GAM partial dependence"][pd_var]["x_values"]
                            pd_data_gam_lower["Lower 95%"] = model_full_results["GAM partial dependence"][pd_var]["lower_95"]
                            pd_chart_gam_lower = alt.Chart(pd_data_gam_lower, height = 200).mark_line(strokeDash=[1,1], color = "darkred").encode(
                                x = alt.X(pd_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Lower 95%", title = "", scale = alt.Scale(domain = [model_full_results["GAM partial dependence min/max"]["min"].min(), model_full_results["GAM partial dependence min/max"]["max"].max()]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Lower 95%"] + [pd_var]
                            )
                            pd_data_gam_upper = pd.DataFrame(columns = [pd_var])
                            pd_data_gam_upper[pd_var] = model_full_results["GAM partial dependence"][pd_var]["x_values"]
                            pd_data_gam_upper["Upper 95%"] = model_full_results["GAM partial dependence"][pd_var]["upper_95"]
                            pd_chart_gam_upper = alt.Chart(pd_data_gam_upper, height = 200).mark_line(strokeDash=[1,1], color = "darkred").encode(
                                x = alt.X(pd_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Upper 95%", title = "", scale = alt.Scale(domain = [model_full_results["GAM partial dependence min/max"]["min"].min(), model_full_results["GAM partial dependence min/max"]["max"].max()]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Upper 95%"] + [pd_var]
                            )
                            if expl_var.index(pd_var)%2 == 0:
                                with fm_gam_figs3_col1:
                                    st.altair_chart(pd_ticks_gam + pd_chart_gam_lower + pd_chart_gam_upper + pd_chart_gam, use_container_width = True)
                            if expl_var.index(pd_var)%2 == 1:
                                with fm_gam_figs3_col2:
                                    st.altair_chart(pd_ticks_gam + pd_chart_gam_lower + pd_chart_gam_upper + pd_chart_gam, use_container_width = True)
                        # if sett_hints:
                        #     st.info(str(fc.learning_hints("mod_md_BRT_partDep")))
                        st.write("")         
                        # Further graphical output
                        fm_gam_figs4_col1, fm_gam_figs4_col2 = st.beta_columns(2)
                        with fm_gam_figs4_col1:
                            st.write("Observed vs Fitted:")
                            observed_fitted_data = pd.DataFrame()
                            observed_fitted_data["Observed"] = df[response_var]
                            observed_fitted_data["Fitted"] = model_full_results["GAM fitted"]
                            observed_fitted_data["Index"] = df.index
                            observed_fitted = alt.Chart(observed_fitted_data, height = 200).mark_circle(size=20).encode(
                                x = alt.X("Fitted", title = "fitted", scale = alt.Scale(domain = [min(observed_fitted_data["Fitted"]), max(observed_fitted_data["Fitted"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Observed", title = "observed", scale = alt.Scale(zero = False), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Observed", "Fitted", "Index"]
                            )
                            observed_fitted_plot = observed_fitted + observed_fitted.transform_regression("Fitted", "Observed").mark_line(size = 2, color = "darkred")
                            st.altair_chart(observed_fitted_plot, use_container_width = True)
                        with fm_gam_figs4_col2:
                            st.write("Residuals vs Fitted:")
                            residuals_fitted_data = pd.DataFrame()
                            residuals_fitted_data["Residuals"] = model_full_results["residuals"]["Generalized Additive Models"]
                            residuals_fitted_data["Fitted"] = model_full_results["GAM fitted"]
                            residuals_fitted_data["Index"] = df.index
                            residuals_fitted = alt.Chart(residuals_fitted_data, height = 200).mark_circle(size=20).encode(
                                x = alt.X("Fitted", title = "fitted", scale = alt.Scale(domain = [min(residuals_fitted_data["Fitted"]), max(residuals_fitted_data["Fitted"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Residuals", title = "residuals", scale = alt.Scale(zero = False), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Residuals", "Fitted", "Index"]
                            )
                            residuals_fitted_plot = residuals_fitted + residuals_fitted.transform_loess("Fitted", "Residuals", bandwidth = 0.5).mark_line(size = 2, color = "darkred")
                            st.altair_chart(residuals_fitted_plot, use_container_width = True) 
                        # if sett_hints:
                        #     st.info(str(fc.learning_hints("mod_md_BRT_obsResVsFit")))

                        # Download link for GAM output
                        output = BytesIO()
                        excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
                        model_full_results["GAM information"].to_excel(excel_file, sheet_name="regression_information")
                        model_full_results["GAM statistics"].to_excel(excel_file, sheet_name="regression_statistics")
                        model_full_results["GAM feature significance"].to_excel(excel_file, sheet_name="feature_significance")
                        gam_varImp_table.to_excel(excel_file, sheet_name="variable_importance")
                        excel_file.save()
                        excel_file = output.getvalue()
                        b64 = base64.b64encode(excel_file)
                        dl_file_name = "GAM full model output__" + df_name + ".xlsx"
                        st.markdown(
                            f"""
                        <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download Generalized Additive Models full model output</a>
                        """,
                        unsafe_allow_html=True)
                        st.write("")

                    # RF specific output
                    if any(a for a in sb_ML_alg if a == "Random Forest"):
                        st.markdown("**Random Forest**")

                        fm_rf_reg_col1, fm_rf_reg_col2 = st.beta_columns(2)
                        # Regression information
                        with fm_rf_reg_col1:
                            st.write("Regression information:")
                            st.write(model_full_results["RF information"])
                        # Regression statistics
                        with fm_rf_reg_col2:
                            st.write("Regression statistics:")
                            rf_error_est = pd.DataFrame(index = ["MSE", "RMSE", "MAE", "Residual SE"], columns = ["Value"])
                            rf_error_est.loc["MSE"] = model_full_results["model comparison"].loc["MSE"]["Random Forest"]
                            rf_error_est.loc["RMSE"] = model_full_results["model comparison"].loc["RMSE"]["Random Forest"]
                            rf_error_est.loc["MAE"] =  model_full_results["model comparison"].loc["MAE"]["Random Forest"]
                            rf_error_est.loc["Residual SE"] = model_full_results["RF Residual SE"]
                            st.write(rf_error_est)
                        # if sett_hints:
                        #     st.info(str(fc.learning_hints("mod_md_BRT_regStat")))
                        st.write("")
                        # Variable importance (via permutation)
                        fm_rf_figs1_col1, fm_rf_figs1_col2 = st.beta_columns(2)
                        with fm_rf_figs1_col1:
                            st.write("Variable importance (via permutation):")
                            rf_varImp_table = model_full_results["RF variable importance"]
                            st.write(rf_varImp_table)
                            st.write("")
                        with fm_rf_figs1_col2:
                            st.write("")
                            st.write("")
                            st.write("")
                            rf_varImp_plot_data = model_full_results["RF variable importance"]
                            rf_varImp_plot_data["Variable"] = rf_varImp_plot_data.index
                            rf_varImp = alt.Chart(rf_varImp_plot_data, height = 200).mark_bar().encode(
                                x = alt.X("mean", title = "variable importance", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Variable", title = None, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), sort = None),
                                tooltip = ["Variable", "mean"]
                            )
                            st.altair_chart(rf_varImp, use_container_width = True) 
                        st.write("") 
                        fm_rf_figs2_col1, fm_rf_figs2_col2 = st.beta_columns(2)
                        # Feature importance
                        with fm_rf_figs2_col1:
                            st.write("Feature importance (impurity-based):")
                            rf_featImp_table = model_full_results["RF feature importance"]
                            st.write(rf_featImp_table)
                            st.write("")
                        with fm_rf_figs2_col2:
                            st.write("")
                            st.write("")
                            st.write("")
                            rf_featImp_plot_data = model_full_results["RF feature importance"]
                            rf_featImp_plot_data["Variable"] = rf_featImp_plot_data.index
                            rf_featImp = alt.Chart(rf_featImp_plot_data, height = 200).mark_bar().encode(
                                x = alt.X("Value", title = "feature importance", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Variable", title = None, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), sort = None),
                                tooltip = ["Variable", "Value"]
                            )
                            st.altair_chart(rf_featImp, use_container_width = True)
                        # if sett_hints:
                        #     st.info(str(fc.learning_hints("mod_md_BRT_varImp")))
                        st.write("") 
                        # Partial dependence plots
                        st.write("Partial dependence plots:")    
                        fm_rf_figs3_col1, fm_rf_figs3_col2 = st.beta_columns(2)
                        for pd_var in expl_var:
                            pd_data_rf = pd.DataFrame(columns = [pd_var])
                            pd_data_rf[pd_var] = model_full_results["RF partial dependence"][pd_var][1][0]
                            pd_data_rf["Partial dependence"] = model_full_results["RF partial dependence"][pd_var][0][0]
                            pd_chart_rf = alt.Chart(pd_data_rf, height = 200).mark_line(color = "darkred").encode(
                                x = alt.X(pd_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Partial dependence", title = "partial dependence", scale = alt.Scale(domain = [model_full_results["RF partial dependence min/max"]["min"].min(), model_full_results["RF partial dependence min/max"]["max"].max()]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Partial dependence"] + [pd_var]
                            )
                            pd_data_ticks_rf = pd.DataFrame(columns = [pd_var])
                            pd_data_ticks_rf[pd_var] = df[pd_var]
                            pd_data_ticks_rf["y"] = [model_full_results["RF partial dependence min/max"]["min"].min()] * df.shape[0]
                            pd_ticks_rf = alt.Chart(pd_data_ticks_rf, height = 200).mark_tick(size = 5, thickness = 1).encode(
                                x = alt.X(pd_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), scale = alt.Scale(domain = [pd_data_ticks_rf[pd_var].min(), pd_data_ticks_rf[pd_var].max()])),
                                y = alt.Y("y", title = "partial dependence", scale = alt.Scale(domain = [model_full_results["RF partial dependence min/max"]["min"].min(), model_full_results["RF partial dependence min/max"]["max"].max()]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = [pd_var]
                            )
                            if expl_var.index(pd_var)%2 == 0:
                                with fm_rf_figs3_col1:
                                    st.altair_chart(pd_ticks_rf + pd_chart_rf, use_container_width = True)
                            if expl_var.index(pd_var)%2 == 1:
                                with fm_rf_figs3_col2:
                                    st.altair_chart(pd_ticks_rf + pd_chart_rf, use_container_width = True)
                        # if sett_hints:
                        #     st.info(str(fc.learning_hints("mod_md_BRT_partDep")))
                        st.write("")         
                        # Further graphical output
                        fm_rf_figs4_col1, fm_rf_figs4_col2 = st.beta_columns(2)
                        with fm_rf_figs4_col1:
                            st.write("Observed vs Fitted:")
                            observed_fitted_data = pd.DataFrame()
                            observed_fitted_data["Observed"] = df[response_var]
                            observed_fitted_data["Fitted"] = model_full_results["RF fitted"]
                            observed_fitted_data["Index"] = df.index
                            observed_fitted = alt.Chart(observed_fitted_data, height = 200).mark_circle(size=20).encode(
                                x = alt.X("Fitted", title = "fitted", scale = alt.Scale(domain = [min(observed_fitted_data["Fitted"]), max(observed_fitted_data["Fitted"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Observed", title = "observed", scale = alt.Scale(zero = False), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Observed", "Fitted", "Index"]
                            )
                            observed_fitted_plot = observed_fitted + observed_fitted.transform_regression("Fitted", "Observed").mark_line(size = 2, color = "darkred")
                            st.altair_chart(observed_fitted_plot, use_container_width = True)
                        with fm_rf_figs4_col2:
                            st.write("Residuals vs Fitted:")
                            residuals_fitted_data = pd.DataFrame()
                            residuals_fitted_data["Residuals"] = model_full_results["residuals"]["Random Forest"]
                            residuals_fitted_data["Fitted"] = model_full_results["RF fitted"]
                            residuals_fitted_data["Index"] = df.index
                            residuals_fitted = alt.Chart(residuals_fitted_data, height = 200).mark_circle(size=20).encode(
                                x = alt.X("Fitted", title = "fitted", scale = alt.Scale(domain = [min(residuals_fitted_data["Fitted"]), max(residuals_fitted_data["Fitted"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Residuals", title = "residuals", scale = alt.Scale(zero = False), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Residuals", "Fitted", "Index"]
                            )
                            residuals_fitted_plot = residuals_fitted + residuals_fitted.transform_loess("Fitted", "Residuals", bandwidth = 0.5).mark_line(size = 2, color = "darkred")
                            st.altair_chart(residuals_fitted_plot, use_container_width = True) 
                        # if sett_hints:
                        #     st.info(str(fc.learning_hints("mod_md_BRT_obsResVsFit")))

                        # Download link for RF output
                        output = BytesIO()
                        excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
                        model_full_results["RF information"].to_excel(excel_file, sheet_name="regression_information")
                        rf_error_est.to_excel(excel_file, sheet_name="regression_statistics")
                        rf_varImp_table.to_excel(excel_file, sheet_name="variable_importance")
                        rf_featImp_table.to_excel(excel_file, sheet_name="feature_importance")
                        excel_file.save()
                        excel_file = output.getvalue()
                        b64 = base64.b64encode(excel_file)
                        dl_file_name = "RF full model output__" + df_name + ".xlsx"
                        st.markdown(
                            f"""
                        <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download Random Forest full model output</a>
                        """,
                        unsafe_allow_html=True)
                        st.write("")

                    # BRT specific output
                    if any(a for a in sb_ML_alg if a == "Boosted Regression Trees"):
                        st.markdown("**Boosted Regression Trees**")

                        fm_brt_reg_col1, fm_brt_reg_col2 = st.beta_columns(2)
                        # Regression information
                        with fm_brt_reg_col1:
                            st.write("Regression information:")
                            st.write(model_full_results["BRT information"])
                        # Regression statistics
                        with fm_brt_reg_col2:
                            st.write("Regression statistics:")
                            brt_error_est = pd.DataFrame(index = ["MSE", "RMSE", "MAE", "Residual SE"], columns = ["Value"])
                            brt_error_est.loc["MSE"] = model_full_results["model comparison"].loc["MSE"]["Boosted Regression Trees"]
                            brt_error_est.loc["RMSE"] = model_full_results["model comparison"].loc["RMSE"]["Boosted Regression Trees"]
                            brt_error_est.loc["MAE"] =  model_full_results["model comparison"].loc["MAE"]["Boosted Regression Trees"]
                            brt_error_est.loc["Residual SE"] = model_full_results["BRT Residual SE"]
                            st.write(brt_error_est)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_BRT_regStat")))
                        st.write("")
                        # Training score (MSE vs. number of trees)
                        st.write("Training score:")
                        train_score = pd.DataFrame(index = range(model_full_results["BRT train score"].shape[0]), columns = ["Training MSE"])
                        train_score["Training MSE"] = model_full_results["BRT train score"]
                        train_score["Trees"] = train_score.index+1
                        train_score_plot = alt.Chart(train_score, height = 200).mark_line(color = "darkred").encode(
                            x = alt.X("Trees", title = "trees", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), scale = alt.Scale(domain = [train_score["Trees"].min(), train_score["Trees"].max()])),
                            y = alt.Y("Training MSE", title = "training MSE", scale = alt.Scale(zero = False), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                            tooltip = ["Training MSE", "Trees"]
                        )     
                        st.altair_chart(train_score_plot, use_container_width = True)
                        st.write("")
                        # Variable importance (via permutation)
                        fm_brt_figs1_col1, fm_brt_figs1_col2 = st.beta_columns(2)
                        with fm_brt_figs1_col1:
                            st.write("Variable importance (via permutation):")
                            brt_varImp_table = model_full_results["BRT variable importance"]
                            st.write(brt_varImp_table)
                            st.write("")
                        with fm_brt_figs1_col2:
                            st.write("")
                            st.write("")
                            st.write("")
                            brt_varImp_plot_data = model_full_results["BRT variable importance"]
                            brt_varImp_plot_data["Variable"] = brt_varImp_plot_data.index
                            brt_varImp = alt.Chart(brt_varImp_plot_data, height = 200).mark_bar().encode(
                                x = alt.X("mean", title = "variable importance", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Variable", title = None, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), sort = None),
                                tooltip = ["Variable", "mean"]
                            )
                            st.altair_chart(brt_varImp, use_container_width = True) 
                        st.write("") 
                        fm_brt_figs2_col1, fm_brt_figs2_col2 = st.beta_columns(2)
                        # Feature importance
                        with fm_brt_figs2_col1:
                            st.write("Feature importance (impurity-based):")
                            brt_featImp_table = model_full_results["BRT feature importance"]
                            st.write(brt_featImp_table)
                            st.write("")
                        with fm_brt_figs2_col2:
                            st.write("")
                            st.write("")
                            st.write("")
                            brt_featImp_plot_data = model_full_results["BRT feature importance"]
                            brt_featImp_plot_data["Variable"] = brt_featImp_plot_data.index
                            brt_featImp = alt.Chart(brt_featImp_plot_data, height = 200).mark_bar().encode(
                                x = alt.X("Value", title = "feature importance", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Variable", title = None, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), sort = None),
                                tooltip = ["Variable", "Value"]
                            )
                            st.altair_chart(brt_featImp, use_container_width = True)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_BRT_varImp")))
                        st.write("") 
                        # Partial dependence plots
                        st.write("Partial dependence plots:")    
                        fm_brt_figs3_col1, fm_brt_figs3_col2 = st.beta_columns(2)
                        for pd_var in expl_var:
                            pd_data_brt = pd.DataFrame(columns = [pd_var])
                            pd_data_brt[pd_var] = model_full_results["BRT partial dependence"][pd_var][1][0]
                            pd_data_brt["Partial dependence"] = model_full_results["BRT partial dependence"][pd_var][0][0]
                            pd_chart_brt = alt.Chart(pd_data_brt, height = 200).mark_line(color = "darkred").encode(
                                x = alt.X(pd_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Partial dependence", title = "partial dependence", scale = alt.Scale(domain = [model_full_results["BRT partial dependence min/max"]["min"].min(), model_full_results["BRT partial dependence min/max"]["max"].max()]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Partial dependence"] + [pd_var]
                            )
                            pd_data_ticks_brt = pd.DataFrame(columns = [pd_var])
                            pd_data_ticks_brt[pd_var] = df[pd_var]
                            pd_data_ticks_brt["y"] = [model_full_results["BRT partial dependence min/max"]["min"].min()] * df.shape[0]
                            pd_ticks_brt = alt.Chart(pd_data_ticks_brt, height = 200).mark_tick(size = 5, thickness = 1).encode(
                                x = alt.X(pd_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), scale = alt.Scale(domain = [pd_data_ticks_brt[pd_var].min(), pd_data_ticks_brt[pd_var].max()])),
                                y = alt.Y("y", title = "partial dependence", scale = alt.Scale(domain = [model_full_results["BRT partial dependence min/max"]["min"].min(), model_full_results["BRT partial dependence min/max"]["max"].max()]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = [pd_var]
                            )
                            if expl_var.index(pd_var)%2 == 0:
                                with fm_brt_figs3_col1:
                                    st.altair_chart(pd_ticks_brt + pd_chart_brt, use_container_width = True)
                            if expl_var.index(pd_var)%2 == 1:
                                with fm_brt_figs3_col2:
                                    st.altair_chart(pd_ticks_brt + pd_chart_brt, use_container_width = True)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_BRT_partDep")))
                        st.write("")         
                        # Further graphical output
                        fm_brt_figs4_col1, fm_brt_figs4_col2 = st.beta_columns(2)
                        with fm_brt_figs4_col1:
                            st.write("Observed vs Fitted:")
                            observed_fitted_data = pd.DataFrame()
                            observed_fitted_data["Observed"] = df[response_var]
                            observed_fitted_data["Fitted"] = model_full_results["BRT fitted"]
                            observed_fitted_data["Index"] = df.index
                            observed_fitted = alt.Chart(observed_fitted_data, height = 200).mark_circle(size=20).encode(
                                x = alt.X("Fitted", title = "fitted", scale = alt.Scale(domain = [min(observed_fitted_data["Fitted"]), max(observed_fitted_data["Fitted"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Observed", title = "observed", scale = alt.Scale(zero = False), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Observed", "Fitted", "Index"]
                            )
                            observed_fitted_plot = observed_fitted + observed_fitted.transform_regression("Fitted", "Observed").mark_line(size = 2, color = "darkred")
                            st.altair_chart(observed_fitted_plot, use_container_width = True)
                        with fm_brt_figs4_col2:
                            st.write("Residuals vs Fitted:")
                            residuals_fitted_data = pd.DataFrame()
                            residuals_fitted_data["Residuals"] = model_full_results["residuals"]["Boosted Regression Trees"]
                            residuals_fitted_data["Fitted"] = model_full_results["BRT fitted"]
                            residuals_fitted_data["Index"] = df.index
                            residuals_fitted = alt.Chart(residuals_fitted_data, height = 200).mark_circle(size=20).encode(
                                x = alt.X("Fitted", title = "fitted", scale = alt.Scale(domain = [min(residuals_fitted_data["Fitted"]), max(residuals_fitted_data["Fitted"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Residuals", title = "residuals", scale = alt.Scale(zero = False), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Residuals", "Fitted", "Index"]
                            )
                            residuals_fitted_plot = residuals_fitted + residuals_fitted.transform_loess("Fitted", "Residuals", bandwidth = 0.5).mark_line(size = 2, color = "darkred")
                            st.altair_chart(residuals_fitted_plot, use_container_width = True) 
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_BRT_obsResVsFit")))

                        # Download link for BRT output
                        output = BytesIO()
                        excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
                        model_full_results["BRT information"].to_excel(excel_file, sheet_name="regression_information")
                        brt_error_est.to_excel(excel_file, sheet_name="regression_statistics")
                        brt_varImp_table.to_excel(excel_file, sheet_name="variable_importance")
                        brt_featImp_table.to_excel(excel_file, sheet_name="feature_importance")
                        excel_file.save()
                        excel_file = output.getvalue()
                        b64 = base64.b64encode(excel_file)
                        dl_file_name = "BRT full model output__" + df_name + ".xlsx"
                        st.markdown(
                            f"""
                        <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download Boosted Regression Trees full model output</a>
                        """,
                        unsafe_allow_html=True)
                        st.write("")

                    # ANN specific output
                    if any(a for a in sb_ML_alg if a == "Artificial Neural Networks"):
                        st.markdown("**Artificial Neural Networks**")

                        fm_ann_reg_col1, fm_ann_reg_col2 = st.beta_columns(2)
                        # Regression information
                        with fm_ann_reg_col1:
                            st.write("Regression information:")
                            st.write(model_full_results["ANN information"])
                        # Regression statistics
                        with fm_ann_reg_col2:
                            st.write("Regression statistics:")
                            ann_error_est = pd.DataFrame(index = ["MSE", "RMSE", "MAE", "Residual SE", "Best loss"], columns = ["Value"])
                            ann_error_est.loc["MSE"] = model_full_results["model comparison"].loc["MSE"]["Artificial Neural Networks"]
                            ann_error_est.loc["RMSE"] = model_full_results["model comparison"].loc["RMSE"]["Artificial Neural Networks"]
                            ann_error_est.loc["MAE"] =  model_full_results["model comparison"].loc["MAE"]["Artificial Neural Networks"]
                            ann_error_est.loc["Residual SE"] = model_full_results["ANN Residual SE"]
                            if ann_finalPara["weight optimization solver"][0] != "lbfgs":
                                ann_error_est.loc["Best loss"] = model_full_results["ANN loss"]
                            st.write(ann_error_est)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_ANN_regStat")))
                        st.write("")
                        # Loss curve (loss vs. number of iterations (epochs))
                        if ann_finalPara["weight optimization solver"][0] != "lbfgs":
                            st.write("Loss curve:")
                            loss_curve = pd.DataFrame(index = range(len(model_full_results["ANN loss curve"])), columns = ["Loss"])
                            loss_curve["Loss"] = model_full_results["ANN loss curve"]
                            loss_curve["Iterations"] = loss_curve.index+1
                            loss_curve_plot = alt.Chart(loss_curve, height = 200).mark_line(color = "darkred").encode(
                                x = alt.X("Iterations", title = "iterations (epochs)", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), scale = alt.Scale(domain = [loss_curve["Iterations"].min(), loss_curve["Iterations"].max()])),
                                y = alt.Y("Loss", title = "loss", scale = alt.Scale(zero = False), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Loss", "Iterations"]
                            )     
                            st.altair_chart(loss_curve_plot, use_container_width = True)    
                        st.write("") 
                        fm_ann_figs1_col1, fm_ann_figs1_col2 = st.beta_columns(2)
                        # Variable importance (via permutation)
                        with fm_ann_figs1_col1:
                            st.write("Variable importance (via permutation):")
                            ann_varImp_table = model_full_results["ANN variable importance"]
                            st.write(ann_varImp_table)
                            st.write("")
                        with fm_ann_figs1_col2:
                            st.write("")
                            st.write("")
                            st.write("")
                            ann_varImp_plot_data = model_full_results["ANN variable importance"]
                            ann_varImp_plot_data["Variable"] = ann_varImp_plot_data.index
                            ann_varImp = alt.Chart(ann_varImp_plot_data, height = 200).mark_bar().encode(
                                x = alt.X("mean", title = "variable importance", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Variable", title = None, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), sort = None),
                                tooltip = ["Variable", "mean"]
                            )
                            st.altair_chart(ann_varImp, use_container_width = True)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_ANN_varImp")))
                        st.write("") 
                        # Partial dependence plots
                        st.write("Partial dependence plots:")    
                        fm_ann_figs2_col1, fm_ann_figs2_col2 = st.beta_columns(2)
                        for pd_var in expl_var:
                            pd_data_ann = pd.DataFrame(columns = [pd_var])
                            pd_data_ann[pd_var] = (model_full_results["ANN partial dependence"][pd_var][1][0]*(df[pd_var].std()))+df[pd_var].mean()
                            pd_data_ann["Partial dependence"] = model_full_results["ANN partial dependence"][pd_var][0][0]
                            pd_chart_ann = alt.Chart(pd_data_ann, height = 200).mark_line(color = "darkred").encode(
                            x = alt.X(pd_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                            y = alt.Y("Partial dependence", title = "partial dependence", scale = alt.Scale(domain = [model_full_results["ANN partial dependence min/max"]["min"].min(), model_full_results["ANN partial dependence min/max"]["max"].max()]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                            tooltip = ["Partial dependence"] + [pd_var]
                            )
                            pd_data_ticks_ann = pd.DataFrame(columns = [pd_var])
                            pd_data_ticks_ann[pd_var] = df[pd_var]
                            pd_data_ticks_ann["y"] = [model_full_results["ANN partial dependence min/max"]["min"].min()] * df.shape[0]
                            pd_ticks_ann = alt.Chart(pd_data_ticks_ann, height = 200).mark_tick(size = 5, thickness = 1).encode(
                                x = alt.X(pd_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), scale = alt.Scale(domain = [pd_data_ticks_ann[pd_var].min(), pd_data_ticks_ann[pd_var].max()])),
                                y = alt.Y("y", title = "partial dependence", scale = alt.Scale(domain = [model_full_results["ANN partial dependence min/max"]["min"].min(), model_full_results["ANN partial dependence min/max"]["max"].max()]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = [pd_var]
                            )
                            if expl_var.index(pd_var)%2 == 0:
                                with fm_ann_figs2_col1:
                                    st.altair_chart(pd_ticks_ann + pd_chart_ann, use_container_width = True)
                            if expl_var.index(pd_var)%2 == 1:
                                with fm_ann_figs2_col2:
                                    st.altair_chart(pd_ticks_ann + pd_chart_ann, use_container_width = True)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_ANN_partDep")))
                        st.write("") 
                        # Further graphical output
                        fm_ann_figs3_col1, fm_ann_figs3_col2 = st.beta_columns(2)
                        with fm_ann_figs3_col1:
                            st.write("Observed vs Fitted:")
                            observed_fitted_data = pd.DataFrame()
                            observed_fitted_data["Observed"] = df[response_var]
                            observed_fitted_data["Fitted"] = model_full_results["ANN fitted"]
                            observed_fitted_data["Index"] = df.index
                            observed_fitted = alt.Chart(observed_fitted_data, height = 200).mark_circle(size=20).encode(
                                x = alt.X("Fitted", title = "fitted", scale = alt.Scale(domain = [min(observed_fitted_data["Fitted"]), max(observed_fitted_data["Fitted"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Observed", title = "observed", scale = alt.Scale(zero = False),  axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Observed", "Fitted", "Index"]
                            )
                            observed_fitted_plot = observed_fitted + observed_fitted.transform_regression("Fitted", "Observed").mark_line(size = 2, color = "darkred")
                            st.altair_chart(observed_fitted_plot, use_container_width = True)
                        with fm_ann_figs3_col2:
                            st.write("Residuals vs Fitted:")
                            residuals_fitted_data = pd.DataFrame()
                            residuals_fitted_data["Residuals"] = model_full_results["residuals"]["Artificial Neural Networks"]
                            residuals_fitted_data["Fitted"] = model_full_results["ANN fitted"]
                            residuals_fitted_data["Index"] = df.index
                            residuals_fitted = alt.Chart(residuals_fitted_data, height = 200).mark_circle(size=20).encode(
                                x = alt.X("Fitted", title = "fitted", scale = alt.Scale(domain = [min(residuals_fitted_data["Fitted"]), max(residuals_fitted_data["Fitted"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Residuals", title = "residuals", scale = alt.Scale(zero = False), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Residuals", "Fitted", "Index"]
                            )
                            residuals_fitted_plot = residuals_fitted + residuals_fitted.transform_loess("Fitted", "Residuals", bandwidth = 0.5).mark_line(size = 2, color = "darkred")
                            st.altair_chart(residuals_fitted_plot, use_container_width = True)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_ANN_obsResVsFit")))  
                        
                        # Download link for ANN output
                        output = BytesIO()
                        excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
                        model_full_results["ANN information"].to_excel(excel_file, sheet_name="regression_information")
                        ann_error_est.to_excel(excel_file, sheet_name="regression_statistics")
                        ann_varImp_table.to_excel(excel_file, sheet_name="variable_importance")
                        excel_file.save()
                        excel_file = output.getvalue()
                        b64 = base64.b64encode(excel_file)
                        dl_file_name = "ANN full model output__" + df_name + ".xlsx"
                        st.markdown(
                            f"""
                        <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download Artificial Neural Networks full model output</a>
                        """,
                        unsafe_allow_html=True)
                        st.write("") 

                    # Performance metrics across all models
                    st.markdown("**Model comparison**")
                    st.write("Performance metrics:")
                    model_comp_sort_enable = (model_full_results["model comparison"]).transpose()
                    st.write(model_comp_sort_enable)
                    if len(sb_ML_alg) > 1:
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_modCompPerf")))  
                    st.write("")
                    model_full_res = pd.DataFrame(index = ["min", "25%-Q", "median", "75%-Q", "max"], columns = sb_ML_alg)
                    for m in sb_ML_alg: 
                        model_full_res.loc["min"][m] = model_full_results["residuals"][m].min()
                        model_full_res.loc["25%-Q"][m] = model_full_results["residuals"][m].quantile(q = 0.25)
                        model_full_res.loc["median"][m] = model_full_results["residuals"][m].quantile(q = 0.5)
                        model_full_res.loc["75%-Q"][m] = model_full_results["residuals"][m].quantile(q = 0.75)
                        model_full_res.loc["max"][m] = model_full_results["residuals"][m].max()
                    st.write("Residuals distribution:")
                    st.write((model_full_res).transpose())
                    if len(sb_ML_alg) > 1:
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_modCompRes")))
                    st.write("")

                    # Download link for model comparison output
                    output = BytesIO()
                    excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
                    model_comp_sort_enable.to_excel(excel_file, sheet_name="performance_metrics")
                    model_full_res.transpose().to_excel(excel_file, sheet_name="residuals_distribution")
                    excel_file.save()
                    excel_file = output.getvalue()
                    b64 = base64.b64encode(excel_file)
                    dl_file_name = "Model comparison full model output__" + df_name + ".xlsx"
                    st.markdown(
                        f"""
                    <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download model comparison output</a>
                    """,
                    unsafe_allow_html=True)
                    st.write("")
            
                #-------------------------------------------------------------

                # Binary response variable
                if response_var_type == "binary":
                    
                    # MLR specific output
                    if any(a for a in sb_ML_alg if a == "Multiple Linear Regression"):
                        st.markdown("**Multiple Linear Regression**")
                        # Regression information
                        fm_mlr_reg_col1, fm_mlr_reg_col2 = st.beta_columns(2)
                        with fm_mlr_reg_col1:
                            st.write("Regression information:")
                            st.write(model_full_results["MLR information"])
                        # Regression statistics
                        with fm_mlr_reg_col2:
                            st.write("Regression statistics:")
                            st.write(model_full_results["MLR statistics"])
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_MLR_regStat")))
                        st.write("")
                        # Coefficients
                        st.write("Coefficients:")
                        st.write(model_full_results["MLR coefficients"])
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_MLR_coef")))
                        st.write("")
                        # ANOVA
                        st.write("ANOVA:")
                        st.write(model_full_results["MLR ANOVA"])
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_MLR_ANOVA")))
                        st.write("")
                        # Heteroskedasticity tests
                        st.write("Heteroskedasticity tests:")
                        st.write(model_full_results["MLR hetTest"])
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_MLR_hetTest")))
                        st.write("")
                        # Variable importance (via permutation)
                        fm_mlr_reg2_col1, fm_mlr_reg2_col2 = st.beta_columns(2)
                        with fm_mlr_reg2_col1: 
                            st.write("Variable importance (via permutation):")
                            mlr_varImp_table = model_full_results["MLR variable importance"]
                            st.write(mlr_varImp_table)
                            st.write("")
                        with fm_mlr_reg2_col2: 
                            st.write("")
                            st.write("")
                            st.write("")
                            mlr_varImp_plot_data = model_full_results["MLR variable importance"]
                            mlr_varImp_plot_data["Variable"] = mlr_varImp_plot_data.index
                            mlr_varImp = alt.Chart(mlr_varImp_plot_data, height = 200).mark_bar().encode(
                                x = alt.X("mean", title = "variable importance", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Variable", title = None, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), sort = None),
                                tooltip = ["Variable", "mean"]
                            )
                            st.altair_chart(mlr_varImp, use_container_width = True)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_MLR_varImp")))
                        st.write("")                                 
                        # Graphical output
                        fm_mlr_figs_col1, fm_mlr_figs_col2 = st.beta_columns(2)
                        with fm_mlr_figs_col1:
                            st.write("Observed vs Fitted:")
                            observed_fitted_data = pd.DataFrame()
                            observed_fitted_data["Observed"] = df[response_var]
                            observed_fitted_data["Fitted"] = model_full_results["MLR fitted"]
                            observed_fitted_data["Index"] = df.index
                            observed_fitted = alt.Chart(observed_fitted_data, height = 200).mark_circle(size=20).encode(
                                x = alt.X("Fitted", title = "fitted", scale = alt.Scale(domain = [min(observed_fitted_data["Fitted"]), max(observed_fitted_data["Fitted"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Observed", title = "observed", scale = alt.Scale(zero = False),  axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Observed", "Fitted", "Index"]
                            )
                            observed_fitted_plot = observed_fitted + observed_fitted.transform_regression("Fitted", "Observed").mark_line(size = 2, color = "darkred")
                            st.altair_chart(observed_fitted_plot, use_container_width = True)
                        with fm_mlr_figs_col2:
                            st.write("Residuals vs Fitted:")
                            residuals_fitted_data = pd.DataFrame()
                            residuals_fitted_data["Residuals"] = model_full_results["residuals"]["Multiple Linear Regression"]
                            residuals_fitted_data["Fitted"] = model_full_results["MLR fitted"]
                            residuals_fitted_data["Index"] = df.index
                            residuals_fitted = alt.Chart(residuals_fitted_data, height = 200).mark_circle(size=20).encode(
                                x = alt.X("Fitted", title = "fitted", scale = alt.Scale(domain = [min(residuals_fitted_data["Fitted"]), max(residuals_fitted_data["Fitted"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Residuals", title = "residuals", scale = alt.Scale(zero = False), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Residuals", "Fitted", "Index"]
                            )
                            residuals_fitted_plot = residuals_fitted + residuals_fitted.transform_loess("Fitted", "Residuals", bandwidth = 0.5).mark_line(size = 2, color = "darkred")
                            st.altair_chart(residuals_fitted_plot, use_container_width = True)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_MLR_obsResVsFit")))
                        st.write("")
                        fm_mlr_figs1_col1, fm_mlr_figs1_col2 = st.beta_columns(2)
                        with fm_mlr_figs1_col1:
                            st.write("Normal QQ-plot:")
                            residuals = model_full_results["residuals"]["Multiple Linear Regression"]
                            qq_plot_data = pd.DataFrame()
                            qq_plot_data["StandResiduals"] = (residuals - residuals.mean())/residuals.std()
                            qq_plot_data["Index"] = df.index
                            qq_plot_data = qq_plot_data.sort_values(by = ["StandResiduals"])
                            qq_plot_data["Theoretical quantiles"] = stats.probplot(residuals, dist="norm")[0][0]
                            qq_plot = alt.Chart(qq_plot_data, height = 200).mark_circle(size=20).encode(
                                x = alt.X("Theoretical quantiles", title = "theoretical quantiles", scale = alt.Scale(domain = [min(qq_plot_data["Theoretical quantiles"]), max(qq_plot_data["Theoretical quantiles"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("StandResiduals", title = "stand. residuals", scale = alt.Scale(zero = False), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["StandResiduals", "Theoretical quantiles", "Index"]
                            )
                            line = alt.Chart(
                                pd.DataFrame({"Theoretical quantiles": [min(qq_plot_data["Theoretical quantiles"]), max(qq_plot_data["Theoretical quantiles"])], "StandResiduals": [min(qq_plot_data["Theoretical quantiles"]), max(qq_plot_data["Theoretical quantiles"])]})).mark_line(size = 2, color = "darkred").encode(
                                        alt.X("Theoretical quantiles"),
                                        alt.Y("StandResiduals"),
                            )
                            st.altair_chart(qq_plot + line, use_container_width = True)
                            if sett_hints:
                                st.info(str(fc.learning_hints("mod_md_MLR_qqplot")))
                        with fm_mlr_figs1_col2:
                            st.write("Scale-Location:")
                            scale_location_data = pd.DataFrame()
                            residuals = model_full_results["residuals"]["Multiple Linear Regression"]
                            scale_location_data["SqrtStandResiduals"] = np.sqrt(abs((residuals - residuals.mean())/residuals.std()))
                            scale_location_data["Fitted"] = model_full_results["MLR fitted"]
                            scale_location_data["Index"] = df.index
                            scale_location = alt.Chart(scale_location_data, height = 200).mark_circle(size=20).encode(
                                x = alt.X("Fitted", title = "fitted", scale = alt.Scale(domain = [min(scale_location_data["Fitted"]), max(scale_location_data["Fitted"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("SqrtStandResiduals", title = "sqrt(|stand. residuals|)", scale = alt.Scale(zero = False), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["SqrtStandResiduals", "Fitted", "Index"]
                            )
                            scale_location_plot = scale_location + scale_location.transform_loess("Fitted", "SqrtStandResiduals", bandwidth = 0.5).mark_line(size = 2, color = "darkred")
                            st.altair_chart(scale_location_plot, use_container_width = True)
                            if sett_hints:
                                st.info(str(fc.learning_hints("mod_md_MLR_scaleLoc")))
                        st.write("")
                        fm_mlr_figs2_col1, fm_mlr_figs2_col2 = st.beta_columns(2)
                        with fm_mlr_figs2_col1:
                            st.write("Residuals vs Leverage:")
                            residuals_leverage_data = pd.DataFrame()
                            residuals = model_full_results["residuals"]["Multiple Linear Regression"]
                            residuals_leverage_data["StandResiduals"] = (residuals - residuals.mean())/residuals.std()
                            residuals_leverage_data["Leverage"] = model_full_results["MLR leverage"]
                            residuals_leverage_data["Index"] = df.index
                            residuals_leverage = alt.Chart(residuals_leverage_data, height = 200).mark_circle(size=20).encode(
                                x = alt.X("Leverage", title = "leverage", scale = alt.Scale(domain = [min(residuals_leverage_data["Leverage"]), max(residuals_leverage_data["Leverage"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("StandResiduals", title = "stand. residuals", scale = alt.Scale(zero = False), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["StandResiduals","Leverage", "Index"]
                            )
                            residuals_leverage_plot = residuals_leverage + residuals_leverage.transform_loess("Leverage", "StandResiduals", bandwidth = 0.5).mark_line(size = 2, color = "darkred")
                            st.altair_chart(residuals_leverage_plot, use_container_width = True)
                        with fm_mlr_figs2_col2:
                            st.write("Cook's distance:")
                            cooksD_data = pd.DataFrame()
                            cooksD_data["CooksD"] = model_full_results["MLR Cooks distance"]
                            cooksD_data["Index"] = df.index
                            cooksD = alt.Chart(cooksD_data, height = 200).mark_bar(size = 2).encode(
                                x = alt.X("Index", title = "index", scale = alt.Scale(domain = [-1, max(cooksD_data["Index"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("CooksD", title = "Cook's distance", scale = alt.Scale(zero = False), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["CooksD", "Index"]
                            )
                            st.altair_chart(cooksD, use_container_width = True)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_MLR_resVsLev_cooksD")))
                        
                        # Download link for MLR output
                        output = BytesIO()
                        excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
                        model_full_results["MLR information"].to_excel(excel_file, sheet_name="regression_information")
                        model_full_results["MLR statistics"].to_excel(excel_file, sheet_name="regression_statistics")
                        model_full_results["MLR coefficients"].to_excel(excel_file, sheet_name="coefficients")
                        model_full_results["MLR ANOVA"].to_excel(excel_file, sheet_name="ANOVA")
                        model_full_results["MLR hetTest"].to_excel(excel_file, sheet_name="heteroskedasticity_tests")
                        mlr_varImp_table.to_excel(excel_file, sheet_name="variable_importance")
                        excel_file.save()
                        excel_file = output.getvalue()
                        b64 = base64.b64encode(excel_file)
                        dl_file_name = "MLR full model output__" + df_name + ".xlsx"
                        st.markdown(
                            f"""
                        <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download Multiple Linear Regression full model output</a>
                        """,
                        unsafe_allow_html=True)
                        st.write("") 
                    
                    # LR specific output
                    if any(a for a in sb_ML_alg if a == "Logistic Regression"):
                        st.markdown("**Logistic Regression**")
                        # Regression information
                        fm_lr_reg_col1, fm_lr_reg_col2 = st.beta_columns(2)
                        with fm_lr_reg_col1:
                            st.write("Regression information:")
                            st.write(model_full_results["LR information"])
                        # Regression statistics
                        with fm_lr_reg_col2:
                            st.write("Regression statistics:")
                            st.write(model_full_results["LR statistics"])
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_LR_regStat")))
                        st.write("")  
                        # Coefficients
                        st.write("Coefficients:")
                        st.write(model_full_results["LR coefficients"])
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_LR_coef")))
                        st.write("")
                        # Variable importance (via permutation)
                        fm_lr_fig1_col1, fm_lr_fig1_col2 = st.beta_columns(2)
                        with fm_lr_fig1_col1: 
                            st.write("Variable importance (via permutation):")
                            lr_varImp_table = model_full_results["LR variable importance"]
                            st.write(lr_varImp_table)
                        with fm_lr_fig1_col2: 
                            st.write("")
                            st.write("")
                            st.write("")
                            lr_varImp_plot_data = model_full_results["LR variable importance"]
                            lr_varImp_plot_data["Variable"] = lr_varImp_plot_data.index
                            lr_varImp = alt.Chart(lr_varImp_plot_data, height = 200).mark_bar().encode(
                                x = alt.X("mean", title = "variable importance", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Variable", title = None, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), sort = None),
                                tooltip = ["Variable", "mean"]
                            )
                            st.altair_chart(lr_varImp, use_container_width = True)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_LR_varImp"))) 
                        st.write("") 
                        fm_lr_fig_col1, fm_lr_fig_col2 = st.beta_columns(2)
                        # Observed vs. Probability of Occurrence 
                        with fm_lr_fig_col1:
                            st.write("Observed vs. Probability of Occurrence:")
                            prob_data = pd.DataFrame(model_full_results["LR fitted"])
                            prob_data["Observed"] = df[response_var]
                            prob_data["ProbabilityOfOccurrence"] = prob_data[1]
                            prob_data["Threshold"] = model_full_results["model comparison thres"].loc["threshold"]["Logistic Regression"]
                            prob_data_plot = alt.Chart(prob_data, height = 200).mark_tick(size = 5, thickness = 1).encode(
                                x = alt.X("ProbabilityOfOccurrence", title = "probability of occurrence", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Observed", title = "observed", scale = alt.Scale(domain = [min(prob_data["Observed"]), max(prob_data["Observed"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Observed", "ProbabilityOfOccurrence", "Threshold"]
                            )
                            thres = alt.Chart(prob_data, height = 200).mark_rule(size = 2, color = "darkred").encode(x = "Threshold", tooltip = ["Threshold"]) 
                            prob_plot = prob_data_plot + thres
                            st.altair_chart(prob_plot, use_container_width = True)
                        # ROC curve 
                        with fm_lr_fig_col2:
                            st.write("ROC curve:")
                            AUC_ROC_data = pd.DataFrame()
                            AUC_ROC_data["FPR"] = model_full_results["LR ROC curve"][0]
                            AUC_ROC_data["TPR"] = model_full_results["LR ROC curve"][1]
                            AUC_ROC_data["AUC ROC"] = model_full_results["model comparison thresInd"].loc["AUC ROC"]["Logistic Regression"]
                            AUC_ROC_data["Threshold"] = model_full_results["model comparison thres"].loc["threshold"]["Logistic Regression"]
                            AUC_ROC_plot= alt.Chart(AUC_ROC_data, height = 200).mark_line().encode(
                                x = alt.X("FPR", title = "1 - specificity (FPR)", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("TPR", title = "sensitivity (TPR)", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["TPR", "FPR", "AUC ROC"]
                            )
                            line = alt.Chart(
                                pd.DataFrame({"FPR": [min(AUC_ROC_data["FPR"]), max(AUC_ROC_data["FPR"])], "TPR": [min(AUC_ROC_data["FPR"]), max(AUC_ROC_data["FPR"])]})).mark_line(size = 2, color = "darkred").encode(
                                        alt.X("FPR"),
                                        alt.Y("TPR"),
                            )
                            st.altair_chart(AUC_ROC_plot + line, use_container_width = True)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_LR_thresAUC"))) 
                        st.write("") 
                        # Partial probabilities
                        st.write("Partial probability plots:")    
                        fm_lr_figs2_col1, fm_lr_figs2_col2 = st.beta_columns(2)
                        for pp_var in expl_var:
                            pp_data = pd.DataFrame(columns = [pp_var])
                            pp_data[pp_var] = model_full_results["LR partial probabilities"][pp_var][pp_var]
                            pp_data["ProbabilityOfOccurrence"] = model_full_results["LR partial probabilities"][pp_var]["prediction"]
                            pp_data["Observed"] = df[response_var]
                            pp_chart = alt.Chart(pp_data, height = 200).mark_line(color = "darkred").encode(
                            x = alt.X(pp_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                            y = alt.Y("ProbabilityOfOccurrence", title = "probability of occurrence", scale = alt.Scale(domain = [0, 1]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                            tooltip = ["ProbabilityOfOccurrence"] + [pp_var]
                            )
                            obs_data_plot = alt.Chart(pp_data, height = 200).mark_tick(size = 5, thickness = 1).encode(
                                x = alt.X(pp_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Observed", title = "probability of occurrence", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Observed", "ProbabilityOfOccurrence"] + [pp_var]
                            )
                            if expl_var.index(pp_var)%2 == 0:
                                with fm_lr_figs2_col1:
                                    st.altair_chart(pp_chart + obs_data_plot, use_container_width = True)
                            if expl_var.index(pp_var)%2 == 1:
                                with fm_lr_figs2_col2:
                                    st.altair_chart(pp_chart + obs_data_plot, use_container_width = True)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_LR_partProb"))) 

                        # Download link for LR output
                        output = BytesIO()
                        excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
                        model_full_results["LR information"].to_excel(excel_file, sheet_name="regression_information")
                        model_full_results["LR statistics"].to_excel(excel_file, sheet_name="regression_statistics")
                        model_full_results["LR coefficients"].to_excel(excel_file, sheet_name="coefficients")
                        lr_varImp_table.to_excel(excel_file, sheet_name="variable_importance")
                        excel_file.save()
                        excel_file = output.getvalue()
                        b64 = base64.b64encode(excel_file)
                        dl_file_name = "LR full model output__" + df_name + ".xlsx"
                        st.markdown(
                            f"""
                        <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download Logistic Regression full model output</a>
                        """,
                        unsafe_allow_html=True)
                        st.write("")

                    # GAM specific output
                    if any(a for a in sb_ML_alg if a == "Generalized Additive Models"):
                        st.markdown("**Generalized Additive Models**")

                        fm_gam_reg_col1, fm_gam_reg_col2 = st.beta_columns(2)
                        # Regression information
                        with fm_gam_reg_col1:
                            st.write("Regression information:")
                            st.write(model_full_results["GAM information"])
                        # Regression statistics
                        with fm_gam_reg_col2:
                            st.write("Regression statistics:")
                            st.write(model_full_results["GAM statistics"])
                        # if sett_hints:
                        #     st.info(str(fc.learning_hints("mod_md_BRT_regStat")))
                        st.write("")
                        # Feature significance
                        st.write("Feature significance:")
                        st.write(model_full_results["GAM feature significance"])
                        # if sett_hints:
                        #     st.info(str(fc.learning_hints("mod_md_MLR_coef")))
                        st.write("")
                        # Variable importance (via permutation)
                        fm_gam_figs1_col1, fm_gam_figs1_col2 = st.beta_columns(2)
                        with fm_gam_figs1_col1:
                            st.write("Variable importance (via permutation):")
                            gam_varImp_table = model_full_results["GAM variable importance"]
                            st.write(gam_varImp_table)
                            st.write("")
                        with fm_gam_figs1_col2:
                            st.write("")
                            st.write("")
                            st.write("")
                            gam_varImp_plot_data = model_full_results["GAM variable importance"]
                            gam_varImp_plot_data["Variable"] = gam_varImp_plot_data.index
                            gam_varImp = alt.Chart(gam_varImp_plot_data, height = 200).mark_bar().encode(
                                x = alt.X("mean", title = "variable importance", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Variable", title = None, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), sort = None),
                                tooltip = ["Variable", "mean"]
                            )
                            st.altair_chart(gam_varImp, use_container_width = True) 
                        st.write("")
                        # Observed vs. Probability of Occurrence
                        fm_gam_figs5_col1, fm_gam_figs5_col2 = st.beta_columns(2) 
                        with fm_gam_figs5_col1:
                            st.write("Observed vs. Probability of Occurrence:")
                            prob_data = pd.DataFrame(model_full_results["GAM fitted"])
                            prob_data["Observed"] = df[response_var]
                            prob_data["ProbabilityOfOccurrence"] = prob_data[0]
                            prob_data["Threshold"] = model_full_results["model comparison thres"].loc["threshold"]["Generalized Additive Models"]
                            prob_data_plot = alt.Chart(prob_data, height = 200).mark_tick(size = 5, thickness = 1).encode(
                                x = alt.X("ProbabilityOfOccurrence", title = "probability of occurrence", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Observed", title = "observed", scale = alt.Scale(domain = [min(prob_data["Observed"]), max(prob_data["Observed"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Observed", "ProbabilityOfOccurrence", "Threshold"]
                            )
                            thres = alt.Chart(prob_data, height = 200).mark_rule(size = 1.5, color = "darkred").encode(x = "Threshold", tooltip = ["Threshold"]) 
                            prob_plot = prob_data_plot + thres
                            st.altair_chart(prob_plot, use_container_width = True)
                        # ROC curve 
                        with fm_gam_figs5_col2:
                            st.write("ROC curve:")
                            AUC_ROC_data = pd.DataFrame()
                            AUC_ROC_data["FPR"] = model_full_results["GAM ROC curve"][0]
                            AUC_ROC_data["TPR"] = model_full_results["GAM ROC curve"][1]
                            AUC_ROC_data["AUC ROC"] = model_full_results["model comparison thresInd"].loc["AUC ROC"]["Generalized Additive Models"]
                            AUC_ROC_data["Threshold"] = model_full_results["model comparison thres"].loc["threshold"]["Generalized Additive Models"]
                            AUC_ROC_plot= alt.Chart(AUC_ROC_data, height = 200).mark_line().encode(
                                x = alt.X("FPR", title = "1 - specificity (FPR)", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("TPR", title = "sensitivity (TPR)", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["TPR", "FPR", "AUC ROC"]
                            )
                            line = alt.Chart(
                                pd.DataFrame({"FPR": [min(AUC_ROC_data["FPR"]), max(AUC_ROC_data["FPR"])], "TPR": [min(AUC_ROC_data["FPR"]), max(AUC_ROC_data["FPR"])]})).mark_line(size = 2, color = "darkred").encode(
                                        alt.X("FPR"),
                                        alt.Y("TPR"),
                            )
                            st.altair_chart(AUC_ROC_plot + line, use_container_width = True)
                        # if sett_hints:
                        #     st.info(str(fc.learning_hints("mod_md_BRT_thresAUC")))
                        st.write("")  
                        # Partial dependence plots
                        st.write("Partial dependence plots:")    
                        fm_gam_figs3_col1, fm_gam_figs3_col2 = st.beta_columns(2)
                        for pd_var in expl_var:
                            pd_data_gam = pd.DataFrame(columns = [pd_var])
                            pd_data_gam[pd_var] = model_full_results["GAM partial dependence"][pd_var]["x_values"]
                            pd_data_gam["Partial dependence"] = model_full_results["GAM partial dependence"][pd_var]["pd_values"]
                            pd_data_gam["Lower 95%"] = model_full_results["GAM partial dependence"][pd_var]["lower_95"]
                            pd_data_gam["Upper 95%"] = model_full_results["GAM partial dependence"][pd_var]["upper_95"]
                            pd_chart_gam = alt.Chart(pd_data_gam, height = 200).mark_line(color = "darkred").encode(
                                x = alt.X(pd_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Partial dependence", title = "partial dependence", scale = alt.Scale(domain = [model_full_results["GAM partial dependence min/max"]["min"].min(), model_full_results["GAM partial dependence min/max"]["max"].max()]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Upper 95%", "Partial dependence", "Lower 95%"] + [pd_var]
                            )
                            pd_data_ticks_gam = pd.DataFrame(columns = [pd_var])
                            pd_data_ticks_gam[pd_var] = df[pd_var]
                            pd_data_ticks_gam["y"] = [model_full_results["GAM partial dependence min/max"]["min"].min()] * df.shape[0]
                            pd_ticks_gam = alt.Chart(pd_data_ticks_gam, height = 200).mark_tick(size = 5, thickness = 1).encode(
                                x = alt.X(pd_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), scale = alt.Scale(domain = [pd_data_ticks_gam[pd_var].min(), pd_data_ticks_gam[pd_var].max()])),
                                y = alt.Y("y", title = "partial dependence", scale = alt.Scale(domain = [model_full_results["GAM partial dependence min/max"]["min"].min(), model_full_results["GAM partial dependence min/max"]["max"].max()]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = [pd_var]
                            )
                            pd_data_gam_lower = pd.DataFrame(columns = [pd_var])
                            pd_data_gam_lower[pd_var] = model_full_results["GAM partial dependence"][pd_var]["x_values"]
                            pd_data_gam_lower["Lower 95%"] = model_full_results["GAM partial dependence"][pd_var]["lower_95"]
                            pd_chart_gam_lower = alt.Chart(pd_data_gam_lower, height = 200).mark_line(strokeDash=[1,1], color = "darkred").encode(
                                x = alt.X(pd_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Lower 95%", title = "", scale = alt.Scale(domain = [model_full_results["GAM partial dependence min/max"]["min"].min(), model_full_results["GAM partial dependence min/max"]["max"].max()]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Lower 95%"] + [pd_var]
                            )
                            pd_data_gam_upper = pd.DataFrame(columns = [pd_var])
                            pd_data_gam_upper[pd_var] = model_full_results["GAM partial dependence"][pd_var]["x_values"]
                            pd_data_gam_upper["Upper 95%"] = model_full_results["GAM partial dependence"][pd_var]["upper_95"]
                            pd_chart_gam_upper = alt.Chart(pd_data_gam_upper, height = 200).mark_line(strokeDash=[1,1], color = "darkred").encode(
                                x = alt.X(pd_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Upper 95%", title = "", scale = alt.Scale(domain = [model_full_results["GAM partial dependence min/max"]["min"].min(), model_full_results["GAM partial dependence min/max"]["max"].max()]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Upper 95%"] + [pd_var]
                            )
                            if expl_var.index(pd_var)%2 == 0:
                                with fm_gam_figs3_col1:
                                    st.altair_chart(pd_ticks_gam + pd_chart_gam_lower + pd_chart_gam_upper + pd_chart_gam, use_container_width = True)
                            if expl_var.index(pd_var)%2 == 1:
                                with fm_gam_figs3_col2:
                                    st.altair_chart(pd_ticks_gam + pd_chart_gam_lower + pd_chart_gam_upper + pd_chart_gam, use_container_width = True)
                        # if sett_hints:
                        #     st.info(str(fc.learning_hints("mod_md_BRT_partDep")))
                        st.write("")                                 

                        # Download link for GAM output
                        output = BytesIO()
                        excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
                        model_full_results["GAM information"].to_excel(excel_file, sheet_name="regression_information")
                        model_full_results["GAM statistics"].to_excel(excel_file, sheet_name="regression_statistics")
                        model_full_results["GAM feature significance"].to_excel(excel_file, sheet_name="feature_significance")
                        gam_varImp_table.to_excel(excel_file, sheet_name="variable_importance")
                        excel_file.save()
                        excel_file = output.getvalue()
                        b64 = base64.b64encode(excel_file)
                        dl_file_name = "GAM full model output__" + df_name + ".xlsx"
                        st.markdown(
                            f"""
                        <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download Generalized Additive Models full model output</a>
                        """,
                        unsafe_allow_html=True)
                        st.write("")

                    # RF specific output
                    if any(a for a in sb_ML_alg if a == "Random Forest"):
                        st.markdown("**Random Forest**")
                        
                        fm_rf_reg_col1, fm_rf_reg_col2 = st.beta_columns(2)
                        # Regression information
                        with fm_rf_reg_col1:
                            st.write("Regression information:")
                            st.write(model_full_results["RF information"])
                        # Regression statistics
                        with fm_rf_reg_col2:
                            st.write("Regression statistics:")
                            rf_error_est = pd.DataFrame(index = ["AUC ROC", "AP", "AUC PRC", "LOG-LOSS"], columns = ["Value"])
                            rf_error_est.loc["AUC ROC"] = model_full_results["model comparison thresInd"].loc["AUC ROC"]["Random Forest"]
                            rf_error_est.loc["AP"] = model_full_results["model comparison thresInd"].loc["AP"]["Random Forest"]
                            rf_error_est.loc["AUC PRC"] =  model_full_results["model comparison thresInd"].loc["AUC PRC"]["Random Forest"]
                            rf_error_est.loc["LOG-LOSS"] = model_full_results["model comparison thresInd"].loc["LOG-LOSS"]["Random Forest"]
                            st.write(rf_error_est)
                        # if sett_hints:
                        #     st.info(str(fc.learning_hints("mod_md_BRT_regStat_bin"))) 
                        st.write("")
                        fm_rf_figs1_col1, fm_rf_figs1_col2 = st.beta_columns(2)
                        # Variable importance (via permutation)
                        with fm_rf_figs1_col1:
                            st.write("Variable importance (via permutation):")
                            rf_varImp_table = model_full_results["RF variable importance"]
                            st.write(rf_varImp_table)
                            st.write("")
                        with fm_rf_figs1_col2:
                            st.write("")
                            st.write("")
                            st.write("")
                            rf_varImp_plot_data = model_full_results["RF variable importance"]
                            rf_varImp_plot_data["Variable"] = rf_varImp_plot_data.index
                            rf_varImp = alt.Chart(rf_varImp_plot_data, height = 200).mark_bar().encode(
                                x = alt.X("mean", title = "variable importance", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Variable", title = None, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), sort = None),
                                tooltip = ["Variable", "mean"]
                            )
                            st.altair_chart(rf_varImp, use_container_width = True) 
                        st.write("") 
                        fm_rf_figs2_col1, fm_rf_figs2_col2 = st.beta_columns(2)
                        # Feature importance
                        with fm_rf_figs2_col1:
                            st.write("Feature importance (impurity-based):")
                            rf_featImp_table = model_full_results["RF feature importance"]
                            st.write(rf_featImp_table)
                        with fm_rf_figs2_col2:
                            st.write("")
                            st.write("")
                            st.write("")
                            rf_featImp_plot_data = model_full_results["RF feature importance"]
                            rf_featImp_plot_data["Variable"] = rf_featImp_plot_data.index
                            rf_featImp = alt.Chart(rf_featImp_plot_data, height = 200).mark_bar().encode(
                                x = alt.X("Value", title = "feature importance", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Variable", title = None, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), sort = None),
                                tooltip = ["Variable", "Value"]
                            )
                            st.altair_chart(rf_featImp, use_container_width = True)
                        # if sett_hints:
                        #     st.info(str(fc.learning_hints("mod_md_BRT_varImp_bin"))) 
                        st.write("") 
                        fm_rf_figs5_col1, fm_rf_figs5_col2 = st.beta_columns(2)
                        # Observed vs. Probability of Occurrence 
                        with fm_rf_figs5_col1:
                            st.write("Observed vs. Probability of Occurrence:")
                            prob_data = pd.DataFrame(model_full_results["RF fitted"])
                            prob_data["Observed"] = df[response_var]
                            prob_data["ProbabilityOfOccurrence"] = prob_data[1]
                            prob_data["Threshold"] = model_full_results["model comparison thres"].loc["threshold"]["Random Forest"]
                            prob_data_plot = alt.Chart(prob_data, height = 200).mark_tick(size = 5, thickness = 1).encode(
                                x = alt.X("ProbabilityOfOccurrence", title = "probability of occurrence", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Observed", title = "observed", scale = alt.Scale(domain = [min(prob_data["Observed"]), max(prob_data["Observed"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Observed", "ProbabilityOfOccurrence", "Threshold"]
                            )
                            thres = alt.Chart(prob_data, height = 200).mark_rule(size = 1.5, color = "darkred").encode(x = "Threshold", tooltip = ["Threshold"]) 
                            prob_plot = prob_data_plot + thres
                            st.altair_chart(prob_plot, use_container_width = True)
                        # ROC curve 
                        with fm_rf_figs5_col2:
                            st.write("ROC curve:")
                            AUC_ROC_data = pd.DataFrame()
                            AUC_ROC_data["FPR"] = model_full_results["RF ROC curve"][0]
                            AUC_ROC_data["TPR"] = model_full_results["RF ROC curve"][1]
                            AUC_ROC_data["AUC ROC"] = model_full_results["model comparison thresInd"].loc["AUC ROC"]["Random Forest"]
                            AUC_ROC_data["Threshold"] = model_full_results["model comparison thres"].loc["threshold"]["Random Forest"]
                            AUC_ROC_plot= alt.Chart(AUC_ROC_data, height = 200).mark_line().encode(
                                x = alt.X("FPR", title = "1 - specificity (FPR)", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("TPR", title = "sensitivity (TPR)", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["TPR", "FPR", "AUC ROC"]
                            )
                            line = alt.Chart(
                                pd.DataFrame({"FPR": [min(AUC_ROC_data["FPR"]), max(AUC_ROC_data["FPR"])], "TPR": [min(AUC_ROC_data["FPR"]), max(AUC_ROC_data["FPR"])]})).mark_line(size = 2, color = "darkred").encode(
                                        alt.X("FPR"),
                                        alt.Y("TPR"),
                            )
                            st.altair_chart(AUC_ROC_plot + line, use_container_width = True)
                        # if sett_hints:
                        #     st.info(str(fc.learning_hints("mod_md_BRT_thresAUC")))
                        st.write("") 
                        # Partial dependence plots
                        st.write("Partial dependence plots:")    
                        fm_rf_figs3_col1, fm_rf_figs3_col2 = st.beta_columns(2)
                        for pd_var in expl_var:
                            pd_data_rf = pd.DataFrame(columns = [pd_var])
                            pd_data_rf[pd_var] = model_full_results["RF partial dependence"][pd_var][1][0]
                            pd_data_rf["Partial dependence"] = model_full_results["RF partial dependence"][pd_var][0][0]
                            pd_chart_rf = alt.Chart(pd_data_rf, height = 200).mark_line(color = "darkred").encode(
                                x = alt.X(pd_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Partial dependence", title = "partial dependence", scale = alt.Scale(domain = [model_full_results["RF partial dependence min/max"]["min"].min(), model_full_results["RF partial dependence min/max"]["max"].max()]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Partial dependence"] + [pd_var]
                            )
                            pd_data_ticks_rf = pd.DataFrame(columns = [pd_var])
                            pd_data_ticks_rf[pd_var] = df[pd_var]
                            pd_data_ticks_rf["y"] = [model_full_results["RF partial dependence min/max"]["min"].min()] * df.shape[0]
                            pd_ticks_rf = alt.Chart(pd_data_ticks_rf, height = 200).mark_tick(size = 5, thickness = 1).encode(
                                x = alt.X(pd_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), scale = alt.Scale(domain = [pd_data_ticks_rf[pd_var].min(), pd_data_ticks_rf[pd_var].max()])),
                                y = alt.Y("y", title = "partial dependence", scale = alt.Scale(domain = [model_full_results["RF partial dependence min/max"]["min"].min(), model_full_results["RF partial dependence min/max"]["max"].max()]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = [pd_var]
                            )
                            if expl_var.index(pd_var)%2 == 0:
                                with fm_rf_figs3_col1:
                                    st.altair_chart(pd_ticks_rf + pd_chart_rf, use_container_width = True)
                            if expl_var.index(pd_var)%2 == 1:
                                with fm_rf_figs3_col2:
                                    st.altair_chart(pd_ticks_rf + pd_chart_rf, use_container_width = True)
                        # if sett_hints:
                        #     st.info(str(fc.learning_hints("mod_md_BRT_partDep_bin")))

                        # Download link for RF output
                        output = BytesIO()
                        excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
                        model_full_results["RF information"].to_excel(excel_file, sheet_name="regression_information")
                        rf_error_est.to_excel(excel_file, sheet_name="regression_statistics")
                        rf_varImp_table.to_excel(excel_file, sheet_name="variable_importance")
                        rf_featImp_table.to_excel(excel_file, sheet_name="feature_importance")
                        excel_file.save()
                        excel_file = output.getvalue()
                        b64 = base64.b64encode(excel_file)
                        dl_file_name = "RF full model output__" + df_name + ".xlsx"
                        st.markdown(
                            f"""
                        <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download Random Forest full model output</a>
                        """,
                        unsafe_allow_html=True)
                        st.write("")

                    # BRT specific output
                    if any(a for a in sb_ML_alg if a == "Boosted Regression Trees"):
                        st.markdown("**Boosted Regression Trees**")
                        
                        fm_brt_reg_col1, fm_brt_reg_col2 = st.beta_columns(2)
                        # Regression information
                        with fm_brt_reg_col1:
                            st.write("Regression information:")
                            st.write(model_full_results["BRT information"])
                        # Regression statistics
                        with fm_brt_reg_col2:
                            st.write("Regression statistics:")
                            brt_error_est = pd.DataFrame(index = ["AUC ROC", "AP", "AUC PRC", "LOG-LOSS"], columns = ["Value"])
                            brt_error_est.loc["AUC ROC"] = model_full_results["model comparison thresInd"].loc["AUC ROC"]["Boosted Regression Trees"]
                            brt_error_est.loc["AP"] = model_full_results["model comparison thresInd"].loc["AP"]["Boosted Regression Trees"]
                            brt_error_est.loc["AUC PRC"] =  model_full_results["model comparison thresInd"].loc["AUC PRC"]["Boosted Regression Trees"]
                            brt_error_est.loc["LOG-LOSS"] = model_full_results["model comparison thresInd"].loc["LOG-LOSS"]["Boosted Regression Trees"]
                            st.write(brt_error_est)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_BRT_regStat_bin"))) 
                        st.write("")
                        # Training score (deviance vs. number of trees)
                        st.write("Training score:")
                        train_score = pd.DataFrame(index = range(model_full_results["BRT train score"].shape[0]), columns = ["Training deviance"])
                        train_score["Training deviance"] = model_full_results["BRT train score"]
                        train_score["Trees"] = train_score.index+1
                        train_score_plot = alt.Chart(train_score, height = 200).mark_line(color = "darkred").encode(
                            x = alt.X("Trees", title = "trees", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), scale = alt.Scale(domain = [train_score["Trees"].min(), train_score["Trees"].max()])),
                            y = alt.Y("Training deviance", title = "training deviance", scale = alt.Scale(zero = False), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                            tooltip = ["Training deviance", "Trees"]
                        )     
                        st.altair_chart(train_score_plot, use_container_width = True)
                        st.write("") 

                        fm_brt_figs1_col1, fm_brt_figs1_col2 = st.beta_columns(2)
                        # Variable importance (via permutation)
                        with fm_brt_figs1_col1:
                            st.write("Variable importance (via permutation):")
                            brt_varImp_table = model_full_results["BRT variable importance"]
                            st.write(brt_varImp_table)
                            st.write("")
                        with fm_brt_figs1_col2:
                            st.write("")
                            st.write("")
                            st.write("")
                            brt_varImp_plot_data = model_full_results["BRT variable importance"]
                            brt_varImp_plot_data["Variable"] = brt_varImp_plot_data.index
                            brt_varImp = alt.Chart(brt_varImp_plot_data, height = 200).mark_bar().encode(
                                x = alt.X("mean", title = "variable importance", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Variable", title = None, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), sort = None),
                                tooltip = ["Variable", "mean"]
                            )
                            st.altair_chart(brt_varImp, use_container_width = True) 
                        st.write("") 
                        fm_brt_figs2_col1, fm_brt_figs2_col2 = st.beta_columns(2)
                        # Feature importance
                        with fm_brt_figs2_col1:
                            st.write("Feature importance (impurity-based):")
                            brt_featImp_table = model_full_results["BRT feature importance"]
                            st.write(brt_featImp_table)
                        with fm_brt_figs2_col2:
                            st.write("")
                            st.write("")
                            st.write("")
                            brt_featImp_plot_data = model_full_results["BRT feature importance"]
                            brt_featImp_plot_data["Variable"] = brt_featImp_plot_data.index
                            brt_featImp = alt.Chart(brt_featImp_plot_data, height = 200).mark_bar().encode(
                                x = alt.X("Value", title = "feature importance", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Variable", title = None, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), sort = None),
                                tooltip = ["Variable", "Value"]
                            )
                            st.altair_chart(brt_featImp, use_container_width = True)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_BRT_varImp_bin"))) 
                        st.write("") 
                        fm_brt_figs5_col1, fm_brt_figs5_col2 = st.beta_columns(2)
                        # Observed vs. Probability of Occurrence 
                        with fm_brt_figs5_col1:
                            st.write("Observed vs. Probability of Occurrence:")
                            prob_data = pd.DataFrame(model_full_results["BRT fitted"])
                            prob_data["Observed"] = df[response_var]
                            prob_data["ProbabilityOfOccurrence"] = prob_data[1]
                            prob_data["Threshold"] = model_full_results["model comparison thres"].loc["threshold"]["Boosted Regression Trees"]
                            prob_data_plot = alt.Chart(prob_data, height = 200).mark_tick(size = 5, thickness = 1).encode(
                                x = alt.X("ProbabilityOfOccurrence", title = "probability of occurrence", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Observed", title = "observed", scale = alt.Scale(domain = [min(prob_data["Observed"]), max(prob_data["Observed"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Observed", "ProbabilityOfOccurrence", "Threshold"]
                            )
                            thres = alt.Chart(prob_data, height = 200).mark_rule(size = 1.5, color = "darkred").encode(x = "Threshold", tooltip = ["Threshold"]) 
                            prob_plot = prob_data_plot + thres
                            st.altair_chart(prob_plot, use_container_width = True)
                        # ROC curve 
                        with fm_brt_figs5_col2:
                            st.write("ROC curve:")
                            AUC_ROC_data = pd.DataFrame()
                            AUC_ROC_data["FPR"] = model_full_results["BRT ROC curve"][0]
                            AUC_ROC_data["TPR"] = model_full_results["BRT ROC curve"][1]
                            AUC_ROC_data["AUC ROC"] = model_full_results["model comparison thresInd"].loc["AUC ROC"]["Boosted Regression Trees"]
                            AUC_ROC_data["Threshold"] = model_full_results["model comparison thres"].loc["threshold"]["Boosted Regression Trees"]
                            AUC_ROC_plot= alt.Chart(AUC_ROC_data, height = 200).mark_line().encode(
                                x = alt.X("FPR", title = "1 - specificity (FPR)", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("TPR", title = "sensitivity (TPR)", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["TPR", "FPR", "AUC ROC"]
                            )
                            line = alt.Chart(
                                pd.DataFrame({"FPR": [min(AUC_ROC_data["FPR"]), max(AUC_ROC_data["FPR"])], "TPR": [min(AUC_ROC_data["FPR"]), max(AUC_ROC_data["FPR"])]})).mark_line(size = 2, color = "darkred").encode(
                                        alt.X("FPR"),
                                        alt.Y("TPR"),
                            )
                            st.altair_chart(AUC_ROC_plot + line, use_container_width = True)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_BRT_thresAUC")))
                        st.write("") 
                        # Partial probabilities
                        # st.write("Partial probability plots:")    
                        # fm_brt_figs4_col1, fm_brt_figs4_col2 = st.beta_columns(2)
                        # for pp_var in expl_var:
                        #     pp_data = pd.DataFrame(columns = [pp_var])
                        #     pp_data[pp_var] = model_full_results["BRT partial probabilities"][pp_var][pp_var]
                        #     pp_data["ProbabilityOfOccurrence"] = model_full_results["BRT partial probabilities"][pp_var]["prediction"]
                        #     pp_data["Observed"] = df[response_var]
                        #     pp_chart = alt.Chart(pp_data, height = 200).mark_line(color = "darkred").encode(
                        #     x = alt.X(pp_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                        #     y = alt.Y("ProbabilityOfOccurrence", title = "probability of occurrence", scale = alt.Scale(domain = [0, 1]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                        #     tooltip = ["ProbabilityOfOccurrence"] + [pp_var]
                        #     )
                        #     obs_data_plot = alt.Chart(pp_data, height = 200).mark_circle(size=20).encode(
                        #         x = alt.X(pp_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                        #         y = alt.Y("Observed", title = "probability of occurrence", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                        #         tooltip = ["Observed", "ProbabilityOfOccurrence"] + [pp_var]
                        #     )
                        #     if expl_var.index(pp_var)%2 == 0:
                        #         with fm_brt_figs4_col1:
                        #             st.altair_chart(pp_chart + obs_data_plot, use_container_width = True)
                        #     if expl_var.index(pp_var)%2 == 1:
                        #         with fm_brt_figs4_col2:
                        #              st.altair_chart(pp_chart + obs_data_plot, use_container_width = True)

                        # Partial dependence plots
                        st.write("Partial dependence plots:")    
                        fm_brt_figs3_col1, fm_brt_figs3_col2 = st.beta_columns(2)
                        for pd_var in expl_var:
                            pd_data_brt = pd.DataFrame(columns = [pd_var])
                            pd_data_brt[pd_var] = model_full_results["BRT partial dependence"][pd_var][1][0]
                            pd_data_brt["Partial dependence"] = model_full_results["BRT partial dependence"][pd_var][0][0]
                            pd_chart_brt = alt.Chart(pd_data_brt, height = 200).mark_line(color = "darkred").encode(
                            x = alt.X(pd_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                            y = alt.Y("Partial dependence", title = "partial dependence", scale = alt.Scale(domain = [model_full_results["BRT partial dependence min/max"]["min"].min(), model_full_results["BRT partial dependence min/max"]["max"].max()]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                            tooltip = ["Partial dependence"] + [pd_var]
                            )
                            pd_data_ticks_brt = pd.DataFrame(columns = [pd_var])
                            pd_data_ticks_brt[pd_var] = df[pd_var]
                            pd_data_ticks_brt["y"] = [model_full_results["BRT partial dependence min/max"]["min"].min()] * df.shape[0]
                            pd_ticks_brt = alt.Chart(pd_data_ticks_brt, height = 200).mark_tick(size = 5, thickness = 1).encode(
                                x = alt.X(pd_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), scale = alt.Scale(domain = [pd_data_ticks_brt[pd_var].min(), pd_data_ticks_brt[pd_var].max()])),
                                y = alt.Y("y", title = "partial dependence", scale = alt.Scale(domain = [model_full_results["BRT partial dependence min/max"]["min"].min(), model_full_results["BRT partial dependence min/max"]["max"].max()]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = [pd_var]
                            )
                            if expl_var.index(pd_var)%2 == 0:
                                with fm_brt_figs3_col1:
                                    st.altair_chart(pd_ticks_brt + pd_chart_brt, use_container_width = True)
                            if expl_var.index(pd_var)%2 == 1:
                                with fm_brt_figs3_col2:
                                    st.altair_chart(pd_ticks_brt + pd_chart_brt, use_container_width = True)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_BRT_partDep_bin")))

                        # Download link for BRT output
                        output = BytesIO()
                        excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
                        model_full_results["BRT information"].to_excel(excel_file, sheet_name="regression_information")
                        brt_error_est.to_excel(excel_file, sheet_name="regression_statistics")
                        brt_varImp_table.to_excel(excel_file, sheet_name="variable_importance")
                        brt_featImp_table.to_excel(excel_file, sheet_name="feature_importance")
                        excel_file.save()
                        excel_file = output.getvalue()
                        b64 = base64.b64encode(excel_file)
                        dl_file_name = "BRT full model output__" + df_name + ".xlsx"
                        st.markdown(
                            f"""
                        <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download Boosted Regression Trees full model output</a>
                        """,
                        unsafe_allow_html=True)
                        st.write("")
         
                    # ANN specific output
                    if any(a for a in sb_ML_alg if a == "Artificial Neural Networks"):
                        st.markdown("**Artificial Neural Networks**")

                        fm_ann_reg_col1, fm_ann_reg_col2 = st.beta_columns(2)
                        # Regression information
                        with fm_ann_reg_col1:
                            st.write("Regression information:")
                            st.write(model_full_results["ANN information"])
                        # Regression statistics
                        with fm_ann_reg_col2:
                            st.write("Regression statistics:")
                            ann_error_est = pd.DataFrame(index = ["AUC ROC", "AP", "AUC PRC", "LOG-LOSS", "Best loss"], columns = ["Value"])
                            ann_error_est.loc["AUC ROC"] = model_full_results["model comparison thresInd"].loc["AUC ROC"]["Artificial Neural Networks"]
                            ann_error_est.loc["AP"] = model_full_results["model comparison thresInd"].loc["AP"]["Artificial Neural Networks"]
                            ann_error_est.loc["AUC PRC"] =  model_full_results["model comparison thresInd"].loc["AUC PRC"]["Artificial Neural Networks"]
                            ann_error_est.loc["LOG-LOSS"] =  model_full_results["model comparison thresInd"].loc["LOG-LOSS"]["Artificial Neural Networks"]
                            if ann_finalPara["weight optimization solver"][0] != "lbfgs":
                                ann_error_est.loc["Best loss"] =  model_full_results["ANN loss"]
                            st.write(ann_error_est)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_ANN_regStat_bin")))
                        st.write("")
                        # Loss curve (loss vs. number of iterations (epochs))
                        if ann_finalPara["weight optimization solver"][0] != "lbfgs":
                            st.write("Loss curve:")
                            loss_curve = pd.DataFrame(index = range(len(model_full_results["ANN loss curve"])), columns = ["Loss"])
                            loss_curve["Loss"] = model_full_results["ANN loss curve"]
                            loss_curve["Iterations"] = loss_curve.index+1
                            loss_curve_plot = alt.Chart(loss_curve, height = 200).mark_line(color = "darkred").encode(
                                x = alt.X("Iterations", title = "iterations (epochs)", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), scale = alt.Scale(domain = [loss_curve["Iterations"].min(), loss_curve["Iterations"].max()])),
                                y = alt.Y("Loss", title = "loss", scale = alt.Scale(zero = False), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Loss", "Iterations"]
                            )     
                            st.altair_chart(loss_curve_plot, use_container_width = True)    
                        st.write("") 
                        fm_ann_figs1_col1, fm_ann_figs1_col2 = st.beta_columns(2)
                        # Variable importance (via permutation)
                        with fm_ann_figs1_col1:
                            st.write("Variable importance (via permutation):")
                            ann_varImp_table = model_full_results["ANN variable importance"]
                            st.write(ann_varImp_table)
                        with fm_ann_figs1_col2:
                            st.write("")
                            st.write("")
                            st.write("")
                            ann_varImp_plot_data = model_full_results["ANN variable importance"]
                            ann_varImp_plot_data["Variable"] = ann_varImp_plot_data.index
                            ann_varImp = alt.Chart(ann_varImp_plot_data, height = 200).mark_bar().encode(
                                x = alt.X("mean", title = "variable importance", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Variable", title = None, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), sort = None),
                                tooltip = ["Variable", "mean"]
                            )
                            st.altair_chart(ann_varImp, use_container_width = True)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_ANN_varImp_bin")))
                        st.write("") 
                        fm_ann_figs5_col1, fm_ann_figs5_col2 = st.beta_columns(2)
                        # Observed vs. Probability of Occurrence 
                        with fm_ann_figs5_col1:
                            st.write("Observed vs. Probability of Occurrence:")
                            prob_data = pd.DataFrame(model_full_results["ANN fitted"])
                            prob_data["Observed"] = df[response_var]
                            prob_data["ProbabilityOfOccurrence"] = prob_data[1]
                            prob_data["Threshold"] = model_full_results["model comparison thres"].loc["threshold"]["Artificial Neural Networks"]
                            prob_data_plot = alt.Chart(prob_data, height = 200).mark_tick(size = 5, thickness = 1).encode(
                                x = alt.X("ProbabilityOfOccurrence", title = "probability of occurrence", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("Observed", title = "observed", scale = alt.Scale(domain = [min(prob_data["Observed"]), max(prob_data["Observed"])]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["Observed", "ProbabilityOfOccurrence", "Threshold"]
                            )
                            thres = alt.Chart(prob_data, height = 200).mark_rule(size = 1.5, color = "darkred").encode(x = "Threshold", tooltip = ["Threshold"]) 
                            prob_plot = prob_data_plot + thres
                            st.altair_chart(prob_plot, use_container_width = True)
                        # ROC curve 
                        with fm_ann_figs5_col2:
                            st.write("ROC curve:")
                            AUC_ROC_data = pd.DataFrame()
                            AUC_ROC_data["FPR"] = model_full_results["ANN ROC curve"][0]
                            AUC_ROC_data["TPR"] = model_full_results["ANN ROC curve"][1]
                            AUC_ROC_data["AUC ROC"] = model_full_results["model comparison thresInd"].loc["AUC ROC"]["Artificial Neural Networks"]
                            AUC_ROC_data["Threshold"] = model_full_results["model comparison thres"].loc["threshold"]["Artificial Neural Networks"]
                            AUC_ROC_plot= alt.Chart(AUC_ROC_data, height = 200).mark_line().encode(
                                x = alt.X("FPR", title = "1 - specificity (FPR)", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                y = alt.Y("TPR", title = "sensitivity (TPR)", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = ["TPR", "FPR", "AUC ROC"]
                            )
                            line = alt.Chart(
                                pd.DataFrame({"FPR": [min(AUC_ROC_data["FPR"]), max(AUC_ROC_data["FPR"])], "TPR": [min(AUC_ROC_data["FPR"]), max(AUC_ROC_data["FPR"])]})).mark_line(size = 2, color = "darkred").encode(
                                        alt.X("FPR"),
                                        alt.Y("TPR"),
                            )
                            st.altair_chart(AUC_ROC_plot + line, use_container_width = True)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_ANN_thresAUC")))
                        st.write("") 
                        # Partial probabilities
                        # st.write("Partial probability plots (stand. expl. variables):")    
                        # fm_ann_figs4_col1, fm_ann_figs4_col2 = st.beta_columns(2)
                        # for pp_var in expl_var:
                        #     pp_data = pd.DataFrame(columns = [pp_var])
                        #     pp_data[pp_var] = model_full_results["ANN partial probabilities"][pp_var][pp_var]
                        #     pp_data["ProbabilityOfOccurrence"] = model_full_results["ANN partial probabilities"][pp_var]["prediction"]
                        #     pp_data["Observed"] = df[response_var]
                        #     pp_chart = alt.Chart(pp_data, height = 200).mark_line(color = "darkred").encode(
                        #     x = alt.X(pp_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                        #     y = alt.Y("ProbabilityOfOccurrence", title = "probability of occurrence", scale = alt.Scale(domain = [0, 1]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                        #     tooltip = ["ProbabilityOfOccurrence"] + [pp_var]
                        #     )
                        #     obs_data_plot = alt.Chart(pp_data, height = 200).mark_circle(size=20).encode(
                        #         x = alt.X(pp_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                        #         y = alt.Y("Observed", title = "probability of occurrence", axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                        #         tooltip = ["Observed", "ProbabilityOfOccurrence"] + [pp_var]
                        #     )
                        #     if expl_var.index(pp_var)%2 == 0:
                        #         with fm_ann_figs4_col1:
                        #             st.altair_chart(pp_chart + obs_data_plot, use_container_width = True)
                        #     if expl_var.index(pp_var)%2 == 1:
                        #         with fm_ann_figs4_col2:
                        #              st.altair_chart(pp_chart + obs_data_plot, use_container_width = True)

                        # Partial dependence plots
                        st.write("Partial dependence plots:")    
                        fm_ann_figs2_col1, fm_ann_figs2_col2 = st.beta_columns(2)
                        for pd_var in expl_var:
                            pd_data_ann = pd.DataFrame(columns = [pd_var])
                            pd_data_ann[pd_var] = (model_full_results["ANN partial dependence"][pd_var][1][0]*(df[pd_var].std()))+df[pd_var].mean()
                            pd_data_ann["Partial dependence"] = model_full_results["ANN partial dependence"][pd_var][0][0]
                            pd_chart_ann = alt.Chart(pd_data_ann, height = 200).mark_line(color = "darkred").encode(
                            x = alt.X(pd_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                            y = alt.Y("Partial dependence", title = "partial dependence", scale = alt.Scale(domain = [model_full_results["ANN partial dependence min/max"]["min"].min(), model_full_results["ANN partial dependence min/max"]["max"].max()]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                            tooltip = ["Partial dependence"] + [pd_var]
                            )
                            pd_data_ticks_ann = pd.DataFrame(columns = [pd_var])
                            pd_data_ticks_ann[pd_var] = df[pd_var]
                            pd_data_ticks_ann["y"] = [model_full_results["ANN partial dependence min/max"]["min"].min()] * df.shape[0]
                            pd_ticks_ann = alt.Chart(pd_data_ticks_ann, height = 200).mark_tick(size = 5, thickness = 1).encode(
                                x = alt.X(pd_var, axis = alt.Axis(titleFontSize = 12, labelFontSize = 11), scale = alt.Scale(domain = [pd_data_ticks_ann[pd_var].min(), pd_data_ticks_ann[pd_var].max()])),
                                y = alt.Y("y", title = "partial dependence", scale = alt.Scale(domain = [model_full_results["ANN partial dependence min/max"]["min"].min(), model_full_results["ANN partial dependence min/max"]["max"].max()]), axis = alt.Axis(titleFontSize = 12, labelFontSize = 11)),
                                tooltip = [pd_var]
                            )
                            if expl_var.index(pd_var)%2 == 0:
                                with fm_ann_figs2_col1:
                                    st.altair_chart(pd_ticks_ann + pd_chart_ann, use_container_width = True)
                            if expl_var.index(pd_var)%2 == 1:
                                with fm_ann_figs2_col2:
                                    st.altair_chart(pd_ticks_ann + pd_chart_ann, use_container_width = True)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_ANN_partDep_bin")))

                        # Download link for ANN output
                        output = BytesIO()
                        excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
                        model_full_results["ANN information"].to_excel(excel_file, sheet_name="regression_information")
                        ann_error_est.to_excel(excel_file, sheet_name="regression_statistics")
                        ann_varImp_table.to_excel(excel_file, sheet_name="variable_importance")
                        excel_file.save()
                        excel_file = output.getvalue()
                        b64 = base64.b64encode(excel_file)
                        dl_file_name = "ANN full model output__" + df_name + ".xlsx"
                        st.markdown(
                            f"""
                        <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download Artificial Neural Networks full model output</a>
                        """,
                        unsafe_allow_html=True)
                        st.write("") 

                    # Performance metrics across all models
                    if any(a for a in sb_ML_alg if a == "Logistic Regression" or a == "Random Forest" or a == "Generalized Additive Models" or a == "Boosted Regression Trees" or a == "Artificial Neural Networks"):
                        st.markdown("**Model comparison**")
                        st.write("Threshold-independent metrics:")
                        st.write((model_full_results["model comparison thresInd"]).transpose())
                        if len(sb_ML_alg) > 1:
                            if sett_hints:
                                st.info(str(fc.learning_hints("mod_md_modCompThresInd")))
                        st.write("")
                        st.write("Thresholds:")
                        st.write(model_full_results["model comparison thres"])
                        st.write("")
                        st.write("Threshold-dependent metrics:")
                        st.write((model_full_results["model comparison thresDep"]).transpose())
                        if len(sb_ML_alg) > 1:
                            if sett_hints:
                                st.info(str(fc.learning_hints("mod_md_modCompThresDep")))
                        st.write("")
                        
                        # Download link for model comparison output
                        output = BytesIO()
                        excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
                        model_full_results["model comparison thresInd"].transpose().to_excel(excel_file, sheet_name="thresh_independent_metrics")
                        model_full_results["model comparison thres"].to_excel(excel_file, sheet_name="thresholds")
                        model_full_results["model comparison thresDep"].transpose().to_excel(excel_file, sheet_name="thresh_dependent_metrics")
                        excel_file.save()
                        excel_file = output.getvalue()
                        b64 = base64.b64encode(excel_file)
                        dl_file_name = "Model comparison full model output__" + df_name + ".xlsx"
                        st.markdown(
                            f"""
                        <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download model comparison output</a>
                        """,
                        unsafe_allow_html=True)
                        st.write("")
            
            else:
                st.warning("Please run models!")
            st.write("")

        #--------------------------------------------------------------------------------------
        # FULL MODEL PREDICTIONS

        prediction_output = st.beta_expander("Full model predictions", expanded = False)
        with prediction_output:
            
            if model_full_results is not None:

                #-------------------------------------------------------------

                # Continuous response variable
                if response_var_type == "continuous":

                    # MLR specific output
                    if any(a for a in sb_ML_alg if a == "Multiple Linear Regression"):
                        st.markdown("**Multiple Linear Regression**")

                        pred_col1, pred_col2 = st.beta_columns(2)
                        with pred_col1:
                            st.write("Predictions for original data:")
                            MLR_pred_orig = pd.DataFrame(columns = [response_var])
                            MLR_pred_orig[response_var] = model_full_results["MLR fitted"]
                            st.write(MLR_pred_orig)
                        with pred_col2:
                            if do_modprednew == "Yes":
                                st.write("Predictions for new data:")
                                MLR_pred_new = pd.DataFrame(columns = [response_var])
                                MLR_pred_new[response_var] = model_full_results["MLR prediction"]
                                st.write(MLR_pred_new)

                    # GAM specific output
                    if any(a for a in sb_ML_alg if a == "Generalized Additive Models"):
                        st.markdown("**Generalized Additive Models**")

                        pred_col1, pred_col2 = st.beta_columns(2)
                        with pred_col1:
                            st.write("Predictions for original data:")
                            GAM_pred_orig = pd.DataFrame(columns = [response_var])
                            GAM_pred_orig[response_var] = model_full_results["GAM fitted"]
                            st.write(GAM_pred_orig)
                        with pred_col2:
                            if do_modprednew == "Yes":
                                st.write("Predictions for new data:")
                                GAM_pred_new = pd.DataFrame(columns = [response_var])
                                GAM_pred_new[response_var] = model_full_results["GAM prediction"]
                                st.write(GAM_pred_new)
                    
                    # RF specific output
                    if any(a for a in sb_ML_alg if a == "Random Forest"):
                        st.markdown("**Random Forest**")

                        pred_col1, pred_col2 = st.beta_columns(2)
                        with pred_col1:
                            st.write("Predictions for original data:")
                            RF_pred_orig = pd.DataFrame(columns = [response_var])
                            RF_pred_orig[response_var] = model_full_results["RF fitted"]
                            st.write(RF_pred_orig)
                        with pred_col2:
                            if do_modprednew == "Yes":
                                st.write("Predictions for new data:")
                                RF_pred_new = pd.DataFrame(columns = [response_var])
                                RF_pred_new[response_var] = model_full_results["RF prediction"]
                                st.write(RF_pred_new)
                    
                    # BRT specific output
                    if any(a for a in sb_ML_alg if a == "Boosted Regression Trees"):
                        st.markdown("**Boosted Regression Trees**")

                        pred_col1, pred_col2 = st.beta_columns(2)
                        with pred_col1:
                            st.write("Predictions for original data:")
                            BRT_pred_orig = pd.DataFrame(columns = [response_var])
                            BRT_pred_orig[response_var] = model_full_results["BRT fitted"]
                            st.write(BRT_pred_orig)
                        with pred_col2:
                            if do_modprednew == "Yes":
                                st.write("Predictions for new data:")
                                BRT_pred_new = pd.DataFrame(columns = [response_var])
                                BRT_pred_new[response_var] = model_full_results["BRT prediction"]
                                st.write(BRT_pred_new)
                    
                    # ANN specific output
                    if any(a for a in sb_ML_alg if a == "Artificial Neural Networks"):
                        st.markdown("**Artificial Neural Networks**")

                        pred_col1, pred_col2 = st.beta_columns(2)
                        with pred_col1:
                            st.write("Predictions for original data:")
                            ANN_pred_orig = pd.DataFrame(columns = [response_var])
                            ANN_pred_orig[response_var] = model_full_results["ANN fitted"]
                            st.write(ANN_pred_orig)
                        with pred_col2:
                            if do_modprednew == "Yes":
                                st.write("Predictions for new data:")
                                ANN_pred_new = pd.DataFrame(columns = [response_var])
                                ANN_pred_new[response_var] = model_full_results["ANN prediction"]
                                st.write(ANN_pred_new)

                #-------------------------------------------------------------

                # Binary response variable
                if response_var_type == "binary":

                    # MLR specific output
                    if any(a for a in sb_ML_alg if a == "Multiple Linear Regression"):
                        st.markdown("**Multiple Linear Regression**")

                        pred_col1, pred_col2 = st.beta_columns(2)
                        with pred_col1:
                            st.write("Predictions for original data:")
                            MLR_pred_orig = pd.DataFrame(columns = [response_var])
                            MLR_pred_orig[response_var] = model_full_results["MLR fitted"]
                            st.write(MLR_pred_orig)
                        with pred_col2:
                            if do_modprednew == "Yes":
                                st.write("Predictions for new data:")
                                MLR_pred_new = pd.DataFrame(columns = [response_var])
                                MLR_pred_new[response_var] = model_full_results["MLR prediction"]
                                st.write(MLR_pred_new)
                        st.write("")

                    # LR specific output
                    if any(a for a in sb_ML_alg if a == "Logistic Regression"):
                        st.markdown("**Logistic Regression**")

                        pred_col1, pred_col2 = st.beta_columns(2)
                        with pred_col1:
                            st.write("Predictions for original data:")
                            LR_pred_orig = pd.DataFrame(columns = [response_var])
                            LR_pred_orig[response_var] = model_full_results["LR fitted"][:, 1]
                            LR_pred_orig[response_var + "_binary"] = model_full_results["LR fitted binary"]
                            st.write(LR_pred_orig)
                        with pred_col2:
                            if do_modprednew == "Yes":
                                st.write("Predictions for new data:")
                                LR_pred_new = pd.DataFrame(columns = [response_var])
                                LR_pred_new[response_var] = model_full_results["LR prediction"][:, 1]
                                LR_pred_new[response_var + "_binary"] = model_full_results["LR prediction binary"]
                                st.write(LR_pred_new)
                        st.write("")

                    # GAM specific output
                    if any(a for a in sb_ML_alg if a == "Generalized Additive Models"):
                        st.markdown("**Generalized Additive Models**")

                        pred_col1, pred_col2 = st.beta_columns(2)
                        with pred_col1:
                            st.write("Predictions for original data:")
                            GAM_pred_orig = pd.DataFrame(columns = [response_var])
                            GAM_pred_orig[response_var] = model_full_results["GAM fitted"]
                            GAM_pred_orig[response_var + "_binary"] = model_full_results["GAM fitted binary"]
                            st.write(GAM_pred_orig)
                        with pred_col2:
                            if do_modprednew == "Yes":
                                st.write("Predictions for new data:")
                                GAM_pred_new = pd.DataFrame(columns = [response_var])
                                GAM_pred_new[response_var] = model_full_results["GAM prediction"]
                                GAM_pred_new[response_var + "_binary"] = model_full_results["GAM prediction binary"]
                                st.write(GAM_pred_new)
                        st.write("")

                    # RF specific output
                    if any(a for a in sb_ML_alg if a == "Random Forest"):
                        st.markdown("**Random Forest**")

                        pred_col1, pred_col2 = st.beta_columns(2)
                        with pred_col1:
                            st.write("Predictions for original data:")
                            RF_pred_orig = pd.DataFrame(columns = [response_var])
                            RF_pred_orig[response_var] = model_full_results["RF fitted"][:, 1]
                            RF_pred_orig[response_var + "_binary"] = model_full_results["RF fitted binary"]
                            st.write(RF_pred_orig)
                        with pred_col2:
                            if do_modprednew == "Yes":
                                st.write("Predictions for new data:")
                                RF_pred_new = pd.DataFrame(columns = [response_var])
                                RF_pred_new[response_var] = model_full_results["RF prediction"][:, 1]
                                RF_pred_new[response_var + "_binary"] = model_full_results["RF prediction binary"]
                                st.write(RF_pred_new)
                        st.write("")
                    
                    # BRT specific output
                    if any(a for a in sb_ML_alg if a == "Boosted Regression Trees"):
                        st.markdown("**Boosted Regression Trees**")

                        pred_col1, pred_col2 = st.beta_columns(2)
                        with pred_col1:
                            st.write("Predictions for original data:")
                            BRT_pred_orig = pd.DataFrame(columns = [response_var])
                            BRT_pred_orig[response_var] = model_full_results["BRT fitted"][:, 1]
                            BRT_pred_orig[response_var + "_binary"] = model_full_results["BRT fitted binary"]
                            st.write(BRT_pred_orig)
                        with pred_col2:
                            if do_modprednew == "Yes":
                                st.write("Predictions for new data:")
                                BRT_pred_new = pd.DataFrame(columns = [response_var])
                                BRT_pred_new[response_var] = model_full_results["BRT prediction"][:, 1]
                                BRT_pred_new[response_var + "_binary"] = model_full_results["BRT prediction binary"]
                                st.write(BRT_pred_new)
                        st.write("")
                    
                    # ANN specific output
                    if any(a for a in sb_ML_alg if a == "Artificial Neural Networks"):
                        st.markdown("**Artificial Neural Networks**")

                        pred_col1, pred_col2 = st.beta_columns(2)
                        with pred_col1:
                            st.write("Predictions for original data:")
                            ANN_pred_orig = pd.DataFrame(columns = [response_var])
                            ANN_pred_orig[response_var] = model_full_results["ANN fitted"][:, 1]
                            ANN_pred_orig[response_var + "_binary"] = model_full_results["ANN fitted binary"]
                            st.write(ANN_pred_orig)
                        with pred_col2:
                            if do_modprednew == "Yes":
                                st.write("Predictions for new data:")
                                ANN_pred_new = pd.DataFrame(columns = [response_var])
                                ANN_pred_new[response_var] = model_full_results["ANN prediction"][:, 1]
                                ANN_pred_new[response_var + "_binary"] = model_full_results["ANN prediction binary"]
                                st.write(ANN_pred_new)
                        st.write("")
                
                #-------------------------------------------------------------
                st.write("")
                # Download links for prediction data
                output = BytesIO()
                predictions_excel = pd.ExcelWriter(output, engine="xlsxwriter")
                if any(a for a in sb_ML_alg if a == "Multiple Linear Regression"):
                    MLR_pred_orig.to_excel(predictions_excel, sheet_name="MLR_pred_orig")
                    if do_modprednew == "Yes":
                        MLR_pred_new.to_excel(predictions_excel, sheet_name="MLR_pred_new")
                if any(a for a in sb_ML_alg if a == "Logistic Regression"):
                    LR_pred_orig.to_excel(predictions_excel, sheet_name="LR_pred_orig")
                    if do_modprednew == "Yes":
                        LR_pred_new.to_excel(predictions_excel, sheet_name="LR_pred_new")
                if any(a for a in sb_ML_alg if a == "Generalized Additive Models"):
                    GAM_pred_orig.to_excel(predictions_excel, sheet_name="GAM_pred_orig")
                    if do_modprednew == "Yes":
                        GAM_pred_new.to_excel(predictions_excel, sheet_name="GAM_pred_new")
                if any(a for a in sb_ML_alg if a == "Random Forest"):
                    RF_pred_orig.to_excel(predictions_excel, sheet_name="RF_pred_orig")
                    if do_modprednew == "Yes":
                        RF_pred_new.to_excel(predictions_excel, sheet_name="RF_pred_new")
                if any(a for a in sb_ML_alg if a == "Boosted Regression Trees"):
                    BRT_pred_orig.to_excel(predictions_excel, sheet_name="BRT_pred_orig")
                    if do_modprednew == "Yes":
                        BRT_pred_new.to_excel(predictions_excel, sheet_name="BRT_pred_new")
                if any(a for a in sb_ML_alg if a == "Artificial Neural Networks"):
                    ANN_pred_orig.to_excel(predictions_excel, sheet_name="ANN_pred_orig")
                    if do_modprednew == "Yes":
                        ANN_pred_new.to_excel(predictions_excel, sheet_name="ANN_pred_new")
                predictions_excel.save()
                predictions_excel = output.getvalue()
                b64 = base64.b64encode(predictions_excel)
                dl_file_name = "Full model predictions__" + df_name + ".xlsx"
                st.markdown(
                    f"""
                <a href="data:file/predictions_excel;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download full model predictions</a>
                """,
                unsafe_allow_html=True)
                st.write("")
        
        #--------------------------------------------------------------------------------------
        # VALIDATION OUTPUT
        
        if do_modval == "Yes":
            val_output = st.beta_expander("Validation output", expanded = False)
            with val_output:
                if model_val_results is not None:
                    
                    #------------------------------------
                    # Continuous response variable

                    if response_var_type == "continuous":

                        # Metrics means
                        st.write("Means of metrics across validation runs:")
                        st.write(model_val_results["mean"].transpose())
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_val_means")))
                        st.write("")

                        # Metrics sd
                        st.write("SDs of metrics across validation runs:")
                        st.write(model_val_results["sd"].transpose())
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_val_sds")))
                        st.write("")
                        val_col1, val_col2 = st.beta_columns(2)
                        with val_col1:
                            # Residuals boxplot
                            if model_val_results["residuals"] is not None:
                                st.write("Boxplot of residuals across validation runs:")
                                residual_results = model_val_results["residuals"]
                                residuals_bplot = pd.melt(residual_results, ignore_index = False, var_name = "Algorithm", value_name = "Residuals")
                                residuals_boxchart = alt.Chart(residuals_bplot, height = 200).mark_boxplot(color = "#1f77b4", median = dict(color = "darkred")).encode(
                                    x = alt.X("Residuals", title = "residuals", scale = alt.Scale(zero = False)),
                                    y = alt.Y("Algorithm", title = None),
                                    color = alt.Color("Algorithm", legend = None)
                                ).configure_axis(
                                    labelFontSize = 12,
                                    titleFontSize = 12
                                )
                                # Scatterplot residuals
                                # residuals_scatter = alt.Chart(residuals_bplot, height = 200).mark_circle(size=60).encode(
                                #     x = "Value",
                                #     y = alt.Y("Algorithm", title = None),
                                #     color = alt.Color("Algorithm", legend=None)
                                # )
                                residuals_plot = residuals_boxchart #+ residuals_scatter
                                st.altair_chart(residuals_plot, use_container_width=True)
                                if sett_hints:
                                    st.info(str(fc.learning_hints("mod_md_val_resBoxplot")))
                        with val_col2:
                            # Variance explained boxplot
                            if model_val_results["variance explained"] is not None:
                                st.write("Boxplot of % VE across validation runs:")
                                ve_results = model_val_results["variance explained"]
                                ve_bplot = pd.melt(ve_results, ignore_index = False, var_name = "Algorithm", value_name = "% VE")
                                ve_boxchart = alt.Chart(ve_bplot, height = 200).mark_boxplot(color = "#1f77b4", median = dict(color = "darkred")).encode(
                                    x = alt.X("% VE", scale = alt.Scale(domain = [min(ve_bplot["% VE"]), max(ve_bplot["% VE"])])),
                                    y = alt.Y("Algorithm", title = None),
                                    color = alt.Color("Algorithm", legend = None)
                                ).configure_axis(
                                    labelFontSize = 12,
                                    titleFontSize = 12
                                )
                                st.altair_chart(ve_boxchart, use_container_width = True)
                                if sett_hints:
                                    st.info(str(fc.learning_hints("mod_md_val_VEBoxplot")))
                        st.write("") 
                        # Variable importance (via permutation)
                        st.write("Means of variable importances:")
                        varImp_table_mean = model_val_results["variable importance mean"]
                        st.write(varImp_table_mean)
                        st.write("")
                        st.write("SDs of variable importances:")
                        varImp_table_sd = model_val_results["variable importance sd"]
                        st.write(varImp_table_sd)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_val_varImp")))
                        st.write("")
                        # Residuals
                        if model_val_results["residuals"] is not None:
                            model_val_res = pd.DataFrame(index = ["min", "25%-Q", "median", "75%-Q", "max"], columns = sb_ML_alg)
                            for m in sb_ML_alg: 
                                model_val_res.loc["min"][m] = model_val_results["residuals"][m].min()
                                model_val_res.loc["25%-Q"][m] = model_val_results["residuals"][m].quantile(q = 0.25)
                                model_val_res.loc["median"][m] = model_val_results["residuals"][m].quantile(q = 0.5)
                                model_val_res.loc["75%-Q"][m] = model_val_results["residuals"][m].quantile(q = 0.75)
                                model_val_res.loc["max"][m] = model_val_results["residuals"][m].max()
                            st.write("Residuals distribution across all validation runs:")
                            st.write(model_val_res.transpose())
                            if sett_hints:
                                st.info(str(fc.learning_hints("mod_md_val_res")))
                        st.write("")

                        # Download link for validation output
                        output = BytesIO()
                        excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
                        model_val_results["mean"].transpose().to_excel(excel_file, sheet_name="performance_metrics_mean")
                        model_val_results["sd"].transpose().to_excel(excel_file, sheet_name="performance_metrics_sd")
                        varImp_table_mean.to_excel(excel_file, sheet_name="variable_importance_mean")
                        varImp_table_sd.to_excel(excel_file, sheet_name="variable_importance_sd")
                        model_val_res.transpose().to_excel(excel_file, sheet_name="residuals_distribution")
                        excel_file.save()
                        excel_file = output.getvalue()
                        b64 = base64.b64encode(excel_file)
                        dl_file_name = "Validation output__" + df_name + ".xlsx"
                        st.markdown(
                            f"""
                        <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download validation output</a>
                        """,
                        unsafe_allow_html=True)
                        st.write("")

                    #------------------------------------
                    # Binary response variable

                    if response_var_type == "binary":
                        if model_val_results["mean_ind"].empty:
                            st.warning("Please select an additional algorithm besides Multiple Linear Regression!")
                        
                        # Metrics (independent)
                        if model_val_results["mean_ind"].empty:
                            st.write("")
                        else:
                            st.write("Means of threshold-independent metrics across validation runs:")
                            st.write(model_val_results["mean_ind"].transpose())
                            if sett_hints:
                                st.info(str(fc.learning_hints("mod_md_val_means_thresInd")))
                            st.write("")
                        
                        # Metrics (independent)
                        if model_val_results["sd_ind"].empty:
                            st.write("")
                        else:
                            st.write("SDs of threshold-independent metrics across validation runs:")
                            st.write(model_val_results["sd_ind"].transpose())
                            if sett_hints:
                                st.info(str(fc.learning_hints("mod_md_val_sds_thresInd")))
                            st.write("")

                        val_col1, val_col2 = st.beta_columns(2)
                        with val_col1: 
                            # AUC ROC boxplot
                            if model_val_results["AUC ROC"].empty:
                                st.write("")
                            else:
                                st.write("Boxplot of AUC ROC across validation runs:")
                                auc_results = model_val_results["AUC ROC"]
                                auc_bplot = pd.melt(auc_results, ignore_index = False, var_name = "Algorithm", value_name = "Value")
                                auc_boxchart = alt.Chart(auc_bplot, height = 200).mark_boxplot(color = "#1f77b4", median = dict(color = "darkred")).encode(
                                    x = alt.X("Value", title = "AUC ROC", scale = alt.Scale(domain = [min(auc_bplot["Value"]), max(auc_bplot["Value"])])),
                                    y = alt.Y("Algorithm", title = None),
                                    color = alt.Color("Algorithm", legend = None)
                                ).configure_axis(
                                    labelFontSize = 12,
                                    titleFontSize = 12
                                )
                                st.altair_chart(auc_boxchart, use_container_width = True) 
                                if sett_hints:
                                    st.info(str(fc.learning_hints("mod_md_val_AUCBoxplot")))
                        with val_col2: 
                            # TSS boxplot
                            if model_val_results["TSS"].empty:
                                st.write("")
                            else:
                                st.write("Boxplot of TSS across validation runs:")
                                tss_results = model_val_results["TSS"]
                                tss_bplot = pd.melt(tss_results, ignore_index = False, var_name = "Algorithm", value_name = "Value")
                                tss_boxchart = alt.Chart(tss_bplot, height = 200).mark_boxplot(color = "#1f77b4", median = dict(color = "darkred")).encode(
                                    x = alt.X("Value", title = "TSS", scale = alt.Scale(domain = [min(tss_bplot["Value"]), max(tss_bplot["Value"])])),
                                    y = alt.Y("Algorithm", title = None),
                                    color = alt.Color("Algorithm", legend = None)
                                ).configure_axis(
                                    labelFontSize = 12,
                                    titleFontSize = 12
                                )
                                st.altair_chart(tss_boxchart, use_container_width = True)
                                if sett_hints:
                                    st.info(str(fc.learning_hints("mod_md_val_TSSBoxplot")))
                        st.write("") 
                        
                        # Threshold
                        # st.write("Means of thresholds across validation runs:")
                        # st.write(model_val_results["mean_thres"])
                        # st.write("")
                        # Variable importance (via permutation)
                        
                        # Threshold
                        # st.write("SD of thresholds across validation runs:")
                        # st.write(model_val_results["sd_thres"])
                        # st.write("")
                        # Variable importance (via permutation)

                        # Variable importance
                        st.write("Means of variable importances:")
                        varImp_table_mean = model_val_results["variable importance mean"]
                        st.write(varImp_table_mean)
                        st.write("")
                        st.write("SDs of variable importances:")
                        varImp_table_sd = model_val_results["variable importance sd"]
                        st.write(varImp_table_sd)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_val_varImp_bin")))
                        st.write("")     

                        # Metrics (dependent)
                        if model_val_results["mean_dep"].empty:
                            st.write("")
                        else:
                            st.write("Means of threshold-dependent metrics across validation runs:")
                            st.write(model_val_results["mean_dep"].transpose())
                            if sett_hints:
                                st.info(str(fc.learning_hints("mod_md_val_means_thresDep")))
                            st.write("")       

                        # Metrics (dependent)
                        if model_val_results["sd_dep"].empty:
                            st.write("")
                        else:
                            st.write("SDs of threshold-dependent metrics across validation runs:")
                            st.write(model_val_results["sd_dep"].transpose())
                            if sett_hints:
                                st.info(str(fc.learning_hints("mod_md_val_sds_thresDep")))
                        st.write("")
                        
                        # Download link for validation output
                        output = BytesIO()
                        excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
                        model_val_results["mean_ind"].transpose().to_excel(excel_file, sheet_name="thresh_independent_metrics_mean")
                        model_val_results["sd_ind"].transpose().to_excel(excel_file, sheet_name="thresh_independent_metrics_sd")
                        varImp_table_mean.to_excel(excel_file, sheet_name="variable_importance_mean")
                        varImp_table_sd.to_excel(excel_file, sheet_name="variable_importance_sd")
                        model_val_results["mean_dep"].transpose().to_excel(excel_file, sheet_name="thresh_dependent_metrics_mean")
                        model_val_results["sd_dep"].transpose().to_excel(excel_file, sheet_name="thresh_dependent_metrics_sd")
                        excel_file.save()
                        excel_file = output.getvalue()
                        b64 = base64.b64encode(excel_file)
                        dl_file_name = "Validation output__" + df_name + ".xlsx"
                        st.markdown(
                            f"""
                        <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download validation output</a>
                        """,
                        unsafe_allow_html=True)
                        st.write("")   

                else:
                    st.warning("Please run models!")
                st.write("")
        
        #--------------------------------------------------------------------------------------
        # HYPERPARAMETER-TUNING OUTPUT

        if any(a for a in sb_ML_alg if a == "Random Forest") or any(a for a in sb_ML_alg if a == "Boosted Regression Trees") or any(a for a in sb_ML_alg if a == "Artificial Neural Networks"):
            if do_hypTune == "Yes":
                hype_title = "Hyperparameter-tuning output"
            if do_hypTune != "Yes":
                hype_title = "Hyperparameter output"
            hype_output = st.beta_expander(hype_title, expanded = False)
            with hype_output:
                
                # Random Forest
                if any(a for a in sb_ML_alg if a == "Random Forest"):
                    st.markdown("**Random Forest**")

                    # Final hyperparameters
                    if rf_finalPara is not None:
                        st.write("Final hyperparameters:")
                        st.write(rf_finalPara)
                        # if sett_hints:
                        #     st.info(str(fc.learning_hints("mod_md_hypeTune_BRT_finPara")))
                        st.write("")
                    else:
                        st.warning("Please run models!")
                    
                    # Tuning details
                    if do_hypTune == "Yes":
                        if rf_tuning_results is not None and rf_finalPara is not None:
                            st.write("Tuning details:")
                            rf_finalTuneMetrics = pd.DataFrame(index = ["value"], columns = ["scoring metric", "number of models", "mean cv score", "standard deviation cv score", "test data score"])
                            rf_finalTuneMetrics["scoring metric"] = [rf_tuning_results.loc["value"]["scoring"]]
                            rf_finalTuneMetrics["number of models"] = [rf_tuning_results.loc["value"]["number of models"]]
                            rf_finalTuneMetrics["mean cv score"] = [rf_tuning_results.loc["value"]["mean score"]]
                            rf_finalTuneMetrics["standard deviation cv score"] = [rf_tuning_results.loc["value"]["std score"]]
                            rf_finalTuneMetrics["test data score"] = [rf_tuning_results.loc["value"]["test score"]]
                            st.write(rf_finalTuneMetrics)
                            # if sett_hints:
                            #     st.info(str(fc.learning_hints("mod_md_hypeTune_BRT_details")))
                            st.write("")

                # Boosted Regression Trees
                if any(a for a in sb_ML_alg if a == "Boosted Regression Trees"):
                    st.markdown("**Boosted Regression Trees**")

                    # Final hyperparameters
                    if brt_finalPara is not None:
                        st.write("Final hyperparameters:")
                        st.write(brt_finalPara)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_hypeTune_BRT_finPara")))
                        st.write("")
                    else:
                        st.warning("Please run models!")
                    
                    # Tuning details
                    if do_hypTune == "Yes":
                        if brt_tuning_results is not None and brt_finalPara is not None:
                            st.write("Tuning details:")
                            brt_finalTuneMetrics = pd.DataFrame(index = ["value"], columns = ["scoring metric", "number of models", "mean cv score", "standard deviation cv score", "test data score"])
                            brt_finalTuneMetrics["scoring metric"] = [brt_tuning_results.loc["value"]["scoring"]]
                            brt_finalTuneMetrics["number of models"] = [brt_tuning_results.loc["value"]["number of models"]]
                            brt_finalTuneMetrics["mean cv score"] = [brt_tuning_results.loc["value"]["mean score"]]
                            brt_finalTuneMetrics["standard deviation cv score"] = [brt_tuning_results.loc["value"]["std score"]]
                            brt_finalTuneMetrics["test data score"] = [brt_tuning_results.loc["value"]["test score"]]
                            st.write(brt_finalTuneMetrics)
                            if sett_hints:
                                st.info(str(fc.learning_hints("mod_md_hypeTune_BRT_details")))
                            st.write("")

                # Artificial Neural Networks
                if any(a for a in sb_ML_alg if a == "Artificial Neural Networks"):
                    st.markdown("**Artificial Neural Networks**")
                    
                    # Final hyperparameters
                    if ann_finalPara is not None:
                        st.write("Final hyperparameters:")
                        st.write(ann_finalPara)
                        if sett_hints:
                            st.info(str(fc.learning_hints("mod_md_hypeTune_ANN_finPara")))
                        st.write("")
                    else:
                        st.warning("Please run models!")
                    
                    # Tuning details
                    if do_hypTune == "Yes":
                        if ann_tuning_results is not None and ann_finalPara is not None:
                            st.write("Tuning details:")
                            ann_finalTuneMetrics = pd.DataFrame(index = ["value"], columns = ["scoring metric", "number of models", "mean cv score", "standard deviation cv score", "test data score"])
                            ann_finalTuneMetrics["scoring metric"] = [ann_tuning_results.loc["value"]["scoring"]]
                            ann_finalTuneMetrics["number of models"] = [ann_tuning_results.loc["value"]["number of models"]]
                            ann_finalTuneMetrics["mean cv score"] = [ann_tuning_results.loc["value"]["mean score"]]
                            ann_finalTuneMetrics["standard deviation cv score"] = [ann_tuning_results.loc["value"]["std score"]]
                            ann_finalTuneMetrics["test data score"] = [ann_tuning_results.loc["value"]["test score"]]
                            st.write(ann_finalTuneMetrics)
                            if sett_hints:
                                st.info(str(fc.learning_hints("mod_md_hypeTune_ANN_details")))
                            st.write("")

                # Download link for hyperparameter output
                output = BytesIO()
                excel_file = pd.ExcelWriter(output, engine="xlsxwriter")
                if any(a for a in sb_ML_alg if a == "Random Forest"):
                    rf_finalPara.to_excel(excel_file, sheet_name="RF_final_hyperparameters")
                    if do_hypTune == "Yes":
                        rf_finalTuneMetrics.to_excel(excel_file, sheet_name="RF_tuning_details")
                if any(a for a in sb_ML_alg if a == "Boosted Regression Trees"):
                    brt_finalPara.to_excel(excel_file, sheet_name="BRT_final_hyperparameters")
                    if do_hypTune == "Yes":
                        brt_finalTuneMetrics.to_excel(excel_file, sheet_name="BRT_tuning_details")
                if any(a for a in sb_ML_alg if a == "Artificial Neural Networks"):
                    ann_finalPara.to_excel(excel_file, sheet_name="ANN_final_hyperparameters")
                    if do_hypTune == "Yes":
                        ann_finalTuneMetrics.to_excel(excel_file, sheet_name="ANN_tuning_details")
                excel_file.save()
                excel_file = output.getvalue()
                b64 = base64.b64encode(excel_file)
                dl_file_name = "Hyperparameter-tuning output__" + df_name + ".xlsx"
                st.markdown(
                    f"""
                <a href="data:file/excel_file;base64,{b64.decode()}" id="button_dl" download="{dl_file_name}">Download hyperparameter-tuning output</a>
                """,
                unsafe_allow_html=True)
                st.write("")

#--------------------------------------------------------------------------------------
