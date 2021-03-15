#!/usr/bin/python3

import sys
import os
import datetime
from ip_to_nome_lat_lon import site_from_ip_addr

# cria diretorios "filtered_data" e "error_log_files" se nao existem
try:
    os.mkdir("filtered_data")
except FileExistsError:
    pass

# 20210215: arthur
try:
    os.mkdir("error_log_files")
except FileExistsError:
    pass

# os.system("sh rsync_to_server.sh")


for i in range(1):
    fin = sys.stdin
    cur_date = ""
    counter = 0
    data  = [ ]
    dict = { }

    last_date = [ 99, 99, 99 ]
    last_hour = [ 99, 99, 99 ]
    last_min_capture = -1
    fout = None
    error_log_file = None
    
    # data positions
    D_DATA = 0
    D_HORA = 1
    D_TTL = 2
    D_PROTO = 3
    D_IP_ID = 4
    D_SIP= 5
    D_DIP= 6
    D_CHECKSUM = 7
    D_FLAGS = 8
    D_QUERY = 9
    D_WHAT = 10
    D_EXTRA = 11
    
    altura = 0
    key = ""

    for line in fin:

        counter += 1

        if counter % 1000 == 0:
            #print("#", end="")
            #sys.stdout.flush()
            pass

        if len(line) == 0: continue
        
        # verifica se eh a linha de header
        if line[0] != ' ' and line[0] != '\t':
        
            # existe algo a ser contabilizado do registro anterior?
            if key != "":
                # nova chave? 
                if not key in dict:
                    dict[key] = { "count":1 }
                else:
                    dict[key]["count"] = dict[key]["count"] + 1
        
            # reinicia as variaveis de memoria
            key = ""
            data = []
            
            # inicia o processamento do novo hash
            clean_line = line.strip()
            items = clean_line.split(" ")

            if len(items) < 3: continue
            if items[2] != "IP": continue
            altura = 0

            n = len(items)
            if n < 6:
                print(items)
            else:
                # [data, hora, val_ttl, val_proto, val_ip_id ] 
                val_proto = items[15][1:-2]
                data = [ items[0], (items[1].split("."))[0], items[6].strip(","), val_proto, items[8].strip(","), "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0" ]
                #print("Data> ", data)
                if data[2] == "oui": print(clean_line)

        # if o header nao tinha dados validos
        elif len(data) == 0:
            continue
            
        # linha do corpo 
        else:
            altura += 1

            items = line.strip().split(" ")
            if len(items) == 0 or len(items[0]) == 0: continue
            
            # testa para ver se eh o sub-header 
            if altura == 1:
                c = items[0][0]
                if c >= '0' and c <= '9':
                    ip_src_a = items[0].split(".")
                    
                    ip_src = ip_src_a[0] + "." + ip_src_a[1] + "." + ip_src_a[2] + "." + ip_src_a[3] 
                    data[D_SIP] = ip_src
                    
                    try:
                        s = site_from_ip_addr(ip_src_a)
                    except:
                        print("Error: Invalid IP =",ip_src_a)
                        
                    if s == None:
                         print(ip_src_a)
                    else:
                        ip_dst_a = items[2].split(".")
                        
                        ip_len = len(ip_dst_a)
                        
                        # remove o ":" do final dos campos do ip_dst
                        ip_dst_a[ip_len-1] = ip_dst_a[ip_len-1] [:-1]
                        
                        # reconstitui o ip
                        ip_dst = ip_dst_a[0] + "." + ip_dst_a[1] + "." + ip_dst_a[2] + "." + ip_dst_a[3] 
                        data[D_DIP] = ip_dst

                        if ip_len == 4:
                            port_dst = "0"
                        else:
                            port_dst = ip_dst_a[4]
                        
                            # concentra portas sem interesse na porta "0"
                            proto_port = data[D_PROTO] + ":" + port_dst
                            #if not proto_port in ["17:53", "6:25", "6:110", "6:995", "6:143", "6:993"]: port_dst = "0"
                        
                        # processa parte do header
                        date = data[D_DATA].split("-")
                        hour = data[D_HORA].split(":")

                        # 20210123: nilson
                        capture_time = 1

                        # pega o minuto da hora
                        min = int(hour[1])
                        
                        # verifica se estourou o tempo de buferizacao
                        min_capture = min - (min % capture_time)

                        # houve mudanca na chave?
                        if date[0] != last_date[0] or date[1] != last_date[1] or date[2] != last_date[2] or \
                            hour[0] != last_hour[0] or last_min_capture != min_capture:
                            
                            # salva o que foi armazenado
                            if fout != None:
                                res = {key: val for key, val in sorted(dict.items(), key = lambda ele: ele[0])}
                                for k in res:
                                    d = dict[k]
                                    print(k,"|",d["count"], sep="", file=fout)
                                fout.close()
