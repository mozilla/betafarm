from topics.models import Topic


def topics(request):
    return {
        'topics': Topic.objects.filter(draft=False)
    }
