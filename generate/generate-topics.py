import csv
import subprocess
import boto3
import os

def upload_to_s3(file_path, bucket, s3_key):
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_path, bucket, s3_key)
        print(f"Successfully uploaded {file_path} to s3://{bucket}/{s3_key}")
    except Exception as e:
        print(f"Error uploading to S3: {str(e)}")

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
                print(f"Error running localBuild.mjs for {title}: {str(e)}")
                continue
                
            # Construct output video path (assuming it's in out/video.mp4)
            video_path = 'out/video.mp4'
            
            if not os.path.exists(video_path):
                print(f"Video file not found for {title}")
                continue
                
            # Construct S3 key
            s3_key = f"{topic_id}-{slug}.mp4"
            
            # Upload to S3
            upload_to_s3(video_path, 'com.numerade/brainrot', s3_key)
            
            # Clean up local video file
            try:
                os.remove(video_path)
            except OSError as e:
                print(f"Error removing temporary file: {str(e)}")

if __name__ == "__main__":
    main()
