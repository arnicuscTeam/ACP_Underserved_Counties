import os
import shutil
import time
import zipfile
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager  # pip install webdriver_manager


def getBDCData(data_dir: str):
    """
    This function downloads the fixed broadband provider data from the BDC. This file contains the most recent
    information about all the providers and their associated IDs.
    :param data_dir: The path to the data folder
    :return: None
    """

    # Set the path to the data folder
    isp_folder = data_dir + "ISP/"

    # Read the zip file inside the bdc folder
    zf = zipfile.ZipFile(isp_folder + "bdc_us_fixed_broadband_provider_summary_123122.zip")

    # Read the csv file inside the zip file
    df = pd.read_csv(zf.open("bdc_us_fixed_broadband_provider_summary_123122.csv"))

    # Drop the "location_count_bus" column
    df = df.drop(columns=["location_count_bus"])
    df = df.drop(columns=["unit_count_bus"])

    # Find the unique company names by grouping the provider_id column
    unique_providers = df.groupby("provider_id").first()

    # Create a df of the unique company names
    unique_providers = unique_providers.reset_index()
    unique_providers = unique_providers[["provider_id", "holding_company"]]

    # Save the unique company names to a csv file
    unique_providers.to_csv(isp_folder + "unique_providers_bdc.csv", index=False)


