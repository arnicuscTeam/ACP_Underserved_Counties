import os
import time
import urllib.request

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager  # pip install webdriver_manager


# Function to get the link to the most recent GeoCorr Application using requests, returns the link
def getMostRecentGeoCorrApplication(data_directory: str, link_year: int = 0) -> str:

    """
    This function gets the link to the most recent GeoCorr Application using requests. It is useful when the user wants
    to download the crosswalk files for a specific year. If the user does not specify a year, the function will use the
    link to the most recent application.
    :param data_directory: The path to the data directory
    :param link_year: The year of the application that the user wants to download the crosswalk files for
    :return: The link to the most recent GeoCorr Application
    """

    directory = data_directory + "GeoCorr"

    # Create directory for downloads
    if not os.path.exists(directory):
        os.makedirs(directory)

    # GeoCorr Applications website
    website = "https://mcdc.missouri.edu/applications/geocorr.html"

    # Main link for the website
    main_link = "https://mcdc.missouri.edu"

    # Request the website
    response = requests.get(website)

    # Parse the website
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all links
    links = soup.find_all("a")

    # Filter the links to only include the links that contain the text "Geocorr"
    links = [link for link in links if "Geocorr" in link.text]

    # The second link is the most recent application
    if link_year != 0:
        for link in links:
            if str(link_year) in link.text:
                newest_link = main_link + link["href"]
    else:
        newest_link = main_link + links[1]["href"]

    return newest_link


