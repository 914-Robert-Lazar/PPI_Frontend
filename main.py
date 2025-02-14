import streamlit as st
import requests
import zipfile
import io
from PIL import Image
from collections import OrderedDict

st.title("🫀Mitral Insights Analyzer")
st.markdown(
    """
    <style>
        div.stButton > button:hover {
            background-color: #006100; /* Change color on hover */
            color: #FFD700; /* Change text color on hover */
        }
    </style>
    <h4>Welcome to the Mitral Insights Analyzer!</h4> 
    <p style='font-size:18px;'>This tool helps analyze data from patients affected by <b>mitral regurgitation</b>, a condition where the heart's mitral valve doesn't close tightly, causing blood to flow backward.</p>
     
    <p style='font-size:18px;'>Our goal is to leverage patient data to <b>identify key clinical parameters</b> that influence the <b>severity and size</b> of the regurgitation.</p>

    <p style='font-size:18px;'>📊 Upload your Excel file, and let’s dive into the insights together!</p>

    <h4>Project Scope</h4>

    <p style='font-size:18px;'>📊 <b>Data Collection</b>: Aggregating comprehensive patient data, including clinical and diagnostic information.</p>

    <p style='font-size:18px;'>🔬 <b>Parameter Analysis</b>: Evaluating multiple clinical parameters such as valve morphology and other relevant metrics to determine their impact on regurgitation size.</p>

    <p style='font-size:18px;'>🤖 <b>Machine Learning Models</b>: Utilizing statistical and machine learning models to predict the importance of relevant metrics in the regurgitation evolution.</p>

    <p style='font-size:18px;'>📈 <b>Visualization</b>: Providing a user-friendly interface to visualize and interpret the data, insights, and predictions for better clinical decision-making.</p>

    <p style='font-size:18px;'>❤️ <b>Outcome</b>: Assisting healthcare professionals in identifying critical factors that contribute to mitral regurgitation severity, potentially guiding more personalized treatment strategies.</p>
    """, unsafe_allow_html=True
)

with st.expander("File constraints"):
    st.markdown(
        """
        <h5>The uploaded .xlsx file contains the following structure:</h5>
        <h5>Columns:</h5>
        <p style='font-size:18px;'>1.	Patient ID (integer) - Identifier for each patient.</p>
        <p style='font-size:18px;'>2.	Cycle (integer) - Represents the cycle number.</p>
        <p style='font-size:18px;'>3.	Frame (integer) - The frame number in the cycle.</p>
        <p style='font-size:18px;'>4.	Time (moment) (integer) - The time point of measurement.</p>
        <p style='font-size:18px;'>5.	MR area cm2 (float) - Mitral Regurgitation area in cm².</p>
        <p style='font-size:18px;'>6.	MR VC mm (float) - Mitral Regurgitation vena contracta in mm.</p>
        <p style='font-size:18px;'>7.	LA area cm2 (float) - Left Atrium area in cm².</p>
        <p style='font-size:18px;'>8.	LA length cm (float) - Left Atrium length in cm.</p>
        <p style='font-size:18px;'>9.	MV tenting height mm (float) - Mitral Valve tenting height in mm.</p>
        <p style='font-size:18px;'>10.	MV annulus mm (float) - Mitral Valve annulus in mm.</p>
        <p style='font-size:18px;'>11.	LV area cm2 (float) - Left Ventricle area in cm².</p>
        <p style='font-size:18px;'>12.	LV length cm (float) - Left Ventricle length in cm.</p>
        <p style='font-size:18px;'>13.	RR interval msec (integer) - RR interval in milliseconds.</p>
        <h5>Data Requirements:</h5>
        <p style='font-size:18px;'>•	Each column must contain non-null values that match the specified data types.</p>
        <p style='font-size:18px;'>•	Patient ID should be unique to each patient.</p>
        <p style='font-size:18px;'>•	Cycle and Frame should represent the temporal progression of the measurements.</p>
        <p style='font-size:18px;'>•	Numerical columns (e.g., MR area, LA area) should be positive values.</p>

        """, unsafe_allow_html=True
    )
if "cross_correlation" not in st.session_state:
    st.session_state.cross_correlation = False

if "analysis_prediction" not in st.session_state:
    st.session_state.analysis_prediction = False

uploaded_file = st.file_uploader("Upload your Excel file with patience data here", type=['xlsx'])

