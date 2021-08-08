from django.core.exceptions import ImproperlyConfigured
from django.http.response import Http404
from django.views.generic import DetailView, UpdateView, CreateView
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import PermissionRequiredMixin
from records.models import Mark, Course, Lesson, User
from records.forms.mark import MarkCreateForm, MarkUpdateForm


class MarkDetailView(PermissionRequiredMixin, DetailView):
    """ Response with Mark's details. Needs mark pk provided as GET param """
    permission_required = ['records.view_mark']
    # raise exception so login form isn't returned as ajax response
    raise_exception = True
    model = Mark
    template_name = 'records/ajax/mark_detail.html'
    context_object_name = 'mark'
    pk = None

    def get_queryset(self):
        """ select/prefetch related instances """
        qs = super().get_queryset().select_related(
            'student', 'teacher', 'course', 'category', 'symbol',
        ).prefetch_related('changehistory_set')
        return qs

    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        queryset = queryset.filter(pk=self.pk)
        try:
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            obj = None
        return obj

    def get(self, request, *args, **kwargs):
        self.pk = self.request.GET.get('pk', None)
        if not self.pk:
            error_msg = _('Error - no PK provided.')
            return JsonResponse(
                {'error_msg': error_msg}, status=400
            )

        self.object = self.get_object()
        if not self.object:
            error_msg = _('Error - object not found.')
            return JsonResponse(
                {'error_msg': error_msg}, status=400
            )

        # include form to update mark in context
        form = MarkUpdateForm(
            instance=self.object,
            prefix='change'
        )
        context = self.get_context_data(object=self.object, form=form)
        return self.render_to_response(context)


class MarkUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ['records.change_mark']
    # raise exception so login form isn't returned as ajax response
    raise_exception = True
    model = Mark
    form_class = MarkUpdateForm
    prefix = 'change'
    context_object_name = 'mark'

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.modifying_user = self.request.user
        instance.save()
        return JsonResponse(
            {
                'pk': instance.pk,
                'symbol': str(instance.symbol)
            },
            status=200
        )

    def form_invalid(self, form):
        errors = form.errors.as_json()
        return JsonResponse({"errors": errors}, status=400)


class MarkCreateView(PermissionRequiredMixin, CreateView):
    """
    View to view and process Mark creation form.
    Needs Lesson [or Course - TODO] provided in url kwargs.
    Queryset for 'student' field is generated based on provided model:
        - student's with Attendance related to Lesson if provided
        - all student's with Assignments to the Course's group if
        Course instance provided
    """
    permission_required = ['records.add_mark']
    # raise exception so login form isn't returned as ajax response
    raise_exception = True
    model = Mark
    form_class = MarkCreateForm
    prefix = 'create'
    template_name = 'records/ajax/mark_create.html'
    course = None
    lesson = None

    def dispatch(self, request, *args, **kwargs):
        if 'lesson' in self.kwargs:
            self.get_lesson()
        elif 'course' in self.kwargs:
            self.get_course()
        else:
            raise ImproperlyConfigured(
                _('View needs Lesson or Course provided')
            )
        return super().dispatch(request, *args, **kwargs)

    def get_lesson(self):
        if self.lesson:
            return self.lesson

        lesson_qs = Lesson.objects\
            .filter(pk=self.kwargs.get('lesson'))\
            .select_related('schedule', 'schedule__course')
        try:
            self.lesson = lesson_qs.get()
            self.course = self.lesson.schedule.course
        except Lesson.DoesNotExist:
            raise Http404(_('Invalid Lesson primary key.'))
        return self.lesson

    def get_course(self):
        if self.course:
            return self.course

        try:
            self.course = Course.objects.get(pk=self.kwargs.get('course'))
        except Course.DoesNotExist:
            raise Http404(_('Invalid Course primary key.'))
        return self.course

    def get_students(self):
        if self.lesson:
            students_pks = self.lesson.attendances.all().values_list(
                'student', flat=True
            )
            students = User.objects.filter(pk__in=students_pks)
        else:
            # TODO: get students from Course
            pass
        return students

    def get_initial(self):
        initial = {
            'teacher': self.request.user,
            'course': self.get_course()
        }
        initial.update(super().get_initial())
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['students'] = self.get_students()
        return kwargs

    def form_valid(self, form):
        instance = form.save()
        return JsonResponse(
            {
                'pk': instance.pk,
                'symbol': str(instance.symbol),
                'student': instance.student.pk
            },
            status=200
        )

    def form_invalid(self, form):
        errors = form.errors.as_json()
        return JsonResponse({"errors": errors}, status=400)