#                                  os.system("sh rsync_to_server.sh")


                            # monta o nome do novo arquivo
                            fname = "filtered_data/" + date[0] + date[1] + date[2] + "_" + hour[0] + "_" + ("%02d"%min_capture) + ".csv"
                            print(fname)
                            
                            last_date[0] = date[0]
                            last_date[1] = date[1]
                            last_date[2] = date[2]
                            last_hour[0] = hour[0]
                            last_min_capture = min_capture
                            fout = open(fname,"at")
                            dict = { }
                            
                        # pega checksum, query, what, flags, extra
                        comunication = ""
                        if proto_port == "17:53": # se for dns
                            if not items[5].find("]"): break
                            data[D_CHECKSUM] = items[6]

                            # 20210215: arthur
                            if len(items) < 10 or ('?' not in items[7] and '?' not in items[8]):
                                if not error_log_file:
                                    f_error_name = "error_log_files/" + date[0] + date[1] + date[2] + "_" + hour[0] + "_" + ("%02d"%min_capture) + ".csv"
                                    error_log_file = open(f_error_name,"w")
                                error_log_file.write(line)
                                continue

                            pos = 7
                            flags = items[pos]
                            if flags[0] != '[':
                                flags = ""
                                pos -= 1

                            data[D_FLAGS] = flags.replace("|","&")
                            data[D_QUERY] = items[pos+1].replace("|","&")
                            data[D_WHAT] = items[pos+2].replace("|","&")
                            data[D_EXTRA] = items[pos+3].replace("|","&")

                            comunication = "DNS/UDP"

                            
                        else: # se for smtp, pop ou imap
                            data[D_CHECKSUM] = items[6]
                            data[D_QUERY] = ""
                            data[D_WHAT] = ""
                            data[D_EXTRA] = ""

                            if proto_port == "6:25":
                                comunication = "SMTP/TCP"
                            elif proto_port == "6:110":
                                comunication = "POP/TCP"
                            elif proto_port == "6:995":
                                comunication = "POP_C/TCP"
                            elif proto_port == "6:143":
                                comunication = "IMAP/TCP"
                            elif proto_port == "6:993":
                                comunication = "IMAP_C/TCP"
                        
                        # key = 'yyyy-mm-dd hh:nn:00; 
                        key =  ( data[D_DATA] + " " + hour[0] + ":" + hour[1] + ":00|"   
                                + data[D_SIP] + '|'  
                                + data[D_TTL] + '|' 
                                + data[D_IP_ID] + '|' 
                                + data[D_DIP] + '|'  
                                + data[D_PROTO] + "|" 
                                + "0" + "|" 
                                + port_dst + "|" 
                                + data[D_QUERY] +"|" 
                                + data[D_WHAT] + "|" 
                                + data[D_FLAGS] + "|" 
                                + data[D_EXTRA] + "|"
                                + "NILSON3" + "|" 
                                + comunication
                            )


                
    # existe algo a ser contabilizado do registro anterior?
    if key != "":
        # nova chave? 
        if not key in dict:
            dict[key] = { "count":1 }
        else:
            dict[key]["count"] = dict[key]["count"] + 1

    # salva o residuo
    if fout != None:
        res = {key: val for key, val in sorted(dict.items(), key = lambda ele: ele[0])}
        for k in res:
            d = dict[k]
            print(k,"|",d["count"], sep="", file=fout)
        fout.close()

    # 20210215: arthur
    if error_log_file:
        error_log_file.close()


