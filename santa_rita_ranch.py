#%%
from bs4 import BeautifulSoup
import pandas as pd
import chardet
import time

with open("santa_rita_ranch.html", "rb") as file:
    raw_data = file.read()
    detected_encoding = chardet.detect(raw_data)["encoding"]

with open("santa_rita_ranch.html", "r", encoding=detected_encoding) as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, "html.parser")

# Find the table that contains the table rows
table = soup.find("table", {"cellspacing": "0", "cellpadding": "0"})

# Extract the rows by searching for the "A12" class
rows = table.find_all("td", class_="A12")

columns = ["Scientific Name", "Common Name", "Family Name", "Image 1", "Image 2", "Image 3", "URL"]
df = pd.DataFrame(columns=columns)

for row in rows:
    scientific_name_tag = row.find("a", class_="dgrayLink")
    common_name_tag = row.find("i")
    family_name_tag = row.find("a", class_="familyLink")

    if scientific_name_tag and common_name_tag and family_name_tag:
        scientific_name = scientific_name_tag.text.strip()
        common_name = common_name_tag.text.strip()
        family_name = family_name_tag.text.strip()

        # Extract image URLs
        images = row.find_all("img", class_="iplPhotoB")
        image_urls = ["https://calflora.org" + img["src"] for img in images]

        # Extract URL
        url = "https://calflora.org" + scientific_name_tag["href"]

        data = {
            "Scientific Name": scientific_name,
            "Common Name": common_name,
            "Family Name": family_name,
            "Image 1": image_urls[0] if len(image_urls) > 0 else None,
            "Image 2": image_urls[1] if len(image_urls) > 1 else None,
            "Image 3": image_urls[2] if len(image_urls) > 2 else None,
            "URL": url
        }
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)

def proper_case(s):
    return s.capitalize()

df['Family Name'] = df['Family Name'].apply(proper_case)

df

# %%
import requests

def get_inaturalist_data(scientific_name):
    base_url = "https://api.inaturalist.org/v1/taxa"
    query = {"q": scientific_name, "order": "desc", "order_by": "observations_count"}
    try:
        response = requests.get(base_url, params=query)
        data = response.json()

        if data["total_results"] > 0:
            result = data["results"][0]

            default_photo_url = result["default_photo"]["url"] if result.get("default_photo") else None
            wikipedia_url = result["wikipedia_url"] if result.get("wikipedia_url") else None

            return default_photo_url, wikipedia_url
        else:
            return None, None
    except Exception as e:
        print(f"Error processing {scientific_name}: {e}")
        return None, None


# ...
# Previous code to create the initial DataFrame (df)
# ...

columns.extend(["iNaturalist Photo URL", "Wikipedia URL"])
df_expanded = pd.DataFrame(columns=columns)

for _, row in df.iterrows():
    time.sleep(1)
    scientific_name = row["Scientific Name"]
    print(f"Processing {scientific_name}")
    default_photo_url, wikipedia_url = get_inaturalist_data(scientific_name)

    data = {
        "Scientific Name": row["Scientific Name"],
        "Common Name": row["Common Name"],
        "Family Name": row["Family Name"],
        "Image 1": row["Image 1"],
        "Image 2": row["Image 2"],
        "Image 3": row["Image 3"],
        "URL": row["URL"],
        "iNaturalist Photo URL": default_photo_url,
        "Wikipedia URL": wikipedia_url
    }
    df_expanded = pd.concat([df_expanded, pd.DataFrame([data])], ignore_index=True)

df_expanded

#%%
df = df_expanded

# %%
jepson = pd.read_csv("jepson_eflora.csv")

# replace subsp. with ssp.
jepson["Scientific Name"] = jepson["Scientific Name"].str.replace("subsp.", "ssp.")

# %% match scientific names in df and jepson and add URL to df
def get_jepson_url(scientific_name):
    try:
        url = jepson[jepson["Scientific Name"] == scientific_name]["URL"].values[0]
        return url
    except:
        return None

# %%
df["Jepson URL"] = df["Scientific Name"].apply(get_jepson_url)
# %%