# Download the crosswalk file, parameter is the weblink, path to the data directory and state, returns the file path
def downloadCrossWalkFile(weblink: str, data_directory: str, state_name: str, source_geography: str,
                          target_geography: str, weight: str = "population") -> tuple[str, str]:
    """
    This function downloads the crosswalk file for the specified source and target geographies. It also cleans the
    crosswalk file.
    :param weblink: The link to the GeoCorr Application.
    :param data_directory: The path to the data directory.
    :param state_name: The name of the state in case the user wants to download the crosswalk file for a specific state.
    :param source_geography: The source geography.
    :param target_geography: The target geography.
    :param weight: The weight to use for the crosswalk file. population, housing, land_area
    :return: The file path to the crosswalk file and the name of the source geography column.
    """

    options = ["state", "county", "county subdivision (township, mcd)",
               "place (city, town, village, cdp, etc.)", "census tract", "census block group", "census block",
               "zip/zcta", "public-use microdata area (puma)", "core-based statistical area (cbsa)",
               "cbsa type (metro or micro)", "metropolitan division", "combined statistical area",
               "necta (new england only)", "necta division (new england only)", "combined necta (new england only)",
               "american indian / alaska native / native hawaiian areas", "state legislative district — upper chamber",
               "state legislative district — lower chamber", "unified school district", "elementary school district",
               "secondary school district", "best school district", "best school district type", "county size category",
               "place size category", "within-a-place code", "state legislative district — upper chamber",
               "state legislative district — lower chamber", "urban-rural portion", "urban Area",
               "118th congress (2023-2024)", "117th congress (2021-2022)", "116th congress (2019-2020)",
               "puma (2012)", "voting tabulation district", "hospital service area (2019)",
               "hospital referral region (2019)", "library district (2022)", "regional planning commissions",
               "u. of missouri extension regions", "mo dept. of economic development regions",
               "mo dept. of transportation districts", "mo area agencies on aging", "mo brfss regions"]

    optionsBeforeSource = options[:options.index(source_geography.lower())]

    temp_geo = source_geography[:]
    temp_geo = temp_geo.replace("/", "_")

    directory = data_directory + f"GeoCorr/{weight.title()}/"
    if not os.path.exists(directory):
        os.makedirs(directory)

    directory += temp_geo

    # Create directory for downloads
    if not os.path.exists(directory):
        os.makedirs(directory)

    # List of states
    states = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
              "District of Columbia", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
              "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
              "Mississippi", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
              "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
              "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas",
              "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]


    # Open the Chrome browser
    chrome_options = Options()

    # Run the browser in headless mode
    chrome_options.add_argument("--headless")

    service = webdriver.chrome.service.Service(ChromeDriverManager().install())

    # Create the driver
    driver = webdriver.Chrome(options=chrome_options, service=service)

    # Go to the website
    driver.get(weblink)

    # Wait for the page to load
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "leftBox")))

    # Find all the input boxes
    inputs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))

    for inp in inputs:
        if inp.get_attribute("value") == "hus20" and weight.title() == "Housing":
            inp.click()
            break
        elif inp.get_attribute("value") == "LandSQMI" and weight == "land_area":
            inp.click()
            break

    # Clicker variable to only click the source geography once on the left side
    clicker = 0

    # Select the state_name, source geography, and target geography
    selectable_options = driver.find_elements(By.TAG_NAME, "option")

    for option in selectable_options:

        # To set the state(s)
        if state_name == "0":
            if option.text in states:
                option.click()
        else:
            # Click the state_name and unclick the auto-selected Missouri
            if option.text == state_name or option.text == "Missouri":
                option.click()

        # To set the targe geography and source geography
        if target_geography.lower() not in optionsBeforeSource:
            # Only click the source geography once on the left side
            if option.text.lower() == source_geography.lower() and clicker == 0:
                option.click()
                clicker += 1

            # To click and unclick the left side target geography
            elif target_geography.lower() == option.text.lower() and (clicker == 1):
                option.click()
                option.click()
                clicker += 1

            elif target_geography.lower() == option.text.lower() and clicker == 2:
                option.click()
                clicker += 1
        else:
            # Only click the source geography once on the left side
            if option.text.lower() == source_geography.lower() and clicker == 0:
                option.click()
                clicker += 1

            # To click and unclick the left side target geography
            elif target_geography.lower() == option.text.lower() and (clicker == 1):
                option.click()
                clicker += 1

    # Click the submit button
    submit_button = driver.find_elements(By.TAG_NAME, "input")
    submit_button[-2].click()

    # Wait for the page to load by looking for the tag h1 and the text associated with it is "Query Output"
    WebDriverWait(driver, 30).until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Query Output"))

    time.sleep(3)

    # Find the link to download the file
    download_link = driver.find_element(By.TAG_NAME, "a")

    # Rename source and target geographies
    source_geography = source_geography.replace("/", "-").title()
    source_geography = source_geography.replace(" ", "-").title()

    target_geography = target_geography.replace("/", "-").title()
    target_geography = target_geography.replace(" ", "-").title()

    if "18" in weblink:
        target_geography = target_geography + "_2018"

    # Rename state_name if it is the United States
    if state_name == "0":
        state_name = "United_States"

    # File name
    file_name = state_name + "_" + source_geography + "_to_" + target_geography + ".csv"

    # Final file path
    file_path = directory + "/" + file_name

    # Download the file to the current directory
    urllib.request.urlretrieve(download_link.get_attribute("href"), file_path)

    # Close the browser
    driver.quit()

    source_col = ""
    if source_geography == "Zip-Zcta":
        source_col = "zcta"
    elif source_geography == "Census Tract":
        source_col = "tract"
    elif source_geography == "County":
        source_col = "county"
    elif source_geography == "Metropolitan Division":
        source_col = "metdiv"
    elif source_geography == "Public-Use-Microdata-Area-(Puma)":
        source_col = "puma"
    elif source_geography == "118Th Congress (2023-2024)":
        source_col = "cd"
    elif source_geography == "Unified School District":
        source_col = "sduni"

    # Clean the crosswalk file
    file_path = cleanCrossWalkFile(file_path, source_col)

    return file_path, source_col


