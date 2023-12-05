import os
import zipfile
import pandas as pd
import requests


def extractProviderBlocks(data_dir: str):
    """
    This function extracts the block_geoid's from the fixed broadband data and creates a csv file for each provider.
    This also deletes every zip file. The files need to be downloaded manually from https://broadbandmap.fcc.gov.
    All the rows that have either less than 25 mbps download speed or 3 mbps upload speed will be dropped. This is done
    by iterating over every technology folder, and inside each technology folder iterating over every state zip file.
    The files created from this are the provider name followed by the technology they provide at the given blocks. The
    blocks inside each file are the blocks in which the provider provides those services. It also removes any characters
    that cannot be used to name a file or in a dataframe column.
    :param data_dir: The path to the data folder.
    :return: None
    """

    # Set the path to the data folder
    isp_dir = data_dir + "ISP/"
    tech_dir = isp_dir + "Technology_Provider_Data/"

    # Iterate through all the technologies
    for folder in os.listdir(tech_dir):

        if "." not in folder:

            # Create the sub folder path
            tech_sub_folder = tech_dir + folder + "/"

            # Create a dictionary to store the block_geoid's for each provider
            brand_dict = {}

            # Iterate through all the zip files in the folder, each zip file is a state
            for zip_file in os.listdir(tech_sub_folder):

                # Check if the file is a zip file
                if zip_file.endswith(".zip"):

                    # Extract the zip file
                    with zipfile.ZipFile(tech_sub_folder + zip_file, "r") as zip_ref:

                        # Get the names of the files inside the zip
                        file_names = zip_ref.namelist()

                        # Loop through the file names
                        for file_name in file_names:

                            # Check if the file is a csv file
                            if file_name.endswith(".csv"):

                                # Read the csv file
                                df = pd.read_csv(zip_ref.open(file_name))

                                # Drop the row if both max_advertised_download_speed is less than 25 or
                                # max_advertised_upload_speed is less than 3
                                df = df[~(df["max_advertised_download_speed"] < 25)]
                                df = df[~(df["max_advertised_upload_speed"] < 3)]

                                # Only keep frn, brand_name, and block_geoid
                                df = df[["provider_id", "brand_name", "block_geoid"]]

                                # Convert the block_geoid column to a string
                                df["block_geoid"] = df["block_geoid"].astype(str)
                                df["block_geoid"] = df["block_geoid"].str.zfill(15)

                                # Unique provider id's
                                provider_ids = df["provider_id"].unique()

                                # Find all the block_geoid's for each frn
                                for provider_id in provider_ids:
                                    # Create a dataframe for each frn
                                    provider_df = df[df["provider_id"] == provider_id]

                                    # Unique block_geoid's as a list
                                    block_geoids = provider_df["block_geoid"].unique().tolist()

                                    # Get the brand name
                                    brand_name = provider_df["brand_name"].iloc[0]
                                    brand_name = brand_name.replace(",", "")

                                    # Strip the brand name
                                    brand_name = brand_name.strip()

                                    # Store the provider id in the brand name for future reference
                                    brand_name = str(provider_id) + "; " + brand_name

                                    # Check if the brand name is in the dictionary
                                    if brand_name in brand_dict:
                                        # Add the block_geoid's to the list
                                        brand_dict[brand_name] += block_geoids
                                    else:
                                        # Create a new list for the brand name
                                        brand_dict[brand_name] = block_geoids

            # Create a dataframe from the dictionary
            main_df = pd.DataFrame.from_dict(brand_dict, orient="index").transpose()

            # Delete the dictionary to save memory
            del brand_dict

            # Reindex the columns
            main_df = main_df.reindex(sorted(main_df.columns), axis=1)
            tech_dict = {"Cable": "40", "Copper": "10", "Fiber": "50", "LBR": "72", "Licensed-Fixed-Wireless": "71",
                         "Unlicensed-Fixed-Wireless": "70"}

            # Create a csv file for each column called brand_name + "_tech.csv"
            for column in main_df.columns:
                # Strip the column name and replace all the characters that are not allowed in a file name
                temp_col = column.strip()
                temp_col = temp_col.split(";")[1]
                temp_col = temp_col.strip()
                temp_col = temp_col.replace("\"", "")
                temp_col = temp_col.replace(" ", "_")
                temp_col = temp_col.replace("/", "_")
                temp_col = temp_col.replace("\\", "_")
                temp_col = temp_col.replace(".", "")
                temp_col = temp_col.replace(",", "")
                temp_col = temp_col.replace("|", "")
                temp_col = temp_col.replace(":", "")
                temp_col = temp_col.replace("\'", "")
                temp_col = temp_col.replace("?", "")

                # Create the file name
                file_name = tech_sub_folder + temp_col + f"_{tech_dict[folder]}.csv"

                # Create a temporary dataframe
                temp_df = main_df[column].copy(deep=True)

                # Drop all the rows that have no block_geoid's
                temp_df = temp_df.dropna()

                # Convert the block_geoid's to integers
                temp_df.to_csv(file_name, index=False)

            # Delete all the zip files in the folder
            for zip_file in os.listdir(tech_sub_folder):
                # Check if the file is a zip file
                if zip_file.endswith(".zip"):
                    # Delete the zip file
                    os.remove(tech_sub_folder + zip_file)


