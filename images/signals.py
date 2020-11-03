from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from images.models import Image


@receiver(m2m_changed, sender=Image.users_like.through)
def user_likes_changed(sender, instance, **kwargs):
    action = kwargs.pop('action', None)
    if action == 'pre_add':
        import pdb
        pdb.set_trace()
        instance.total_likes = instance.users_like.count()
        instance.save()
    return instance
