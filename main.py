import streamlit as st
import requests
import zipfile
import io
from PIL import Image
from collections import OrderedDict, defaultdict

st.title("🫀Mitral Insights Analyzer")
st.markdown(
    """
    <h4>Welcome to the Mitral Insights Analyzer!</h4> 
    <p style='font-size:18px;'>This tool helps analyze data from patients affected by <b>mitral regurgitation</b>, a condition where the heart's mitral valve doesn't close tightly, causing blood to flow backward.</p>
     
    <p style='font-size:18px;'>Our goal is to leverage patient data to <b>identify key clinical parameters</b> that influence the <b>severity and size</b> of the regurgitation.</p>

    <p style='font-size:18px;'>📊 Upload your Excel file, and let’s dive into the insights together!</p>
    """, unsafe_allow_html=True
)

uploaded_file = st.file_uploader("Upload your Excel file with patience data here", type=['xlsx'])

if uploaded_file is not None:
    st.success("File uploaded successfully!")
    cross_correlation_button = st.button("Process File for Cross Correlation")
    analysis_prediction_button = st.button("Process File for Analysis and Prediction")

    if cross_correlation_button:
        try:
            with st.spinner("Processing the file..."):
                files = {"file": uploaded_file}
                response = requests.post("http://localhost:8000/get-cross-correlation/", files=files)

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

                        # Display results in tables for each patient
                    for patient, comparisons in patient_images.items():
                        st.subheader(f"Results for {patient}")

                        # Collect all column headers
                        col_headers = set()
                        for row_data in comparisons.values():
                            col_headers.update(row_data.keys())
                        col_headers = sorted(col_headers)

                        # Create a table for the patient
                        for row_criteria, col_data in comparisons.items():
                            row = st.columns(spec=len(col_headers))
                            i = 0
                            for col_criteria in col_headers:
                                if col_criteria in col_data:
                                    image = col_data[col_criteria]
                                    row[i].image(image=image, caption=f"{row_criteria} vs {col_criteria}")
                                i += 1
                else:
                    st.error(f"Failed to process the file. Error: {response.text}")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    
    if analysis_prediction_button:
        try:
            with st.spinner("Processing the file..."):
                files = {"file": uploaded_file}
                response = requests.post("http://localhost:8000/analyze-data/", files=files)

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

                    for type, predictions in analysis_images.items():
                        st.subheader(type)

                        col_headers = set()
                        for row_data in predictions.values():
                            col_headers.update(row_data.keys())
                        col_headers = sorted(col_headers)

                        for row_criteria, col_data in predictions.items():
                            row = st.columns(spec=len(col_headers))
                            i = 0
                            for col_criteria in col_headers:
                                if col_criteria in col_data:
                                    image = col_data[col_criteria]
                                    row[i].image(image=image, caption=f"{row_criteria}: {col_criteria}")
                                i += 1
                else:
                    st.error(f"Failed to process the file. Error: {response.text}")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")


