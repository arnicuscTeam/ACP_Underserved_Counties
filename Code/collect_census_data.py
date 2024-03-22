import os
import urllib.request
import zipfile
import geopandas as gpd

import pandas as pd
import requests


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
    This function downloads the shape files for all the block in the US from the census website
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

    census_mid_files = data_dir + "Census_Data/Census_Mid_Files/"
    pop_density_file = census_mid_files + "pop_density.xlsx"

    df = pd.read_excel(pop_density_file, sheet_name="in", dtype={'fips': str})

    # zfill the fips column to 12 characters
    df['fips'] = df['fips'].apply(lambda x: x.zfill(12))

    county_df = df.copy()

    # Create a county column, which is the first 5 characters of the fips column
    county_df['county'] = county_df['fips'].apply(lambda x: x[:5])

    # Create a tract column, which is the first 11 characters of the fips column
    df['tract'] = df['fips'].apply(lambda x: x[:11])

    # Aggregate the total_population and area_land columns by the tract column
    df = df.groupby('tract').agg({'total_population': 'sum', 'area_land': 'sum'}).reset_index()

    # Aggregate the total_population and area_land columns by the county column
    county_df = county_df.groupby('county').agg({'total_population': 'sum', 'area_land': 'sum'}).reset_index()

    # Create a pop_density column, which is the total_population divided by the area_land
    df['pop_density'] = df['total_population'] / df['area_land']

    # Create a pop_density column, which is the total_population divided by the area_land
    county_df['pop_density'] = county_df['total_population'] / county_df['area_land']

    # If pop_density is null, set it to 0
    df['pop_density'] = df['pop_density'].fillna(0)

    # If pop_density is null, set it to 0
    county_df['pop_density'] = county_df['pop_density'].fillna(0)

    # Save the dataframe as a csv
    df.to_csv(pop_density_file.replace('.xlsx', "_tract.csv"), index=False)
    county_df.to_csv(pop_density_file.replace('.xlsx', "_county.csv"), index=False)


def clean_tract_covered_pops(data_dir: str):
    """
    This function cleans the tract covered populations file from the FCC.
    :param data_dir: The path to the data folder.
    :return: None
    """

    census_mid_files = data_dir + "Census_Data/Census_Mid_Files/"
    tract_covered_pops_file = census_mid_files + "county_tract_total_covered_populations.xlsx"

    covered_populations_folder = data_dir + "Covered_Populations/"

    df = pd.read_excel(tract_covered_pops_file, sheet_name="tract_total_covered_populations",
                       dtype={'geo_id': str})

    county_df = pd.read_excel(tract_covered_pops_file, sheet_name="county_total_covered_population",
                              dtype={'geo_id': str})

    # if pct or MOE in a column, remove the column
    for col in df.columns:
        if "pct" in col.lower() or "moe" in col.lower():
            df.drop(col, axis=1, inplace=True)

    for col in county_df.columns:
        if "pct" in col.lower() or "moe" in col.lower():
            county_df.drop(col, axis=1, inplace=True)

    # Drop geography name column
    df.drop("geography_name", axis=1, inplace=True)

    county_df.drop("geography_name", axis=1, inplace=True)

    # Turn rural into binary, 1 if Rural, 0 if Not rural
    df['rural'] = df['rural'].apply(lambda x: 1 if x == "Rural" else 0)

    # Turn rural into binary, 1 if Rural, 0 if Not rural
    county_df['rural'] = county_df['rural'].apply(lambda x: 1 if x == "Rural" else 0)

    df.to_csv(covered_populations_folder + "tract_total_covered_populations.csv", index=False)
    county_df.to_csv(covered_populations_folder + "county_total_covered_populations.csv", index=False)


def clean_high_cost_areas(data_dir: str):
    file = f"{data_dir}/Census_Data/Census_Mid_Files/high_cost_areas.csv"

    census_key = "494a9ee04209e13f2786105dd68cd4b5ac37f49d"

    df = pd.read_csv(file)

    df["Census Block Group"] = df["Census Block Group"].astype(str)
    df["Census Block Group"] = df["Census Block Group"].str.zfill(12)

    df["Tract"] = df["Census Block Group"].str[0:11]
    df["County"] = df["Census Block Group"].str[0:5]

    df = df.drop(columns=["State Name", "State FIPS"])

    df = df.rename(columns={"Census Block Group": "Block Group", "High Cost Block Group": "High Cost"})

    # Turn the high-cost column into a binary column
    df["High Cost"] = df["High Cost"].replace("High Cost", 1)

    for index, row in df.iterrows():
        block_group = row["Block Group"]
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

    df.to_csv(f"{data_dir}/Census_Data/Census_Mid_Files/high_cost_areas_clean.csv", index=False)


def collect_tribal_blocks(data_dir: str):
    isp_dir = data_dir + "Census_Data/"
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


