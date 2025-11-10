# File: backend/aws/glue_jobs.py
# Purpose: AWS Glue ETL job definitions

"""
AWS Glue ETL Jobs
Data transformation and loading jobs for match history processing
"""

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

def match_history_etl_job():
    """
    Glue ETL job for processing raw match history
    Transforms raw JSON data into structured format for Athena queries
    """
    # Initialize Glue context
    sc = SparkContext()
    glueContext = GlueContext(sc)
    spark = glueContext.spark_session
    
    # Read raw match data from S3
    raw_data = glueContext.create_dynamic_frame.from_catalog(
        database="synergyscope",
        table_name="raw_matches"
    )
    
    # Transform data
    # 1. Flatten nested structures
    flattened = raw_data.resolveChoice(specs=[('_col0', 'cast:string')])
    
    # 2. Extract relevant fields
    # 3. Calculate derived metrics
    
    # Write to processed data location
    glueContext.write_dynamic_frame.from_options(
        frame=flattened,
        connection_type="s3",
        connection_options={
            "path": "s3://synergyscope-data/processed/matches/",
            "partitionKeys": ["patch_version", "year", "month"]
        },
        format="parquet"
    )


def patch_aggregation_job():
    """
    Glue ETL job for patch-level aggregation
    Aggregates match data by patch for meta analysis
    """
    sc = SparkContext()
    glueContext = GlueContext(sc)
    spark = glueContext.spark_session
    
    # Read processed match data
    matches = glueContext.create_dynamic_frame.from_catalog(
        database="synergyscope",
        table_name="processed_matches"
    )
    
    # Convert to Spark DataFrame for aggregation
    df = matches.toDF()
    
    # Aggregate by patch
    patch_stats = df.groupBy("patch_version", "summoner_id").agg(
        count("match_id").alias("games_played"),
        sum(when(col("win") == True, 1).otherwise(0)).alias("wins"),
        avg("kda").alias("avg_kda")
    )
    
    # Write aggregated data
    patch_stats.write.mode("overwrite").parquet(
        "s3://synergyscope-data/aggregated/patch_stats/"
    )
