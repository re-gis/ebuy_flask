# uploading to cloudinary
from cloudinary.uploader import upload
import cloudinary
from flask import jsonify
import os

cloudinary.config(
    cloud_name=os.getenv("cloud_name"),
    api_key=os.getenv("api_key"),
    api_secret=os.getenv("api_secret"),
)


def upload_image(file) -> str:
    if not file:
        return jsonify({"error": "No file part"}), 400

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Upload the image to Cloudinary
    try:
        upload_result = upload(file)
        return upload_result["url"]
    except Exception as e:
        return jsonify({"error": str(e)}), 500
