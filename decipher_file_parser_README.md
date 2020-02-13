## How to parse data from MCGM_RD_individual_genes.csv for Decipher Bulk Upload
  - By Tengyue Zheng
  - 13/02/2020
  email: tengyue.zheng@mft.nhs.uk

## Description
  
  Create a python script that parses data from MCGM_RD_individual_genes.csv file that conforms to Decipher csv template for bulk upload.

## Getting Started

  1. Format of Decipher CSV files:
    
    - URL: https://decipher.sanger.ac.uk/about#downloads/documents
    - bulk_cnv.csv
    - bulk_snv.csv
    - bulk_snv_hgvs.csv

## Prerequisites

  1. Make sure you have all the dependencies for your program installed and loaded before you run the script

  2. Perform a thorough code review for the script before executing the script

  3. for instructions on how to set up an API to deposit variants in the future
  - URL: https://decipher.sanger.ac.uk/api-docs

## Main scripts:
  - /users/tz1/git/production_v2/python/decipher_csv_parser.py

## Unit testing scripts:
  
## Reference files:
  - /users/tz1/git/production_v2/python/bulk_cnv.csv
  - /users/tz1/git/production_v2/python/bulk_snv.csv
  - /users/tz1/git/production_v2/python/bulk_snv_hgvs.csv

## User Requirements:

  * Delete all '.bam' and 'bam.bai' in specified directory

## Instructions:

  Put requirements under the "User Requirements:" (see above)
  
  1. Load dependencies

    ```Bash
    $ module add libs/pandas/0.24.2/gcc-4.8.5+python-2.7.8+numpy-1.16.2
    ``` 
    - if the python package sqlalchemy has not been installed ojn the system, create a virtualenv and install sqlalchemy within the python environment. do the following in your working dir.

    ```Bash
    $ module add apps/virtualenv/16.0.0/python-2.7.8
    $ cd <working dir>
    $ virtualenv venv
    $ source /users/tz1/git/crontab_jobs/venv/bin/activate

  2. Run your script

    ```Bash
    $ python production_v2/python/decipher_csv_parser.py | tee decipher_YYYYMMDD.log
    ```
  
  3. Check the output of job

    It should display the information on terminal:

    ```Bash
    $ Data Frame for /mnt/repository/Bioinformatics/tengyue_zheng_projects/Decipher_API_upload/MCGM_RD_individual_genes.csv generated
    $ Check if variant is intergenic using vep_consequences
    $ SELECT Gender from Samples where labno = 17027602
    $ 1
    $ SELECT Gender from Samples where labno = 17027602
    $ 1
    $ SELECT Gender from Samples where labno = 17027294
    $ 1
    $ SELECT Gender from Samples where labno = 17027294
    $ 1
    $ SELECT Gender from Samples where labno = 17027294
    $ 1
    $ SELECT Gender from Samples where labno = 17027783
    $ 1
    $ SELECT Gender from Samples where labno = 17027081
    $ 2
    $ SELECT Gender from Samples where labno = 17027081
    $ ...
    $ Extraction COMPLETE
    $ end position (cnv_only): 'end'
    $ cnv_type (cnv_only): 'cnv_type'
    $ Inputting data into df_dict
    $ Convert /mnt/repository/Bioinformatics/tengyue_zheng_projects/Decipher_API_upload/bulk_cnv_template.xlsx to Data Frame
    $ Check and populate Pathogenicity and Genotype in csv_dict of each variant against upload template terms
    $ Inputting data from csv_dict into Data Frame
    $   Internal reference number or ID Chromosome     Start  ...      Pathogenicity Phenotypes Responsible contact
    $ 0                WS89611_17027602         11  61719352  ...  Likely pathogenic                               
    $ 1                WS89611_17027602         11  61719352  ...  Likely pathogenic                               
    $ 2                WS89611_17027294         11  61719322  ...  Likely pathogenic                               
    $ 3                WS89611_17027294         11  61719322  ...  Likely pathogenic                               
    $ 4                WS89611_17027294         11  61719322  ...  Likely pathogenic
    $ [5 rows x 18 columns]
    $ ...
    $ check COMPLETE
    $ LOG for modified dates and file paths created: <root/path>/crontab_jobs/YYYY-MM-DD.bam.bai.deletion.log```
    ```

  5. When the job is completed, check that log files have been generated. If in doubt consult Tengyue Zheng or senior member of the bioinformatics team.

    ```Bash
    $ less <path/to/dir>/decipher_YYYYMMDD.log
    ```

    You should see the outputs as above