def ServicedBlocks(data_dir: str):
    """
    This function creates a csv file for each state that shows which blocks are serviced by which providers. Stores the
    provider_id, brand_name, and money received from the FCC for ACP for each provider.
    :param data_dir: The path to the data folder
    :return: None
    """

    isp_folder = data_dir + "ISP/"
    tech_dir = isp_folder + "Technology_Provider_Data/"

    # Final Folder where the files will be stored
    mid_folder = isp_folder + "Providers_by_State/"
    end_folder = mid_folder + "Serviced_Blocks/"

    # Create the folder if it doesn't exist
    if not os.path.exists(mid_folder):
        os.makedirs(mid_folder)

    # Create the folder if it doesn't exist
    if not os.path.exists(end_folder):
        os.makedirs(end_folder)

    # Spending file
    spending_file = isp_folder + "Final.csv"

    # Read the spending file
    spending_df = pd.read_csv(spending_file, dtype={"provider_id": str})

    # Unique provider id's
    provider_ids = spending_df["provider_id"].unique().tolist()

    # Create a dictionary to store the state abbreviations
    state_dict = {"01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE",
                  "11": "DC", "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA",
                  "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
                  "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM",
                  "36": "NY", "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
                  "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
                  "54": "WV", "55": "WI", "56": "WY", "72": "PR"}

    # Iterate through all the states
    for i in range(73):

        # Create the state number
        state_num = str(i).zfill(2)

        # Only continue if the state number is in the dictionary
        if state_num in state_dict:

            # Create the state abbreviation
            state_abbrev = state_dict[state_num]

            # Create the state file name
            final_file = end_folder + state_abbrev + "_Serviced_Blocks.csv"

            # Create a dictionary to store the block_geoid's
            block_dict = {}

            # Iterate through all the technologies
            for folder in os.listdir(tech_dir):

                # Open only folders
                if "." not in folder:

                    # Create the sub folder path
                    folder_path = tech_dir + folder + "/"

                    # Iterate through all the companies for the technology
                    for file in os.listdir(folder_path):

                        # Check if the file is a csv file
                        if file.endswith(".csv"):

                            # Create the file path for the company
                            file_path = folder_path + file

                            # Read the csv file
                            df = pd.read_csv(file_path)

                            # Get the company name
                            company = df.columns[0]

                            # Provider ID
                            provider_id = company[:]
                            provider_id = provider_id.split(";")[0]
                            provider_id = provider_id.strip()

                            # Re-read the csv file but with the blocks as strings
                            df = pd.read_csv(file_path, dtype={company: str})

                            # Blocks are 15 characters long
                            df[company] = df[company].str.zfill(15)

                            # Only keep the rows where the observation starts with the current state number
                            df = df[df[company].str.startswith(state_num)]

                            # Check if the provider id is in the list of provider ids
                            if provider_id in provider_ids:

                                # Get the ACP 2022 column
                                acp_2022 = spending_df[spending_df["provider_id"] == provider_id]["ACP2022"].values[0]

                                # Get the ACP 2023 column
                                acp_2023 = spending_df[spending_df["provider_id"] == provider_id]["ACP2023"].values[0]

                                # Add up the ACP 2022 and ACP 2023
                                acp_total = acp_2022 + acp_2023

                                # Add the ACP total to the company name
                                new_company = company + f"; ${acp_total}"

                            else:

                                # Add a 0 to the company name
                                new_company = company + "; $0"

                            # Put the block number into the dictionary
                            for block in df[company]:

                                # Check if the block is in the dictionary
                                if block in block_dict:

                                    # Check if the technology is in the dictionary
                                    if folder in block_dict[block]:

                                        # Add the company to the tech list
                                        block_dict[block][folder].append(new_company)

                                    # Initialize the list for the technology
                                    else:
                                        block_dict[block][folder] = [new_company]

                                else:
                                    # Initialize the dictionary for the block
                                    block_dict[block] = {folder: [new_company]}

            # Create a list to store the rows
            rows = []
            cable_data = []
            copper_data = []
            fiber_data = []
            lbr_data = []
            lfw_data = []
            ufw_data = []

            # Loop through the keys and values in the dictionary
            for key, value in block_dict.items():
                # Get the values for each technology
                cable = value.get("Cable", [])
                copper = value.get("Copper", [])
                fiber = value.get("Fiber", [])
                lbr = value.get("LBR", [])
                lfw = value.get("Licensed-Fixed-Wireless", [])
                ufw = value.get("Unlicensed-Fixed-Wireless", [])

                # Convert the lists to strings, separated by " -- "
                cable_data.append(' -- '.join(cable))
                copper_data.append(' -- '.join(copper))
                fiber_data.append(' -- '.join(fiber))
                lbr_data.append(' -- '.join(lbr))
                lfw_data.append(' -- '.join(lfw))
                ufw_data.append(' -- '.join(ufw))

                # Add the block_geoid to the list
                rows.append(key)

            # Create a dataframe from the lists
            df = pd.DataFrame({
                "Block": rows,
                "Cable": cable_data,
                "Copper": copper_data,
                "Fiber": fiber_data,
                "LBR": lbr_data,
                "LFW": lfw_data,
                "UFW": ufw_data
            })

            # Set the index to the Block column
            df.set_index("Block", inplace=True)

            # Save the dataframe to a csv file
            df.to_csv(final_file)