# Clean the crosswalk file, parameter is the crosswalk file name, returns the file name
def cleanCrossWalkFile(file_name: str, source_col: str) -> str:

    """
    This function cleans the crosswalk file. This is necessary because the crosswalk files have an extra row at the top
    :param file_name: The name of the crosswalk file
    :param source_col: The name of the source geography column
    :return:
    """

    df = pd.read_csv(file_name, encoding="ISO-8859-1", dtype=str)

    # remove the first row
    df = df.iloc[1:]
    columns = df.columns.tolist()

    for column in columns:
        if source_col.lower() in column.lower():
            source_col = column
            break

    df[source_col] = df[source_col].astype(str)
    df[source_col] = df[source_col].str.strip()

    # Always do this
    try:
        # zcta column is a string
        df["zcta"] = df["zcta"].astype(str)
        df["zcta"] = df["zcta"].str.strip()

        # zcta column is five characters long
        df["zcta"] = df["zcta"].str.zfill(5)
    except:
        pass

    # Also always do this
    try:
        df["state"] = df["state"].astype(str)
        df["state"] = df["state"].str.strip()
        df["state"] = df["state"].str.zfill(2)
    except:
        pass

    # Make the puma column 7 characters long
    if "puma" in source_col:
        df[source_col] = df[source_col].astype(str)
        df[source_col] = df[source_col].str.strip()
        df[source_col] = df[source_col].str.zfill(5)
        df[source_col] = df["state"] + df[source_col]


    # If target is Unified School District
    try:
        # sduni20 column is a string
        df["sduni20"] = df["sduni20"].astype(str)
        df["sduni20"] = df["sduni20"].str.strip()

        # sduni20 column is five characters long
        df["sduni20"] = df["sduni20"].str.zfill(5)

        # State column is a string
        df["state"] = df["state"].astype(str)

        # State column is two characters long
        df["state"] = df["state"].str.zfill(2)

        # Combine the state and sduni20 columns
        df["sduni20"] = df["state"] + df["sduni20"]

        # Drop the state column
        df = df.drop(columns=["state"])
    except:
        pass

    # If target is metropolitan division
    try:
        # metdiv20 column is a string
        df["metdiv20"] = df["metdiv20"].astype(str)
        df["metdiv20"] = df["metdiv20"].str.strip()

        # metdiv20 column is five characters long
        df["metdiv20"] = df["metdiv20"].str.zfill(5)

        df = df.drop(columns=["state"])
    except:
        pass

    # If target is census tract
    try:
        # Tract column is a string
        df["tract"] = df["tract"].astype(str)
        df["tract"] = df["tract"].str.strip()

        # Remove the decimal
        df["tract"] = df["tract"].str.replace(".", "", regex=False)

        # Tract column is six characters long
        df["tract"] = df["tract"].str.pad(width=6, side='right', fillchar='0')

        # County column is a string
        df["county"] = df["county"].astype(str)

        # County column is five characters long
        df["county"] = df["county"].str.zfill(5)

        # Combine the county and tract columns
        df["tract"] = df["county"] + df["tract"]

        # Drop the county column
        df = df.drop(columns=["county"])

        # Rename the tract column if we are using 2018 geocorr
        if "2018" in file_name:
            df = df.rename(columns={"tract": "tract10"})
    except:
        pass

    # If target is county
    try:
        # County column is a string
        df["county"] = df["county"].astype(str)
        df["county"] = df["county"].str.strip()

        # County column is five characters long
        df["county"] = df["county"].str.zfill(5)
    except:
        pass

    # If target is 118th Congress (2023-2024)
    try:
        # cd118 column is a string
        df["cd118"] = df["cd118"].astype(str)
        df["cd118"] = df["cd118"].str.strip()

        # cd118 column is two characters long
        df["cd118"] = df["cd118"].str.zfill(2)

        # State column is a string
        df["state"] = df["state"].astype(str)

        # State column is two characters long
        df["state"] = df["state"].str.zfill(2)

        # Combine the state and cd118 columns
        df["cd118"] = df["state"] + df["cd118"]

        # Drop the state column
        df = df.drop(columns=["state"])
    except:
        pass

    # If target is public-use microdata area (PUMA)
    try:
        if "puma" not in source_col:
            # puma22 column is a string
            df["puma22"] = df["puma22"].astype(str)
            df["puma22"] = df["puma22"].str.strip()

            # puma22 column is five characters long
            df["puma22"] = df["puma22"].str.zfill(5)

            # State column is a string
            df["state"] = df["state"].astype(str)
            df["state"] = df["state"].str.strip()

            # State column is two characters long
            df["state"] = df["state"].str.zfill(2)

            # Combine the state and puma22 columns
            df["puma22"] = df["state"] + df["puma22"]

            # Make the puma22 column 7 characters long
            df["puma22"] = df["puma22"].str.zfill(7)

        # Drop the state column if it is not the source or target geography
        temp_name = file_name.split("States")[1]

        if "State" not in temp_name:
            df = df.drop(columns=["state"])
    except:
        pass

    try:
        # Drop the rows that have 00000 as the zip code
        df = df[df["zcta"] != "00000"]
    except:
        pass

    finally:
        # Save the file
        df.to_csv(file_name, index=False)

        # Delete the df to free up memory
        del df

    return file_name
