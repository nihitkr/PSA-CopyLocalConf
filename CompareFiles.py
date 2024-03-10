pip install pandas
pip install numpy
import os
import datetime
import shutil
import pandas as pd
import numpy as np

##Enter Server Details
model_server = "files\modelServer\etc\\"
new_server = "files\\newServer\etc\\"

'''
filex = File name with Extension
fname = File name without Extension
fext = File extension
path = Complete File path
d_entries = (List) Entries from file in New Server
s_entries = (List) Entries from file in Model Server
'''

##Taking backup of original File Model Server
def take_file_backup(filex):
    path = new_server + filex
    fname, fext = os.path.splitext(path)
    new_filex = fname + '_NEW_' + datetime.datetime.now().strftime("%Y-%m-%d") + fext  #passwd_NEW_2024-12-31.txt
    backup = fname + '_BKP_' + datetime.datetime.now().strftime("%Y-%m-%d") + fext  #passwd_BKP_2024-12-31.txt
    shutil.copy(path, backup)
    print("Backup created:", backup)
    return new_filex
    
##Reading entries from file
def read_entries(file_name):
    file = open(file_name, 'r')
    entries = file.readlines()
    file.close()
    return entries

##Comparing and adding missing entries in passwd,shadow, users.ignore
def compare_and_add_entries1(s_entries, d_entries):
    for line in s_entries[s_entries.index('unixsa\n'):]: #Checking for entries after unixsa
        if (line[0]=='#'):
            print ("Not copied (Commented):", line)
            continue
        try:
            d_entries.index(line)
        except:
            d_entries.append(line)
            print('Added:',line)
        else:
            print ('Already present:',line)
    return d_entries

##Update missing entries in file
def update_entries_in_file(d_entries, new_filex):
    file = open(new_filex,"w")
    file.writelines(d_entries)
    file.close()

filex = input("Enter file to copy (without extention): ") + '.txt'
new_filex = take_file_backup(filex)

s_entries = read_entries(model_server + filex) ##Read entries from Model server
d_entries = read_entries(new_server + filex)  ##Read entries from New Server
print("Comparing entries from model server....")

compare_and_add_entries1(s_entries, d_entries)

update_entries_in_file (d_entries, new_filex)

###########################################################################
####COMPARISION IN GROUP FILE:


##Importing data from group files of both source and destination server
sdf = pd.read_csv('files\\test\modelGroup.txt', sep=':', names=["gname", "source_uid", "source_gid", "source_mem"])
ddf = pd.read_csv("files\\test\\newGroup.txt", sep=':', names=["gname", "dest_uid", "dest_gid", "dest_mem"])


##DO NOT UNCOMMENT THESE, For Testing and Data Anlysis
#common_cols = sdf.columns.intersection(ddf.columns)
#common_idx = ddf.index.intersection(ddf.index)
#merged_df = pd.DataFrame(index=pd.concat([sdf["user"], ddf["user"]]).unique())
#merged_df = pd.DataFrame(index=pd.concat([sdf["user"], ddf["user"]]).unique())

# Join DataFrames based on the first column using outer join
df_joined = sdf.merge(ddf, on="gname", how='outer')
df_joined["final_mem"] = df_joined["dest_mem"]

def add_missing_members(smem, dmem):
    
    #Convert string to numpy for comparision
    slist = np.array(smem.split(","))
    dlist = np.array(dmem.split(","))
    
    #Comparing differences and adding missing members
    missing = np.setdiff1d(slist, dlist)
    dlist = np.concatenate((dlist, missing))
    
    #Converting nummpy back to string
    return np.array2string(dlist)[2:-2].replace("' '", ","), missing

def check_group_file():
    for index, row in df_joined.iterrows():
        smem = row['source_mem']
        dmem = row['dest_mem']
        suid = row['source_uid']
        duid = row['dest_uid']
        group = str(row['gname'])
        print(str(row['gname']) +" | "+  str(smem) +" | "+ str(dmem))
    
        if duid is np.nan:
            df_joined['final_mem'][index] = smem
            df_joined['dest_uid'][index] = suid
            df_joined['dest_gid'][index] = df_joined['source_gid'][index]
            print("Added group("+group+"): ",smem)
        
        if smem == dmem:        ##Nothing to cmompare if the members already matches
            df_joined['final_mem'][index] = dmem
        elif smem is not np.nan and dmem is not np.nan:      ##Only add missing members to the group
            df_joined['final_mem'][index], missing = add_missing_members(str(smem), str(dmem))
            print("Members added to group("+group+"):",missing)
        elif smem is not np.nan:    ##Copy all members if model has no members
            df_joined['final_mem'][index] = smem
            print("Members added to group("+group+"): ",smem)
        
check_group_file(df_joined)

df_joined = df_joined.astype({'dest_gid': 'int32'})

df = df_joined.to_string(index=False, header=None, na_rep='$', columns=['gname','dest_uid','dest_gid','final_mem']).split('\n')
df = [':'.join(ele.split()) for ele in df]
df = [ele+"\n" for ele in df]
df = [element.replace('$','') for element in df]
