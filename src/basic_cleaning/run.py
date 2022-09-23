#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(filename)s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()

    logger.info("Fetching wandb artifact")
    local_path = wandb.use_artifact(args.input_artifact).file()
    df = pd.read_csv(local_path)
    logger.info("Performing basic cleaning operations")
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()
    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])
    #adding point out of boundaries
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()
    logger.info("Exporting dataframe to csv")
    df.to_csv("clean_sample.csv", index=False)
    artifact = wandb.Artifact(
     args.output_artifact,
     type=args.output_type,
     description=args.output_description,
    )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)

    

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="the dataset artifact on which the cleaning will be performed",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="the cleaned dataset artifact",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="the output artifact type",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="a description of the output artifact",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="the minimum value for the price column of the dataset",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="the minimum value for the price column of the dataset",
        required=True
    )


    args = parser.parse_args()

    go(args)
