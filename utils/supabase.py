import uuid
from supabase import create_client
from django.conf import settings

supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_KEY
)

def upload_product_image(file, bucket_name):

    try:
        file_ext = file.name.split(".")[-1]
        filename = f"{uuid.uuid4()}.{file_ext}"

        file_bytes = file.read()

        supabase.storage.from_(bucket_name).upload(
            path=filename,
            file=file_bytes,
            file_options={
                "content-type": file.content_type
            }
        )

        public_url = supabase.storage.from_(bucket_name).get_public_url(filename)

        return public_url

    except Exception as e:
        print("❌ SUPABASE UPLOAD ERROR:", str(e))
        raise e