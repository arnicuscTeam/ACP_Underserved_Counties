import os
import random
import shutil
import time
import urllib.request
import zipfile
from datetime import datetime
import geopandas as gpd

import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager  # pip install webdriver_manager


def downloadShapeFiles_Block_Group(data_dir: str):
    """
    This function downloads the shape files for all the block groups in the US from the census website
    :param data_dir: The path to the data folder
    :return: None
    """

    shape_folder = data_dir + "Shape_Files/"

    block_group_folder = shape_folder + "Block_Group/"

    if not os.path.exists(block_group_folder):
        os.makedirs(block_group_folder)

    # Create a dictionary to store the state abbreviations
    state_dict = {"01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE",
                  "11": "DC", "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA",
                  "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
                  "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM",
                  "36": "NY", "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
                  "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
                  "54": "WV", "55": "WI", "56": "WY"}

    for key, value in state_dict.items():
        # Link for all 2022 block group shape files
        link = f"https://www2.census.gov/geo/tiger/TIGER2022/BG/tl_2022_{key}_bg.zip"

        # Create the folder name where all the contents from the zip will be stored
        folder_name = block_group_folder + value + "_Shape_Folder/"

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # Download the zip file
        urllib.request.urlretrieve(link, folder_name + f"tl_2022_{key}_bg22.zip")

        # Extract the zip file
        with zipfile.ZipFile(folder_name + f"tl_2022_{key}_bg22.zip", "r") as zip_ref:
            zip_ref.extractall(folder_name)

        # Delete the zip file
        os.remove(folder_name + f"tl_2022_{key}_bg22.zip")


def downloadShapeFiles_TabBlock(data_dir: str):
    """
    This function downloads the shape files for all the block in the US from the census website. This is used to find
    the blocks that are classified as Tribal by USAC. USAC provides a shape file for all tribal lands in the United
    States, but it does not have any descriptive information. Using ArcGIS, we map the block shape files and snap the
    block shape files to the Tribal shapefiles to identify which blocks are considered tribal and the associated data.
    :param data_dir: The path to the data folder
    :return: None
    """

    shape_folder = data_dir + "Shape_Files/"

    block_folder = shape_folder + "Block/"

    if not os.path.exists(block_folder):
        os.makedirs(block_folder)

    # Create a dictionary to store the state abbreviations
    state_dict = {"01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE",
                  "11": "DC", "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA",
                  "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
                  "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM",
                  "36": "NY", "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
                  "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
                  "54": "WV", "55": "WI", "56": "WY"}

    for key, value in state_dict.items():
        # Link for all 2022 block group shape files
        link = f"https://www2.census.gov/geo/tiger/TIGER2022/TABBLOCK20/tl_2022_{key}_tabblock20.zip"

        # Create the folder name where all the contents from the zip will be stored
        folder_name = block_folder + value + "_Shape_Folder/"

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # Download the zip file
        urllib.request.urlretrieve(link, folder_name + f"tl_2022_{key}_tabblock20.zip")

        # Extract the zip file
        with zipfile.ZipFile(folder_name + f"tl_2022_{key}_tabblock20.zip", "r") as zip_ref:
            zip_ref.extractall(folder_name)

        # Delete the zip file
        os.remove(folder_name + f"tl_2022_{key}_tabblock20.zip")


def clean_pop_density_file(data_dir: str):
    """
    This function cleans the population density file from the FCC.
    :param data_dir: The path to the data folder.
    :return: None
    """

    census_mid_files = data_dir + "ISP/Census_Mid_Files/"
    pop_density_file = census_mid_files + "pop_density.xlsx"

    df = pd.read_excel(pop_density_file, sheet_name="in", dtype={'fips': str})

    # zfill the fips column to 12 characters
    df['fips'] = df['fips'].apply(lambda x: x.zfill(12))

    # Create a tract column, which is the first 11 characters of the fips column
    df['tract'] = df['fips'].apply(lambda x: x[:11])

    # Aggregate the total_population and area_land columns by the tract column
    df = df.groupby('tract').agg({'total_population': 'sum', 'area_land': 'sum'}).reset_index()

    # Create a pop_density column, which is the total_population divided by the area_land
    df['pop_density'] = df['total_population'] / df['area_land']

    # If pop_density is null, set it to 0
    df['pop_density'] = df['pop_density'].fillna(0)

    # Save the dataframe as a csv
    df.to_csv(pop_density_file.replace('.xlsx', ".csv"), index=False)


