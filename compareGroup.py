import os
from datetime import datetime as dt
import numpy as np
import shutil
import pandas as pd

##Enter Server Details
#model_server = "files\\test\\"
#new_server = "files\\test\\"
model_server = "files\modelServer\etc\\"
new_server = "files\\newServer\etc\\"
summary = "SUMMARY:"

'''
filex = File name with Extension
fname = File name without Extension
fext = File extension
path = Complete File path
d_entries = (List) Entries from file in New Server
s_entries = (List) Entries from file in Model Server


##Taking backup of original File Model Server
def take_backup(s):
    timestamp = str(dt.now().strftime("%Y-%m-%d-%H-%M-%S"))
    file = "newGroup"
    #file = input("Enter file to copy (without extention): ")
    original_file = new_server + file + ".txt"
    file_name, file_extension = os.path.splitext(original_file)
    new_file = file_name + "_NEW_" + timestamp + file_extension
    backup_file = file_name + "_BKP_" + timestamp + file_extension
    shutil.copy(original_file, backup_file)
    print("Backup created:",backup_file)
    s=s+"\nBackup created:"+backup_file
    return new_file, s
'''

##Taking backup of original File Model Server
def take_file_backup(filex,s):
    timestamp = str(dt.now().strftime("%Y-%m-%d-%H-%M-%S"))
    path = new_server + filex
    fname, fext = os.path.splitext(path)
    new_filex = fname + '_NEW_' + timestamp + fext  #passwd_NEW_2024-12-31.txt
    backup = fname + '_BKP_' + timestamp + fext  #passwd_BKP_2024-12-31.txt
    shutil.copy(path, backup)
    print("Backup created:", backup)
    s=s+"\nBackup created:"+backup
    return new_filex, s

#Reading data and analysing as Pandas Dataframe
#Called from compare_entries() function
def read_group_and_analyse(source_path='files\\test\modelGroup.txt', dest_path='files\\test\\newGroup.txt'):
    sdf = pd.read_csv(source_path, sep=':', names=["gname", "source_uid", "source_gid", "source_mem"])
    ddf = pd.read_csv(dest_path, sep=':', names=["gname", "dest_uid", "dest_gid", "dest_mem"])

    # Find common columns and indices
    #common_cols = sdf.columns.intersection(ddf.columns)
    #common_idx = ddf.index.intersection(ddf.index)
    #all_values = pd.concat([sdf["gname"], ddf["gname"]]).unique()
    #final_mem_df = pd.DataFrame(index=all_values)

    # Join DataFrames based on the first column using outer join
    df_joined = sdf.merge(ddf, on="gname", how='outer')
    df_joined["final_mem"] = df_joined["dest_mem"]
    
    return df_joined


#Called from compare_entries() function
def add_missing_members(smem, dmem):
    
    #Convert string to numpy for comparison
    slist = np.array(smem.split(","))
    dlist = np.array(dmem.split(","))
    
    #Comparing differences and adding missing members
    missing = np.setdiff1d(slist, dlist)
    dlist = np.concatenate((dlist, missing))
    
    #Converting nummpy back to string
    return np.array2string(dlist)[2:-2].replace("' '", ","), missing


def compare_group_entries (s):
    
    #Import and analyze the group file data in both the servers
    df_joined = read_group_and_analyse()

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
            s=s+"\nAdded group("+group+"): "+str(smem)
            print("Added group("+group+"): ",smem)
        
        elif smem == dmem:        ##Nothing to cmompare if the members already matches
            df_joined['final_mem'][index] = dmem
        elif smem is not np.nan and dmem is not np.nan:      ##Only add missing members to the group
            df_joined['final_mem'][index], missing = add_missing_members(str(smem), str(dmem))
            s=s+"\nMembers added to group("+group+"):"+str(missing)
            print("Members added to group("+group+"):",missing)
        elif smem is not np.nan:    ##Copy all members if model has no members
            df_joined['final_mem'][index] = smem
            s=s+"\nMembers added to group("+group+"): "+smem
            print("Members added to group("+group+"): ",smem)
            
        print("------")
    
    df_joined = df_joined.astype({'dest_gid': 'int32'})

    ##Converting Datafrome into String
    modified = df_joined.to_string(index=False, header=None, na_rep='$', columns=['gname','dest_uid','dest_gid','final_mem']).split('\n')
    modified = [':'.join(ele.split()) for ele in modified]
    modified = [ele+"\n" for ele in modified]
    modified = [element.replace('$','') for element in modified]
    return modified,s

##Saving final changes to a new file from String
def save_changes(output, path, s):
    file = open(path,"w+")
    file.writelines(output)
    file.close()
    s = s+"\nChanges have been made and new file has been created: "+path
    return s
   

filex = input("Enter file to copy (without extention): ") + '.txt'
new_filex, summary = take_file_backup(filex,summary)

#new_file, summary = take_file_backup(summary)
output, summary = compare_group_entries(summary)
summary = save_changes (output, new_filex, summary)

print (summary)