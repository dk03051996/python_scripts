import boto3
import datetime
import pytz  # Import the pytz library for timezone conversion

def convert_utc_to_ist(utc_time):
    # Set the UTC timezone
    utc_timezone = pytz.timezone('UTC')
    
    # Set the IST timezone
    ist_timezone = pytz.timezone('Asia/Kolkata')

    # Convert UTC time to IST time
    ist_time = utc_timezone.localize(utc_time).astimezone(ist_timezone)

    return ist_time

def lambda_handler(event, context):
    # Set the AWS region
    region = 'ap-south-1'

    # Create an EC2 client
    ec2 = boto3.client('ec2', region_name=region)

    # Get the current time in the UTC timezone
    current_time_utc = datetime.datetime.utcnow()

    # Convert UTC time to IST time
    current_time_ist = convert_utc_to_ist(current_time_utc)

    # Set the cutoff time for stopping instances (in IST)
    cutoff_time_ist = datetime.datetime(current_time_ist.year, current_time_ist.month, current_time_ist.day, 19, 0, 0)

    # Check if the current time is after 6 PM IST
    if current_time_ist > cutoff_time_ist:
        # Describe all EC2 instances in the region
        instances = ec2.describe_instances()

        # Iterate through reservations and instances
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                state = instance['State']['Name']

                # Stop the instance if it's running
                if state == 'running':
                    print(f"Stopping EC2 instance {instance_id}")
                    ec2.stop_instances(InstanceIds=[instance_id])
                else:
                    print(f"Instance {instance_id} is not running, skipping.")

    else:
        print("It's not yet 6 PM IST. No EC2 instances will be stopped.")

    return {
        'statusCode': 200,
        'body': 'Lambda function executed successfully!'
    }

