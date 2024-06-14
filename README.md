1. Build the image base hadoop image in *./hadoop/base*:
```docker
docker build -t ionicastefan20/hadoop:3.3.6 .
```

2. Start all the containers:
```docker
docker compose up -d --build
```

3. Add the image to the local hadoop volume (make sure to check the ```INFILENAME``` variable in the script):
```bash
./upload.sh
```

4. Copy the script to the spark local volume:
```bash
cp ./run.py data/spark
```

5. Run the script:
```docker
docker compose exec spark-master spark-submit --master spark://spark-master:7077 /spark_data/run.py
```

The results can be found at ```data/spark/proc_image.tif```.

In order to change the input file name, output file name, and extension modify the ```INFILENAME```, ```OUTFILENAME```, and ```EXT``` global variables in *./run.py*. ```INFILENAME``` Must be the same as ```INFILENAME``` in *./upload.sh*.

The docker images used for this project were adapted to an *arm64* computer. To make it run on x86_64 chips please change the Debian image from ```arm64v8/debian:11``` to ```debian:11``` or ```amd64/debian:11``` in each *Dockerfile*.