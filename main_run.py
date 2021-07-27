from re import sub
import git
import os
import docker
import subprocess
from distutils.dir_util import copy_tree
from kubernetes import client, config
import time

dir_path = os.path.dirname(os.path.realpath(__file__))
docker_client = docker.from_env()

def create_env_file(token,port,version):
    os.chdir("weather-api")
    file = open(".env", "w").close
    file = open(".env", "w")
    file.write("API_TOKEN="+token+"\n") 
    file.write("PORT="+port+"\n") 
    file.write("VERSION="+version+"\n") 
    file.close() 

def setup_files():
    if not (os.path.isdir('weather-api')):
        git.Git(".").clone("https://github.com/culture-trip/weather-api.git")
    src = dir_path + '/docker_files/'
    trg = dir_path + '/weather-api/'
    copy_tree(src, trg)

# clone weather-api repo and copy Docker files
setup_files()

if 'API_KEY' not in os.environ:
    print("insert API KEY: ")
    token = input()
    os.environ["API_KEY"] = token
else:
    token=os.environ["API_KEY"]

if 'PORT' not in os.environ:
    print("insert app port: ")
    port = input()
    os.environ["PORT"] = port
    if port == "":
        port = 3000
else:
    port=os.environ["PORT"]

if 'VERSION' not in os.environ:
    print("set app version")
    version = input()
    os.environ["VERSION"] = version
else:
    version=os.environ["VERSION"]

# create .env file with key, port, and version
create_env_file(token,port,version)

# build docker image, login to docker hub and push to registry
subprocess.run(["docker", "compose", "build"])
subprocess.run(["docker", "login"])
print(docker_client.images.push("yishaitamir/weather_image",version))

print("Image succesfully uploaded to registry")

print("Deploy to k8s cluster? [Y \ N]")
print("If you want to deploy to k8s, please make sure you are in the correct context before selection.")
selection = input()

if selection == "Y":
    try:
        print("validating k8s context connection")
        config.load_kube_config()
        v1 = client.CoreV1Api()
        time.sleep(1)
        ret = v1.list_pod_for_all_namespaces(watch=False)
        time.sleep(1)
        print("context validated! deploying HELM chart.")
    except:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!!  failed to connect to k8s context  !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("sorry about that... please retry. ")
        exit(0)
    
    try:
        os.chdir("../weather-api-chart")
        print("deploying weather-api HELM chart version: "+version)
        subprocess.run(["helm", "install", "--set","service.port="+port,"--set","image.tag="+version,"--set","api_key="+token,"--create-namespace","-n","weather","-f","values.yaml","weather","."])
        time.sleep(2)
        print("\n\n\ninstallation completed\nCheck your api on http://127.0.0.1:"+port+"?cityName=Tel-aviv")
        pods = v1.list_namespaced_pod("weather")
        for pod in pods.items:
            pod_name=pod.metadata.name
        print(pod_name)
        subprocess.run(["kubectl","port-forward", "-n", "weather",pod_name,port+":"+port])
    except:
        print("#################################")
        print("## Failed to deploy HELM chart ##")
        print("#################################")
print("\n\n\n Done! good bye.")