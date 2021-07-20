from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Period(models.Model):
    time_start = models.TimeField(
        blank=False,
        null=False
    )

    time_end = models.TimeField(
        blank=False,
        null=False
    )

    class Meta:
        verbose_name = _('Period')
        verbose_name_plural = _('Periods')
        ordering = ['time_start']

    def _get_colliding_periods(self):
        """
        Return list of colliding periods,
        empty list if no colliding period exists.
        """
        qs = Period.objects.filter(
            time_start__lte=self.time_end,
            time_end__gte=self.time_start
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        return list(qs)

    def clean(self) -> None:
        super().clean()
        # check if ending time isn't earlier or same as starting time
        if self.time_end <= self.time_start:
            raise ValidationError({
                'time_end': _("Period's ending time can't "
                              "be earlier than start time.")
            })
        # check if there is period with colliding time
        colliding_periods = self._get_colliding_periods()
        if colliding_periods:
            raise ValidationError(
                _("Time collision with: %(colliding_periods)s") % {
                    'colliding_periods': colliding_periods
                }
            )

    def __str__(self):
        return "{} - {}".format(
            self.time_start.strftime('%H:%M'),
            self.time_end.strftime('%H:%M')
        )