def clean_tract_covered_pops(data_dir):
    """
    This function cleans the tract covered populations file from the FCC.
    :param data_dir: The path to the data folder.
    :return: None
    """

    census_mid_files = data_dir + "ISP/Census_Mid_Files/"
    tract_covered_pops_file = census_mid_files + "county_tract_total_covered_populations.xlsx"

    covered_populations_folder = data_dir + "Covered_Populations/"

    df = pd.read_excel(tract_covered_pops_file, sheet_name="tract_total_covered_populations",
                       dtype={'geo_id': str})

    # if pct or MOE in a column, remove the column
    for col in df.columns:
        if "pct" in col.lower() or "moe" in col.lower():
            df.drop(col, axis=1, inplace=True)

    # Drop geography name column
    df.drop("geography_name", axis=1, inplace=True)

    # Turn rural into binary, 1 if Rural, 0 if Not rural
    df['rural'] = df['rural'].apply(lambda x: 1 if x == "Rural" else 0)

    df.to_csv(covered_populations_folder + "tract_total_covered_populations.csv", index=False)


def clean_high_cost_areas(data_dir: str):

    """
    This function cleans the high-cost area file from the FCC.
    :param data_dir: The path to the data folder.
    :return: None
    """

    file = f"{data_dir}/ISP/Census_Mid_Files/high_cost_areas.csv"

    census_key = "494a9ee04209e13f2786105dd68cd4b5ac37f49d"

    df = pd.read_csv(file)

    df["Census Block Group"] = df["Census Block Group"].astype(str)
    df["Census Block Group"] = df["Census Block Group"].str.zfill(12)

    df["Tract"] = df["Census Block Group"].str[0:11]

    df = df.drop(columns=["State Name", "State FIPS"])

    df = df.rename(columns={"Census Block Group": "Block Group", "High Cost Block Group": "High Cost"})

    # Turn the high-cost column into a binary column
    df["High Cost"] = df["High Cost"].replace("High Cost", 1)

    for index, row in df.iterrows():
        block_group = row["Block Group"]
        high_cost = row["High Cost"]
        state = block_group[0:2]
        county = block_group[2:5]
        tract = block_group[5:11]
        block_group = block_group[11:12]

        url = (
            f"https://api.census.gov/data/2021/acs/acs5?get=B01003_001E&for=block%20group:{block_group}&in=state:{state}"
            f"&in=county:{county}&in=tract:{tract}&key={census_key}")
        try:
            response = requests.get(url).json()

            population = response[1][0]

            df.loc[index, "Population"] = population

        except:
            df.loc[index, "Population"] = 0

    df.to_csv(f"{data_dir}/ISP/Census_Mid_Files/high_cost_areas_clean.csv", index=False)


def collect_tribal_blocks(data_dir: str):
    isp_dir = data_dir + "ISP/"
    mid_files = isp_dir + "Census_Mid_Files/"
    tribal_blocks_folder = mid_files + "Tribal_blocks/"

    df = pd.DataFrame()

    for folder in os.listdir(tribal_blocks_folder):
        gdf = gpd.read_file(tribal_blocks_folder + folder + "/Tribal_Blocks.shp", dtype=str)

        gdf = gdf[["GEOID20", "HOUSING20", "POP20"]]

        df = pd.concat([df, gdf], ignore_index=True)

    df["HOUSING20"] = df["HOUSING20"].round(0).astype(int)
    df["POP20"] = df["POP20"].round(0).astype(int)

    df = df.rename(columns={"GEOID20": "Block", "HOUSING20": "Housing Units", "POP20": "Population"})

    df.to_csv(mid_files + "Tribal_Blocks.csv", index=False)