def getMonthZips(start_date, end_date, data_dir):
    """
    This function downloads the zip file from the USA Spending website, given a start date and end date. This uses
    Selenium to automate the process of downloading the zip file. The zip file is downloaded to a temp folder, then
    renamed and moved to the data folder.
    :param start_date: The start date for the month we want to download
    :param end_date: The end date for the month we want to download
    :param data_dir: The path to the data folder
    :return: None
    """

    # Set the path to the data folder
    spending_data_folder = 'usaspending'

    # The temp folder where the zip file will be downloaded
    tmp_folder = 'tmp'

    # Website
    website = "https://www.usaspending.gov/search"

    # Set the options for the Chrome driver
    options = Options()

    options.add_argument("--window-size=1920,1200")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Set the desired download directory
    options.add_experimental_option("prefs", {
        "download.default_directory": os.getcwd() + '/' + spending_data_folder + '/' + tmp_folder
    })

    # Create the service
    service = webdriver.chrome.service.Service(ChromeDriverManager().install())

    # Create the driver
    driver = webdriver.Chrome(options=options, service=service)

    # Go to the website
    driver.get(website)

    # Wait for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "filter-date-range-tab")))

    # Click on the date range tab to set the date range
    date_range_tab = driver.find_element(By.ID, "filter-date-range-tab")

    # Click on the date range tab
    date_range_tab.click()

    # Wait for the options to load
    time.sleep(5)

    # Get the inputs
    inputs = driver.find_elements(By.TAG_NAME, "input")

    # Set the dates
    for i in inputs:
        # Wait for the inputs to load
        time.sleep(1.5)
        # Set the start date
        if i.get_attribute("aria-label") == "Action Date Start":
            start = i
            start.send_keys(start_date)
        # Set the end date
        elif i.get_attribute("aria-label") == "Action Date End":
            end = i
            end.send_keys(end_date)

    # Wait for the inputs to load
    time.sleep(1.5)

    # Click on the set date range button
    buttons = driver.find_elements(By.TAG_NAME, "button")

    # Look for the button with the text "Filter by date range"
    for b in buttons:
        if b.get_attribute("aria-label") == "Filter by date range":
            b.click()
            break

    # Wait for the page to load
    time.sleep(0.5)

    # Find the Awarding Agency menu
    buttons = driver.find_elements(By.TAG_NAME, "button")

    # Look for the button with the text "Agency"
    for b in buttons:
        if b.get_attribute("aria-label") == "Agency":
            actions = ActionChains(driver)

            # Move to the element and click
            actions.move_to_element(b).perform()
            actions.move_to_element(b).perform()
            b.click()
            break

    # Wait for the page to load
    time.sleep(1.5)

    # Set the Awarding Agency
    inputs = driver.find_elements(By.TAG_NAME, "input")

    # Look for the input with the placeholder "Awarding Agency"
    for i in inputs:
        if i.get_attribute("placeholder") == "Awarding Agency":
            # Set the value to "Federal Communications Commission"
            i.send_keys("Federal Communications Commission")
            time.sleep(5)
            i.send_keys(Keys.ENTER)
            break

    # Wait for the page to load
    time.sleep(1)

    # Find the Assistance Listing (CFDA Program) button
    buttons = driver.find_elements(By.TAG_NAME, "button")

    # Look for the button with the text "Assistance Listing (CFDA Program)" in order enter the CFDA number
    for b in buttons:
        if b.get_attribute("aria-label") == "Assistance Listing (CFDA Program)":
            actions = ActionChains(driver)

            # Move to the element and click
            actions.move_to_element(b)
            actions.scroll_to_element(b)
            actions.perform()
            b.click()
            break

    # Wait for the page to load
    time.sleep(3)

    # Set the Assistance Listing (CFDA Program)
    inputs = driver.find_elements(By.TAG_NAME, "input")

    # Look for the input with the placeholder "e.g., 93.778 - Medical Assistance Program"
    for i in inputs:
        if i.get_attribute("placeholder") == "e.g., 93.778 - Medical Assistance Program":
            i.send_keys("32.008")
            time.sleep(5)
            i.send_keys(Keys.ENTER)
            break

    # Wait for the page to load
    time.sleep(1)

    # Find submit button
    element = driver.find_element(By.CLASS_NAME, "submit-button")

    # Create an instance of ActionChains
    actions = ActionChains(driver)
    time.sleep(1)

    # Move to the element and click
    actions.move_to_element(element).click().perform()
    actions.move_to_element(element).click().perform()

    time.sleep(2)

    # Wait for the page to load
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "header-sort")))

    # Find the filters
    filters = driver.find_element(By.CLASS_NAME, "search-top-filters-content")

    # Only get the actual filter names
    new_filters = filters.find_elements(By.CLASS_NAME, "filter-item-title")

    # If there are less than 3 filters, then the results are wrong
    if len(new_filters) < 3:
        driver.quit()
        return 1

    # Wait for the page to load
    time.sleep(10)

    # Find the download button
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "usda-button")))
    download_button = driver.find_element(By.CLASS_NAME, "usda-button")

    # Click the download button
    download_button.click()

    # Find all "level-button" elements to click on "Award"
    buttons = driver.find_elements(By.CLASS_NAME, "level-button")

    # Click on the "Transaction" button to get the transaction data
    for b in buttons:
        if b.get_attribute("aria-label") == "Transaction":
            time.sleep(0.5)
            b.click()
            time.sleep(0.5)
            break

    # Find all "level-button" elements to click on "Everything"
    buttons = driver.find_elements(By.CLASS_NAME, "level-button")

    # Click on the "Everything" button to get all the data
    for b in buttons:
        if b.get_attribute("aria-label") == "Everything":
            time.sleep(0.5)
            b.click()
            time.sleep(0.5)
            break

    count = 0

    # Break once the file has been downloaded to the temp folder, with a max wait time of 3 minutes
    while len(os.listdir(
            os.getcwd() + '/' + spending_data_folder + '/' + tmp_folder)) != 1 and count < 180:
        time.sleep(1)
        count += 1

    # List the files in the temp folder, which should only have one file
    files = os.listdir(os.getcwd() + '/' + spending_data_folder + '/' + tmp_folder)

    try:
        # Wait for the file to finish downloading
        while files[0].endswith(".crdownload"):
            time.sleep(1)
            files = os.listdir(os.getcwd() + '/' + spending_data_folder + '/' + tmp_folder)

        # Set the end file name
        end_file = data_dir + "ACP_Awards/Mid_Files/" + start_date[0:2] + '_' + start_date[6:] + ".zip"

        # Rename the file and move it to the data folder
        os.rename(os.getcwd() + '/' + spending_data_folder + '/' + tmp_folder + '/' + files[0], end_file)

    except:
        pass

    # Close the driver
    driver.quit()