def providersByBlock(data_dir: str):
    """
    This function creates a csv file for each state that shows which blocks are serviced by which providers. Stores the
    population for each block, which is used to determine if an ISP services a block group or tract.
    :param data_dir: The path to the data folder
    :return: None
    """

    # Set the path to the data folders
    isp_folder = data_dir + "ISP/"
    providers_folder = isp_folder + "Providers_by_State/"
    serviced_folder = providers_folder + "Serviced_Blocks/"
    end_folder = providers_folder + "Providers_by_Block/"

    # Create the folder if it doesn't exist
    if not os.path.exists(end_folder):
        os.makedirs(end_folder)

    # API key for census.gov
    census_key = "494a9ee04209e13f2786105dd68cd4b5ac37f49d"

    # Create a dictionary to store the state abbreviations
    state_dict = {"01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE",
                  "11": "DC", "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA",
                  "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
                  "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM",
                  "36": "NY", "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
                  "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
                  "54": "WV", "55": "WI", "56": "WY", "72": "PR"}

    # Iterate through all the states
    for i in range(73):
        # Create the state number
        state_num = str(i).zfill(2)

        # Only continue if the state number is in the dictionary
        if state_num in state_dict:
            # File name for the state with the serviced blocks
            serviced_file = serviced_folder + state_dict[state_num] + "_Serviced_Blocks.csv"

            # Create a dataframe from the csv file
            serviced_df = pd.read_csv(serviced_file, dtype=str, header=0)

            # Create a list of the columns
            cols = ["Cable", "Copper", "Fiber", "LBR", "LFW", "UFW"]

            # Loop through the rows
            for index, row in serviced_df.iterrows():
                # Create a list to store the unique providers
                unique_providers = []

                # Loop through the columns
                for col in cols:
                    # Check if the value is not nan
                    if str(row[col]) != "nan":
                        # Add the providers to the list
                        unique_providers += str(row[col]).split(" -- ")

                # Get the unique providers
                unique_providers = set(unique_providers)

                # Turn the set into a list
                unique_providers = list(unique_providers)

                # Create a list to store the providers that receive ACP
                acp_providers = []

                # Loop through the unique providers
                for provider in unique_providers:
                    # Get the amount of ACP
                    provider_acp = str(provider.split("$")[1])

                    # Check if the provider receives ACP
                    if provider_acp != "0":
                        # Add the provider to the list
                        acp_providers.append(provider)
                # Add the columns to the dataframe
                serviced_df.loc[index, "ISPs"] = " -- ".join(unique_providers)
                serviced_df.loc[index, "ISPs Count"] = len(unique_providers)
                serviced_df.loc[index, "ISPs ACP Count"] = len(acp_providers)
            if state_num != "72":
                serviced_df = serviced_df[["Block", "ISPs", "ISPs Count", "ISPs ACP Count"]]
            else:
                serviced_df = pd.DataFrame()

            # Fill the nan values with 0
            serviced_df.fillna(0, inplace=True)

            # Read the serviced file
            url = f"https://api.census.gov/data/2020/dec/dhc?get=P1_001N&for=block:*&in=state:{state_num}&in=county" \
                  f":*&in=tract:*&key={census_key}"

            # Get the response
            response = requests.get(url)

            # Get the json data
            data = response.json()

            # Create a dataframe from the json data
            df = pd.DataFrame(data[1:], columns=data[0], dtype=str)

            # Rename the columns
            df.rename(columns={"P1_001N": "Population", "state": "State", "county": "County", "tract": "Tract",
                               "block": "Block"}, inplace=True)

            # Add leading zeros to the state, county, tract, and block columns
            df["State"] = df["State"].str.zfill(2)
            df["County"] = df["County"].str.zfill(3)
            df["Tract"] = df["Tract"].str.zfill(6)
            df["Block"] = df["Block"].str.zfill(4)

            # Combine the state, county, tract, and block columns
            df["Block"] = df["State"] + df["County"] + df["Tract"] + df["Block"]

            # Drop the state, county, and tract columns
            df.drop(columns=["State", "County", "Tract"], inplace=True)

            # Rearrange the columns
            df = df[["Block", "Population"]]

            # Merge the dataframes
            if state_num != "72":
                main_df = pd.concat([df.set_index("Block"), serviced_df.set_index("Block")], axis=1, join="outer"). \
                    reset_index()

                # Fill the nan values with 0
                main_df.fillna(0, inplace=True)

                # Save the dataframe to a csv file
                main_df.to_csv(end_folder + state_dict[state_num] + "_Providers_by_Block.csv", index=False)

            else:
                df.to_csv(end_folder + state_dict[state_num] + "_Providers_by_Block.csv", index=False)


