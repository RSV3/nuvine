import base64
import os
import mimetypes

from django.core.files.uploadedfile import SimpleUploadedFile
from tastypie import fields
from django import forms


# ref - https://gist.github.com/cellofellow/5493290
class Base64FileField(fields.FileField):
    """
    A django-tastypie field for handling file-uploads through raw post data.
    It uses base64 for en-/decoding the contents of the file.
    Usage:

    class MyResource(ModelResource):
        file_field = Base64FileField("file_field")

        class Meta:
            queryset = ModelWithFileField.objects.all()

    In the case of multipart for submission, it would also pass the filename.
    By using a raw post data stream, we have to pass the filename within our
    file_field structure:

    file_field = {
        "name": "myfile.png",
        "file": "longbas64encodedstring",
        "content_type": "image/png" # on hydrate optional
    }

    Your file_field will by dehydrated in the above format if the return64
    keyword argument is set to True on the field, otherwise it will simply
    return the URL.
    """

    def __init__(self, *args, **kwargs):
        self.return64 = kwargs.pop('return64', False)
        super(Base64FileField, self).__init__(*args, **kwargs)

    def dehydrate(self, bundle, for_list=True):
        if not self.return64:
            instance = getattr(bundle.obj, self.instance_name, None)
            try:
                url = getattr(instance, 'url', None)
            except ValueError:
                url = None
            return url
        else:
            if (not self.instance_name in bundle.data
                    and hasattr(bundle.obj, self.instance_name)):
                file_field = getattr(bundle.obj, self.instance_name)
                if file_field:
                    content_type, encoding = mimetypes.guess_type(
                        file_field.file.name)
                    b64 = open(
                        file_field.file.name, "rb").read().encode("base64")
                    ret = {"name": os.path.basename(file_field.file.name),
                           "file": b64,
                           "content-type": (content_type or
                                            "application/octet-stream")}
                    return ret
            return None

    def hydrate(self, bundle):
        value = super(Base64FileField, self).hydrate(bundle)
        if value and isinstance(value, dict):
            return SimpleUploadedFile(value["name"],
                                      base64.b64decode(value["file"]),
                                      value.get("content_type",
                                                "application/octet-stream"))
        elif isinstance(value, basestring):
            return value
        else:
            return None


class Base64MultiField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        kwargs['fields'] = (
            forms.CharField(),
            forms.CharField(max_length=100),
            forms.CharField(),
        )
        super(Base64MultiField, self).__init__(*args, **kwargs)

    def compress(self, data_list):
        f = SimpleUploadedFile(
            data_list[1],
            base64.b64decode(data_list[0]),
            content_type=data_list[2])
        return f
