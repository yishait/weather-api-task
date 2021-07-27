Deploy weather city api to k8s cluster

task description:
create a deployment pipeline, packing node.js application in Docker image, and deployed using HELM in k8s cluster

By running source init.sh file the following actions are taken:
1) check if virtualenv exists, if not - create it
2) install all dependencies required 
3) trigger the main_run.py script

main_run.py script
1) import dependencies, check running dir and create Docker client 
2) if weather-api repo does not exist, clone it
3) copy Docker files content into the weather-api repo:
   Dockerfile - copy app files to docker, run npm install, set entrypoint npm start
   docker-compose - set image name, version, and port
4) interactively create a .env file with API_KEY, PORT and version.
5) login to docker hub registry and push the image

K8s deployment - I created a free tier k8s cluster with 2 nodes 1 master using this guide:
https://aws.plainenglish.io/how-to-setup-a-kubernetes-cluster-with-aws-free-tier-and-a-free-domain-514d010ae456

created a hosted-zone, security group, bucket for the cluster state
and evantually spin it up using this command:
kops create cluster --name=kube.dynst.ml --state=s3://yishai-bucket --zones=eu-west-1a --node-count=2 --node-size=t3.medium --master-size=t3.medium --dns-zone=kube.dynst.ml --yes

5) validate k8s context 
6) helm install using chart in weather-api-task repo
   pass --set selected version and port 
   pass the api_key in encrypted secret.yaml 
   Api key and port are saved as environment variables in container

   equivilant to the following commands
   $ helm install --set service.port=8080 --set image.tag=v3  --create-namespace  -n weather -f values.yaml weather .
   $ kubectl -n weather port-forward weather-chart-56db6d6b74-bn4lx 3000:3000

   to uninstall:
   $ helm uninstall -n weather weather 