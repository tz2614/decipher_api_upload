#!usr/bin/python3

import sys
import os
import subprocess
import datetime
import argparse
import pandas as pd
from pandas import Series, DataFrame
import csv
import pprint
from sqlalchemy import create_engine
from get_gender import connect_to_db, run_query_in_db, disconnect_to_db

pp = pprint.PrettyPrinter(indent=4)


"""
create a script that parse data from "MCGM_RD_individual_genes.csv" to create three separate csv files called
"bulk_cnv.csv"
"bulk_snv.csv"
"bulk_snv_hgvs.csv"
output variant info related to each gene
"""

# author: Tengyue Zheng
# date: 13/01/2020

filedate = str(datetime.date.today())
filedate = "".join(filedate.split("-"))
mcgm_csv = "/mnt/repository/Bioinformatics/tengyue_zheng_projects/Decipher_API_upload/MCGM_RD_individual_genes.csv"
bulk_cnv_template = "/mnt/repository/Bioinformatics/tengyue_zheng_projects/Decipher_API_upload/bulk_cnv_template.xlsx"
bulk_snv_hgvs_template = "/mnt/repository/Bioinformatics/tengyue_zheng_projects/Decipher_API_upload/bulk_snv_hgvs_template.xlsx"
bulk_snv_template = "/mnt/repository/Bioinformatics/tengyue_zheng_projects/Decipher_API_upload/bulk_snv_template.xlsx"
cnv_output_csv = "/mnt/repository/Bioinformatics/tengyue_zheng_projects/Decipher_API_upload/{0}_cnv_output.csv".format(filedate)
snv_hgvs_output_csv = "/mnt/repository/Bioinformatics/tengyue_zheng_projects/Decipher_API_upload/{0}_snv_hgvs_output.csv".format(filedate)
snv_output_csv = "/mnt/repository/Bioinformatics/tengyue_zheng_projects/Decipher_API_upload/{0}_snv_output.csv".format(filedate)
sample_db = "/users/tz1/git/decipher_api_upload/samples_be.db"

def parse_mcgm_var_to_df(mcgm_csv):

    mcgm_csv = os.path.abspath(mcgm_csv)
    #print (mcgm_csv)
    
    # import data from MCGM_RD_individual_genes.csv

    csv_df = pd.read_csv(mcgm_csv, na_values=[" "], encoding='UTF-8')

    print ("Data Frame for {0} generated".format(mcgm_csv))

    return csv_df

def convert_template_xls_to_df(template_xls):
    
    # get a list of sheet names from template xlsx
    
    template_xls = os.path.abspath(template_xls)
    print ("Convert {0} to Data Frame".format(template_xls))
    
    xls_obj = pd.ExcelFile(template_xls)
    sheet_names = xls_obj.sheet_names
    
    return sheet_names, xls_obj

def parse_ref_from_sheet_to_dict(sheet_names, xls_obj):
    
    # parse info from template excel sheets as lists 
    
    template_refs = {}
    
    #print (sheet_names)
    
    for name in sheet_names:
        df = xls_obj.parse(name, header=None)
        
        if "Data" in name:            
            template_refs["headers"] = df.iloc[0, :].tolist()
            #print (template_refs["headers"] )
        
        elif "Inheritance" in name:            
            template_refs["Inheritance"] = df.iloc[:, 0].tolist()
            #print (template_refs["Inheritance"])
            
        elif "Pathogenicity" in name:
            template_refs["Pathogenicity"] = df.iloc[:, 0].tolist()
            #print (template_refs["Pathogenicity"])
            
        elif "Genotype" in name:
            template_refs["Genotype"] = df.iloc[:, 0].tolist()
            #print (template_refs["Genotype"])

        elif "Phenotypes" in name:
            phenotype_ids = df.iloc[:, 0].tolist()
            hpo_terms = df.iloc[:, 2].tolist()
            phenotype_dict = dict(zip(phenotype_ids, hpo_terms))
            template_refs["Phenotypes"] = phenotype_dict
            #print (template_refs["Phenotypes"])
        
        elif "Class" in name:
            CNV_class = df.iloc[:, 0].tolist()
            #print (CNV_class)
            template_refs["CNV_class"] = CNV_class
    
    #print (template_refs)
    return template_refs

def intergenic_determination(csv_df):
        
    # check if variant is intergenic using vep_consequence column
    print ("Check if variant is intergenic using vep_consequences and populate Intergenic column")
    vep_consequences = Series.tolist(csv_df.loc[:,"vep_consequence"])
    vep_consequences = ["Yes" if "intergenic" in x or "intragenic" in x else "No" for x in vep_consequences]
    
    return vep_consequences

