# hdfs-web-tool
A python based web tool that integrates with thrift hosts

# Docker Build
docker build --rm --no-cache -t wrui:1.0.0 .

# Docker Run
docker run -d -p 80:5000 --name wrui wrui:1.0.0
