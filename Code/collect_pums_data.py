import os
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from typing import Any
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from pandas import Series, DataFrame
import warnings

warnings.filterwarnings("ignore")


def code_to_source_dict(crosswalk_file: str, source_col: str) \
        -> tuple[dict[str, list[tuple[str, Series | Series | DataFrame]]], str | Any]:
    """
    This function will create a dictionary with the target codes as keys and the source codes as values. It will also
    return the column name for the target codes. It does so by reading the crosswalk file and finding the column with
    the target codes. It then groups the source codes by the target codes, and creates a dictionary with the target
    codes as keys and the source codes as values.
    An example of the dictionary is:
    {puma22: [(zcta1, afact1), (zcta2, afact2), ...]}
    :param crosswalk_file: The path to the crosswalk file
    :param source_col: the column name for the source codes
    :return: a dictionary with the target codes as keys and the source codes as values, and the column name for the
    target codes
    """

    code_col = ""

    # Get the column name for the source geography
    df_zeros = pd.read_csv(crosswalk_file)
    for col in df_zeros.columns.tolist():
        if source_col in col:
            source_col = col
            break

    # Read the crosswalk file to get the column names
    df_zeros = pd.read_csv(crosswalk_file, dtype={source_col: str})

    # Read the column names
    col_names = df_zeros.columns.tolist()
    col_names.remove(source_col)

    # Find the column with the target codes
    for col in col_names:
        if "zcta" in col:
            code_col = col
            break
        elif "county" in col and "tract" not in col_names:
            code_col = col
            break
        elif "metdiv" in col:
            code_col = col
            break
        elif "puma" in col:
            code_col = col
            break
        elif "tract" in col:
            code_col = col
            break
        elif "cd" in col:
            code_col = col
            break
        elif "sdbest" in col:
            code_col = col
            break
        elif "sdelem" in col:
            code_col = col
            break
        elif "sdsec" in col:
            code_col = col
            break
        elif "sduni" in col:
            code_col = col
            break
        elif "state" in col:
            code_col = col
            break

    try:
        df = pd.read_csv(crosswalk_file, dtype={source_col: str, code_col: str})
    except:
        df = pd.read_csv(crosswalk_file, dtype={source_col: str})

    # Group the source by code
    cw_lists = df.groupby(code_col)[source_col].apply(list)

    # Initialize the dictionary to store the data
    code_zcta_dict = {}

    # Iterate through the target codes
    for index, row in cw_lists.items():
        data = []
        for item in row:
            # Find the afact on the crosswalk dataframe by the source code and the target code
            afact = df.loc[(df[source_col] == item) & (df[code_col] == index), 'afact'].iloc[0]

            # Create a tuple with the source code and the afact
            tup = (str(item), afact)

            # Add the tuple to the list
            data.append(tup)

        # Add the list to the dictionary
        code_zcta_dict[str(index)] = data

    # Return the dictionary and the column name for the target codes
    return code_zcta_dict, code_col


# Download the PUMS files from the Census website, and save them to the PUMS folder in the data directory
def downloadPUMSFiles(data_directory: str, year: str | list):
    """
    This function downloads the most recent 1-year PUMS files from the Census website, and saves them to the PUMS
    folder. It downloads both .zip files for household and person data for every state. It does so by using the
    requests and BeautifulSoup packages to parse the Census website and find the links to the files. It then uses
    urllib to download the files. The files are saved to the PUMS folder in the data directory into state folders.
    """
    acs_webpage = "https://www2.census.gov/programs-surveys/acs/data/pums/"

    data_year = "1"

    # Request the website
    response = requests.get(acs_webpage)

    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table element
    table = soup.find("table")

    # Find all the links in the table
    links = table.find_all("a")

    if type(year) is str:
        year = [year]

    if type(year) is list:

        for yr in year:

            recent_year = str(yr)

            # Path to the folder where the PUMS files will be saved
            pums_folder = data_directory + f"ACS_PUMS/{recent_year}_Data/"

            # Create the folder if it doesn't exist
            if not os.path.exists(pums_folder):
                os.makedirs(pums_folder)

            state_data_folder = pums_folder + "/state_data"

            if not os.path.exists(state_data_folder):
                os.makedirs(state_data_folder)

            pums_folder = state_data_folder + "/"

            year_link = [link["href"] for link in links if recent_year in link.text]

            if len(year_link) == 0:
                raise Exception("Year not found")
            else:
                year_link = year_link[0]

            # Get the most recent year, which is the last link in the table
            new_link = acs_webpage + year_link + data_year + "-Year/"

            # Request the website
            response = requests.get(new_link)

            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the table element
            table = soup.find("table")

            # Find all the links in the table
            links = table.find_all("a")

            # Download the zip files
            for link in links:

                # Do not download the US file
                if "us" not in link.text:

                    # Only download the csv files
                    if link.text.startswith("csv_"):

                        # Get the state acronym from the file name
                        period = link.text.find(".zip")
                        state_acronym = link.text[period - 2:period]

                        # Create the folder if it doesn't exist
                        if not os.path.exists(pums_folder + state_acronym):
                            os.makedirs(pums_folder + state_acronym)

                        # Download the file
                        if not os.path.exists(pums_folder + state_acronym + "/" + link.text):
                            print(link.text)
                            urllib.request.urlretrieve(new_link + link["href"],
                                                       pums_folder + state_acronym + "/" + link.text)
                        else:
                            continue

        # Delete variables that are no longer needed
        del table
        del links
        del soup
        del response