def extracting_data_from_csv(csv_df):
    
    # get data required from mcgm for the template
    
    ids = Series.tolist(csv_df.loc[:,"patient_id"])
    genes = Series.tolist(csv_df.loc[:,"gene_name"])
    genotype = Series.tolist(csv_df.loc[:,"genotype"])
    start = Series.tolist(csv_df.loc[:,"start"])
    chroms = Series.tolist(csv_df.loc[:,"chr"])
    refseq_tx = [x.split(":")[0] for x in Series.tolist(csv_df.loc[:,"hgvs_c"])]
    hgvs_code = Series.tolist(csv_df.loc[:,"hgvs_c"])
    intergenic = intergenic_determination(csv_df)
    ensembl_gene_id = Series.tolist(csv_df.loc[:,"ensembl_id"])
    lab_ids = Series.tolist(csv_df.loc[:,"reference"])
    
    # column we can extract data from but not required
    #note = Series.tolist(csv_df.loc[:,"sanitised_comment"])
    pathogenicity = [x.split(":")[1].split(",")[0].strip() for x in Series.tolist(csv_df.loc[:,"decision"])]
    #print (pathogenicity)
    # optional columns
    missing = ["" for x in range(len(ids))]
    
    aneuploidy = missing
    consent = missing
    age = missing
    prenatal_age = missing
    inheritance = missing
    phenotypes = missing
    data_owner = missing
    mean_ratio = missing
    note = missing
    
    # extract gender of patient from sample_be.db

    print ("Extracting gender from samples_be.db")
    sex = []
    conn = connect_to_db(sample_db)
    for identifier in lab_ids:
    	identifier = int(identifier.split("_")[-1])
    	gender = str(run_query_in_db(identifier, conn))
    	if gender == "1":
    		sex.append("46XY")
    	elif gender == "2":
    		sex.append("46XX")
    	else:
    		print ("issue with querying Samples_be.db database, check {0} in /users/tz1/git/decipher_api_upload/samples_be_sqlite_db.log".format(identifier))
    		sex.append("SEX UNKNOWN")
    disconnect_to_db(conn)
    print ("Extraction COMPLETE")

    # Generate a list of genome builds
    build = ["GRCh37" for x in range(len(ids))]

    # handling missing columns of data that maybe required
    try:
        ref = Series.tolist(csv_df.loc[:,"ref_allele"])
    except Exception as e:
        print ("ref_allele: {}".format(e))
        ref = missing
    
    try:
        alt = Series.tolist(csv_df.loc[:,"alt_allele"])
    except Exception as e:
        print ("alt_allele: {}".format(e))
        alt = missing
        
    try:
        end = Series.tolist(csv_df.loc[:,"end"])
    except Exception as e:
        print ("end position (cnv_only): {}".format(e))       
        end = missing  
    
    try:
        cnv_type = Series.tolist(csv_df.loc[:,"cnv_type"])
    except Exception as e:
        print ("cnv_type (cnv_only): {}".format(e))       
        cnv_type = missing  
    
    try:
        cnv_type = Series.tolist(csv_df.loc[:,"chromosomal sex"])
    except Exception as e:
        print ("sex: {}".format(e))       
        sex = missing  
        
   # output data as nested lists

    print ("Inputting data into df_dict")
    df_dict = {}
    df_dict["Internal reference number or ID"] = lab_ids
    df_dict["Chromosome"] = chroms
    df_dict["Start"] = start
    df_dict["End"] = end
    df_dict["Genome assembly"] = build
    df_dict["Reference allele"] = ref
    df_dict["Alternate allele"] = alt
    df_dict["Transcript"] = refseq_tx
    df_dict["Gene name"] = genes
    df_dict["Intergenic"] = intergenic
    df_dict["Chromosomal sex"] = sex
    df_dict["Other rearrangements/aneuploidy"] = aneuploidy
    df_dict["Open-access consent"] = consent
    df_dict["Age at last clinical assessment"] = age
    df_dict["Prenatal age in weeks"] = prenatal_age
    df_dict["Note"] = note
    df_dict["Inheritance"] = inheritance
    df_dict["Pathogenicity"] = pathogenicity
    df_dict["Phenotypes"] = phenotypes
    df_dict["Genotype"] = genotype
    df_dict["Responsible contact"] = data_owner
    df_dict["HGVS code"] = hgvs_code
    df_dict["Class"] = cnv_type
    df_dict["Mean ratio"] = mean_ratio
    df_dict["ensembl_gene_id"] = ensembl_gene_id
    df_dict["patient id"] = ids
   
    #generic_df_list = [ids, chroms, start, end, build, ref, alt, refseq_tx, genes, intergenic, sex, aneuploidy, consent, age, prenatal_age, note, inheritance, pathogenicity, phenotypes, genotype, data_owner, hgvs_code, cnv_type, mean_ratio, ensembl_gene_id]
    #print ("no cnv/snv/snv_hgvs data available, generic data exported")    
    #print (df_dict.keys())
    return df_dict
   
def import_data_to_new_df(csv_dict, headers):
    
    # create new df from "Data" tab of each template
    
    print ("Inputting data from csv_dict into Data Frame")
    new_df = pd.DataFrame(csv_dict, columns=headers)
            
    #print (new_df)
    return new_df