def downloadAllMonths(data_dir: str):
    """
    This function downloads all the zip files from the USA Spending website from the start of ACP until the latest full
    month. This uses the getMonthZips function to download the zip files.
    :param data_dir: The path to the data folder
    :return: None
    """

    # Set the path to the data folder
    spending_data_folder = 'usaspending'

    # Create the directory if it doesn't exist
    if not os.path.exists(spending_data_folder):
        os.makedirs(spending_data_folder)

    # Create the temp folder if it doesn't exist
    tmp_folder = 'tmp'
    if not os.path.exists(spending_data_folder + '/' + tmp_folder):
        os.makedirs(spending_data_folder + '/' + tmp_folder)

    # Set the path to the data folder where the zip files will be stored
    path_to_data = data_dir + "ACP_Awards/Mid_Files/"

    # Create the directory if it doesn't exist
    if not os.path.exists(path_to_data):
        os.makedirs(path_to_data)

    years = ["2022", "2023"]

    start_months = ["01/01", "02/01", "03/01", "04/01", "05/01", "06/01", "07/01", "08/01", "09/01", "10/01", "11/01",
                    "12/01"]

    end_months = ["01/31", "02/28", "03/31", "04/30", "05/31", "06/30", "07/31", "08/31", "09/30", "10/31", "11/30",
                  "12/31"]

    # Loop through the years and months
    for year in years:

        # Loop through the months
        for index, month in enumerate(start_months):
            # Set the current file name
            current_file_name = start_months[index][:2] + "_" + year + ".zip"

            # Set the end date
            end_date = end_months[index] + "/" + year

            # Get the current date
            current_day = time.strftime("%d")
            current_month = time.strftime("%m")
            current_year = time.strftime("%Y")

            # Set the current date as a datetime object
            current_date = current_month + "/" + current_day + "/" + current_year
            current_date = datetime.strptime(current_date, "%m/%d/%Y")

            # Set the end date as a datetime object
            test_date = datetime.strptime(end_date, "%m/%d/%Y")

            # If the end date is before the current date, then download the zip file
            if test_date < current_date:
                # Keep trying to download the zip file until it is downloaded
                while current_file_name not in os.listdir(path_to_data):
                    # If the zip file is already in the folder, then break
                    if current_file_name in os.listdir(path_to_data):
                        break
                    # If the zip file is not in the folder, then download it by calling the getMonthZips function
                    else:
                        getMonthZips(start_months[index] + "/" + year, end_months[index] + "/" + year, data_dir)


def collectFundingData(df: pd.DataFrame, funding_type: str):
    """
    This function collects the funding data for the ACP Awards. It takes in a dataframe and a funding type, then returns
    a dataframe with the company names, award amounts, and UEIs.
    :param df: The dataframe with the ACP Awards data
    :param funding_type: The funding type, which is either ACP or EBB
    :return: A dataframe with the company names, award amounts, and UEIs
    """

    # Only use the rows where award_id_fain starts with AC
    df = df[df["award_id_fain"].str.startswith(funding_type)]

    # If the row does not have a value for the recipient_parent_name column, then set the value to the value in the
    # recipient_name column
    df.loc[df["recipient_parent_name"].isnull(), "recipient_parent_name"] = df["recipient_name"]

    # Get the unique companies
    unique_companies = df["recipient_parent_name"].unique()
    company_groups = df.groupby("recipient_parent_name")

    # Create a dictionary to store the company names and their respective dataframes
    main_dict = {}

    # Loop through the unique companies
    for company in unique_companies:
        company_df = company_groups.get_group(company)

        # Get the award amounts
        award_amounts = company_df["federal_action_obligation"].astype(float).sum()

        # Store the award amounts in the dictionary
        main_dict[company] = {}
        main_dict[company]["Award"] = round(award_amounts)
        main_dict[company]["UEI"] = company_df["recipient_uei"].unique()[0]

    # Create a dataframe from the dictionary
    rows = []
    awards = []
    ueis = []

    for key, value in main_dict.items():
        rows.append(key)
        awards.append(value["Award"])
        ueis.append(value["UEI"])

    main_df = pd.DataFrame({"Company Name": rows, "UEI": ueis, "Award": awards})

    main_df.set_index("Company Name", inplace=True)

    return main_df