# Determine eligibility for ACP, params are the person and household dataframes, output file name, and state
def create_state_sheet(df_person: pd.DataFrame, df_household: pd.DataFrame, output_file: str, state_code: str):
    """

    :param df_person: the person dataframe from the PUMS person zip file
    :param df_household: the household dataframe from the PUMS household zip file
    :param output_file: the name of the file to save the data to
    :param state_code: the state code, used to create the full 7-digit puma code
    :return: Dataframe of the eligibility criteria for ACP

    This function will create a csv file containing the eligibility criteria for ACP for each SERIALNO in the PUMS data,
    as well as the PUMA code, the weight, and demographic information. This will be used later to determine eligibility
    depending on the projected criteria.

    """
    # Make state code 2 digits
    state_code = str(state_code).zfill(2)

    # Merge the two dataframes
    merged = pd.merge(df_person, df_household, on="SERIALNO", how="left", suffixes=('_person', '_household'),
                      indicator=True, validate="m:1")

    # Drop the RT column that came from the household file
    merged = merged.drop(columns=['RT_household'])

    # Drop the _merge column
    merged = merged.drop(columns=['_merge'])

    # Generate program eligibility variables
    merged["HINS4"] = merged["HINS4"].replace(2, 0)
    merged["number_hins4"] = merged.groupby("SERIALNO")["HINS4"].transform("sum")
    merged["has_hins4"] = (merged["number_hins4"] >= 1).astype(int)

    # Turn the pap variable into a binary variable of 0 or 1
    merged["number_pap"] = merged.groupby("SERIALNO")["PAP"].transform("sum")
    merged["has_pap"] = (merged["number_pap"] > 0).astype(int)

    # Turn the ssip variable into a binary variable of 0 or 1
    merged["number_ssip"] = merged.groupby("SERIALNO")["SSIP"].transform("sum")
    merged["has_ssip"] = (merged["number_ssip"] > 0).astype(int)

    # Turn the snap variable into a binary variable of 0 or 1
    merged["FS"] = merged["FS"].replace(2, 0)
    merged["number_fs"] = merged.groupby("SERIALNO")["FS"].transform("sum")
    merged["has_snap"] = (merged["number_fs"] > 0).astype(int)

    merged["PUMA_person"] = merged["PUMA_person"].astype(int)

    # Collect the demographic information
    merged["RACAIAN"] = merged["RACAIAN"].astype(int)
    merged["RACASN"] = merged["RACASN"].astype(int)
    merged["RACBLK"] = merged["RACBLK"].astype(int)
    merged["RACNH"] = merged["RACNH"].astype(int)
    merged["RACPI"] = merged["RACPI"].astype(int)
    merged["RACWHT"] = merged["RACWHT"].astype(int)
    merged["HISP"] = merged["HISP"].astype(int)
    merged["AGEP"] = merged["AGEP"].astype(int)
    merged["DIS"] = merged["DIS"].astype(int)
    merged["ENG"] = merged["ENG"].fillna(0)
    merged["ENG"] = merged["ENG"].astype(int)

    # Turn the hispanic variable into a binary variable. In the original file, one means not hispanic; anything else is
    # a specific hispanic origin. We want to turn this into a binary variable of zero or one, where one means hispanic.
    merged["HISP"] = merged["HISP"].replace(1, 0)
    merged["HISP"] = (merged["HISP"] > 0).astype(int)

    # Veteran period of service into a binary variable
    merged["VPS"] = merged["VPS"].fillna(0)
    merged["VPS"] = (merged["VPS"] > 0).astype(int)

    # Elderly variable
    merged["AGEP"] = merged["AGEP"].fillna(0)
    merged["Elderly"] = (merged["AGEP"] >= 60).astype(int)

    # People with disabilities variable
    merged["DIS"] = merged["DIS"].replace(2, 0)

    # People who speak English less than "very well"
    merged["ENG"] = (merged["ENG"] > 1).astype(int)

    merged["HINCP"] = merged["HINCP"].fillna(0)
    merged["HINCP"] = merged["HINCP"].astype(int)

    merged["ADJINC_household"] = merged["ADJINC_household"].fillna(0)
    merged["ADJINC_household"] = merged["ADJINC_household"].astype(int)

    merged["HH Income"] = merged["HINCP"] * (merged["ADJINC_household"] / 1000000)

    # Rename the columns
    merged = merged.rename(columns={"RACAIAN": "American Indian and Alaska Native", "RACASN": "Asian",
                                    "RACBLK": "Black or African American", "RACNH": "Native Hawaiian",
                                    "RACPI": "Pacific Islander", "RACWHT": "White", "HISP": "Hispanic or Latino",
                                    "VPS": "Veteran", "ENG": "English less than very well"})

    # Create a new dataframe with the variables we need.
    # First means we get that information from the first person in the household.
    # Mean means we get that information from the means of the household.
    # Max means we keep the highest value for that variable in the household, being either 0 or 1 for binary variables.
    collapsed = merged.groupby("SERIALNO").agg({
        "POVPIP": "first",
        "has_pap": "mean",
        "has_ssip": "mean",
        "has_hins4": "mean",
        "has_snap": "mean",
        "PUMA_person": "mean",
        "WGTP": "mean",
        "American Indian and Alaska Native": "max",
        "Asian": "max",
        "Black or African American": "max",
        "Native Hawaiian": "max",
        "Pacific Islander": "max",
        "White": "max",
        "Hispanic or Latino": "max",
        "Veteran": "max",
        "Elderly": "max",
        "DIS": "max",
        "English less than very well": "max",
        "HH Income": "mean"
    })

    # Drop the rows where WGTP is 0, they will not be used regardless
    collapsed = collapsed[collapsed["WGTP"] != 0]

    # Round all the variables to integers
    collapsed["POVPIP"] = collapsed["POVPIP"].round(0).astype(int)
    collapsed["has_pap"] = collapsed["has_pap"].round(0).astype(int)
    collapsed["has_ssip"] = collapsed["has_ssip"].round(0).astype(int)
    collapsed["has_hins4"] = collapsed["has_hins4"].round(0).astype(int)
    collapsed["has_snap"] = collapsed["has_snap"].round(0).astype(int)
    collapsed["WGTP"] = collapsed["WGTP"].round(0).astype(int)
    collapsed["HH Income"] = collapsed["HH Income"].round(0).astype(int)

    collapsed["American Indian and Alaska Native"] = (
            collapsed["WGTP"] * collapsed["American Indian and Alaska Native"]).astype(int)
    collapsed["Asian"] = (collapsed["WGTP"] * collapsed["Asian"]).astype(int)
    collapsed["Black or African American"] = (collapsed["WGTP"] * collapsed["Black or African American"]).astype(int)
    collapsed["Native Hawaiian"] = (collapsed["WGTP"] * collapsed["Native Hawaiian"]).astype(int)
    collapsed["Pacific Islander"] = (collapsed["WGTP"] * collapsed["Pacific Islander"]).astype(int)
    collapsed["White"] = (collapsed["WGTP"] * collapsed["White"]).astype(int)
    collapsed["Hispanic or Latino"] = (collapsed["WGTP"] * collapsed["Hispanic or Latino"]).astype(int)
    collapsed["Veteran"] = (collapsed["WGTP"] * collapsed["Veteran"]).astype(int)
    collapsed["Elderly"] = (collapsed["WGTP"] * collapsed["Elderly"]).astype(int)
    collapsed["DIS"] = (collapsed["WGTP"] * collapsed["DIS"]).astype(int)
    collapsed["English less than very well"] = (collapsed["WGTP"] * collapsed["English less than very well"]).astype(
        int)

    # Add the state code to the puma code
    collapsed["PUMA_person"] = collapsed["PUMA_person"].astype(str)
    collapsed["PUMA_person"] = collapsed["PUMA_person"].str.split(".").str[0]
    collapsed["PUMA_person"] = collapsed["PUMA_person"].str.zfill(5)
    collapsed["PUMA_person"] = state_code + collapsed["PUMA_person"]

    collapsed = collapsed.reset_index()

    # Save the data
    collapsed.to_csv(output_file, index=False)

    # Delete variables that are no longer needed
    del merged

    return collapsed