def check_required_fields_in_df(csv_dict, headers, refs):
 
    # mandatory fields
    cnv_list = ["Internal reference number or ID", "Chromosome", "Start", "End", "Class", "Chromosomal sex"]
    snv_hgvs_list = ["Internal reference number or ID", "HGVS code", "Genome assembly", "Transcript", "Gene name", "Intergenic", "Chromosomal sex", "Genotype"]
    snv_list = ["Internal reference number or ID", "Chromosome", "Start", "Genome assembly", "Transcript", "Reference allele", "Alternate allele",  "Gene name", "Intergenic", "Chromosomal sex", "Genotype"]
    
    print ("Check and populate Pathogenicity and Genotype in csv_dict of each variant against upload template terms")
    # check variant classification from mcgm csv compliant with Decipher API upload template requirements
    csv_dict["Pathogenicity"] = ["Uncertain" if x=="Uncertain significance" else x for x in csv_dict["Pathogenicity"]]
    csv_dict["Pathogenicity"] = ["" if x not in refs["Pathogenicity"] else x for x in csv_dict["Pathogenicity"]]
    #print (csv_dict["Pathogenicity"])
    # check variant genotype from mcgm csv compliant with Decipher API upload template requirements
    csv_dict["Genotype"] = ["" if x not in refs["Genotype"] else x for x in csv_dict["Genotype"]]

    if all(x in csv_dict.keys() for x in cnv_list):
        new_csv_dict = {}
        for h in headers:
            new_csv_dict[h] = csv_dict[h]
        #print (new_csv_dict)
        return new_csv_dict
    
    elif all(x in csv_dict.keys() for x in snv_hgvs_list):
        new_csv_dict = {}
        for h in headers:
            new_csv_dict[h] = csv_dict[h]
        #print (new_csv_dict)
        return new_csv_dict
    
    elif all(x in csv_dict.keys() for x in snv_list):
        new_csv_dict = {}
        for h in headers:
            new_csv_dict[h] = csv_dict[h]
        #print (new_csv_dict)
        return new_csv_dict
    
    else:
        print ("Data do not conform to CNV, SNV or SNV_HGVS template for Decipher Upload")
        print ("Check: {}".format(mcgm_csv))

def output_csv(new_df, new_output_csv):
    
    new_df.to_csv(new_output_csv, sep=",", encoding='utf-8', index=False)
    
    return new_output_csv
        
def main():

    csv_df = parse_mcgm_var_to_df(mcgm_csv)
    csv_dict = extracting_data_from_csv(csv_df)
    # print (csv_dict)
    
    # create CNV Decipher upload csv

    # parse template info into cnv_refs
    cnv_sn, cnv_obj = convert_template_xls_to_df(bulk_cnv_template)
    cnv_refs = parse_ref_from_sheet_to_dict(cnv_sn, cnv_obj)
    cnv_headers = cnv_refs["headers"]
    

    # parse info from mgcm_csv into cnv_df, then converting to csv
    new_csv_dict = check_required_fields_in_df(csv_dict, cnv_headers, cnv_refs)
    cnv_df = import_data_to_new_df(new_csv_dict, cnv_headers)
    print (cnv_df.head())
    cnv_csv = output_csv(cnv_df, cnv_output_csv)
    
    # create SNV HGVS Decipher upload csv

    # parse template info into snv_hgvs_refs
    snv_hgvs_sn, snv_hgvs_obj = convert_template_xls_to_df(bulk_snv_hgvs_template)
    snv_hgvs_refs = parse_ref_from_sheet_to_dict(snv_hgvs_sn, snv_hgvs_obj)
    snv_hgvs_headers = snv_hgvs_refs["headers"]

    #parse info from mgcm_csv into snv_hgvs_df, then converting to csv
    new_csv_dict = check_required_fields_in_df(csv_dict, snv_hgvs_headers, snv_hgvs_refs)
    snv_hgvs_df = import_data_to_new_df(new_csv_dict, snv_hgvs_headers)
    print (snv_hgvs_df.head())
    snv_hgvs_csv = output_csv(snv_hgvs_df, snv_hgvs_output_csv)
    
    # create SNV Decipher upload csv

     # parse template info into snv_refs
    snv_sn, snv_obj = convert_template_xls_to_df(bulk_snv_template)
    snv_refs = parse_ref_from_sheet_to_dict(snv_sn, snv_obj)
    snv_headers = snv_refs["headers"]

    #parse info from mgcm_csv into snv_df, then converting to csv
    new_csv_dict = check_required_fields_in_df(csv_dict, snv_headers, snv_refs)
    snv_df = import_data_to_new_df(new_csv_dict, snv_headers)        
    print (snv_df.head())    
    snv_csv = output_csv(snv_df, snv_output_csv)
    
if __name__ == "__main__":
    main()