def mergeAllCSV(data_dir: str):
    """
    This function merges all the csv files from the ACP Awards into one csv file. It takes in the path to the data.
    :param data_dir: The path to the data folder
    :return: None
    """

    # Set the path to the temp csv folder
    csv_folder = data_dir + "ACP_Awards/Temp_CSV_Folder/"

    # Get the csv files
    csv_files = os.listdir(csv_folder)

    # Sort the file names by date
    new_csv_files = []

    # Loop through the csv files
    while len(new_csv_files) < len(csv_files):
        # Loop through the csv files
        for file in csv_files:
            # Get the month and year
            underscore = file.find("_")
            zip_end = file.find(".csv")
            month = file[:underscore]
            year = file[underscore + 1:zip_end]

            # Get the file number
            file_num = int(month) + ((int(year) % 2022) * 12)

            # If the file number is equal to the length of the new csv files plus 1
            if file_num == len(new_csv_files) + 1:
                # Add the file name to the list
                new_csv_files.append(file)

    # Return the list in reverse order, so we have newest to oldest
    new_csv_files = new_csv_files[::-1]

    main_df = pd.DataFrame()

    # Loop through the csv files
    for index, file in enumerate(new_csv_files):
        # Read the csv file
        df = pd.read_csv(csv_folder + file, index_col=0)

        # If it is the first csv file
        if index == 0:
            # Create the main dataframe
            main_df = pd.concat([main_df, df], axis=1)

        else:
            # Merge the dataframes
            main_df = pd.merge(main_df, df, on=["Company Name", "UEI"], how="outer")

    # Change all null values to 0
    main_df.fillna(0, inplace=True)

    # Save the dataframe as a csv file
    main_df.to_csv(data_dir + "ACP_Awards/ACP_Awards.csv")

    # Delete the temp csv folder
    shutil.rmtree(csv_folder)


def collectAllSpendingData(data_dir: str):
    """
    This function collects all the data from the ACP Awards, storing each month in a separate csv file, then merging
    all the csv files into one csv file by calling the mergeAllCSV function. It takes in the path to the data.
    :param data_dir: The path to the data folder
    :return: None
    """

    # Set the path to the awards folder
    awards_dir = data_dir + "ACP_Awards/"

    # Set the path to the zip files
    path_to_data = awards_dir + "Mid_Files/"

    # Set the path to the temp csv folder to store temp csv files
    temp_csv_folder = awards_dir + "Temp_CSV_Folder/"

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # Create the temp csv folder if it doesn't exist
    if not os.path.exists(temp_csv_folder):
        os.makedirs(temp_csv_folder)

    # Get the file names
    file_names = os.listdir(path_to_data)

    new_file_names = []

    # Sort the file names by date
    while len(new_file_names) < len(file_names):
        # Loop through the file names
        for file in file_names:
            # Get the month and year
            underscore = file.find("_")
            zip_end = file.find(".zip")
            month = file[:underscore]
            year = file[underscore + 1:zip_end]

            # Get the file number
            file_num = int(month) + ((int(year) % 2022) * 12)

            # If the file number is equal to the length of the new file names plus 1
            if file_num == len(new_file_names) + 1:
                # Add the file name to the list
                new_file_names.append(file)

    # Loop through the file names
    for file in new_file_names:

        try:
            # Unzip the file
            with zipfile.ZipFile(path_to_data + file, 'r') as zip_ref:
                # Loop through the files in the zip file
                for csv in zip_ref.namelist():
                    # If the file is the Assistance_PrimeTransactions csv file
                    if csv.startswith("Assistance_Prime"):
                        # Read the csv file
                        df = pd.read_csv(zip_ref.open(csv), low_memory=False)

                        # Collect the data
                        df_acp = collectFundingData(df, "AC")
                        df_ebb = collectFundingData(df, "EB")

                        # Get the month
                        index = file.find("_")
                        end = file.find(".")
                        month = file[:index]
                        month = int(month) - 1

                        # Rename the columns
                        df_acp.columns = ["UEI ACP", months[month] + file[index:end] + " ACP"]
                        df_ebb.columns = ["UEI EBB", months[month] + file[index:end] + " EBB"]

                        # Rename the index column
                        df_acp.index.name = "Company Name"
                        df_ebb.index.name = "Company Name"

                        # Merge the dataframes
                        df = pd.merge(df_acp, df_ebb, on="Company Name", how="outer")

                        # If UEI ACP is null, get the EBB UEI
                        df["UEI ACP"] = df["UEI ACP"].fillna(df["UEI EBB"])

                        # Drop UEI EBB
                        df.drop("UEI EBB", axis=1, inplace=True)

                        # Rename UEI ACP
                        df.rename(columns={"UEI ACP": "UEI"}, inplace=True)

                        # Change all null values to 0
                        df.fillna(0, inplace=True)

                        # Create the temp csv file
                        df.to_csv(temp_csv_folder + file.replace(".zip", ".csv"))
        except:
            # If there is an error, print the error and the file name
            print("Error with file: " + file)

            # Delete the file
            # os.remove(path_to_data + file)

            continue

    # Merge all the temp csv files
    mergeAllCSV(data_dir)


