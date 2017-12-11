#!/usr/bin/env python
import MySQLdb
from sys import argv
db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                     passwd="XXX",  # your password
                     db="molecular_rotors")        # name of the data base

cur = db.cursor()
table_name="energies"
cur.execute("SHOW columns FROM energies")
column_names=[column[0] for column in cur.fetchall()]

au2ev=float(27.211386017)
def get_s0(file):
    energies=[]
    for line in file:
        if " SCF Done:" in line:
            energies.append(float(line.split()[4]))

    return energies[0]

def get_es(file,multiplicity):
    energies_eV=[]
    for line in file:
        if " Excited State  " in line:
            if multiplicity==1:
                if line.split()[3][0]=="S":
                    energies_eV.append(float(line.split()[4]))
            elif multiplicity==3:
                if line.split()[3][0]=="T":
                    energies_eV.append(float(line.split()[4]))

    es_energies_au=[i/au2ev for i in energies_eV]
    return es_energies_au

def get_s0_cc2(file):
    for line in file:
        if "     *   Final CC2 energy                        :" in line:
            energy=float(line.split()[5])
            break
    return energy

def get_es_cc2(file):
    es_energies=[]
    for line in file:
        if "Energy:" in line:
            es_energies.append(float(line.split()[1]))
    return es_energies

def update_table(table, column, value, model, leveloftheory):
    command="UPDATE {} SET `{}`='{}' WHERE model='{}' AND level_of_theory='{}'".format(table,column,value,model,lot)
    cur.execute(command)
    db.commit()
    return

models=["m1","m4"]
lot="DFT"
for model in models:
    FC=open(str(model+"-FC.out"),"r").read().splitlines()
    s1min=open(str(model+"-s1min.out"),"r").read().splitlines()
    t1min=open(str(model+"-t1min.out"),"r").read().splitlines()
    FC_s0=get_s0(FC)
    FC_singlets=[i+FC_s0 for i in get_es(FC,1)]
    FC_triplets=[i+FC_s0 for i in get_es(FC,3)]
    s1min_s0=get_s0(s1min)
    s1min_singlets=[i+s1min_s0 for i in get_es(s1min,1)]
    s1min_singlets.insert(0,s1min_s0)
    s1min_triplets=[i+s1min_s0 for i in get_es(s1min,3)]

    t1min_s0=get_s0(t1min)
    t1min_singlets=[i+t1min_s0 for i in get_es(t1min,1)]
    t1min_singlets.insert(0,t1min_s0)
    t1min_triplets=[i+t1min_s0 for i in get_es(t1min,3)]

    command="INSERT INTO energies (`{}`,`{}`) VALUES ('{}','{}')".format(column_names[0],column_names[1],model,lot)
    print command
    cur.execute(command)
    db.commit()
    command="UPDATE energies SET `{}`='{}' WHERE model='{}' AND level_of_theory='{}'".format(column_names[2],FC_s0,model,lot)
    cur.execute(command)
    print command
    db.commit()

    for i in range(1,6):
        update_table("energies", column_names[2+i], FC_singlets[i-1], model,lot)
    for i in range(1,4):
        update_table("energies", column_names[7+i], FC_triplets[i-1], model,lot)
    for i in range(2):
        update_table("energies", column_names[11+i], s1min_singlets[i], model,lot)
    update_table("energies", column_names[13], s1min_triplets[0], model,lot)
    for i in range(2):
        update_table("energies", column_names[14+i],t1min_singlets[i],model,lot)
        db.commit()
    update_table("energies", column_names[16],t1min_triplets[0],model,lot)

lot="cc2"
for model in models:
    FC_s=open(str(model+"-"+lot+"-FC-singlets"),"r").read().splitlines()
    FC_t=open(str(model+"-"+lot+"-FC-triplets"),"r").read().splitlines()
    s1min_s=open(str(model+"-"+lot+"-s1min-singlets"),"r").read().splitlines()
    s1min_t=open(str(model+"-"+lot+"-s1min-triplets"),"r").read().splitlines()
    t1min_s=open(str(model+"-"+lot+"-t1min-singlets"),"r").read().splitlines()
    t1min_t=open(str(model+"-"+lot+"-t1min-triplets"),"r").read().splitlines()
    FC_s0=get_s0_cc2(FC_s)
    FC_singlets=[i+FC_s0 for i in get_es_cc2(FC_s)]
    FC_triplets=[i+FC_s0 for i in get_es_cc2(FC_t)]

    s1min_s0=get_s0_cc2(s1min_s)

    s1min_singlets=[i+s1min_s0 for i in get_es_cc2(s1min_s)]

    s1min_singlets.insert(0,s1min_s0)

    s1min_triplets=[i+s1min_s0 for i in get_es_cc2(s1min_t)]

    t1min_s0=get_s0_cc2(t1min_s)
    t1min_singlets=[i+t1min_s0 for i in get_es_cc2(t1min_s)]
    t1min_singlets.insert(0,t1min_s0)
    t1min_triplets=[i+t1min_s0 for i in get_es_cc2(t1min_t)]

    command="INSERT INTO energies (`{}`,`{}`) VALUES ('{}','{}')".format(column_names[0],column_names[1],model,lot)
    cur.execute(command)
    db.commit()
    command="UPDATE energies SET  `{}`='{}' WHERE model='{}' and level_of_theory='{}'".format(column_names[2],FC_s0,model,lot)
    cur.execute(command)
    db.commit()

    for i in range(1,6):
        update_table("energies", column_names[2+i], FC_singlets[i-1], model,lot)
    for i in range(1,4):
        update_table("energies", column_names[7+i], FC_triplets[i-1], model,lot)
    for i in range(2):
        update_table("energies", column_names[11+i], s1min_singlets[i], model,lot)
    update_table("energies", column_names[13], s1min_triplets[0], model,lot)
    for i in range(2):
        update_table("energies", column_names[14+i],t1min_singlets[i],model,lot)
    update_table("energies", column_names[16],t1min_triplets[0],model,lot)

db.close()
