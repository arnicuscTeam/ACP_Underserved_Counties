# ACP Underserved Counties (Deliverable #2)

This repo contains the information and files to fact check and data check delierable #2 of the Measuring the Effectiveness of Digital Inclusion Approaches (MEDIA) project - phase 2
The report title is Evaluating the Impact of the Affordable Connectivity Program. The file is [here](/Deliverable#2.docx)

## Interactive Map Data

The data for the interactive map is composed of four different parts:

1. Categorizing Counties
2. County Filters
3. Race/Ethnicity
4. Connectivity

### Categorizing Counties
The three choices of the categorization are:

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

### County Filters
The county filters are the following:

1. Median Household Income
2. Percent Units Served by Broadband

For median household income, we used the 2022 ACS 5-year API to collect the median household income for each
county. The list of available APIs can be found under https://www.census.gov/data/developers/data-sets.html. The code
to collect the census data can be found under [get_census_data_county](Code/collect_census_data.py).

To collect the percent units served by broadband, we used the FCC's Broadband Deployment data, which can be found under
https://broadbandmap.fcc.gov/home. We downloaded the national data and filtered so that all wired and licensed fixed
wireless technologies were included, with a minimum advertised speed of 25/3Mbps, only for residential service. This data
is available at the county level.

### Race/Ethnicity
The totals for each race and ethnicity were collected from the 2022 ACS 5-year API. The list of available APIs can be
found under https://www.census.gov/data/developers/data-sets.html. The code to collect the census data can be found
under [get_census_data_county](Code/collect_census_data.py).

### Connectivity
The five rows of connectivity are the following:

1. Households
2. ACP Subscribed Households
3. Computer and Broadband Internet subscription
4. Computer and no Internet access
5. Computer with dial-up Internet subscription alone

To collect the ACP subscribed households, we used the ACP Enrollment and Claims Tracker webpage provided by USAC. The
data is published in 6-month periods by ZIP code and County. To find the data, we used the following link:
https://www.usac.org/about/affordable-connectivity-program/acp-enrollment-and-claims-tracker/. 

To collect the rest of the connectivity data, we used the 2022 ACS 5-year API. The list of available APIs can be found
under https://www.census.gov/data/developers/data-sets.html. The code to collect the census data can be found under
[get_census_data_county](Code/collect_census_data.py).


## Underserved Counties Scatterplot

The scatterplot is composed of the following:

1. Percent Units Served by Broadband
2. Median Household Income
3. Percent of County Households Subscribed to ACP
4. Total Households
5. Rural
6. Tribal
7. High Cost

To collect the percent units served by broadband, we used the FCC's Broadband Deployment data, which can be found under
https://broadbandmap.fcc.gov/home. We downloaded the national data and filtered so that all wired and licensed fixed
wireless technologies were included, with a minimum advertised speed of 25/3Mbps (residential only). This data
is available at the county level.

To collect the median household income, we used the 2022 ACS 5-year API. The list  of available APIs can be found under 
https://www.census.gov/data/developers/data-sets.html. The code to collect the census data can be found under 
[get_census_data_county](Code/collect_census_data.py).

To collect the percent of county households subscribed to ACP and total households, we used the ACP Enrollment and Claims
Tracker webpage provided by USAC. The data is published in 6-month periods by ZIP code and County. To find the data, we
used the following link: https://www.usac.org/about/affordable-connectivity-program/acp-enrollment-and-claims-tracker/.

To collect the rural counties, we downloaded the covered populations file from the Census, which can be found under
https://www.census.gov/programs-surveys/community-resilience-estimates/partnerships/ntia/digital-equity.html. Here,
the census determined if a county was considered rural.

To collect the tribal counties, we downloaded the shapefile of Tribal blocks provided by USAC, which can be downloaded
using https://www.usac.org/wp-content/uploads/lifeline/documents/tribal/shapefile-of-tribal-lands.zip. Since the blocks
are not identified in this file, we used ArcGIS and overlayed the tribal blocks with the tabulation blocks to determine
which blocks were tribal. From here, we aggregated the number of people that lived in these tribal blocks, and if the
majority of the population within that county was in a tribal block, then the county was categorized as tribal.

To collect the high-cost counties, we downloaded the high_cost areas file provided by the NTIA, which can be found under
https://www.internet4all.gov/program/broadband-equity-access-and-deployment-bead-program/bead-allocation-methodology.
From here, we aggregated the number of people that lived in these High-Cost block groups and if the majority of the
population within that county was in a high-cost block group, then the county was categorized as high-cost.


## Other Data in Report

The data referenced in the difference in differences sections of the report is panel data collected from the ACS 1-year estimates over a 
period of 6 years, from 2016 to 2022, excluding 2020 for which data is not available. The data was collected using the 1-year ACS API, which can be 
found under https://www.census.gov/data/developers/data-sets.html. The code to collect the census data can be found 
under [get_county_panel_internet_data](Code/collect_census_data.py).

To determine the income threshold (Appendix A), we collected PUMS 2022 data from the Census Bureau. In depth explanation
of this step can be found in the readme found in the following repository: 
https://github.com/arnicuscTeam/ACP-Eligibility. The section titled American Community Survey PUMS (ACS PUMS) explains
how the data was collected, cleaned, crosswalked, and used. The code used to collect, clean, and crosswalk the data can
be found in the [collect_pums_data.py](Code/collect_pums_data.py) file. The code used to download and clean the
crosswalk files can be found in the [geocorr.py](Code/geocorr.py) file.
Once all the PUMS data was crosswalked to the county level, we used the following function to determine the income
distribution at the county level for four different states: California, Texas, Ohio, and Alabama. The function can be
found in the [determine_income_threshold](Code/collect_census_data.py) file.
