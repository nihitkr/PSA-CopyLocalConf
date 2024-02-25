import os
import datetime
import shutil

##Enter Server Details
#model_server = input ("Enter Model Server Name: ") #E.g. Server123
#built_server = input("Enter newly built Server Name: ") #E.g. Server789


##Taking backup of original File Model Server
original_file = "E:\Python\PythonScripting\\" + input("Enter file to copy: ")
#original_file = 'new.txt' 
file_name, file_extension = os.path.splitext(original_file)
backup_file = file_name + '_BKP' + datetime.datetime.now().strftime("%Y-%m-%d") + file_extension
shutil.copy(original_file, backup_file)
print("Backup created:",backup_file)

    
##Taking entries from file in model server
source_file = open('E:\Python\PythonScripting\\model.txt', 'r')
s_entries = source_file.readlines()
source_file.close()

##Taking entries from file in new server
dest_file = open(original_file, 'r')
d_entries = dest_file.readlines()
dest_file.close


print("Comparing entries from model server....")

##Comparing and adding missing entries
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
file = open(original_file,"w")
file.writelines(d_entries)
file.close()