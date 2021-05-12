from pathlib import Path
import numpy as np
import pandas as pd
from src import utils

class genericDataSet:
    def  __init__(self, level = 'block'):

        #self.file_name= [] provide in subclasses
        self.tot_pop = [];   
        self.level = level
        self.LoadAndClean()

    def LoadAndClean(self):
        
        Data_path =  utils.DATA['master']  / self.file_name
        Data =  pd.read_csv(Data_path, dtype = {'GEOID':'object'},\
        index_col = 1)
        self.CleanData(Data) 


    def MungeData(self,tot_pop,level='block'):


        Data = self.data 
        Data = Data.multiply(tot_pop['tot_population'],axis= 'index')
     
        Data.index , tot_pop.index  = Data.index.str[1:utils.GEOID[level]], \
                                  tot_pop.index.str[1:utils.GEOID[level]]

        Data, tot_pop = Data.groupby(Data.index).sum(), \
                   tot_pop.groupby(tot_pop.index).sum()

        self.data = Data.divide(tot_pop['tot_population'],axis = 'index')
        self.tot_pop = tot_pop

    
    def CleanData(self):
        pass


    
class ACSData(genericDataSet):
    def __init__(self,level):
        self.file_name = 'ACS 5YR Block Group Data.csv'
        super().__init__(level)


    def CleanData(self,ACS):

        ## Cleans and munges ACS data 
        #  'ACS' - ACS variable from LoadACS
        #  'self.level' - geography level to munge the data to
        #            levels can be found in utils.GEOID
        #            #Note: this can function can only aggregate data    

        # Ensures GEOID variable is in the correct format and sets it as the dataframe index
        ACS['GEOID'] = ACS['GEOID'].str[2:]
        
        ACS.set_index(['GEOID'],inplace = True)

        # Removes extraneous features (i.e. non-numeric) in the dataframe
        if 'Unnamed: 0' in ACS.columns:
            ACS.drop('Unnamed: 0','columns',inplace= True)
        
        if 'NAME' in ACS.columns:
            ACS.drop('NAME','columns',inplace= True)
        
        if 'inc_pcincome' in ACS.columns:
            ACS.drop('inc_pcincome','columns',inplace= True)
        
        
        tot_pop = ACS[['tot_population']].groupby('GEOID').sum()
        # Drop all total count columns in ACS and keeps all percentage columns
        cols = ACS.columns.to_list()
        for col in cols:
            if  col.find('tot') != -1 : 
                ACS.drop(col,'columns', inplace = True)
        
        

        # Integer indexing for all rows, but gets rid of county_name, state_name, and in_poverty
        ACS = ACS.iloc[:,3:]
        
        # Remove missing values from dataframe
        ACS.replace([np.inf, -np.inf], np.nan,inplace = True)
        ACS.dropna(inplace = True)
        
        ## ACS Munging
        #education adjustment 
        ACS['educ_less_12th'] =  ACS.loc[:,'educ_nursery_4th':'educ_12th_no_diploma'].sum(axis =1 )
        ACS['educ_high_school'] =  ACS.loc[:,'educ_high_school_grad':'educ_some_col_no_grad'].sum(axis =1 )
        ACS.drop(ACS.loc[:, 'educ_nursery_4th':'educ_some_col_no_grad'], inplace = True, axis = 1)

        # house age adjustment 
        ACS['house_yr_pct_before_1960'] =ACS.loc[:,'house_yr_pct_1950_1959':'house_yr_pct_earlier_1939'].sum(axis =1 )
        ACS['house_yr_pct_after_2000'] = ACS.loc[:, 'house_yr_pct_2014_plus':'house_yr_pct_2000_2009'].sum(axis = 1 )
        ACS['house_yr_pct_1960_2000'] = ACS.loc[:, 'house_yr_pct_1990_1999':'house_yr_pct_1960_1969'].sum(axis = 1 )
        ACS.drop(ACS.loc[:, 'house_yr_pct_2014_plus':'house_yr_pct_earlier_1939'], inplace = True, axis = 1)
        
        # housing Price adjustment
        ACS['house_val_less_50K']=ACS.loc[:,'house_val_less_10K':'house_val_40K_50K'].sum(axis =1 )
        ACS['house_val_50_100K']=ACS.loc[:,'house_val_50K_60K':'house_val_90K_100K'].sum(axis =1 )
        ACS['house_val_100K_300K']=ACS.loc[:,'house_val_100K_125K':'house_val_250K_300K'].sum(axis =1 )
        ACS['house_val_300K_500K']=ACS.loc[:,'house_val_300K_400K':'house_val_400K_500K'].sum(axis =1 )
        ACS['house_val_more_500K'] = ACS.loc[:,'house_val_500K_750K':'house_val_more_2M'].sum(axis = 1)
        ACS.drop(ACS.loc[:, 'house_val_less_10K':'house_val_more_2M'], inplace = True, axis = 1)

        # package 
        self.data = ACS
        
        # munge to appropriate level 

        if  self.level =='block_group':
            #ACS data already at block_group level
            self.tot_pop = tot_pop
        else:
            self.MungeData(tot_pop,self.level)
    




