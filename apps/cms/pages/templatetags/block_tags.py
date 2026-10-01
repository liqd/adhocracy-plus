from django import template

register = template.Library()


@register.simple_tag
def file_type(media_file):
    media_file = media_file.lower()
    if media_file.endswith(".mp4"):
        return "video/mp4"
    elif media_file.endswith(".webm"):
        return "video/webm"
    elif media_file.endswith(".mov"):
        return "video/quicktime"
    elif media_file.endswith(".avi"):
        return "video/x-msvideo"
    elif media_file.endswith(".mkv"):
        return "video/x-matroska"
    elif media_file.endswith(".mp3"):
        return "audio/mpeg"
    elif media_file.endswith(".wav"):
        return "audio/wav"
    elif media_file.endswith(".ogg"):
        return "audio/ogg"
    else:
        return "type invalid"
