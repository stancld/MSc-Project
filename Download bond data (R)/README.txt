# The manual how to download corporate bond data for individul markets;
# Subsequently, these data are used for creating a bond dataset in STEP 4

## STEP 1 ##
- run 'Bond lookup.R' [search bonds associated with equities from Bloomberg]
- here, one must specify:
    1. company_path: Excel/CSV of companies (provided)
    2. output_path: Output file of this file containing 
                    
## STEP 2 ##
- run 'Extract bond names.py' [fix bond names to be ready for downloading the bond data]
- here, one must specify:
    1. data_path: Output_path from STEP 1
    2. output_path: Output file containing fixed corporate bond names used in STEP 3

## STEP 3 ##
- run 'Download bond data.R'
- here, one must specify:
    1. bond_path: Output_path from STEP 2
    2. bond_path: Output_path from STEP 1
    3. output_path: Output file of this program used for creating dataset in STEP 4

## STEP 4 ##
- run 'Create Bond dataset.py'
- here, one must specify:
    1. bond_path: Output_path from STEP 3
    2. output_path: Output file of this program, which can be ingested directly to PortfolioConstruction.py


