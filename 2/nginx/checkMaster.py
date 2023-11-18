#!/usr/bin/python -u
import redis
import time
import traceback
import os

last_server = "1.1.1.1"
last_port = 6379
debug = False

def write_ex(ex):
    try:
        arr = traceback.format_exc().strip("\n").split("\n")
        ln = len(arr)
        
        err_message = arr[ln-1].strip().split(":")[0].strip()
        if "redis.exceptions.ReadOnlyError" == err_message and debug == False:
            return

        m = "ERR: [ E: "+ arr[ln-1].strip()
        m = m + ", C: " + arr[ln-3].strip()
        m = m + ", F: " + arr[1].strip()+" ]"

        print(m)
    except Exception as e:
        print("ERR: Unexpected Error: " + str(ex))

def test_redis(host, port, password="", key = "testNginx"):
    try:
        global last_server, last_port, debug

        if debug:
            print("INF: Test host: " + host + ":" + str(port))

        time.sleep(1)

        r = redis.Redis(host=host, port=port, password=password, decode_responses=True)
        control = r.set(key, "ok")
        if control == False: 
            print("ERR: Write Error: "+ host + ":" + str(port))
            return False
        
        read = r.get(key)
        if read != "ok":
            print("ERR: Read Error: "+ host + ":" + str(port) + " - " + read)
            return False
        
        if last_server == host and last_port == port:
            if debug:
                print("INF: Already master same: " + host + ":" + str(port))

            return False

        print("ERR: Master changed: " + last_server + " -> " + host + " - " + str(last_port) + " -> " + str(port))

        last_server = host
        last_port = port

        return True
        
    except Exception as e:
        write_ex(e)
        return False

def write_new_config_and_reload_nginx():
    try:
        global last_server, last_port

        print("INF: Writing new config file: " + last_server + ":" + str(last_port))

        with open("/etc/nginx/nginx.conf", "w") as file:
            lines_to_write = [
                "worker_processes auto;\n",
                "error_log /var/log/nginx/error.log;\n",
                "pid /var/run/nginx.pid;\n",
                "\n",
                "events {\n",
                "    worker_connections 1024;\n",
                "}\n",
                "\n",
                "stream {\n",
                "    upstream backend {\n",
                "        server "+last_server+":"+str(last_port)+";\n",
                "    }\n",
                "\n",
                "    server {\n",
                "        listen 6381;\n",
                "        proxy_pass backend;\n",
                "    }\n",
                "}"
            ]

            file.writelines(lines_to_write) 

        print("INF: Writed new config file: " + last_server + ":" + str(last_port))
            
        reload_nginx()
    except Exception as e:
        write_ex(e)
        return False

def reload_nginx():
    print("ERR: Nginx service restarting")
    os.system("service nginx reload")

def monitor():
    while True:
        servers = [ ["1.1.1.1", 6379, "pswd12345"], ["1.1.1.2", 6379, "pswd12345"], ["1.1.1.3", 6379, "pswd12345"]]
        for server in servers:
            control = test_redis(server[0], server[1], server[2])
            if control:
                write_new_config_and_reload_nginx()

        time.sleep(1)

if __name__ == "__main__":
    print("INF: Starting...")
    monitor()
