import os
import datetime
import shutil

##Enter Server Details
model_server = "files\modelServer\etc\\"
new_server = "files\\newServer\etc\\"


##Taking backup of original File Model Server
file = input("Enter file to copy (without extention): ")
original_file = new_server + file + ".txt"
file_name, file_extension = os.path.splitext(original_file)
new_file = file_name + '_NEW_' + datetime.datetime.now().strftime("%Y-%m-%d") + file_extension
backup_file = file_name + '_BKP' + datetime.datetime.now().strftime("%Y-%m-%d") + file_extension
shutil.copy(original_file, backup_file)
print("Backup created:",backup_file)

    
##Reading entries from file in model server
source_file = open(model_server + file + '.txt', 'r')
s_entries = source_file.readlines()
source_file.close()


#T#aking entries from file in new server
dest_file = open(original_file, 'r')
d_entries = dest_file.readlines()
dest_file.close

print("Comparing entries from model server....")

##Comparing and adding missing entries in passwd,shadow, users.ignore
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


##Update missing entries in file
file = open(new_file,"w")
file.writelines(d_entries)
file.close()