def providersByBlockGroup(data_dir: str):
    """
    This function creates a csv file for each state that shows which block groups are serviced by which providers. This
    is done using a 50% threshold for the population of the block group.
    :param data_dir: The path to the data folder
    :return: None
    """

    # Path to the data folders
    isp_folder = data_dir + "ISP/"
    prov_by_state_folder = isp_folder + "Providers_by_State/"
    prov_by_block_folder = prov_by_state_folder + "Providers_by_Block/"
    prov_by_block_group_folder = prov_by_state_folder + "Providers_by_Block_Group/"

    # Set the threshold for the percentage of the population that must be covered
    threshold = 0.5

    # Create the folder if it doesn't exist
    if not os.path.exists(prov_by_block_group_folder):
        os.mkdir(prov_by_block_group_folder)

    # Iterate through the files in the block folder
    for file in os.listdir(prov_by_block_folder):
        # Only continue if the file is a csv file
        if file.endswith(".csv") and not file.startswith("PR"):
            # Initialize the final dataframe
            final_df = pd.DataFrame(columns=["Block Group", "Population", "ISPs", "ISPs Count", "ISPs ACP Count"])

            # Get the file path
            file_path = prov_by_block_folder + file

            # Find the final file name
            final_file = file_path[:].replace("Block", "Block_Group")

            # Create a dataframe from the csv file
            df = pd.read_csv(file_path, dtype={"Block": str, "ISPs": str, "Population": int, "ISPs Count": int,
                                               "ISPs ACP Count": int}, header=0)

            # Create the block group column
            df["Block Group"] = df["Block"].str[:12]

            # List of unique block groups
            block_groups = df["Block Group"].unique().tolist()

            # Iterate through the block groups
            for block_group in block_groups:
                # Create a dataframe for the block group
                bg_df = df[df["Block Group"] == block_group]

                # Get the total population of the block group
                total_pop = bg_df["Population"].sum()

                # Get the providers in the block group
                providers = bg_df["ISPs"].unique().tolist()

                # Initialize the list of unique providers
                unique_providers = []

                # Iterate through the providers
                for provider in providers:
                    # Split the providers
                    split_providers = provider.split(" -- ")

                    if split_providers[0] != "0":
                        # Add the providers to the list
                        unique_providers += split_providers

                # Get the unique providers
                unique_providers = list(set(unique_providers))

                # Initialize the list of providers that serve the majority of the block group
                majority_providers = []

                # Only iterate if pop of a block group is greater than 0
                if total_pop > 0:
                    # Iterate through the unique providers
                    for provider in unique_providers:
                        # Population the provider serves
                        provider_pop = 0

                        # Iterate through the block group dataframe
                        for index, row in bg_df.iterrows():
                            # Get the providers in the row
                            isps = str(row["ISPs"]).split(" -- ")

                            # Check if the provider is in the row
                            if provider in isps:
                                # Add the population to the provider
                                provider_pop += row["Population"]

                        # Check if the provider serves the majority of the block group
                        if provider_pop / total_pop >= threshold:
                            # Add the provider to the list
                            majority_providers.append(provider)

                # Initialize the list of providers that receive ACP
                acp_providers = []

                # Iterate through the majority providers
                for provider in majority_providers:
                    # Find the acp amount
                    acp_amount = provider.split("$")[1]

                    # Check if the provider receives ACP
                    if acp_amount != "0":
                        # Add the provider to the list
                        acp_providers.append(provider)

                # Add the block group to the dataframe
                final_df = pd.concat([final_df, pd.DataFrame({"Block Group": [block_group], "Population": [total_pop],
                                                              "ISPs": [" -- ".join(majority_providers)],
                                                              "ISPs Count": [len(majority_providers)],
                                                              "ISPs ACP Count": [len(acp_providers)]})],
                                     ignore_index=True)

            # Iterate through the rows to create new columns for each provider
            for index, row in final_df.iterrows():
                temp_dict = {}
                isps = row["ISPs"].split(" -- ")

                for num, isp in enumerate(isps):
                    key_num = "ISP " + str(num + 1)
                    id_num = "ID " + str(num + 1)
                    if ";" in isp:
                        comp = isp.split("; ")[1]
                        provider_id = isp.split("; ")[0]
                    else:
                        comp = None
                        provider_id = None

                    if provider_id not in temp_dict.values():
                        temp_dict[key_num] = comp
                        temp_dict[id_num] = provider_id

                for key, value in temp_dict.items():
                    final_df.loc[index, key] = value

            final_df.drop(columns=["ISPs"], inplace=True)

            # Fill the nan values with 0
            final_df.fillna('0', inplace=True)

            # Save the dataframe to a csv file
            final_df.to_csv(final_file, index=False)

            # Save the dataframe to an excel file as well, making it easier for ArcGIS to read
            final_df.to_excel(final_file.replace(".csv", ".xlsx"), index=False)


