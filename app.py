import streamlit as st 
from streamlit_option_menu import option_menu
import numpy as np 
import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt 
from minio import Minio
from PIL import Image, ImageOps
from io import BytesIO
import plotly.express as px
import hydralit_components as hc
import utils as ut
import os
import requests
import streamlit.components.v1 as components
import uuid
#from katonic.pipeline.pipeline import dsl, create_component_from_func, compiler, Client
#import kfp 
import os
os.system("pip install pandas pmdarima statsmodels minio")
from minio import Minio
import statsmodels.api as sm
import time
import sys
import os
import shutil
import errno
import subprocess
import tempfile
from tempfile import mkdtemp
import shortuuid

ACCESS_KEY = "DNPD2SAYLBELJ423HCNU"
SECRET_KEY = "zF7F6W93HS8vt+JKen4U17+zhcHiwH47AMuO3ap0"
PUBLIC_BUCKET = "shared-storage"

client = Minio(
        endpoint="minio-server.default.svc.cluster.local:9000",
        access_key=ACCESS_KEY,
        secret_key=SECRET_KEY,
        secure=False,
    )

count1 = 0
routes = os.environ["ROUTE"]

response = requests.get(url='https://katonic.ai/favicon.ico')
im = Image.open(BytesIO(response.content))

st.set_page_config(
    page_title='Multi-Touch-Attribution-markov-chain', 
    page_icon = im, 
    layout = 'wide', 
    initial_sidebar_state = 'auto'
)

menu_data = [
        {'icon': "🚀", 'label':"User-guide"},
        {'icon': "🚀", 'label':"App"},
]

over_theme = {'txc_inactive': '#FFFFFF'}
menu_id = hc.nav_bar(menu_definition=menu_data,home_name='Home',override_theme=over_theme)

if menu_id=="Home":
    st.title("ocr-PDF-to-Text Extractor📃")

    st.write("""The PDF (Portable Document Format) is here to stay. In today’s work environment, the PDF became ubiquitous as a digital replacement for paper and holds a variety of important business data.
    But what are the options if you want to extract data from PDF documents? Manually rekeying PDF data is often the first reflex but fails most of the time for various reasons.""")
    st.write("""OCR technology in **bank statement processing** has enabled financial institutions to automate data extraction from account statements and process information more efficiently. 
            Bank statement processing automation involves accurately scanning forms and document images, interpreting them, and validating data to ensure there are no errors or missing values.""")

    img1 = Image.open('image/pdf-to-ocr.jpg')
    st.image(img1,use_column_width=False)


if menu_id=="User-guide":
    st.title("User-Guide")

    st.write("#### Automation to the tedious Data-entry Work")  
    st.write("---")
    st.write("""#### Step 1: Upload pdf.""")
    st.write("""###### you can upload multiple pdf files/Scanned pdf files at a time size_limit=200MB.""")
    st.write("""#### Step 2: Extract the text.""")
    st.write("""###### click on the extract the text button to process your uploaded pdf to get extracted.""")  
    st.write("""#### Step 3: Download the Extracted Text.""")
    st.write("""###### you can review and download your extracted text for further usage.""")