def get_census_data(data_dir: str):
    """
    This function downloads the census data for each state and saves it to a csv file. It also adds relevant data
    associated with the tract.
    :param data_dir: Path to the data directory.
    :return: None
    """

    acp_folder = data_dir + "ACP_Households/Final_Files/"
    tract_file = acp_folder + "Total-ACP-Households-by-tract.csv"

    acp_df = pd.read_csv(tract_file, dtype={"tract": str, "Total Subscribers": int})

    # Keep unique tracts and keep the last row for each tract after it is sorted by Data Month
    acp_df = acp_df.sort_values(by=["Data Month"])
    acp_df = acp_df.drop_duplicates(subset=["tract"], keep="last")
    acp_df = acp_df.reset_index(drop=True)
    acp_df = acp_df[["tract", "Total Subscribers"]]

    # Rename Total Subscribers to Total ACP Subscribed Households
    acp_df = acp_df.rename(columns={"Total Subscribers": "Total ACP Subscribed Households",
                                    "tract": "Tract"})

    covered_pop_folder = data_dir + "Covered_Populations/"
    covered_pop_file = covered_pop_folder + "tract_total_covered_populations.csv"

    covered_df = pd.read_csv(covered_pop_file, dtype={"geo_id": str, "rural": int})

    # Only keep geo_id and rural
    covered_df = covered_df[["geo_id", "rural"]]

    # Rename geo_id to tract
    covered_df = covered_df.rename(columns={"geo_id": "Tract"})

    population_density_file = data_dir + "ISP/Census_Mid_Files/pop_density.csv"

    pop_density_df = pd.read_csv(population_density_file, dtype={"tract": str})

    # Drop total_population and area_land columns
    pop_density_df = pop_density_df.drop(["total_population", "area_land"], axis=1)

    # Rename tract to Tract
    pop_density_df = pop_density_df.rename(columns={"tract": "Tract"})

    pop_density_df["pop_density"] = pop_density_df["pop_density"].round(2)

    providers_by_tract_folder = data_dir + "ISP/Providers_by_State/Providers_by_Tract/"

    high_cost_file = data_dir + "ISP/Census_Mid_Files/high_cost_areas_clean.csv"

    high_cost_df = pd.read_csv(high_cost_file, dtype={"Tract": str})

    high_cost_dict = {}

    for tract in high_cost_df["Tract"].unique():
        total_high_cost_pop = high_cost_df[high_cost_df["Tract"] == tract]["Population"].sum()

        high_cost_dict[tract] = total_high_cost_pop

    tribal_file = data_dir + "ISP/Census_Mid_Files/Tribal_Blocks.csv"

    tribal_df = pd.read_csv(tribal_file, dtype={"Block": str})

    tribal_df["Tract"] = tribal_df["Block"].str[:11]

    tribal_dict = {}

    for tract in tribal_df["Tract"].unique():
        total_tribal_pop = tribal_df[tribal_df["Tract"] == tract]["Population"].sum()

        tribal_dict[tract] = total_tribal_pop

    # Create a dictionary to store the state abbreviations
    state_dict = {"01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE",
                  "11": "DC", "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA",
                  "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
                  "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM",
                  "36": "NY", "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
                  "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
                  "54": "WV", "55": "WI", "56": "WY"}

    census_key = "494a9ee04209e13f2786105dd68cd4b5ac37f49d"

    # Path to the data folders
    census_data_folder = data_dir + "Census_Data/"

    # Create the folder if it doesn't exist
    if not os.path.exists(census_data_folder):
        os.mkdir(census_data_folder)

    # Iterate through the states
    for key, value in state_dict.items():

        provider_df = pd.read_csv(providers_by_tract_folder + value + "_Providers_by_Tract.csv", dtype=str)

        provider_df = provider_df[["Tract", "ISPs Count", "ISPs ACP Count"]]

        end_file = census_data_folder + value + "_Census_Tract_Data.csv"

        TOTAL_POPULATION = "B01003_001E"

        # RACE
        WHITE = "B02001_002E"
        BLACK = "B02001_003E"
        AIAN = "B02001_004E"
        ASIAN = "B02001_005E"
        NHOPI = "B02001_006E"
        HISPANIC = "B03003_003E"

        MEDIAN_AGE = "B01002_001E"
        HH_WITH_UNDER_18 = "B11005_002E"

        MEDIAN_HOUSEHOLD_INCOME = "B19013_001E"

        EDUCATION_8 = "B15003_012E"
        EDUCATION_12 = "B15003_017E"
        EDUCATION_12_ALT = "B15003_018E"
        EDUCATION_16 = "B15003_022E"
        EDUCATION_MASTERS = "B15003_023E"
        EDUCATION_PROFESSIONAL_DEGREE = "B15003_024E"
        EDUCATION_PHD = "B15003_024E"

        INC_TO_POVERTY_UNDER50 = "C17002_002E"
        INC_TO_POVERTY_50TO99 = "C17002_003E"

        TENURE = "B25003_001E"
        TENURE_OWNER_OCCUPIED = "B25003_002E"
        TENURE_RENTER_OCCUPIED = "B25003_003E"

        COMPUTER_AND_DIAL_UP = "B28003_003E"
        COMPUTER_AND_BROADBAND = "B28003_004E"
        COMPUTER_AND_NO_INTERNET = "B28003_005E"
        NO_COMPUTER = "B28003_006E"

        INTERNET_SUB = "B28002_002E"
        INTERNET_ANY_BB = "B28002_004E"
        NO_INTERNET_ACCESS = "B28002_013E"

        # Tract variables
        CITIZEN_BORN_US = "B05001_002E"
        CITIZEN_BORN_US_TERRITORIES = "B05001_003E"
        CITIZEN_BORN_ABROAD_AMERICAN_PARENTS = "B05001_004E"
        CITIZEN_NATURALIZATION = "B05001_005E"
        NOT_CITIZEN = "B05001_006E"
        LIMITED_ENGLISH_SPANISH = "B06007_005E"
        LIMITED_ENGLISH_OTHER = "B06007_008E"

        variables = {TOTAL_POPULATION: "Total Population",
                     WHITE: "White",
                     BLACK: "Black",
                     AIAN: "American Indian and Alaska Native",
                     ASIAN: "Asian",
                     NHOPI: "Native Hawaiian and Other Pacific Islander",
                     HISPANIC: "Hispanic",
                     MEDIAN_AGE: "Median Age",
                     MEDIAN_HOUSEHOLD_INCOME: "Median Household Income",
                     EDUCATION_8: "Less than 9th grade",
                     EDUCATION_12: "High school graduate",
                     EDUCATION_12_ALT: "GED or alternative credential",
                     EDUCATION_16: "Bachelor's degree",
                     EDUCATION_MASTERS: "Master's degree",
                     EDUCATION_PROFESSIONAL_DEGREE: "Professional school degree",
                     EDUCATION_PHD: "Doctorate degree",
                     INC_TO_POVERTY_UNDER50: "Under 50% of poverty level",
                     INC_TO_POVERTY_50TO99: "50% to 99% of poverty level",
                     TENURE: "Total housing units",
                     TENURE_OWNER_OCCUPIED: "Owner occupied",
                     TENURE_RENTER_OCCUPIED: "Renter occupied",
                     HH_WITH_UNDER_18: "Households with one more more people under 18",
                     COMPUTER_AND_DIAL_UP: "Computer with dial-up Internet subscription alone",
                     COMPUTER_AND_BROADBAND: "Computer and Broadband Internet subscription",
                     COMPUTER_AND_NO_INTERNET: "Computer and no Internet access",
                     NO_COMPUTER: "No computer",
                     INTERNET_SUB: "Internet Subscription",
                     INTERNET_ANY_BB: "Any Broadband Internet subscription",
                     NO_INTERNET_ACCESS: "No Internet access",
                     CITIZEN_BORN_US: "Born in the United States",
                     CITIZEN_BORN_US_TERRITORIES: "Born in Puerto Rico, U.S. Island areas, or born abroad to "
                                                  "American parent(s)",
                     CITIZEN_BORN_ABROAD_AMERICAN_PARENTS: "Born abroad to American parent(s)",
                     CITIZEN_NATURALIZATION: "Naturalized U.S. citizen",
                     NOT_CITIZEN: "Not a U.S. citizen",
                     LIMITED_ENGLISH_SPANISH: "Speak English less than \"very well\" (Spanish)",
                     LIMITED_ENGLISH_OTHER: "Speak English less than \"very well\" (other than Spanish)"
                     }

        host = 'https://api.census.gov/data'

        year = '/2021'

        detailed = '/acs/acs5'

        g = '?get='

        vrs = ''

        for v in variables.keys():
            vrs += f'{v},'

        vrs = vrs[:-1]

        location = f'&for=tract:*&in=state:{key}&in=county:*'

        usr_key = f"&key={census_key}"

        tract_query_url = f"{host}{year}{detailed}{g}{vrs}{location}{usr_key}"

        # Use requests package to call out the API
        response = requests.get(tract_query_url, timeout=100)

        # Convert the Response to text and print the result
        data = response.text.split("\n")

        new_data = []

        for row in data:
            row = row.replace("[", "")
            row = row.replace("]", "")
            row = row.replace("\"", "")
            row = row[:-1]

            row = row.split(",")
            new_data.append(row)

        census_df = pd.DataFrame(new_data[1:], columns=new_data[0])

        for column in census_df.columns:
            if column in variables.keys():
                census_df.rename(columns={column: variables[column]}, inplace=True)

        census_df["Tract"] = census_df['state'] + census_df['county'] + census_df['tract']

        census_df = census_df.drop(columns=['state', 'county', 'tract'])

        census_columns = census_df.columns.tolist()

        census_columns = census_columns[-1:] + census_columns[:-1]

        census_df = census_df[census_columns]

        # Replace all the -666666666 values with 0
        census_df = census_df.replace('-666666666', 0)
        census_df = census_df.replace('-666666666.0', 0)

        census_df = census_df.merge(acp_df, on="Tract", how="left")
        census_df = census_df.merge(covered_df, on="Tract", how="left")
        census_df = census_df.merge(pop_density_df, on="Tract", how="left")
        census_df = census_df.merge(provider_df, on="Tract", how="left")

        census_df["Total ACP Subscribed Households"] = census_df["Total ACP Subscribed Households"].fillna(0)
        census_df["Total ACP Subscribed Households"] = census_df["Total ACP Subscribed Households"].astype(int)

        census_df["rural"] = census_df["rural"].fillna(0)
        census_df["rural"] = census_df["rural"].astype(int)

        census_df["pop_density"] = census_df["pop_density"].fillna(0)

        census_df["ISPs Count"] = census_df["ISPs Count"].fillna(0)
        census_df["ISPs Count"] = census_df["ISPs Count"].astype(int)
        census_df["ISPs ACP Count"] = census_df["ISPs ACP Count"].fillna(0)
        census_df["ISPs ACP Count"] = census_df["ISPs ACP Count"].astype(int)
        census_df["Total Population"] = census_df["Total Population"].fillna(0)
        census_df["Total Population"] = census_df["Total Population"].astype(int)
        census_df["Total ACP Subscribed Households"] = census_df["Total ACP Subscribed Households"].fillna(0)
        census_df["Total ACP Subscribed Households"] = census_df["Total ACP Subscribed Households"].astype(int)

        census_df["High Cost"] = census_df.apply(lambda x: 1 if x["Tract"] in high_cost_dict.keys() and
                                                                high_cost_dict[x["Tract"]] >= x[
                                                                    "Total Population"] * 0.5 else 0, axis=1)

        census_df["Tribal"] = census_df.apply(lambda x: 1 if x["Tract"] in tribal_dict.keys() and
                                                             tribal_dict[x["Tract"]] >= x[
                                                                 "Total Population"] * 0.5 else 0, axis=1)

        census_df["ISP Desert"] = census_df.apply(
            lambda x: 1 if x["ISPs Count"] == 0 and (x["Total Population"] >= 50) else 0, axis=1)

        # Create the ACP Desert column if ISPs ACP Count is 0 and ISPs Count is not 0
        census_df["ACP Desert"] = census_df.apply(lambda x: 1 if x["ISPs ACP Count"] == 0 and
                                                                 (x["ISPs Count"] != 0 or
                                                                  x["Total ACP Subscribed Households"] > 0) else
        0, axis=1)

        for column in census_df.columns:
            if column == "Tract":
                census_df[column] = census_df[column].str.zfill(11)
            elif column == "Median Age" or column == "pop_density":
                census_df[column] = census_df[column].astype(float)
            else:
                census_df[column] = census_df[column].astype(int)

        census_df.to_csv(end_file, index=False)
        census_df.to_excel(end_file.replace(".csv", ".xlsx"), index=False)
