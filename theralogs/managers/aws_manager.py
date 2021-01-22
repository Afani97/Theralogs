import json

import boto3
from botocore.config import Config

from theralogs.utils import format_transcript
from theralogsproject.settings import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_STORAGE_BUCKET_NAME,
)


class aws_manager:
    region = "us-east-1"
    my_config = Config(region_name=region)

    @classmethod
    def create_medical_transcript(cls, job_name, file_uri):
        transcribe = boto3.client(
            "transcribe",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            config=cls.my_config,
        )

        try:
            transcribe.start_medical_transcription_job(
                MedicalTranscriptionJobName=job_name,
                Media={"MediaFileUri": file_uri},
                LanguageCode="en-US",
                Specialty="PRIMARYCARE",
                Type="CONVERSATION",
                OutputBucketName=AWS_STORAGE_BUCKET_NAME,
                Settings={"ShowSpeakerLabels": True, "MaxSpeakerLabels": 2},
            )
        except:
            return None
        return True

    @classmethod
    def get_transcription_from_s3(cls, job_name):
        s3 = boto3.resource(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            config=cls.my_config,
        )
        obj = s3.Object(AWS_STORAGE_BUCKET_NAME, f"medical/{job_name}.json")
        file_content = obj.get()["Body"].read().decode("utf-8")
        json_content = json.loads(file_content)
        formatted_transcript = format_transcript(json_content)
        return formatted_transcript