if menu_id=="App":
    st.title("Pdf-to-Text Extractor")
    uuids = []
    uploaded_file = st.file_uploader('Choose single or multiple .pdf files', type="pdf",accept_multiple_files=True)
    for i in uploaded_file:
        #suuid = shortuuid.ShortUUID().random(length=10)
        with open(os.path.join("inputs",i.name),"wb") as f:
            f.write(i.getbuffer())
        #uuids.append(suuid)
        if uploaded_file is not None:
            client_data = f"/pdf-to-text_uploaded_input/{i.name}"
            client.fput_object(
                PUBLIC_BUCKET,
                client_data,
                f"inputs/{i.name}"
            )
            
    print(uploaded_file)
    print(uuids)
    
    try:
        from PIL import Image
    except ImportError:
        print('Error: You need to install the "Image" package. Type the following:')
        print('pip install Image')

    try:
        import pytesseract
    except ImportError:
        print('Error: You need to install the "pytesseract" package. Type the following:')
        print('pip install pytesseract')
        exit()

    try:
        from pdf2image import convert_from_path, convert_from_bytes
    except ImportError:
        print('Error: You need to install the "pdf2image" package. Type the following:')
        print('pip install pdf2image')
        exit()

    def update_progress(progress):
        barLength = 10 
        status = ""
        if isinstance(progress, int):
            progress = float(progress)
        if not isinstance(progress, float):
            progress = 0
            status = "error: progress var must be float\r\n"
        if progress < 0:
            progress = 0
            status = "Halt...\r\n"
        if progress >= 1:
            progress = 1
            status = "\r\n"
        block = int(round(barLength*progress))
        text = "\rPercent: [{0}] {1}% {2}".format(
            "#"*block + "-"*(barLength-block), progress*100, status)
        sys.stdout.write(text)
        sys.stdout.flush()

    def run(args): 
        try:
            pipe = subprocess.Popen(
                args,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
        except OSError as e:
            if e.errno == errno.ENOENT:
                # File not found.
                # This is equivalent to getting exitcode 127 from sh
                raise exceptions.ShellError(
                    ' '.join(args), 127, '', '',
                )

        # pipe.wait() ends up hanging on large files. using
        # pipe.communicate appears to avoid this issue
        stdout, stderr = pipe.communicate()

        # if pipe is busted, raise an error (unlike Fabric)
        if pipe.returncode != 0:
            raise exceptions.ShellError(
                ' '.join(args), pipe.returncode, stdout, stderr,
            )

        return stdout, stderr

    def extract_tesseract(filename):
        temp_dir = mkdtemp()
        base = os.path.join(temp_dir, 'conv')
        print("----------")
        print(base)
        print("----------")
        contents = []
        try:
            stdout, _ = run(['pdftoppm', filename, base])
            print("----------")
            print(stdout)
            print("----------")
            for page in sorted(os.listdir(temp_dir)):
                page_path = os.path.join(temp_dir, page)
                page_content = pytesseract.image_to_string(Image.open(page_path))
                contents.append(page_content)
            return ''.join(contents)
        finally:
            shutil.rmtree(temp_dir)

    def convert_recursive(source, destination, count):
        pdfCounter = 0
        for dirpath, dirnames, files in os.walk(source):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdfCounter += 1
    
        for dirpath, dirnames, files in os.walk(source):
            for name in files:
                filename, file_extension = os.path.splitext(name)
                if (file_extension.lower() != '.pdf'):
                    continue
                relative_directory = os.path.relpath(dirpath, source)
                source_path = os.path.join(dirpath, name)
                output_directory = os.path.join(destination, relative_directory)
                output_filename = os.path.join(output_directory, filename + '.txt')
                if not os.path.exists(output_directory):
                    os.makedirs(output_directory)
                count = convert(source_path, output_filename, count, pdfCounter)
            print("----------")
            print(count)
            print("----------")
        print(count)
        return count

    def convert(sourcefile, destination_file, count, pdfCounter):
        text = extract_tesseract(sourcefile)
        with open(destination_file, 'w', encoding='utf-8') as f_out:
            f_out.write(text)
        
        #output = st.text_area("Extracted_text...",text,height=220)
        #st.download_button(label="Download data as txt", data=output, file_name='output.txt', mime='txt')

        print('Converted ' + source)
        count += 1
        update_progress(count / pdfCounter)
        return count

    count = 0
    print('********************************')
    print('*** PDF to TXT file, via OCR ***')
    print('********************************')
    source = 'inputs'
    destination = 'outputs'
    
    if (os.path.exists(source)):
        if (os.path.isdir(source)):
            count = convert_recursive(source, destination, count)
        elif os.path.isfile(source):  
            filepath, fullfile = os.path.split(source)
            filename, file_extension = os.path.splitext(fullfile)
            if (file_extension.lower() == '.pdf'):
                count = convert(source, os.path.join(destination, filename + '.txt'), count, 1)
        plural = 's'
        if count == 1:
            plural = ''
            print(str(count) + ' file' + plural + ' converted')
        else:
            print('The path ' + source + 'seems to be invalid')

    import glob
    my_files = glob.glob('outputs/*.txt')
    if st.button("Extact Text"):
        for i in my_files:
            out_files = open(i)
            text = out_files.read()
            output = st.text_area("Extracted_text...",text,height=220)
            st.download_button(label="Download data as txt", data=output, file_name=i, mime='txt')

        for i in my_files:
            extracted_text = f"pdf_to_text_app_output/{i}"  
            client.fput_object(
                PUBLIC_BUCKET,
                extracted_text,
                i
            )
        st.success("Successfully extracted the text, you can download your generated-text now")

    
