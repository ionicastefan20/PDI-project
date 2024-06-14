import math
import cv2 as cv
import numpy as np
from pyspark import SparkFiles
from pyspark.sql import SparkSession


INFILENAME='Sentinel_2024'
OUTFILENAME='proc_image'
EXT = '.tif'


def split_image(bytes, N):
    blocks = []

    nparr = np.frombuffer(bytes, np.uint8)
    image = cv.imdecode(nparr, cv.IMREAD_COLOR)

    # Get the dimensions of the image
    height, width = image.shape[:2]

    # Calculate the dimensions of each grid cell
    cell_width = math.ceil(width / N)
    cell_height = math.ceil(height / N)

    # Split the image into NxN grid
    for i in range(N):
        for j in range(N):
            x_start = j * cell_width
            y_start = i * cell_height
            x_end = min(x_start + cell_width, width)
            y_end = min(y_start + cell_height, height)
            block = image[y_start:y_end, x_start:x_end]

            # Append each grid cell to the list
            _, buffer = cv.imencode(EXT, block)
            blocks.append(buffer.tobytes())

    return blocks


def process_block(bytes):
    nparr = np.frombuffer(bytes, np.uint8)
    img = cv.imdecode(nparr, cv.IMREAD_COLOR)
    proc_img = cv.bitwise_not(img)
    _, buffer = cv.imencode(EXT, proc_img)
    return buffer.tobytes()


def main():

    # Initialize SparkSession
    spark = SparkSession.builder \
        .appName("HelloWorld") \
        .master("spark://spark-master:7077") \
        .getOrCreate()

    hdfs_url = "hdfs://namenode:9000"
    image_path = f"{hdfs_url}/user/spark/input/{INFILENAME}{EXT}"

    spark.sparkContext.addFile(image_path)

    # Read image as binary file
    with open(SparkFiles.get(image_path.split('/')[-1]), "rb") as f:
        image_data = f.read()

    # Split the image into 4x4 grid
    blocks = split_image(image_data, 2)

    # Create an RDD from the blocks
    blocks_rdd = spark.sparkContext.parallelize(blocks)

    # Apply the processing function to each block
    processed_blocks = blocks_rdd.map(process_block).collect()

    offset = 0
    rows = []
    while offset < len(processed_blocks):
        decoded_block = [cv.imdecode(np.frombuffer(block, np.uint8), cv.IMREAD_COLOR) for block in processed_blocks]
        rows.append(np.concatenate(decoded_block[offset:offset + 2], axis=1))
        offset += 2

    proc_img = np.concatenate(rows, axis=0)

    _, buffer = cv.imencode(EXT, proc_img)
    output_path = f"/spark_data/{OUTFILENAME}{EXT}"
    with open(output_path, "wb") as f:
        f.write(buffer.tobytes())

    # Stop the SparkSession
    spark.stop()


if __name__ == "__main__":
    main()
