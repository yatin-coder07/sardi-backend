import uuid
from supabase import create_client
from django.conf import settings

supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_KEY
)


def upload_product_image(file):

    file_ext = file.name.split(".")[-1]

    filename = f"{uuid.uuid4()}.{file_ext}"

    bucket_name = "product_image"

    # upload to supabase storage
    supabase.storage.from_(bucket_name).upload(
        filename,
        file.read(),
        {"content-type": file.content_type}
    )

    # get public url
    public_url = supabase.storage.from_(bucket_name).get_public_url(filename)

    return public_url