def collectCompNamesUSA(data_dir: str):
    """
    This function collects the unique company names from the ACP Awards. It takes in the path to the data.
    :param data_dir: The path to the data folder
    :return: None
    """

    # Set the path to the awards folder and the isp folder
    awards_dir = data_dir + "ACP_Awards/"

    # Read the csv file
    df = pd.read_csv(awards_dir + "ACP_Awards.csv")

    # Get the unique company names
    names_temp = df["Company Name"].unique()

    # Create a dictionary to store the companies that have used multiple names
    temp_same_company = {}

    # Loop through the company names to compare them with each other
    for i in range(len(names_temp)):

        # Get the first name
        name = names_temp[i]

        # Loop through the company names again
        for j in range(i + 1, len(names_temp)):

            # Get the second name
            name2 = names_temp[j]

            # Get the UEI for each company
            uei1 = df.loc[df["Company Name"] == name, "UEI"].values[0]
            uei2 = df.loc[df["Company Name"] == name2, "UEI"].values[0]

            # Check if they are the same company based off the UEI
            if uei1 == uei2 and name != name2 and str(uei1) != "0":
                # Store the company names in the dictionary
                name = name.strip()
                name = name.strip("\"")
                name2 = name2.strip()
                name2 = name2.strip("\"")

                temp_same_company[name] = name2

    # Manually add more companies that have used multiple names, based off the BDC file
    temp_same_company["Charter Communications"] = "CHARTER COMMUNICATIONS OPERATING LLC"
    temp_same_company["T-MOBILE US, INC."] = "T-Mobile USA, Inc."

    # Write out the dictionary to a csv file
    df_dict = pd.DataFrame.from_dict(temp_same_company, orient="index")
    df_dict.to_csv(awards_dir + "same_company.csv", header=False)

    # Loop through the keys and values in the dictionary to replace the ACPs and EBBs
    for key, value in temp_same_company.items():
        try:
            # Fill both company names with the data from the other company and only keep the row that uses the key name
            comp_col = 'Company Name'
            companies = [key, value]

            filtered_df = df.loc[df[comp_col].isin(companies)].copy()

            filtered_df.loc[:, "dummy"] = 1

            merged_df = filtered_df.groupby('dummy').max().drop(columns=comp_col)

            df.loc[df[comp_col].isin(companies), df.columns != comp_col] = merged_df.values

            # Replace the name of the company
            df.loc[df["Company Name"].isin([key, value]), "Company Name"] = key

            # Drop the duplicate rows
            df = df.drop_duplicates(subset="Company Name", keep="first")
        except:
            pass

    # Get the company names and UEIs and store them in a dictionary so that we have the correct UEI for each company
    company_names = df["Company Name"].unique()

    # Create a dictionary to store the company names and their respective UEIs
    main_dict = {}

    # Loop through the company names
    for company in company_names:
        # Get the UEI
        uei = df.loc[df["Company Name"] == company, "UEI"].values[0]

        # Store the company name and UEI in the dictionary
        main_dict[company] = uei

    # Create a dataframe from the dictionary
    comp_list = []
    uei_list = []

    for key, value in main_dict.items():
        comp_list.append(key)
        uei_list.append(value)

    small_df = pd.DataFrame({"Company Name": comp_list, "UEI": uei_list})

    # Column to store the total ACP award amount for 2022
    small_df["ACP2022"] = 0

    # Keep only the columns that have 2022 and ACP in the column name, along with the company name
    df_temp_2022 = df.filter(regex="2022|Company Name|ACP")

    # Loop through the company names
    for company in df_temp_2022["Company Name"]:
        # Get the sum of the row
        temp_frame = df_temp_2022.loc[df_temp_2022["Company Name"] == company].sum()

        # Convert the row to numeric values
        temp_frame = pd.to_numeric(temp_frame, errors="coerce")
        acp_sum = temp_frame.sum()

        # Store the sum in the dataframe
        small_df.loc[small_df["Company Name"] == company, "ACP2022"] = acp_sum

    # Column to store the total ACP award amount for 2023
    small_df["ACP2023"] = 0

    # Keep only the columns that have 2023 and ACP in the column name, along with the company name
    df_temp_2023 = df.filter(regex="2023|Company Name|ACP")

    # Loop through the company names
    for company in df_temp_2023["Company Name"]:
        # Get the sum of the row
        temp_frame = df_temp_2023.loc[df_temp_2023["Company Name"] == company].sum()

        # Convert the row to numeric values
        temp_frame = pd.to_numeric(temp_frame, errors="coerce")
        acp_sum = temp_frame.sum()

        # Store the sum in the dataframe
        small_df.loc[small_df["Company Name"] == company, "ACP2023"] = acp_sum

    # Column to store the total EBB award amount for 2022
    small_df["EBB2022"] = 0

    # Keep only the columns that have 2022 and EBB in the column name, along with the company name
    ebb_temp_2022 = df.filter(regex="2022|Company Name|EBB")

    # Loop through the company names
    for company in ebb_temp_2022["Company Name"]:
        # Get the sum of the row
        temp_frame = ebb_temp_2022.loc[ebb_temp_2022["Company Name"] == company].sum()

        # Convert the row to numeric values
        temp_frame = pd.to_numeric(temp_frame, errors="coerce")
        ebb_sum = temp_frame.sum()

        # Store the sum in the dataframe
        small_df.loc[small_df["Company Name"] == company, "EBB2022"] = ebb_sum

    # Column to store the total EBB award amount for 2023
    small_df["EBB2023"] = 0

    # Keep only the columns that have 2023 and EBB in the column name, along with the company name
    ebb_temp_2023 = df.filter(regex="2023|Company Name|EBB")

    # Loop through the company names
    for company in ebb_temp_2023["Company Name"]:
        # Get the sum of the row
        temp_frame = ebb_temp_2023.loc[ebb_temp_2023["Company Name"] == company].sum()

        # Convert the row to numeric values
        temp_frame = pd.to_numeric(temp_frame, errors="coerce")
        ebb_sum = temp_frame.sum()

        # Store the sum in the dataframe
        small_df.loc[small_df["Company Name"] == company, "EBB2023"] = ebb_sum

    # Write out the dataframe to a csv file
    small_df.to_csv(awards_dir + "Current_Spending.csv", index=False)


