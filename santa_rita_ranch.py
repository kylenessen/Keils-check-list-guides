#%%
from bs4 import BeautifulSoup
import pandas as pd
import chardet

with open("santa_rita_ranch.html", "rb") as file:
    raw_data = file.read()
    detected_encoding = chardet.detect(raw_data)["encoding"]

with open("santa_rita_ranch.html", "r", encoding=detected_encoding) as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, "html.parser")

main_div = soup.find("div", {"id": "ipl-content"})

rows = main_div.find_all("td", class_="A12")

columns = ["Scientific Name", "Common Name", "Family Name"]
df = pd.DataFrame(columns=columns)

for row in rows:
    scientific_name = row.find("a", class_="dgrayLink").text.strip()
    common_name = row.find("i").text.strip()
    family_name = row.find("a", class_="familyLink").text.strip()
    
    data = {"Scientific Name": scientific_name, "Common Name": common_name, "Family Name": family_name}
    df = df.append(data, ignore_index=True)


# %%
