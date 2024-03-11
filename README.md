# ACP Underserved Counties (Deliverable #2)

This repo contains the information and files to fact check and data check delierable #2 of the Measuring the Effectiveness of Digital Inclusion Approaches (MEDIA) project - phase 2
The report title is Evaluating the Impact of the Affordable Connectivity Program. The Word file is [here](/Deliverable2.docx) See the comments in the Word file that refer each section to different datasets and code.
The final files are in Stata format, and can be found [here](Data/Stata_final_files)

# 1. DATA CHECK

## How the datasets were created

### a. Categorizing Counties
The three key dimensions of the county categorization are:

1. Rural
2. Tribal
3. High Cost

To identify rural counties, we downloaded the covered populations file from the Census Bureau, which can be found under 
https://www.census.gov/programs-surveys/community-resilience-estimates/partnerships/ntia/digital-equity.html. Here, 
the Census Bureau determined if a county is considered rural.

To identify tribal counties, we downloaded the shapefile of Tribal blocks provided by USAC, which can be downloaded
using https://www.usac.org/wp-content/uploads/lifeline/documents/tribal/shapefile-of-tribal-lands.zip. Since the blocks
are not identified in this file, we used ArcGIS and overlayed the tribal blocks with the tabulation blocks to determine
which blocks were tribal. From here, we aggregated the number of people that lived in these tribal blocks, and if the
majority of the population within that county was in a tribal block, then the county was categorized as tribal.

To identify high-cost counties, we downloaded the high_cost areas file provided by the NTIA, which can be found under 
https://www.internet4all.gov/program/broadband-equity-access-and-deployment-bead-program/bead-allocation-methodology.
From here, we aggregated the number of people that lived in these High-Cost block groups and if the majority of the 
population within that county was in a high-cost block group, then the county was categorized as high-cost.

### b. County income and broadband service

For median household income, we used the 2022 ACS 5-year API to collect the median household income for each
county. The list of available APIs can be found under https://www.census.gov/data/developers/data-sets.html. The code
to collect the census data can be found under [get_census_data_county](Code/collect_census_data.py).

To collect the percent units served by broadband, we used the FCC's Broadband Deployment data, which can be found under
https://broadbandmap.fcc.gov/home. We downloaded the national data and filtered so that all wired and licensed fixed
wireless technologies were included, with a minimum advertised speed of 25/3Mbps, only for residential service. This data
is available at the county level.

### c. ACS data
To collect demographic characteristics, indluing broadband adoption, we used both ACS 5-year data and ACS 1-year data.
The list of available APIs can be found under https://www.census.gov/data/developers/data-sets.html. The code to collect 5-year ACS census data can be found
under [get_census_data_county](Code/collect_census_data.py).

The data referenced in the difference in differences sections of the report is panel data collected from the ACS 1-year estimates over a 
period of 6 years, from 2016 to 2022, excluding 2020 for which data is not available. The data was collected using the 1-year ACS API, which can be 
found under https://www.census.gov/data/developers/data-sets.html. The code to collect the census data can be found 
under [get_county_panel_internet_data](Code/collect_census_data.py).

### d. USAC data
To collect the ACP subscribed households, we used the ACP Enrollment and Claims Tracker webpage provided by USAC. The
data is published in 6-month periods by ZIP code and County. To find the data, we used the following link:
https://www.usac.org/about/affordable-connectivity-program/acp-enrollment-and-claims-tracker/. 

### APPENDIX A

To determine the income threshold (Appendix A), we collected PUMS 2022 data from the Census Bureau. In depth explanation
of this step can be found in the readme found in the following repository: 
https://github.com/arnicuscTeam/ACP-Eligibility. The section titled American Community Survey PUMS (ACS PUMS) explains
how the data was collected, cleaned, crosswalked, and used. The code used to collect, clean, and crosswalk the data can
be found in the [collect_pums_data.py](Code/collect_pums_data.py) file. The code used to download and clean the
crosswalk files can be found in the [geocorr.py](Code/geocorr.py) file.
Once all the PUMS data was crosswalked to the county level, we used the following function to determine the income
distribution at the county level for four different states: California, Texas, Ohio, and Alabama. The function can be
found in the [determine_income_threshold](Code/collect_census_data.py) file.

# 2. FACT CHECK

All files referenced in the report are included in pdf format [here](Data/fact_check_docs.zip)
