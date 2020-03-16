#!/usr/bin/env python
# coding: utf-8

# In[57]:


import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from datetime import timedelta
import pandas as pd

def extract_numbers_from_text(text):
    # Se parte el código por cualquiera de los caracteres incdicados en la regex
    splited = re.compile("[,;:\[\]\(\)\s]").split(text)
    # Se devuelven los que sean dígitos
    return [int(i) for i in splited if i.isdigit()] 


# In[64]:


AWS_ACCESS_KEY_ID = 'AKIAY3VGYQU2MOJPJIMN'
AWS_SECRET_ACCESS_KEY = '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'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = 'images.webbuildeer.com'
AWS_S3_REGION_NAME = 'eu-west-1'
AWS_DEFAULT_ACL = None


# In[74]:


import boto3
from botocore.exceptions import NoCredentialsError

def upload_to_aws(local_file, bucket, s3_file, access_key, secret_key):
    s3 = boto3.client('s3', aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


# In[45]:


# Loads HTML into soup.
url = "https://www.elmundo.es/ciencia-y-salud/salud/2020/03/11/5e68b4e621efa06b2f8b45f6.html"
class_ = "ue-c-card__link"

response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Locates target table with usefull info.
target_links = soup.find_all("a", class_=class_)
target_url = target_links[0]["href"]


# In[75]:


class_ = "ue-c-article_list"

response = requests.get(target_url)
soup = BeautifulSoup(response.content, "html.parser")

# Locates target table with usefull info.
target_tables = soup.find_all("ul", class_=class_)
target_total = target_tables[0].find("p")
target_data = target_tables[0].findAll("li")


altas = extract_numbers_from_text(target_data.pop().get_text().replace('.', ''))[0]
total = extract_numbers_from_text(target_total.get_text().replace('.', ''))[0]
print(total)

datos_espana = []
fecha = datetime.now() + timedelta(hours=1)
fecha = fecha.strftime('%Y-%m-%d %H:%M')
timestamp = datetime.now().timestamp()

for line in target_data:
    comunidad = [timestamp, fecha]
    text = line.get_text().replace('.', '')
    comunidad.append(text.split('en ')[1].split(' (')[0])
    for dato in extract_numbers_from_text(text):
        comunidad.append(dato)
    datos_espana.append(comunidad)

total_muertes = 0
for dato in datos_espana:
    try:
        total_muertes += dato[4]
    except:
        pass

pd.DataFrame([[timestamp,fecha,total,total_muertes,altas]]).to_csv("coronavirus-total.csv", mode='a', header=False, index=False)
pd.DataFrame(datos_espana).to_csv("coronavirus.csv", mode='a', header=False, index=False)
upload_to_aws("coronavirus.csv", AWS_STORAGE_BUCKET_NAME, "coronavirus.csv", AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
upload_to_aws("coronavirus-total.csv", AWS_STORAGE_BUCKET_NAME, "coronavirus-total.csv", AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

