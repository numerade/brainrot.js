import csv
import subprocess
import boto3
import os
from datetime import datetime

def write_to_log_csv(topic_id, title, status, error_message=""):
    log_file = 'generation_log.csv'
    file_exists = os.path.exists(log_file)
    
    with open(log_file, 'a', newline='') as csvfile:
        fieldnames = ['timestamp', 'topic_id', 'title', 'status', 'error_message']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header if file is new
        if not file_exists:
            writer.writeheader()
        
        writer.writerow({
            'timestamp': datetime.now().isoformat(),
            'topic_id': topic_id,
            'title': title,
            'status': status,
            'error_message': error_message
        })

def upload_to_s3(file_path, bucket, s3_key):
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_path, bucket, s3_key)
        print(f"Successfully uploaded {file_path} to s3://{bucket}/{s3_key}")
        return True, None
    except Exception as e:
        error_msg = str(e)
        print(f"Error uploading to S3: {error_msg}")
        return False, error_msg

def main():
    # Read the CSV file
    with open('topics.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            topic_id = row['id']
            title = row['title']
            slug = row['slug']
            course_title = row['curriculum_title']
            video_description = title if not course_title else f"{title} from the course {course_title}"

            print(f"Processing topic: {title}")
            
            # Run the node command
            try:
                subprocess.run(['node', 'localBuild.mjs', video_description], check=True)
            except subprocess.CalledProcessError as e:
                error_msg = f"Error running localBuild.mjs: {str(e)}"
                write_to_log_csv(topic_id, title, "FAILED", error_msg)
                continue
                
            # Construct output video path (assuming it's in out/video.mp4)
            video_path = 'out/video.mp4'
            
            if not os.path.exists(video_path):
                error_msg = "Video file not found"
                write_to_log_csv(topic_id, title, "FAILED", error_msg)
                continue
                
            # Construct S3 key
            s3_key = f"brainrot/{topic_id}-{slug}.mp4"
            
            # Upload to S3
            success, error_msg = upload_to_s3(video_path, 'com.numerade', s3_key)
            
            if success:
                write_to_log_csv(topic_id, title, "SUCCESS")
            else:
                write_to_log_csv(topic_id, title, "FAILED", error_msg)
            
            # Clean up local video file
            try:
                os.remove(video_path)
            except OSError as e:
                print(f"Error removing temporary file: {str(e)}")

if __name__ == "__main__":
    main()
