import os
import datetime
import shutil

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