def providersByTract(data_dir: str):
    """
        This function creates a csv file for each state that shows which block groups are serviced by which providers. This
        is done using a 50% threshold for the population of the block group.
        :param data_dir: The path to the data folder
        :return: None
        """

    # Path to the data folders
    isp_folder = data_dir + "ISP/"
    prov_by_state_folder = isp_folder + "Providers_by_State/"
    prov_by_block_folder = prov_by_state_folder + "Providers_by_Block/"
    prov_by_tract_folder = prov_by_state_folder + "Providers_by_Tract/"

    # Set the threshold for the percentage of the population that must be covered
    threshold = 0.5

    # Create the folder if it doesn't exist
    if not os.path.exists(prov_by_tract_folder):
        os.mkdir(prov_by_tract_folder)

    # Iterate through the files in the block folder
    for file in os.listdir(prov_by_block_folder):
        # Only continue if the file is a csv file
        if file.endswith(".csv") and not file.startswith("PR"):
            # Initialize the final dataframe
            final_df = pd.DataFrame(columns=["Tract", "Population", "ISPs", "ISPs Count", "ISPs ACP Count"])

            # Get the file path
            file_path = prov_by_block_folder + file

            # Find the final file name
            final_file = file_path[:].replace("Block", "Tract")

            # Create a dataframe from the csv file
            df = pd.read_csv(file_path, dtype={"Block": str, "ISPs": str, "Population": int, "ISPs Count": int,
                                               "ISPs ACP Count": int}, header=0)

            # Create the block group column
            df["Tract"] = df["Block"].str[:11]

            # List of unique block groups
            tracts = df["Tract"].unique().tolist()

            # Iterate through the block groups
            for tract in tracts:
                # Create a dataframe for the block group
                tract_df = df[df["Tract"] == tract]

                # Get the total population of the block group
                total_pop = tract_df["Population"].sum()

                # Get the providers in the block group
                providers = tract_df["ISPs"].unique().tolist()

                # Initialize the list of unique providers
                unique_providers = []

                # Iterate through the providers
                for provider in providers:
                    # Split the providers
                    split_providers = provider.split(" -- ")

                    if split_providers[0] != "0":
                        # Add the providers to the list
                        unique_providers += split_providers

                # Get the unique providers
                unique_providers = list(set(unique_providers))

                # Initialize the list of providers that serve the majority of the block group
                majority_providers = []

                # Only iterate if pop of a block group is greater than 0
                if total_pop > 0:
                    # Iterate through the unique providers
                    for provider in unique_providers:
                        # Population the provider serves
                        provider_pop = 0

                        # Iterate through the block group dataframe
                        for index, row in tract_df.iterrows():
                            # Get the providers in the row
                            isps = str(row["ISPs"]).split(" -- ")

                            # Check if the provider is in the row
                            if provider in isps:
                                # Add the population to the provider
                                provider_pop += row["Population"]

                        # Check if the provider serves the majority of the block group
                        if provider_pop / total_pop >= threshold:
                            # Add the provider to the list
                            majority_providers.append(provider)

                # Initialize the list of providers that receive ACP
                acp_providers = []

                # Iterate through the majority providers
                for provider in majority_providers:
                    # Find the acp amount
                    acp_amount = provider.split("$")[1]

                    # Check if the provider receives ACP
                    if acp_amount != "0":
                        # Add the provider to the list
                        acp_providers.append(provider)

                # Add the block group to the dataframe
                final_df = pd.concat([final_df, pd.DataFrame({"Tract": [tract], "Population": [total_pop],
                                                              "ISPs": [" -- ".join(majority_providers)],
                                                              "ISPs Count": [len(majority_providers)],
                                                              "ISPs ACP Count": [len(acp_providers)]})],
                                     ignore_index=True)

            # Iterate through the rows to create new columns for each provider
            for index, row in final_df.iterrows():
                temp_dict = {}
                isps = row["ISPs"].split(" -- ")

                for num, isp in enumerate(isps):
                    key_num = "ISP " + str(num + 1)
                    id_num = "ID " + str(num + 1)
                    if ";" in isp:
                        comp = isp.split("; ")[1]
                        provider_id = isp.split("; ")[0]
                    else:
                        comp = None
                        provider_id = None

                    if provider_id not in temp_dict.values():
                        temp_dict[key_num] = comp
                        temp_dict[id_num] = provider_id

                for key, value in temp_dict.items():
                    final_df.loc[index, key] = value

            final_df.drop(columns=["ISPs"], inplace=True)

            # Fill the nan values with 0
            final_df.fillna('0', inplace=True)

            # Save the dataframe to a csv file
            final_df.to_csv(final_file, index=False)

            # Save the dataframe to an excel file as well, making it easier for ArcGIS to read
            final_df.to_excel(final_file.replace(".csv", ".xlsx"), index=False)