if uploaded_file is not None:
    st.success("File uploaded successfully!")
    cross_correlation_button = st.button("Process File for Cross Correlation")
    analysis_prediction_button = st.button("Process File for Analysis and Prediction")

    if cross_correlation_button:
        st.session_state.analysis_prediction = False
        try:
            with st.spinner("Processing the file..."):
                files = {"file": uploaded_file}
                response = requests.post("https://ppi-backend-ejsz.onrender.com/get-cross-correlation/", files=files)

                if response.status_code == 200:
                    st.success("File processed successfully! Retrieving results...")

                    zip_content = io.BytesIO(response.content)

                    patient_images = OrderedDict()

                    with zipfile.ZipFile(zip_content, 'r') as zip_ref:
                        for file_name in zip_ref.namelist():
                            if file_name.endswith('.png'):
                                parts = file_name.split('_')
                                if len(parts) >= 5:
                                    patient = parts[0] + ": " + parts[1]
                                    row_criteria = parts[2] + " " + parts[3]
                                    col_criteria = " ".join(parts[5:]).replace(".png", "")
                                    image = Image.open(zip_ref.open(file_name))

                                    if patient not in patient_images:
                                        patient_images[patient] = OrderedDict()

                                    if row_criteria not in patient_images[patient]:
                                        patient_images[patient][row_criteria] = OrderedDict()

                                    patient_images[patient][row_criteria][col_criteria] = image

                    st.session_state.patient_images = patient_images
                    st.session_state.cross_correlation = True
                else:
                    st.error(f"❌ Failed to process the file. Error: {response.text}")

        except Exception as e:
            st.error(f"⚠️ An error occurred: {str(e)}")
    if st.session_state.cross_correlation:
    
        def next(): 
            if st.session_state.patient_counter < len(st.session_state.patient_images) - 1:
                st.session_state.patient_counter += 1
        def prev(): 
            if st.session_state.patient_counter > 0:
                st.session_state.patient_counter -= 1

        if 'patient_counter' not in st.session_state: st.session_state.patient_counter = 0

        patient_images = st.session_state.patient_images
        patient_list = list(patient_images.keys())
        selected_patient = patient_list[st.session_state.patient_counter]

        comparisons = patient_images[selected_patient]
        st.subheader(f"📊 Results for {selected_patient}")

        col_headers = sorted({col for row_data in comparisons.values() for col in row_data.keys()})

        for row_criteria, col_data in comparisons.items():
            row = st.columns(len(col_headers))
            for i, col_criteria in enumerate(col_headers):
                if col_criteria in col_data:
                    image = col_data[col_criteria]
                    row[i].image(image=image, caption=f"{row_criteria} vs {col_criteria}")

        cols = st.columns(2)
        with cols[1]: st.button("Next ➡️", on_click=next, use_container_width=True)
        with cols[0]: st.button("⬅️ Previous", on_click=prev, use_container_width=True) 

            
    if analysis_prediction_button:
        st.session_state.cross_correlation = False
        try:
            with st.spinner("Processing the file..."):
                files = {"file": uploaded_file}
                response = requests.post("https://ppi-backend-ejsz.onrender.com/analyze-data/", files=files)

                if response.status_code == 200:
                    st.success("File processed successfully! Retrieving results...")

                    zip_content = io.BytesIO(response.content)

                    analysis_images = OrderedDict()

                    with zipfile.ZipFile(zip_content, 'r') as zip_ref:
                        for file_name in zip_ref.namelist():
                            if file_name.endswith('.png'):
                                parts = file_name.split('_')
                                if len(parts) >= 4:
                                    type = parts[0]
                                    row_criteria = parts[1]
                                    col_criteria = " ".join(parts[2:]).replace(".png", "")
                                    image = Image.open(zip_ref.open(file_name))

                                    if type not in analysis_images:
                                        analysis_images[type] = OrderedDict()

                                    if row_criteria not in analysis_images[type]:
                                        analysis_images[type][row_criteria] = OrderedDict()

                                    analysis_images[type][row_criteria][col_criteria] = image

                    # image_files = ["classification_MR area cm2_actual_vs_predicted.png", "classification_MR area cm2_feature_importance.png",
                    #                "classification_MR VC mm_actual_vs_predicted.png", "classification_MR VC mm_feature_importance.png",
                    #                "regression_MR area cm2_actual_vs_predicted.png", "regression_MR area cm2_feature_importance.png",
                    #                "regression_MR VC mm_actual_vs_predicted.png", "regression_MR VC mm_feature_importance.png"]
                    # for file_name in image_files:
                    #     if file_name.endswith('.png'):
                    #         parts = file_name.split('_')
                    #         if len(parts) >= 4:
                    #             type = parts[0]
                    #             row_criteria = parts[1]
                    #             col_criteria = " ".join(parts[2:]).replace(".png", "")
                    #             image = Image.open(file_name)

                    #             if type not in analysis_images:
                    #                 analysis_images[type] = OrderedDict()

                    #             if row_criteria not in analysis_images[type]:
                    #                 analysis_images[type][row_criteria] = OrderedDict()

                    #             analysis_images[type][row_criteria][col_criteria] = image
                    
                    st.session_state.analysis_images = analysis_images
                    st.session_state.analysis_prediction = True

    
                else:
                    st.error(f"❌ Failed to process the file. Error: {response.text}")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    if st.session_state.analysis_prediction:

        def next(): 
            if st.session_state.type_counter < len(st.session_state.analysis_images) - 1:
                st.session_state.type_counter += 1
        def prev(): 
            if st.session_state.type_counter > 0:
                st.session_state.type_counter -= 1

        if 'type_counter' not in st.session_state: st.session_state.type_counter = 0

        analysis_images = st.session_state.analysis_images
        type_list = list(analysis_images.keys())
        selected_type = type_list[st.session_state.type_counter]

        predictions = analysis_images[selected_type]
        st.subheader(selected_type)

        col_headers = set()
        for row_data in predictions.values():
            col_headers.update(row_data.keys())
        col_headers = sorted(col_headers)

        for row_criteria, col_data in predictions.items():
            row = st.columns(spec=len(col_headers))
            for i, col_criteria in enumerate(col_headers):
                if col_criteria in col_data:
                    image = col_data[col_criteria]
                    row[i].image(image=image, caption=f"{row_criteria}: {col_criteria}")

        cols = st.columns(2)
        with cols[1]: st.button("Next ➡️", on_click=next, use_container_width=True)
        with cols[0]: st.button("⬅️ Previous", on_click=prev, use_container_width=True) 

