# DAPCOR -- Digital Assistant for Plant Control_Room
**A virtual assistant that reduces the barrier to information access for plant personnel by accepting voice-based queries in natural language to analyze process data.**

![DAPCOR in Plant Control Room Illustration](/img/DAPCOR_usageIllustration.jpg)

DAPCOR - created for plant managers and plant operators - reduces the barrier to access of information and advanced data analysis. Users can ask their queries in their natural language, and DAPCOR will fetch and process relevant data as needed and provide appropriate answer. The idea is that if you are in a plant control room and you want to know something, you should not have to go to your computer and open dashboards or trending tools just to get some quick information - DAPCOR should be able to do that for you. (DAPCOR is not meant to replace the dashboards and trending tools, but make their results more accessible to control room personnel.)

Sample questions that DAPCOR is being designed to answer: 

- Are all my sensors healthy?
- What's the forecast for the site power consumption for the week?
- Are there any active or pending alerts in any of my plant dashboards?
- Anything unusual going on in my plant?
- Is my plant operating efficiently?

## Tool Demo: 

[See on YouTube](https://youtu.be/sxgx0wNplPs)

## Current Features: 

- listens to voice commands; 'wakes up' upon hearing 'OK Digital Assistant'
- fetches data from SQL query and verbally answers the user
- plots appropriate graphs based on the query

## Features Coming Soon: 

The following features will soon be added to DAPCOR in upcoming releases:

- ability to perform automated advanced data analysis using Python to adequately respond to user queries
- ability to accept follow-up queries
- RAG abilities to utilize enterprise documents while framing response
- more robustness (to different 'error' scenarios)
- centralized deployment (instead of on-site deploymnet)

## Repository content: 

- tutorial notebooks: Jupyter notebooks that showcase how to use the individual agents of DAPCOR 
- DAPCOR: the source code
- DAPCOR_interface.py: the main script that is run to start DAPCOR's interface

## How to run DAPCOR: 

- Prerequisites: Python, OpenAI API key 
- Clone the repository OR download repository as ZIP and unzip the files
- Install the packages mentioned in the requirements.txt file (**pip install -r requirements.txt**), preferrably in a new virtual environment
- With DAPCOR--DIGITAL_ASSISTANT_FOR_PLANT_CONTROL_ROOM as the working directory, execute the following command in the terminal

    *streamlit run ./DAPCOR_interface.py*

## How to customize DAPCOR for your specific Database: 

- Put your Sqlite database in the 'data' folder and update the 'DB_OPTIONS' dictionary in 'DAPCOR_interface.py' script
- OR, update the codebase to use MSSQL, MSSQL Server, etc. 

## License

See LICENSE file for details. 
This project is adapted from the ['ai-data-science-team' project](https://github.com/business-science/ai-data-science-team) which is shared under MIT license.