# Determine eligibility for ACP for all states, params is the data directory, run determineEligibility for each state
def everyStateEligibility(data_directory: str, old_puma: bool = True, year: str = "2022"):
    """
    This function will determine eligibility for ACP for all states. It does so by iterating through all the states and
    calling the determineEligibility function for each state. It will save the data to a csv file in the state folder.
    :param year: The year of the PUMS data
    :param data_directory: The path to the data directory which contains the ACS_PUMS folder
    :param old_puma: Whether the old puma codes are used
    :return: None, but saves the data to csv files
    """

    def process_chunk(process_df, new_puma_dict, old_geo, next_geo):
        final_df = pd.DataFrame()
        for second_geo in new_puma_dict.keys():
            for tup in new_puma_dict[second_geo]:
                first_geo = tup[0]
                afact = tup[1]

                if first_geo in process_df[old_geo].unique():

                    temp_df = process_df[process_df[old_geo] == first_geo]

                    for index, row in temp_df.iterrows():
                        row[old_geo] = second_geo
                        row["WGTP"] = round((row["WGTP"] * afact), 2)

                        row = row.rename({old_geo: next_geo})

                        if row["American Indian and Alaska Native"] > 1:
                            row["American Indian and Alaska Native"] = 1
                        if row["Asian"] > 1:
                            row["Asian"] = 1
                        if row["Black or African American"] > 1:
                            row["Black or African American"] = 1
                        if row["Native Hawaiian"] > 1:
                            row["Native Hawaiian"] = 1
                        if row["Pacific Islander"] > 1:
                            row["Pacific Islander"] = 1
                        if row["White"] > 1:
                            row["White"] = 1
                        if row["Hispanic or Latino"] > 1:
                            row["Hispanic or Latino"] = 1
                        if row["Veteran"] > 1:
                            row["Veteran"] = 1
                        if row["Elderly"] > 1:
                            row["Elderly"] = 1
                        if row["DIS"] > 1:
                            row["DIS"] = 1
                        if row["English less than very well"] > 1:
                            row["English less than very well"] = 1

                        # Turn from series to dataframe
                        row = row.to_frame().transpose()

                        final_df = pd.concat([final_df, row], ignore_index=True)

                        final_df = (
                            final_df.groupby([next_geo, "POVPIP", "has_pap", "has_ssip", "has_hins4",
                                              "has_snap", "American Indian and Alaska Native", "Asian",
                                              "Black or African American", "Native Hawaiian",
                                              "Pacific Islander", "White", "Hispanic or Latino",
                                              "Veteran", "Elderly", "DIS",
                                              "English less than very well", "HH Income"]).
                            agg({"WGTP": "sum"}).reset_index())
        return final_df

    # Path to the folder where the PUMS files are saved
    data_dir = data_directory + f"ACS_PUMS/{year}_Data/"
    state_dir = data_dir + "state_data/"
    geocorr_folder = data_directory + "Geocorr/Housing/"
    puma_cw_folder = geocorr_folder + "Public-use microdata area (PUMA)/"
    puma_equivalency_file = puma_cw_folder + "puma_equivalency.csv"

    geos = {"county": "United_States_Public-Use-Microdata-Area-(Puma)_to_County.csv"}

    county_dc, county_code_col = code_to_source_dict(puma_cw_folder + geos["county"], "puma22")
    new_puma_dc, new_puma_code_col = code_to_source_dict(puma_equivalency_file, "puma12")

    geos = {"county": county_dc}

    states = [name for name in os.listdir(state_dir) if os.path.isdir(os.path.join(state_dir, name))]
    states = sorted(states)

    # Iterate through all folders in the ACS_PUMS folder
    for state in states:
        print("State: " + state)

        end_file = state_dir + state + "/" + state + "-eligibility.csv"

        # if True:
        if not os.path.exists(end_file.replace(".csv", "-puma22.csv")):

            # Initialize the dataframes
            person_df = pd.DataFrame()

            household_df = pd.DataFrame()

            # Iterate through all zipped files in the state folder
            for zip_folder in os.listdir(state_dir + state):
                # Only unzip the zip files
                if zip_folder.endswith(".zip"):
                    # Get the folder name
                    folder_name = state_dir + state + "/" + zip_folder

                    # Unzip the file
                    with zipfile.ZipFile(folder_name, 'r') as zip_file:
                        # Iterate through all files in the zipped folder
                        for file in zip_file.namelist():
                            # Only read the csv files
                            if file.endswith("csv"):
                                # Get the state code from the file name
                                end = file.find(".csv")

                                state_code = str(file[end - 2:end])

                                state_code = state_code.zfill(2)

                                # Read the file
                                if file.startswith("psam_h"):
                                    household_df = pd.concat(
                                        [household_df, pd.read_csv(zip_file.open(file), dtype={"PUMA": str})])
                                elif file.startswith("psam_p"):
                                    person_df = pd.concat(
                                        [person_df, pd.read_csv(zip_file.open(file), dtype={"PUMA": str})])

            if not person_df.empty and not household_df.empty:
                # Call the function to determine eligibility
                df = create_state_sheet(person_df, household_df, end_file, state_code)

                df = df.drop(columns=["SERIALNO"])

                df = df.rename(columns={"PUMA_person": "puma22"})

                df["puma22"] = df["puma22"].astype(str).str.zfill(7)

                cols = df.columns.tolist()

                cols.remove("puma22")

                cols.insert(0, "puma22")

                cols.remove("WGTP")

                cols.insert(1, "WGTP")

                df = df[cols]

                if old_puma:
                    df = df.rename(columns={"puma22": "puma12"})

                    temp_new_puma_dc = {
                        new_geo_code: [(old_geo_code, afact) for old_geo_code, afact in old_geo_code_tuple if
                                       old_geo_code
                                       in df["puma12"].unique()] for new_geo_code, old_geo_code_tuple
                        in new_puma_dc.items()}

                    temp_new_puma_dc = {new_geo_code: old_geo_code_tuple for new_geo_code, old_geo_code_tuple in
                                        temp_new_puma_dc.items() if
                                        old_geo_code_tuple}

                    num_chunks = 5000
                    chunk_size = len(df) // num_chunks

                    if chunk_size != 0:
                        df_chunks = [df.iloc[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
                    else:
                        df_chunks = [df.iloc[i:i + 1] for i in range(0, len(df), 1)]

                    with ThreadPoolExecutor(max_workers=num_chunks) as executor:
                        futures = [executor.submit(process_chunk, chunk, temp_new_puma_dc, "puma12", "puma22") for
                                   chunk in df_chunks]

                    df = [future.result() for future in futures]

                    df = pd.concat(df)

                df = (df.groupby(["puma22", "POVPIP", "has_pap", "has_ssip", "has_hins4", "has_snap",
                                  "American Indian and Alaska Native", "Asian", "Black or African American",
                                  "Native Hawaiian", "Pacific Islander", "White", "Hispanic or Latino", "Veteran",
                                  "Elderly", "DIS", "English less than very well", "HH Income"]).agg({"WGTP": "sum"}).
                      reset_index())

                df["WGTP"] = df["WGTP"].astype(np.float64)
                df["WGTP"] = df["WGTP"].round(0).astype(int)
                df["American Indian and Alaska Native"] = (df["WGTP"] * df["American Indian and Alaska Native"]).round(
                    0).astype(int)
                df["Asian"] = (df["WGTP"] * df["Asian"]).round(0).astype(int)
                df["Black or African American"] = (df["WGTP"] * df["Black or African American"]).round(0).astype(int)
                df["Native Hawaiian"] = (df["WGTP"] * df["Native Hawaiian"]).round(0).astype(int)
                df["Pacific Islander"] = (df["WGTP"] * df["Pacific Islander"]).round(0).astype(int)
                df["White"] = (df["WGTP"] * df["White"]).round(0).astype(int)
                df["Hispanic or Latino"] = (df["WGTP"] * df["Hispanic or Latino"]).round(0).astype(int)
                df["Veteran"] = (df["WGTP"] * df["Veteran"]).round(0).astype(int)
                df["Elderly"] = (df["WGTP"] * df["Elderly"]).round(0).astype(int)
                df["DIS"] = (df["WGTP"] * df["DIS"]).round(0).astype(int)
                df["English less than very well"] = (df["WGTP"] * df["English less than very well"]).round(0).astype(
                    int)

                # Drop the rows where WGTP is 0, they will not be used regardless
                df = df[df["WGTP"] != 0]

                df.to_csv(end_file.replace(".csv", "-puma22.csv"), index=False)

        else:
            df = pd.read_csv(state_dir + state + "/" + state + "-eligibility-puma22.csv", dtype={"puma22": str},
                             low_memory=False)

        for geo in geos.keys():

            if not os.path.exists(end_file.replace(".csv", "-" + geo + ".csv")):
                print(geo)

                dc = geos[geo]

                cols = df.columns.tolist()

                cols.remove("puma22")

                cols.insert(0, geo)

                temp_new_puma_dc = {
                    new_geo_code: [(old_geo_code, afact) for old_geo_code, afact in old_geo_code_tuple if
                                   old_geo_code
                                   in df["puma22"].unique()] for new_geo_code, old_geo_code_tuple
                    in dc.items()}

                temp_new_puma_dc = {new_geo_code: old_geo_code_tuple for new_geo_code, old_geo_code_tuple in
                                    temp_new_puma_dc.items() if
                                    old_geo_code_tuple}

                num_chunks = 5000
                chunk_size = len(df) // num_chunks

                if chunk_size != 0:
                    df_chunks = [df.iloc[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
                else:
                    df_chunks = [df.iloc[i:i + 1] for i in range(0, len(df), 1)]

                with ThreadPoolExecutor(max_workers=num_chunks) as executor:
                    futures = [executor.submit(process_chunk, chunk, temp_new_puma_dc, "puma22", geo) for
                               chunk in df_chunks]

                new_df = [future.result() for future in futures]

                new_df = pd.concat(new_df)

                new_df = (
                    new_df.groupby([geo, "POVPIP", "has_pap", "has_ssip", "has_hins4", "has_snap",
                                    "American Indian and Alaska Native", "Asian", "Black or African American",
                                    "Native Hawaiian", "Pacific Islander", "White", "Hispanic or Latino",
                                    "Veteran", "Elderly", "DIS", "English less than very well",
                                    "Individual Income"]).agg({"WGTP": "sum"}).reset_index())

                new_df["WGTP"] = new_df["WGTP"].astype(np.float64)
                new_df["WGTP"] = new_df["WGTP"].round(0).astype(int)
                new_df["American Indian and Alaska Native"] = (
                            new_df["WGTP"] * new_df["American Indian and Alaska Native"]).round(
                    0).astype(int)
                new_df["Asian"] = (new_df["WGTP"] * new_df["Asian"]).round(0).astype(int)
                new_df["Black or African American"] = (new_df["WGTP"] * new_df["Black or African American"]).round(
                    0).astype(int)
                new_df["Native Hawaiian"] = (new_df["WGTP"] * new_df["Native Hawaiian"]).round(0).astype(int)
                new_df["Pacific Islander"] = (new_df["WGTP"] * new_df["Pacific Islander"]).round(0).astype(int)
                new_df["White"] = (new_df["WGTP"] * new_df["White"]).round(0).astype(int)
                new_df["Hispanic or Latino"] = (new_df["WGTP"] * new_df["Hispanic or Latino"]).round(0).astype(int)
                new_df["Veteran"] = (new_df["WGTP"] * new_df["Veteran"]).round(0).astype(int)
                new_df["Elderly"] = (new_df["WGTP"] * new_df["Elderly"]).round(0).astype(int)
                new_df["DIS"] = (new_df["WGTP"] * new_df["DIS"]).round(0).astype(int)
                new_df["English less than very well"] = (new_df["WGTP"] * new_df["English less than very well"]).round(
                    0).astype(
                    int)

                new_df.to_csv(end_file.replace(".csv", "-" + geo + ".csv"), index=False)

        # Delete variables that are no longer needed
        try:
            del person_df
        except:
            pass
        try:
            del household_df
        except:
            pass

