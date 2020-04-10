docker container rm -f CONTAINER $(docker ps -a -q -f "name=github-fetcher")

docker build -t github-fetcher .
docker run -t -d --name github-fetcher github-fetcher