def get_census_data_tract(data_dir: str, date: str = "06_30_2023"):
    """
    This function downloads the census data for each state and saves it to a csv file.
    :param data_dir: Path to the data directory.
    :param date: The date of the data we want to download
    :return: None
    """

    acp_folder = data_dir + "ACP_Households/Final_Files/"
    tract_file = acp_folder + "Total-ACP-Households-by-tract.csv"

    acp_df = pd.read_csv(tract_file, dtype={"tract": str, "Total Subscribers": int})

    # Keep unique tracts and keep the last row for each tract after it is sorted by Data Month
    acp_df = acp_df.sort_values(by=["Data Month"])
    acp_df = acp_df.drop_duplicates(subset=["tract"], keep="last")
    acp_df = acp_df.reset_index(drop=True)
    most_recent_date = acp_df["Data Month"].max()
    acp_df = acp_df[["tract", "Total Subscribers"]]

    # Rename Total Subscribers to Total ACP Subscribed Households
    acp_df = acp_df.rename(columns={"Total Subscribers": f"Total ACP Subscribed Households as of {most_recent_date}",
                                    "tract": "Tract"})

    covered_pop_folder = data_dir + "Covered_Populations/"
    covered_pop_file = covered_pop_folder + "tract_total_covered_populations.csv"

    covered_df = pd.read_csv(covered_pop_file, dtype={"geo_id": str, "rural": int})

    # Only keep geo_id and rural
    covered_df = covered_df[["geo_id", "rural"]]

    # Rename geo_id to tract
    covered_df = covered_df.rename(columns={"geo_id": "Tract"})

    population_density_file = data_dir + "Census_Data/Census_Mid_Files/pop_density_tract.csv"

    pop_density_df = pd.read_csv(population_density_file, dtype={"tract": str})

    # Drop total_population and area_land columns
    pop_density_df = pop_density_df.drop(["total_population", "area_land"], axis=1)

    # Rename tract to Tract
    pop_density_df = pop_density_df.rename(columns={"tract": "Tract"})

    pop_density_df["pop_density"] = pop_density_df["pop_density"].round(2)

    providers_by_tract_folder = data_dir + f"ISP/{date}/Providers_by_State/Providers_by_Tract/"

    high_cost_file = data_dir + "Census_Data/Census_Mid_Files/high_cost_areas_clean.csv"

    high_cost_df = pd.read_csv(high_cost_file, dtype={"Tract": str})

    high_cost_dict = {}

    for tract in high_cost_df["Tract"].unique():
        total_high_cost_pop = high_cost_df[high_cost_df["Tract"] == tract]["Population"].sum()

        high_cost_dict[tract] = total_high_cost_pop

    tribal_file = data_dir + "Census_Data/Census_Mid_Files/Tribal_Blocks.csv"

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

    if not os.path.exists(census_data_folder):
        os.mkdir(census_data_folder)

    tract_data_folder = census_data_folder + "Tract/"

    # Create the folder if it doesn't exist
    if not os.path.exists(tract_data_folder):
        os.mkdir(tract_data_folder)

    full_df = pd.DataFrame()

    # Iterate through the states
    for key, value in state_dict.items():

        provider_df = pd.read_csv(providers_by_tract_folder + value + "_Providers_by_Tract.csv", dtype=str)

        provider_df["ISPs ACP Count"] = provider_df["ISPs ACP Count"].astype(int)
        provider_df["ISPs Count"] = provider_df["ISPs Count"].astype(int)
        provider_df["Population"] = provider_df["Population"].astype(int)

        columns = provider_df.columns.tolist()

        columns = [columns[0]] + columns[4:]

        temp_prov = provider_df[columns].astype(str)

        # Create a new column called All ISPs
        temp_prov["All ISPs"] = ""

        # If the column starts with ISP, then add it to the All ISPs column
        for index, row in temp_prov.iterrows():
            for column in columns:
                if column.startswith("ISP"):
                    if row[column] != "nan" and row[column] != "0" and row[column] is not None:
                        temp_prov.at[index, "All ISPs"] += row[column] + " -- "

            temp_prov.at[index, "All ISPs"] = temp_prov.at[index, "All ISPs"][:-4]

            if temp_prov.at[index, "All ISPs"] == "":
                temp_prov.at[index, "All ISPs"] = "0"

        provider_df = provider_df[["Tract", "ISPs Count", "ISPs ACP Count"]]

        provider_df = provider_df.merge(temp_prov[["Tract", "All ISPs"]], on="Tract", how="left")

        end_file = tract_data_folder + value + "_Census_Tract_Data.csv"

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

        M5TO9 = "B01001_004E"
        M10TO14 = "B01001_005E"
        M15TO17 = "B01001_006E"
        M18TO19 = "B01001_007E"
        M20 = "B01001_008E"
        M21 = "B01001_009E"
        M22TO24 = "B01001_010E"
        M25TO29 = "B01001_011E"
        M30TO34 = "B01001_012E"
        M35TO39 = "B01001_013E"
        M40TO44 = "B01001_014E"
        M45TO49 = "B01001_015E"
        M50TO54 = "B01001_016E"
        M55TO59 = "B01001_017E"
        M60TO61 = "B01001_018E"
        M62TO64 = "B01001_019E"
        M65TO66 = "B01001_020E"
        M67TO69 = "B01001_021E"
        M70TO74 = "B01001_022E"
        M75TO79 = "B01001_023E"
        M80TO84 = "B01001_024E"
        M85PLUS = "B01001_025E"

        F5TO9 = "B01001_028E"
        F10TO14 = "B01001_029E"
        F15TO17 = "B01001_030E"
        F18TO19 = "B01001_031E"
        F20 = "B01001_032E"
        F21 = "B01001_033E"
        F22TO24 = "B01001_034E"
        F25TO29 = "B01001_035E"
        F30TO34 = "B01001_036E"
        F35TO39 = "B01001_037E"
        F40TO44 = "B01001_038E"
        F45TO49 = "B01001_039E"
        F50TO54 = "B01001_040E"
        F55TO59 = "B01001_041E"
        F60TO61 = "B01001_042E"
        F62TO64 = "B01001_043E"
        F65TO66 = "B01001_044E"
        F67TO69 = "B01001_045E"
        F70TO74 = "B01001_046E"
        F75TO79 = "B01001_047E"
        F80TO84 = "B01001_048E"
        F85PLUS = "B01001_049E"

        ONEPERSONHH = "B08201_007E"
        TWOPERSONHH = "B08201_013E"
        THREEPERSONHH = "B08201_019E"
        FOURMOREPERSONHH = "B08201_025E"

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
        INTERNET_SUB_CABLE_FIBER_DSL = "B28002_007E"
        NO_INTERNET_ACCESS = "B28002_013E"

        LT10KINC = "B28004_002E"
        LT10KINC_BB_SUB = "B28004_004E"
        GT10KINC_LT20KINC = "B28004_006E"
        GT10KINC_LT20KINC_BB_SUB = "B28004_008E"
        GT20KINC_LT35KINC = "B28004_010E"
        GT20KINC_LT35KINC_BB_SUB = "B28004_012E"
        GT35KINC_LT50KINC = "B28004_014E"
        GT35KINC_LT50KINC_BB_SUB = "B28004_016E"

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

                     M5TO9: "Male 5 to 9 years",
                     M10TO14: "Male 10 to 14 years",
                     M15TO17: "Male 15 to 17 years",
                     M18TO19: "Male 18 to 19 years",
                     M20: "Male 20 years",
                     M21: "Male 21 years",
                     M22TO24: "Male 22 to 24 years",
                     M25TO29: "Male 25 to 29 years",
                     M30TO34: "Male 30 to 34 years",
                     M35TO39: "Male 35 to 39 years",
                     M40TO44: "Male 40 to 44 years",
                     M45TO49: "Male 45 to 49 years",
                     M50TO54: "Male 50 to 54 years",
                     M55TO59: "Male 55 to 59 years",
                     M60TO61: "Male 60 to 61 years",
                     M62TO64: "Male 62 to 64 years",
                     M65TO66: "Male 65 to 66 years",
                     M67TO69: "Male 67 to 69 years",
                     M70TO74: "Male 70 to 74 years",
                     M75TO79: "Male 75 to 79 years",
                     M80TO84: "Male 80 to 84 years",
                     M85PLUS: "Male 85 and Over years",

                     F5TO9: "Female 5 to 9 years",
                     F10TO14: "Female 10 to 14 years",
                     F15TO17: "Female 15 to 17 years",
                     F18TO19: "Female 18 to 19 years",
                     F20: "Female 20 years",
                     F21: "Female 21 years",
                     F22TO24: "Female 22 to 24 years",
                     F25TO29: "Female 25 to 29 years",
                     F30TO34: "Female 30 to 34 years",
                     F35TO39: "Female 35 to 39 years",
                     F40TO44: "Female 40 to 44 years",
                     F45TO49: "Female 45 to 49 years",
                     F50TO54: "Female 50 to 54 years",
                     F55TO59: "Female 55 to 59 years",
                     F60TO61: "Female 60 to 61 years"}

        vars2 = {F62TO64: "Female 62 to 64 years",
                 F65TO66: "Female 65 to 66 years",
                 F67TO69: "Female 67 to 69 years",
                 F70TO74: "Female 70 to 74 years",
                 F75TO79: "Female 75 to 79 years",
                 F80TO84: "Female 80 to 84 years",
                 F85PLUS: "Female 85 and Over years",

                 ONEPERSONHH: "One person household",
                 TWOPERSONHH: "Two person household",
                 THREEPERSONHH: "Three person household",
                 FOURMOREPERSONHH: "Four or more person household",

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
                 INTERNET_SUB_CABLE_FIBER_DSL: "Cable, fiber optic, or DSL Internet subscription",
                 NO_INTERNET_ACCESS: "No Internet access",
                 LT10KINC: "Less than $10,000 household income",
                 LT10KINC_BB_SUB: "Less than $10,000 household income with Broadband Internet subscription",
                 GT10KINC_LT20KINC: "$10K to $20K household income",
                 GT10KINC_LT20KINC_BB_SUB: "$10K to $20K household income with Broadband Internet subscription",
                 GT20KINC_LT35KINC: "$20K to $35K household income",
                 GT20KINC_LT35KINC_BB_SUB: "$20K to $35K household income with Broadband Internet subscription",
                 GT35KINC_LT50KINC: "$35K to $50K household income",
                 GT35KINC_LT50KINC_BB_SUB: "$35K to $50K household income with Broadband Internet subscription",

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

        year = '/2022'

        detailed = '/acs/acs5'

        g = '?get='

        vrs = ''
        vrs2 = ''

        for v in variables.keys():
            vrs += f'{v},'

        for v in vars2.keys():
            vrs2 += f'{v},'

        vrs = vrs[:-1]
        vrs2 = vrs2[:-1]

        location = f'&for=tract:*&in=state:{key}&in=county:*'

        usr_key = f"&key={census_key}"

        tract_query_url = f"{host}{year}{detailed}{g}{vrs}{location}{usr_key}"
        tract_query_url2 = f"{host}{year}{detailed}{g}{vrs2}{location}{usr_key}"

        # Use requests package to call out the API
        response = requests.get(tract_query_url, timeout=100)
        response2 = requests.get(tract_query_url2, timeout=100)

        # Convert the Response to text and print the result
        data = response.text.split("\n")
        data2 = response2.text.split("\n")

        new_data = []
        new_data2 = []

        for row in data:
            index = data.index(row)

            row = row.replace("[", "")
            row = row.replace("]", "")
            row = row.replace("\"", "")
            if index < len(data) - 1:
                row = row[:-1]

            row = row.split(",")
            new_data.append(row)

        for row in data2:
            index = data2.index(row)

            row = row.replace("[", "")
            row = row.replace("]", "")
            row = row.replace("\"", "")
            if index < len(data2) - 1:
                row = row[:-1]

            row = row.split(",")
            new_data2.append(row)

        census_df = pd.DataFrame(new_data[1:], columns=new_data[0])
        census_df2 = pd.DataFrame(new_data2[1:], columns=new_data2[0])

        census_df = census_df.replace('-666666666', 0)
        census_df = census_df.replace('-666666666.0', 0)
        census_df2 = census_df2.replace('-666666666', 0)
        census_df2 = census_df2.replace('-666666666.0', 0)

        for column in census_df.columns:
            if column in variables.keys():
                census_df.rename(columns={column: variables[column]}, inplace=True)

        for column in census_df2.columns:
            if column in vars2.keys():
                census_df2.rename(columns={column: vars2[column]}, inplace=True)

        census_df = census_df.merge(census_df2, on=["state", "county", "tract"], how="left")

        census_df["state"] = census_df["state"].str.zfill(2)
        census_df["county"] = census_df["county"].str.zfill(3)
        census_df["tract"] = census_df["tract"].str.zfill(6)

        census_df["Tract"] = census_df['state'] + census_df['county'] + census_df['tract']

        census_df = census_df.drop(columns=['state', 'county', 'tract'])

        census_columns = census_df.columns.tolist()

        census_columns = census_columns[-1:] + census_columns[:-1]

        census_df = census_df[census_columns]

        # Replace all the -666666666 values with 0
        census_df = census_df.replace('-666666666', 0)
        census_df = census_df.replace('-666666666.0', 0)

        for column in census_df.columns:
            if column == "Tract":
                census_df[column] = census_df[column].str.zfill(11)
            elif column == "Median Age" or column == "pop_density":
                census_df[column] = census_df[column].astype(float)
            else:
                census_df[column] = census_df[column].astype(int)

        census_df["Total Over 25 Years Old"] = census_df["Male 25 to 29 years"] + census_df["Female 25 to 29 years"] + \
                                               census_df["Male 30 to 34 years"] + census_df["Female 30 to 34 years"] + \
                                               census_df["Male 35 to 39 years"] + census_df["Female 35 to 39 years"] + \
                                               census_df["Male 40 to 44 years"] + census_df["Female 40 to 44 years"] + \
                                               census_df["Male 45 to 49 years"] + census_df["Female 45 to 49 years"] + \
                                               census_df["Male 50 to 54 years"] + census_df["Female 50 to 54 years"] + \
                                               census_df["Male 55 to 59 years"] + census_df["Female 55 to 59 years"] + \
                                               census_df["Male 60 to 61 years"] + census_df["Female 60 to 61 years"] + \
                                               census_df["Male 62 to 64 years"] + census_df["Female 62 to 64 years"] + \
                                               census_df["Male 65 to 66 years"] + census_df["Female 65 to 66 years"] + \
                                               census_df["Male 67 to 69 years"] + census_df["Female 67 to 69 years"] + \
                                               census_df["Male 70 to 74 years"] + census_df["Female 70 to 74 years"] + \
                                               census_df["Male 75 to 79 years"] + census_df["Female 75 to 79 years"] + \
                                               census_df["Male 80 to 84 years"] + census_df["Female 80 to 84 years"] + \
                                               census_df["Male 85 and Over years"] + census_df[
                                                   "Female 85 and Over years"]

        census_df["Total Over 5 Years Old"] = census_df["Male 5 to 9 years"] + census_df["Female 5 to 9 years"] + \
                                              census_df["Male 10 to 14 years"] + census_df["Female 10 to 14 years"] + \
                                              census_df["Male 15 to 17 years"] + census_df["Female 15 to 17 years"] + \
                                              census_df["Male 18 to 19 years"] + census_df["Female 18 to 19 years"] + \
                                              census_df["Male 20 years"] + census_df["Female 20 years"] + census_df[
                                                  "Male 21 years"] + census_df["Female 21 years"] + census_df[
                                                  "Male 22 to 24 years"] + census_df["Female 22 to 24 years"] + \
                                              census_df["Total Over 25 Years Old"]

        # Drop the columns that are not needed
        census_df = census_df.drop(columns=["Male 5 to 9 years", "Female 5 to 9 years", "Male 10 to 14 years",
                                            "Female 10 to 14 years", "Male 15 to 17 years", "Female 15 to 17 years",
                                            "Male 18 to 19 years", "Female 18 to 19 years", "Male 20 years",
                                            "Female 20 years", "Male 21 years", "Female 21 years",
                                            "Male 22 to 24 years", "Female 22 to 24 years", "Male 25 to 29 years",
                                            "Female 25 to 29 years", "Male 30 to 34 years", "Female 30 to 34 years",
                                            "Male 35 to 39 years", "Female 35 to 39 years", "Male 40 to 44 years",
                                            "Female 40 to 44 years", "Male 45 to 49 years", "Female 45 to 49 years",
                                            "Male 50 to 54 years", "Female 50 to 54 years", "Male 55 to 59 years",
                                            "Female 55 to 59 years", "Male 60 to 61 years", "Female 60 to 61 years",
                                            "Male 62 to 64 years", "Female 62 to 64 years", "Male 65 to 66 years",
                                            "Female 65 to 66 years", "Male 67 to 69 years", "Female 67 to 69 years",
                                            "Male 70 to 74 years", "Female 70 to 74 years", "Male 75 to 79 years",
                                            "Female 75 to 79 years", "Male 80 to 84 years", "Female 80 to 84 years",
                                            "Male 85 and Over years", "Female 85 and Over years"])

        census_df["Total Households"] = census_df["One person household"] + census_df["Two person household"] + \
                                        census_df["Three person household"] + census_df["Four or more person household"]

        census_df = census_df.drop(columns=["One person household", "Two person household", "Three person household",
                                            "Four or more person household"])

        # Merge the dataframes that were collected earlier so that we can have one full, large dataframe
        census_df = census_df.merge(acp_df, on="Tract", how="left")
        census_df = census_df.merge(covered_df, on="Tract", how="left")
        census_df = census_df.merge(pop_density_df, on="Tract", how="left")
        census_df = census_df.merge(provider_df, on="Tract", how="left")

        census_df[f"Total ACP Subscribed Households as of {most_recent_date}"] = census_df[
            f"Total ACP Subscribed Households as of {most_recent_date}"].fillna(0)
        census_df[f"Total ACP Subscribed Households as of {most_recent_date}"] = census_df[
            f"Total ACP Subscribed Households as of {most_recent_date}"].astype(int)

        census_df["rural"] = census_df["rural"].fillna(0)
        census_df["rural"] = census_df["rural"].astype(int)

        census_df["pop_density"] = census_df["pop_density"].fillna(0)

        census_df["ISPs Count"] = census_df["ISPs Count"].fillna(0)
        census_df["ISPs Count"] = census_df["ISPs Count"].astype(int)
        census_df["ISPs ACP Count"] = census_df["ISPs ACP Count"].fillna(0)
        census_df["ISPs ACP Count"] = census_df["ISPs ACP Count"].astype(int)
        census_df["Total Population"] = census_df["Total Population"].fillna(0)
        census_df["Total Population"] = census_df["Total Population"].astype(int)
        census_df[f"Total ACP Subscribed Households as of {most_recent_date}"] = census_df[
            f"Total ACP Subscribed Households as of {most_recent_date}"].fillna(0)
        census_df[f"Total ACP Subscribed Households as of {most_recent_date}"] = census_df[
            f"Total ACP Subscribed Households as of {most_recent_date}"].astype(int)

        # Create the High Cost column if the tract is in the high cost dictionary and the high cost population is
        # greater than or equal to 50% of the total population
        census_df["High Cost"] = census_df.apply(lambda x: 1 if x["Tract"] in high_cost_dict.keys() and
                                                                high_cost_dict[x["Tract"]] >= x[
                                                                    "Total Population"] * 0.5 else 0, axis=1)

        # Create the Tribal column if the tract is in the tribal dictionary and the tribal population is greater than or
        # equal to 50% of the total population
        census_df["Tribal"] = census_df.apply(lambda x: 1 if x["Tract"] in tribal_dict.keys() and
                                                             tribal_dict[x["Tract"]] >= x[
                                                                 "Total Population"] * 0.5 else 0, axis=1)

        census_df["ISP Desert"] = census_df.apply(
            lambda x: 0 if x["ISPs Count"] == 0 and (x["Total Population"] > 0) else 1, axis=1)

        # Create the ACP Desert column if ISPs ACP Count is 0 and ISPs Count is not 0
        census_df["ACP Desert"] = census_df.apply(lambda x: 0 if x["ISPs ACP Count"] == 0 and
                                                                 (x["ISPs Count"] != 0 or
                                                                  x[
                                                                      f"Total ACP Subscribed Households as of {most_recent_date}"] > 0)
                                                                 and (x["Total Population"] > 0)
        else 1, axis=1)

        for column in census_df.columns:
            if column == "Tract":
                census_df[column] = census_df[column].str.zfill(11)
            elif column == "Median Age" or column == "pop_density":
                census_df[column] = census_df[column].astype(float)
            elif column == "All ISPs":
                census_df[column] = census_df[column].astype(str)
            else:
                census_df[column] = census_df[column].astype(int)

        census_df.to_csv(end_file, index=False)
        census_df.to_excel(end_file.replace(".csv", ".xlsx"), index=False)

        if full_df.empty:
            full_df = census_df

        else:
            full_df = pd.concat([full_df, census_df], ignore_index=True)

    full_df.to_csv(census_data_folder + "Tract_Census.csv", index=False)


def get_census_data_county(data_dir: str, date: str = "06_30_2023"):
    """
    This function downloads the census data for each state and saves it to a csv file.
    :param data_dir: Path to the data directory.
    :param date: The date of the data we want to download
    :return: None
    """

    acp_folder = data_dir + "ACP_Households/Final_Files/"
    tract_file = acp_folder + "Total-ACP-Households-by-county.csv"

    acp_df = pd.read_csv(tract_file, dtype={"county": str, "Total Subscribers": int})

    # Keep unique tracts and keep the last row for each tract after it is sorted by Data Month
    acp_df = acp_df.sort_values(by=["Data Month"])
    acp_df = acp_df.drop_duplicates(subset=["county"], keep="last")
    acp_df = acp_df.reset_index(drop=True)
    most_recent_date = acp_df["Data Month"].max()
    acp_df = acp_df[["county", "Total Subscribers"]]

    # Rename Total Subscribers to Total ACP Subscribed Households
    acp_df = acp_df.rename(columns={"Total Subscribers": f"Total ACP Subscribed Households as of {most_recent_date}",
                                    "county": "County"})

    covered_pop_folder = data_dir + "Covered_Populations/"
    covered_pop_file = covered_pop_folder + "county_total_covered_populations.csv"

    covered_df = pd.read_csv(covered_pop_file, dtype={"geo_id": str, "rural": int})

    # Only keep geo_id and rural
    covered_df = covered_df[["geo_id", "rural"]]

    # Rename geo_id to tract
    covered_df = covered_df.rename(columns={"geo_id": "County"})

    population_density_file = data_dir + "Census_Data/Census_Mid_Files/pop_density_county.csv"

    pop_density_df = pd.read_csv(population_density_file, dtype={"county": str})

    # Drop total_population and area_land columns
    pop_density_df = pop_density_df.drop(["total_population", "area_land"], axis=1)

    # Rename tract to Tract
    pop_density_df = pop_density_df.rename(columns={"county": "County"})

    pop_density_df["pop_density"] = pop_density_df["pop_density"].round(2)

    providers_by_county_folder = data_dir + f"ISP/{date}/Providers_by_State/Providers_by_County/"

    high_cost_file = data_dir + "Census_Data/Census_Mid_Files/high_cost_areas_clean.csv"

    high_cost_df = pd.read_csv(high_cost_file, dtype={"County": str})

    high_cost_dict = {}

    for county in high_cost_df["County"].unique():
        total_high_cost_pop = high_cost_df[high_cost_df["County"] == county]["Population"].sum()

        high_cost_dict[county] = total_high_cost_pop

    tribal_file = data_dir + "Census_Data/Census_Mid_Files/Tribal_Blocks.csv"

    tribal_df = pd.read_csv(tribal_file, dtype={"Block": str})

    tribal_df["County"] = tribal_df["Block"].str[:5]

    tribal_dict = {}

    for county in tribal_df["County"].unique():
        total_tribal_pop = tribal_df[tribal_df["County"] == county]["Population"].sum()

        tribal_dict[county] = total_tribal_pop

    """
    Collect the data regarding what percentage of the county is served by fixed broadband
    """

    served_file = data_dir + "Census_Data/Census_Mid_Files/county_fixed_served.csv"

    # Read the served file
    served_df = pd.read_csv(served_file, dtype={"geography_id": str})

    # Fill in the leading zeros for the geography_id
    served_df["geography_id"] = served_df["geography_id"].str.zfill(5)

    # Rename the columns
    served_df = served_df.rename(columns={"geography_id": "County",
                                          "Calculated percentage of units for broadband serviceable locations contained within the geography for which providers report residential fixed broadband service with Copper, Cable, Fiber to the Premises, or Licensed Fixed Wireless technology and speeds of at least 25 / 3 Mbps.": "Served Percentage"})

    # Keep only the columns we need for the analysis
    served_df = served_df[["County", "Served Percentage"]]

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

    county_data_folder = census_data_folder + "County/"

    # Create the folder if it doesn't exist
    if not os.path.exists(county_data_folder):
        os.mkdir(county_data_folder)

    full_df = pd.DataFrame()
    full_panel_df = pd.DataFrame()

    # Iterate through the states
    for key, value in state_dict.items():

        provider_df = pd.read_csv(providers_by_county_folder + value + "_Providers_by_County.csv", dtype=str)

        provider_df["ISPs ACP Count"] = provider_df["ISPs ACP Count"].astype(int)
        provider_df["ISPs Count"] = provider_df["ISPs Count"].astype(int)
        provider_df["Population"] = provider_df["Population"].astype(int)

        columns = provider_df.columns.tolist()

        columns = [columns[0]] + columns[4:]

        temp_prov = provider_df[columns].astype(str)

        # Create a new column called All ISPs
        temp_prov["All ISPs"] = ""

        # If the column starts with ISP, then add it to the All ISPs column
        for index, row in temp_prov.iterrows():
            for column in columns:
                if column.startswith("ISP"):
                    if row[column] != "nan" and row[column] != "0" and row[column] is not None:
                        temp_prov.at[index, "All ISPs"] += row[column] + " -- "

            temp_prov.at[index, "All ISPs"] = temp_prov.at[index, "All ISPs"][:-4]

            if temp_prov.at[index, "All ISPs"] == "":
                temp_prov.at[index, "All ISPs"] = "0"

        provider_df = provider_df[["County", "ISPs Count", "ISPs ACP Count"]]

        provider_df = provider_df.merge(temp_prov[["County", "All ISPs"]], on="County", how="left")

        end_file = county_data_folder + value + "_Census_County_Data.csv"

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

        M5TO9 = "B01001_004E"
        M10TO14 = "B01001_005E"
        M15TO17 = "B01001_006E"
        M18TO19 = "B01001_007E"
        M20 = "B01001_008E"
        M21 = "B01001_009E"
        M22TO24 = "B01001_010E"
        M25TO29 = "B01001_011E"
        M30TO34 = "B01001_012E"
        M35TO39 = "B01001_013E"
        M40TO44 = "B01001_014E"
        M45TO49 = "B01001_015E"
        M50TO54 = "B01001_016E"
        M55TO59 = "B01001_017E"
        M60TO61 = "B01001_018E"
        M62TO64 = "B01001_019E"
        M65TO66 = "B01001_020E"
        M67TO69 = "B01001_021E"
        M70TO74 = "B01001_022E"
        M75TO79 = "B01001_023E"
        M80TO84 = "B01001_024E"
        M85PLUS = "B01001_025E"

        F5TO9 = "B01001_028E"
        F10TO14 = "B01001_029E"
        F15TO17 = "B01001_030E"
        F18TO19 = "B01001_031E"
        F20 = "B01001_032E"
        F21 = "B01001_033E"
        F22TO24 = "B01001_034E"
        F25TO29 = "B01001_035E"
        F30TO34 = "B01001_036E"
        F35TO39 = "B01001_037E"
        F40TO44 = "B01001_038E"
        F45TO49 = "B01001_039E"
        F50TO54 = "B01001_040E"
        F55TO59 = "B01001_041E"
        F60TO61 = "B01001_042E"
        F62TO64 = "B01001_043E"
        F65TO66 = "B01001_044E"
        F67TO69 = "B01001_045E"
        F70TO74 = "B01001_046E"
        F75TO79 = "B01001_047E"
        F80TO84 = "B01001_048E"
        F85PLUS = "B01001_049E"

        ONEPERSONHH = "B08201_007E"
        TWOPERSONHH = "B08201_013E"
        THREEPERSONHH = "B08201_019E"
        FOURMOREPERSONHH = "B08201_025E"

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
        INTERNET_SUB_CABLE_FIBER_DSL = "B28002_007E"
        NO_INTERNET_ACCESS = "B28002_013E"

        LT10KINC = "B28004_002E"
        LT10KINC_BB_SUB = "B28004_004E"
        GT10KINC_LT20KINC = "B28004_006E"
        GT10KINC_LT20KINC_BB_SUB = "B28004_008E"
        GT20KINC_LT35KINC = "B28004_010E"
        GT20KINC_LT35KINC_BB_SUB = "B28004_012E"
        GT35KINC_LT50KINC = "B28004_014E"
        GT35KINC_LT50KINC_BB_SUB = "B28004_016E"

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

                     M5TO9: "Male 5 to 9 years",
                     M10TO14: "Male 10 to 14 years",
                     M15TO17: "Male 15 to 17 years",
                     M18TO19: "Male 18 to 19 years",
                     M20: "Male 20 years",
                     M21: "Male 21 years",
                     M22TO24: "Male 22 to 24 years",
                     M25TO29: "Male 25 to 29 years",
                     M30TO34: "Male 30 to 34 years",
                     M35TO39: "Male 35 to 39 years",
                     M40TO44: "Male 40 to 44 years",
                     M45TO49: "Male 45 to 49 years",
                     M50TO54: "Male 50 to 54 years",
                     M55TO59: "Male 55 to 59 years",
                     M60TO61: "Male 60 to 61 years",
                     M62TO64: "Male 62 to 64 years",
                     M65TO66: "Male 65 to 66 years",
                     M67TO69: "Male 67 to 69 years",
                     M70TO74: "Male 70 to 74 years",
                     M75TO79: "Male 75 to 79 years",
                     M80TO84: "Male 80 to 84 years",
                     M85PLUS: "Male 85 and Over years",

                     F5TO9: "Female 5 to 9 years",
                     F10TO14: "Female 10 to 14 years",
                     F15TO17: "Female 15 to 17 years",
                     F18TO19: "Female 18 to 19 years",
                     F20: "Female 20 years",
                     F21: "Female 21 years",
                     F22TO24: "Female 22 to 24 years",
                     F25TO29: "Female 25 to 29 years",
                     F30TO34: "Female 30 to 34 years",
                     F35TO39: "Female 35 to 39 years",
                     F40TO44: "Female 40 to 44 years",
                     F45TO49: "Female 45 to 49 years",
                     F50TO54: "Female 50 to 54 years",
                     F55TO59: "Female 55 to 59 years",
                     F60TO61: "Female 60 to 61 years"}

        vars_2 = {F62TO64: "Female 62 to 64 years",
                  F65TO66: "Female 65 to 66 years",
                  F67TO69: "Female 67 to 69 years",
                  F70TO74: "Female 70 to 74 years",
                  F75TO79: "Female 75 to 79 years",
                  F80TO84: "Female 80 to 84 years",
                  F85PLUS: "Female 85 and Over years",

                  ONEPERSONHH: "One person household",
                  TWOPERSONHH: "Two person household",
                  THREEPERSONHH: "Three person household",
                  FOURMOREPERSONHH: "Four or more person household",

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
                  INTERNET_SUB_CABLE_FIBER_DSL: "Cable, fiber optic, or DSL Internet subscription",
                  NO_INTERNET_ACCESS: "No Internet access",
                  LT10KINC: "Less than $10,000 household income",
                  LT10KINC_BB_SUB: "Less than $10,000 household income with Broadband Internet subscription",
                  GT10KINC_LT20KINC: "$10K to $20K household income",
                  GT10KINC_LT20KINC_BB_SUB: "$10K to $20K household income with Broadband Internet subscription",
                  GT20KINC_LT35KINC: "$20K to $35K household income",
                  GT20KINC_LT35KINC_BB_SUB: "$20K to $35K household income with Broadband Internet subscription",
                  GT35KINC_LT50KINC: "$35K to $50K household income",
                  GT35KINC_LT50KINC_BB_SUB: "$35K to $50K household income with Broadband Internet subscription",

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

        year = '/2022'

        detailed = '/acs/acs5'

        g = '?get='

        vrs = ''
        vrs2 = ''

        for v in variables.keys():
            vrs += f'{v},'

        for v in vars_2.keys():
            vrs2 += f'{v},'

        vrs = vrs[:-1]
        vrs2 = vrs2[:-1]

        location = f'&for=county:*&in=state:{key}'

        usr_key = f"&key={census_key}"

        county_query_url = f"{host}{year}{detailed}{g}{vrs}{location}{usr_key}"
        county_query_url2 = f"{host}{year}{detailed}{g}{vrs2}{location}{usr_key}"

        # Use requests package to call out the API
        response = requests.get(county_query_url, timeout=100)
        response2 = requests.get(county_query_url2, timeout=100)

        # Convert the Response to text and print the result
        data = response.text.split("\n")
        data2 = response2.text.split("\n")

        new_data = []
        new_data2 = []

        for row in data:
            index = data.index(row)

            row = row.replace("[", "")
            row = row.replace("]", "")
            row = row.replace("\"", "")
            if index < len(data) - 1:
                row = row[:-1]

            row = row.split(",")
            new_data.append(row)

        for row in data2:
            index = data2.index(row)
            row = row.replace("[", "")
            row = row.replace("]", "")
            row = row.replace("\"", "")
            if index < len(data2) - 1:
                row = row[:-1]

            row = row.split(",")
            new_data2.append(row)

        census_df = pd.DataFrame(new_data[1:], columns=new_data[0])
        census_df2 = pd.DataFrame(new_data2[1:], columns=new_data2[0])

        census_df = census_df.replace('-666666666', 0)
        census_df = census_df.replace('-666666666.0', 0)
        census_df2 = census_df2.replace('-666666666', 0)
        census_df2 = census_df2.replace('-666666666.0', 0)

        for column in census_df.columns:
            if column in variables.keys():
                census_df.rename(columns={column: variables[column]}, inplace=True)

        for column in census_df2.columns:
            if column in vars_2.keys():
                census_df2.rename(columns={column: vars_2[column]}, inplace=True)

        census_df = census_df.merge(census_df2, on=["state", "county"], how="left")

        census_df["state"] = census_df["state"].str.zfill(2)
        census_df["county"] = census_df["county"].str.zfill(3)

        census_df["County"] = census_df['state'] + census_df['county']

        census_df = census_df.drop(columns=['state', 'county'])

        census_columns = census_df.columns.tolist()

        census_columns = census_columns[-1:] + census_columns[:-1]

        census_df = census_df[census_columns]

        # Replace all the -666666666 values with 0
        census_df = census_df.replace('-666666666', 0)
        census_df = census_df.replace('-666666666.0', 0)

        for column in census_df.columns:
            if column == "County":
                census_df[column] = census_df[column].str.zfill(5)
            elif column == "Median Age" or column == "pop_density":
                census_df[column] = census_df[column].astype(float)
            else:
                census_df[column] = census_df[column].astype(int)

        census_df["Total Over 25 Years Old"] = census_df["Male 25 to 29 years"] + census_df["Female 25 to 29 years"] + \
                                               census_df["Male 30 to 34 years"] + census_df["Female 30 to 34 years"] + \
                                               census_df["Male 35 to 39 years"] + census_df["Female 35 to 39 years"] + \
                                               census_df["Male 40 to 44 years"] + census_df["Female 40 to 44 years"] + \
                                               census_df["Male 45 to 49 years"] + census_df["Female 45 to 49 years"] + \
                                               census_df["Male 50 to 54 years"] + census_df["Female 50 to 54 years"] + \
                                               census_df["Male 55 to 59 years"] + census_df["Female 55 to 59 years"] + \
                                               census_df["Male 60 to 61 years"] + census_df["Female 60 to 61 years"] + \
                                               census_df["Male 62 to 64 years"] + census_df["Female 62 to 64 years"] + \
                                               census_df["Male 65 to 66 years"] + census_df["Female 65 to 66 years"] + \
                                               census_df["Male 67 to 69 years"] + census_df["Female 67 to 69 years"] + \
                                               census_df["Male 70 to 74 years"] + census_df["Female 70 to 74 years"] + \
                                               census_df["Male 75 to 79 years"] + census_df["Female 75 to 79 years"] + \
                                               census_df["Male 80 to 84 years"] + census_df["Female 80 to 84 years"] + \
                                               census_df["Male 85 and Over years"] + census_df[
                                                   "Female 85 and Over years"]

        census_df["Total Over 5 Years Old"] = census_df["Male 5 to 9 years"] + census_df["Female 5 to 9 years"] + \
                                              census_df["Male 10 to 14 years"] + census_df["Female 10 to 14 years"] + \
                                              census_df["Male 15 to 17 years"] + census_df["Female 15 to 17 years"] + \
                                              census_df["Male 18 to 19 years"] + census_df["Female 18 to 19 years"] + \
                                              census_df["Male 20 years"] + census_df["Female 20 years"] + census_df[
                                                  "Male 21 years"] + census_df["Female 21 years"] + census_df[
                                                  "Male 22 to 24 years"] + census_df["Female 22 to 24 years"] + \
                                              census_df["Total Over 25 Years Old"]

        # Drop the columns that are not needed
        census_df = census_df.drop(columns=["Male 5 to 9 years", "Female 5 to 9 years", "Male 10 to 14 years",
                                            "Female 10 to 14 years", "Male 15 to 17 years", "Female 15 to 17 years",
                                            "Male 18 to 19 years", "Female 18 to 19 years", "Male 20 years",
                                            "Female 20 years", "Male 21 years", "Female 21 years",
                                            "Male 22 to 24 years", "Female 22 to 24 years", "Male 25 to 29 years",
                                            "Female 25 to 29 years", "Male 30 to 34 years", "Female 30 to 34 years",
                                            "Male 35 to 39 years", "Female 35 to 39 years", "Male 40 to 44 years",
                                            "Female 40 to 44 years", "Male 45 to 49 years", "Female 45 to 49 years",
                                            "Male 50 to 54 years", "Female 50 to 54 years", "Male 55 to 59 years",
                                            "Female 55 to 59 years", "Male 60 to 61 years", "Female 60 to 61 years",
                                            "Male 62 to 64 years", "Female 62 to 64 years", "Male 65 to 66 years",
                                            "Female 65 to 66 years", "Male 67 to 69 years", "Female 67 to 69 years",
                                            "Male 70 to 74 years", "Female 70 to 74 years", "Male 75 to 79 years",
                                            "Female 75 to 79 years", "Male 80 to 84 years", "Female 80 to 84 years",
                                            "Male 85 and Over years", "Female 85 and Over years"])

        census_df["Total Households"] = census_df["One person household"] + census_df["Two person household"] + \
                                        census_df["Three person household"] + census_df["Four or more person household"]

        census_df = census_df.drop(columns=["One person household", "Two person household", "Three person household",
                                            "Four or more person household"])

        panel_data_folder = data_dir + "Census_Data/Panel_Data/"

        # Create the folder if it doesn't exist
        if not os.path.exists(panel_data_folder):
            os.mkdir(panel_data_folder)

        # Collect the panel data for each county in the current state using the get_county_panel_internet_data function
        panel_df = get_county_panel_internet_data(key)

        # If the full panel data is empty, set it to the panel data
        if full_panel_df.empty:
            full_panel_df = panel_df

        # Otherwise, concatenate the panel data to the full panel data
        else:
            full_panel_df = pd.concat([full_panel_df, panel_df], ignore_index=True)

        # Save the panel data to a csv file
        panel_df.to_csv(panel_data_folder + value + "_Panel_Data.csv", index=False)

        # Combine the panel data to the census data
        census_df = census_df.merge(panel_df, on="County", how="left")

        # Combine the apc household data to the census data
        census_df = census_df.merge(acp_df, on="County", how="left")

        # Combine the covered population data to the census data
        census_df = census_df.merge(covered_df, on="County", how="left")

        # Combine the population density data to the census data
        census_df = census_df.merge(pop_density_df, on="County", how="left")

        # Combine the provider data to the census data
        census_df = census_df.merge(provider_df, on="County", how="left")

        # Combine the served data to the census data
        census_df = census_df.merge(served_df, on="County", how="left")

        # Fill in the missing values with 0
        census_df[f"Total ACP Subscribed Households as of {most_recent_date}"] = census_df[
            f"Total ACP Subscribed Households as of {most_recent_date}"].fillna(0)
        census_df[f"Total ACP Subscribed Households as of {most_recent_date}"] = census_df[
            f"Total ACP Subscribed Households as of {most_recent_date}"].astype(int)

        # Fill in the missing values with 0
        census_df["rural"] = census_df["rural"].fillna(0)
        census_df["rural"] = census_df["rural"].astype(int)

        # Fill in the missing values with 0
        census_df["pop_density"] = census_df["pop_density"].fillna(0)

        # Turn all the columns into integers
        census_df["ISPs Count"] = census_df["ISPs Count"].fillna(0)
        census_df["ISPs Count"] = census_df["ISPs Count"].astype(int)
        census_df["ISPs ACP Count"] = census_df["ISPs ACP Count"].fillna(0)
        census_df["ISPs ACP Count"] = census_df["ISPs ACP Count"].astype(int)
        census_df["Total Population"] = census_df["Total Population"].fillna(0)
        census_df["Total Population"] = census_df["Total Population"].astype(int)
        census_df[f"Total ACP Subscribed Households as of {most_recent_date}"] = census_df[
            f"Total ACP Subscribed Households as of {most_recent_date}"].fillna(0)
        census_df[f"Total ACP Subscribed Households as of {most_recent_date}"] = census_df[
            f"Total ACP Subscribed Households as of {most_recent_date}"].astype(int)

        # Create the High Cost column, using 1 as the identifier if more than 50% of the population is in a high-cost area
        census_df["High Cost"] = census_df.apply(lambda x: 1 if x["County"] in high_cost_dict.keys() and
                                                                high_cost_dict[x["County"]] >= x[
                                                                    "Total Population"] * 0.5 else 0, axis=1)

        # Create the Tribal column, using 1 as the identifier if more than 50% of the population is tribal
        census_df["Tribal"] = census_df.apply(lambda x: 1 if x["County"] in tribal_dict.keys() and
                                                             tribal_dict[x["County"]] >= x[
                                                                 "Total Population"] * 0.5 else 0, axis=1)

        # Create the ISP Desert column if ISPs Count is 0 and Total Population is not 0
        census_df["ISP Desert"] = census_df.apply(
            lambda x: 0 if x["ISPs Count"] == 0 and (x["Total Population"] > 0) else 1, axis=1)

        # Create the ACP Desert column if ISPs ACP Count is 0 and ISPs Count is not 0
        census_df["ACP Desert"] = census_df.apply(lambda x: 0 if x["ISPs ACP Count"] == 0 and
                                                                 (x["ISPs Count"] != 0 or
                                                                  x[
                                                                      f"Total ACP Subscribed Households as of {most_recent_date}"] > 0)
                                                                 and (x["Total Population"] > 0)
        else 1, axis=1)

        census_df = census_df.fillna(0)

        for column in census_df.columns:
            if column == "County":
                census_df[column] = census_df[column].str.zfill(5)
            elif column == "Median Age" or column == "pop_density" or column == "Served Percentage":
                census_df[column] = census_df[column].astype(float)
            elif column == "All ISPs":
                census_df[column] = census_df[column].astype(str)
            else:
                census_df[column] = census_df[column].astype(int)

        census_df = census_df.drop_duplicates(subset=["County"], keep="first")

        census_df.to_csv(end_file, index=False)
        census_df.to_excel(end_file.replace(".csv", ".xlsx"), index=False)

        if full_df.empty:
            full_df = census_df

        else:
            full_df = pd.concat([full_df, census_df], ignore_index=True)

    full_df = full_df.drop_duplicates(subset=["County"], keep="first")

    full_df.to_csv(census_data_folder + "County_Census.csv", index=False)
    full_panel_df.to_csv(census_data_folder + "County_Panel_Data.csv", index=False)

    only_acp_deserts = full_df[full_df["ACP Desert"] == 0]

    only_acp_deserts.to_csv(census_data_folder + "County_Census_Only_ACP_Deserts.csv", index=False)


def get_county_panel_internet_data(state_num: str):
    census_key = "494a9ee04209e13f2786105dd68cd4b5ac37f49d"

    main_df = pd.DataFrame()

    for yr in range(2016, 2023):

        if yr != 2020:

            host = 'https://api.census.gov/data'

            year = f'/{yr}'

            sup = '/acs/acsse'

            g = '?get=K202801_004E'

            location = f'&for=county:*&in=state:{state_num}'

            usr_key = f"&key={census_key}"

            county_query_url = f"{host}{year}{sup}{g}{location}{usr_key}"

            # Use requests package to call out the API
            response = requests.get(county_query_url, timeout=100)

            # Convert the Response to text and print the result
            data = response.text.split("\n")

            new_data = []

            for row in data:
                row = row.replace("[", "")
                row = row.replace("]", "")
                row = row.replace("\"", "")
                if row.endswith(","):
                    row = row[:-1]

                row = row.split(",")
                new_data.append(row)

            census_df = pd.DataFrame(new_data[1:], columns=new_data[0])

            census_df["state"] = census_df["state"].str.zfill(2)
            census_df["county"] = census_df["county"].str.zfill(3)

            census_df["County"] = census_df['state'] + census_df['county']

            census_df = census_df.drop(columns=['state', 'county'])

            census_columns = census_df.columns.tolist()

            census_columns = census_columns[-1:] + census_columns[:-1]

            census_df = census_df[census_columns]

            census_df = census_df.rename(
                columns={"K202801_004E": f"{yr} Total Households with Computer and have Internet "
                                         f"Sub"})

            census_df[f"{yr} Total Households with Computer and have Internet Sub"] = (
                census_df[f"{yr} Total Households with Computer and have Internet Sub"].replace("null", 0))

            census_df[f"{yr} Total Households with Computer and have Internet Sub"] = (
                census_df[f"{yr} Total Households with Computer and have Internet Sub"].astype(int))

            census_df = census_df.drop_duplicates(subset=["County"], keep="first")

            if main_df.empty:
                main_df = census_df
            else:
                main_df = main_df.merge(census_df, on="County", how="left")
                main_df = main_df.drop_duplicates(subset=["County"], keep="first")

    return main_df


# This function will determine the income distribution for each state
def determine_income_threshold(data_dir, data_year):
    """
    This function will determine the number of people eligible for ACP in each state based on the income thresholds.
    :param data_dir: The directory where the data is stored
    :param data_year: The year of the data
    :return: None
    """

    # Open the folder that contains the state data
    state_data_folder = data_dir + f"ACS_PUMS/{data_year}_Data/state_data/"

    # We only want to look at the following states
    states = ["ca", "tx", "oh", "al"]

    # Create a dictionary to store the data
    full_dc = {state + "_" + str(x) + "K": 0 for state in states for x in range(30, 71, 10)}

    for state in states:

        # Open the file that contains the county data
        file = f"{state_data_folder}{state}/{state}-eligibility-county.csv"

        df = pd.read_csv(file)

        # Create a new column called acp_eligible
        df["acp_eligible"] = 0

        # Determine if the person is eligible for ACP
        df.loc[(df["POVPIP"] <= 200) | (df["has_pap"] == 1) | (df["has_ssip"] == 1) | (df["has_hins4"] == 1) | (
                df["has_snap"] == 1), "acp_eligible"] = 1

        # Iterate through the income thresholds
        for x in range(30, 71, 10):
            # Keep only the households whose income is less than the threshold
            df2 = df[df["HH Income"] <= x * 1000]

            # Determine the total number of households
            total_hh = df2["WGTP"].sum()

            # Keep only the households that are eligible for ACP
            df2 = df2[df2["acp_eligible"] == 1]

            # Determine the percentage of households that are eligible for ACP
            full_dc[state + "_" + str(x) + "K"] = round(df2["WGTP"].sum() * 100 / total_hh, 2)

    print(full_dc)
