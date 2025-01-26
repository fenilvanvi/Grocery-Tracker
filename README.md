# Grocery-Tracker
Make sure Dockerfile is present in the root folder of the project.

Go to the root folder and run the Docker using the following command:
```
sudo docker build -t grocery-tracker . && sudo docker container run --restart unless-stopped -dit --log-opt max-size=2m --log-opt max-file=3 --name grocerytracker --net=host --publish 8002:8002 grocery-tracker:latest
```

To stop and remove the Docker container and image, run the following command:
```
sudo docker container stop grocerytracker && sudo docker container rm grocerytracker && sudo docker image rm -f grocery-tracker
```
