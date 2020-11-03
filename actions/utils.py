from django.contrib.contenttypes.models import ContentType
from datetime import timedelta
from django.utils import timezone
from actions.models import Action


def create_action(user, verb, target=None):
    # Check for any similar actions in the last minute
    now = timezone.now()
    last_minute = now - timedelta(seconds=60)
    similar_actions = Action.objects.filter(user_id=user.id, verb=verb,
                                            created__gte=last_minute)
    if target:
        target_ct = ContentType.objects.get_for_model(target)
        similar_actions = Action.objects.filter(target_ct=target_ct, target_id=target_ct.id)

    import pdb
    pdb.set_trace()
    if not similar_actions:
        action = Action(user=user, verb=verb, target=target)
        action.save()
        return True
    return False
