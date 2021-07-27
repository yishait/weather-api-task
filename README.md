# weather-api-task

## task description:
create a deployment pipeline, packing node.js application in Docker image, and deployed using HELM in k8s cluster
as mentioned in https://github.com/culture-trip/weather-api

Clone the repo and run:
```sh
source init.sh
```

By running source init.sh file the following actions are taken:
1) check if virtualenv exists, if not - create it
2) install all dependencies required 
3) trigger the main_run.py script

## main_run.py script
1) import dependencies, check running dir and create Docker client 
2) if weather-api repo does not exist, clone it
3) copy Docker files content into the weather-api repo:
   Dockerfile - copy app files to docker, run npm install, set entrypoint npm start
   docker-compose - set image name, version, and port
4) interactively create a .env file with API_KEY, PORT and version.
5) login to docker hub registry and push the image

## K8s deployment
for testing I created a free tier k8s cluster with 2 nodes 1 master using this guide:
https://aws.plainenglish.io/how-to-setup-a-kubernetes-cluster-with-aws-free-tier-and-a-free-domain-514d010ae456

created a hosted-zone, security group, bucket for the cluster state
and evantually spin it up using this command:
```sh
kops create cluster --name=kube.dynst.ml --state=s3://yishai-bucket --zones=eu-west-1a --node-count=2 --node-size=t3.medium --master-size=t3.medium --dns-zone=kube.dynst.ml --yes
```


5) validate k8s context 
6) helm install using chart in weather-api-task repo
   pass --set selected version and port 
   pass the api_key in encrypted secret.yaml 
   Api key and port are saved as environment variables in container

   equivilant to the following commands
   ```sh
   $ helm install --set service.port=8080 --set image.tag=v3  --create-namespace  -n weather -f values.yaml weather .
   $ kubectl -n weather port-forward weather-chart-56db6d6b74-bn4lx 3000:3000
   ```

   to uninstall:
   ```sh
   $ helm uninstall -n weather weather 
   ```
   Destroy free cluster:
   ```sh
   $ kops delete cluster --name=kube.dynst.ml --state=s3://yishai-bucket --yes
   ```

For additional Monitoring: 
   open another tab and run:
   ```sh
   $ kubectl apply -f "https://cloud.weave.works/k8s/scope.yaml?k8s-version=$(kubectl version | base64 | tr -d '\n')"
   ```
   ```sh
   $ kubectl port-forward -n weave "$(kubectl get -n weave pod --selector=weave-scope-component=app -o jsonpath='{.items..metadata.name}')" 4040
   ```
   
   this will give you an overview of the containers used resources, uptime, networking and footprint etcetera
   
![image](https://user-images.githubusercontent.com/37850722/127234021-9ac9566b-35cc-42a3-9907-0a42ce62bde1.png)

For scaling we can increase the replica count and implement load balancing to achieve High availability using Nginx Controllers.
   
   ![image](https://user-images.githubusercontent.com/37850722/127230596-fc17ec95-8f7c-4e99-8419-d9f41c2bf5bf.png)

