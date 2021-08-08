from records.models import Mark, ChangeHistory


def mark_history_pre_save(sender, instance, *args, **kwargs):
    """ Load mark value from before change """
    if instance.pk:
        qs = Mark.objects\
            .filter(pk=instance.pk)\
            .select_related('symbol')
        old_instance = qs.get()

        instance.value_old = old_instance.symbol


def mark_history_post_save(sender, instance, created, *args, **kwargs):
    """ Save mark change history"""
    if created:
        history = ChangeHistory(
            mark=instance,
            type=ChangeHistory.TYPE_ADD,
            user=instance.modifying_user or instance.teacher,
            value_new=instance.symbol
        )
    else:
        history = ChangeHistory(
            mark=instance,
            type=ChangeHistory.TYPE_MODIFY,
            user=instance.modifying_user or instance.teacher,
            value_old=instance.value_old,
            value_new=instance.symbol
        )
    history.save()