def combineBDCwithUSA(data_dir: str):
    """
    This function combines the BDC data with the USA Spending data. It takes in the path to the data.
    :param data_dir: The path to the data folder
    :return: None
    """

    # Set the path to the data folder
    isp_folder = data_dir + "ISP/"
    awards_folder = data_dir + "ACP_Awards/"

    # Set the path to the files
    bdc_file = isp_folder + "unique_providers_bdc.csv"
    usa_spending_file = awards_folder + "Current_Spending.csv"

    # The File contains the companies that have used multiple names
    cross_dict_file = awards_folder + "same_company.csv"

    # Turn the cross_dict_file into a dictionary
    main_dict = {}

    df = pd.read_csv(cross_dict_file, header=None)
    for index, row in df.iterrows():
        # Store the original name and the name to change it to in the main dictionary
        main_dict[row[0]] = row[1]

    # Read the BDC and USA Spending files
    bdc_df = pd.read_csv(bdc_file)
    usa_spending_df = pd.read_csv(usa_spending_file)

    # Create a list of the unique company names in the USA Spending file
    unique_usa_spending_names = usa_spending_df["Company Name"].unique()

    # Create a new dataframe to store the data
    main_df = pd.DataFrame()

    # Merge the empty dataframe with the BDC dataframe
    main_df = pd.concat([main_df, bdc_df], axis=1)

    # Create the columns for the USA Spending data
    main_df["ACP2022"] = 0
    main_df["ACP2023"] = 0
    main_df["EBB2022"] = 0
    main_df["EBB2023"] = 0

    # Loop through the rows in the BDC dataframe
    for index, row in bdc_df.iterrows():
        # Create a variable to determine if the company name is in the cross_dict_temp dictionary
        cont = False

        # Get the company name from the row
        name = row["holding_company"]

        # Remove all the commas, periods, and dashes from the name and lower it
        temp_name = name.lower()
        temp_name = temp_name.split(",")
        temp_name = "".join(temp_name)
        temp_name = temp_name.split(".")
        temp_name = "".join(temp_name)
        temp_name = temp_name.split("-")
        temp_name = "".join(temp_name)

        # Loop through the keys and values in the dictionary of companies that have used multiple names
        for k, v in main_dict.items():

            # Create temporary variables to store the keys and values
            temp_v = v[:].lower()
            temp_v = temp_v.split(",")
            temp_v = "".join(temp_v)
            temp_v = temp_v.split(".")
            temp_v = "".join(temp_v)
            temp_v = temp_v.split("-")
            temp_v = "".join(temp_v)
            temp_k = k[:].lower()
            temp_k = temp_k.split(",")
            temp_k = "".join(temp_k)
            temp_k = temp_k.split(".")
            temp_k = "".join(temp_k)
            temp_k = temp_k.split("-")
            temp_k = "".join(temp_k)

            # Check if the name is equal to the key or value
            if temp_name == temp_v or temp_name == temp_k:

                # If the name is equal to the value, then set the name to the key
                usa_spending_df_temp = usa_spending_df[usa_spending_df["Company Name"] == k]

                # If no rows are returned, then set the name to the value
                if len(usa_spending_df_temp) == 0:
                    usa_spending_df_temp = usa_spending_df[usa_spending_df["Company Name"] == v]

                # Reset the index
                usa_spending_df_temp = usa_spending_df_temp.reset_index(drop=True)

                # Rename the company name in the temp dataframe
                usa_spending_df_temp.loc[usa_spending_df_temp.index[0], "Company Name"] = name

                # Set the values in the main dataframe
                main_df.loc[index, "ACP2022"] = usa_spending_df_temp.loc[usa_spending_df_temp.index[0], "ACP2022"]
                main_df.loc[index, "ACP2023"] = usa_spending_df_temp.loc[usa_spending_df_temp.index[0], "ACP2023"]
                main_df.loc[index, "EBB2022"] = usa_spending_df_temp.loc[usa_spending_df_temp.index[0], "EBB2022"]
                main_df.loc[index, "EBB2023"] = usa_spending_df_temp.loc[usa_spending_df_temp.index[0], "EBB2023"]
                cont = True
                break

        # If the name is not in the dictionary, then loop through the unique company names in the USA Spending file
        if not cont:
            for name2 in unique_usa_spending_names:
                # Remove all the commas, periods, and dashes from the name and lower it
                temp_name2 = name2.lower().split("-")
                temp_name2 = "".join(temp_name2)
                temp_name2 = temp_name2.split(",")
                temp_name2 = "".join(temp_name2)
                temp_name2 = temp_name2.split(".")
                temp_name2 = "".join(temp_name2)

                # If the name is equal to the name in the USA Spending file, then set the values in the main dataframe
                if temp_name == temp_name2:
                    # Create a temporary dataframe
                    usa_spending_df_temp = usa_spending_df[usa_spending_df["Company Name"] == name2]

                    # Reset the index
                    usa_spending_df_temp = usa_spending_df_temp.reset_index(drop=True)

                    # Rename the company name in the temp dataframe
                    usa_spending_df_temp.loc[usa_spending_df_temp.index[0], "Company Name"] = name

                    # Set the values in the main dataframe
                    main_df.loc[index, "ACP2022"] = usa_spending_df_temp.loc[usa_spending_df_temp.index[0], "ACP2022"]
                    main_df.loc[index, "ACP2023"] = usa_spending_df_temp.loc[usa_spending_df_temp.index[0], "ACP2023"]
                    main_df.loc[index, "EBB2022"] = usa_spending_df_temp.loc[usa_spending_df_temp.index[0], "EBB2022"]
                    main_df.loc[index, "EBB2023"] = usa_spending_df_temp.loc[usa_spending_df_temp.index[0], "EBB2023"]
                    break

    main_df.to_csv(isp_folder + "Final.csv", index=False)


