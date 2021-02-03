### Function hex to ipv4
def iphex(ip):
    bytes = ["".join(x) for x in zip(*[iter(ip)]*2)]
    bytes = [int(x, 16) for x in bytes]
    ip_format = '.'.join(str(x) for x in bytes)
    return ip_format
### Function cdp with SG300
def cisco_sg300(IP, COMMUNITY):
    from puresnmp import walk
    from puresnmp import get
    from puresnmp import table
    import pandas as pd
    oid_name = "1.3.6.1.4.1.9.9.23.1.3.4.0"
    oid_if = "1.3.6.1.4.1.9.9.23.1.1.1.1"
    oid_cdp = "1.3.6.1.4.1.9.9.23.1.2.1"
    oid_if_remote="1.3.6.1.4.1.9.9.23.1.2.1.1.7"
    oid_ip_remote="1.3.6.1.4.1.9.9.23.1.2.1.1.4"
    oid_name_remote="1.3.6.1.4.1.9.9.23.1.2.1.1.6"
    oid_model_remote="1.3.6.1.4.1.9.9.23.1.2.1.1.8"
    try:
        local_name = get(IP, COMMUNITY, oid_name)
        local_name=local_name.decode()
        interfaces = table(IP, COMMUNITY, oid_if)
        interfaces=interfaces[0]
        remote =[]
        local_if = []
        for row in walk(IP, COMMUNITY, oid_name_remote):
            interface = str(row[0])
            interface= interface.split(".")
            port=interfaces[interface[14]]
            remote.append(row[1].decode())
            local_if.append(port.decode())
        df_result = pd.DataFrame({'local':local_name, 'local_if': local_if, 'remote': remote})
        ## interface remota
        result_remote_if = table(IP, COMMUNITY, oid_if_remote)
        result_remote_if=result_remote_if[0]
        del result_remote_if['0']
        remote_if=list(result_remote_if.values())
        remote_if=[i.decode() for i in remote_if]
        df_result['remote_if']=remote_if
        ### ips remote
        ips = table(IP, COMMUNITY, oid_ip_remote)
        ips=ips[0]
        del ips['0']
        ips=list(ips.values())
        ips=[i.hex() for i in ips]
        ips=[iphex(i) for i in ips]
        df_result['remote_ip']=ips
        ### remote model
        model_remote = table(IP, COMMUNITY, oid_model_remote)
        model_remote=model_remote[0]
        del model_remote['0']
        model_remote=list(model_remote.values())
        model_remote=[i.decode() for i in model_remote]
        df_result['remote_model']=model_remote
        return df_result
    except:
        print ("error : " + IP)
        column_names = ["local", "local_if", "remote", "remote_if","remote_ip","remote_model"]
        df_result = pd.DataFrame(columns = column_names)
        return df_result
### Function cdp with Cisco IOS
def cisco_ios(IP, COMMUNITY):
    from puresnmp import table
    from puresnmp import get
    import pandas as pd
    oid_name = "1.3.6.1.4.1.9.9.23.1.3.4.0"
    oid_if = "1.3.6.1.4.1.9.9.23.1.1.1.1"
    oid_cdp = "1.3.6.1.4.1.9.9.23.1.2.1"
    column_names = ["local", "local_if", "remote", "remote_if","remote_ip","remote_model"]
    df_result = pd.DataFrame(columns = column_names)
    try:
        local_name = get(IP, COMMUNITY, oid_name)
        local_name=local_name.decode()
        interfaces = table(IP, COMMUNITY, oid_if)
        neighbors = table(IP, COMMUNITY, oid_cdp)
        for neighbor in neighbors:
            interface=interfaces[0]
            new_row = {"local":local_name, "local_if":interface[str(int(float(neighbor['0'])))].decode(), "remote": neighbor['6'].decode(), "remote_if":neighbor['7'].decode(),"remote_ip":iphex(neighbor['4'].hex()),"remote_model":neighbor['8'].decode()}
            df_result = df_result.append(new_row, ignore_index=True)
        return df_result
    except:
        #print ("error en: " + IP)
        return df_result

def bulk(FILE):
    import pandas as pd
    df = pd.read_csv(FILE)
    column_names = ["local", "local_if", "remote", "remote_if","remote_ip","remote_model"]
    df_result = pd.DataFrame(columns = column_names)
    for index, device in df.iterrows():
        device_type=device["type"]
        if device_type == "cisco_ios":
            df1 = cisco_ios(device["ip"],device["community"])
            df_result = pd.concat([df_result, df1])
            del df1
        elif device_type == "cisco_sg300":
            df1 = cisco_sg300(device["ip"],device["community"])
            df_result = pd.concat([df_result, df1])
            del df1
    df_result.reset_index(drop=True, inplace=True)
    return df_result


