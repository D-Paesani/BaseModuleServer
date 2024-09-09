


-> docker build -t bmserver . -> copy the files mentioned in the gitignore file -> ./dockerrun.sh


ADD  /Users/dp/Documents/Software/Python/km3net/logs ./logs 

sudo docker run -v -it -p 5001:5001 -d bmserver -v /Users/dp/Documents/Software/Python/km3net/bmsvol:./var
sudo docker run -v /Users/dp/Documents/Software/Python/km3net/bmsvol:/mypath -it -p 5001:5001 -d bmserver

docker images -a   
docker ps -a

docker rmi -f bmserver   
