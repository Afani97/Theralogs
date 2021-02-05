import requests
from decouple import config

from theralogs.utils import read_file


class audio_transcribe_manager:
    endpoint = "https://api.assemblyai.com/v2"

    @classmethod
    def upload_audio_file(cls, temp_file_path):
        headers = {"authorization": config("ASSEMBLY_AI_KEY")}
        response = requests.post(
            f"{cls.endpoint}/upload",
            headers=headers,
            data=read_file(temp_file_path),
        )

        json_response = response.json()
        upload_url = json_response["upload_url"]

        return upload_url

    @classmethod
    def upload_audio_url(cls, webhook_base, upload_url, session_id):
        json_body = {
            "audio_url": upload_url,
            "webhook_url": f"{webhook_base}/main/aai-webhook?session_id={session_id}",
            "speaker_labels": True,
        }

        headers = {
            "authorization": config("ASSEMBLY_AI_KEY"),
            "content-type": "application/json",
        }

        response = requests.post(
            f"{cls.endpoint}/transcript", json=json_body, headers=headers
        )
        return True

    @classmethod
    def get_transcript(cls, transcript_id):
        headers = {
            "authorization": config("ASSEMBLY_AI_KEY"),
        }

        response = requests.get(
            f"{cls.endpoint}/transcript/{transcript_id}", headers=headers
        )
        response_json = response.json()

        return response_json
