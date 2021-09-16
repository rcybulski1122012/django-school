from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, TemplateView, UpdateView

from django_school.apps.classes.models import Class
from django_school.apps.common.utils import IsTeacherMixin, teacher_view
from django_school.apps.grades.forms import (
    BulkGradeCreationCommonInfoForm,
    BulkGradeCreationFormSet,
    GradeForm,
)
from django_school.apps.grades.models import Grade, GradeCategory
from django_school.apps.lessons.models import Lesson, Subject

User = get_user_model()


class GradesViewMixin:
    school_class = None
    subject = None

    def dispatch(self, request, *args, **kwargs):
        self.school_class = get_object_or_404(Class, slug=self.kwargs["class_slug"])
        self.subject = get_object_or_404(Subject, slug=self.kwargs["subject_slug"])

        if not self.does_the_teacher_teach_the_subject_to_the_class():
            raise Http404

        return super().dispatch(request, *args, **kwargs)

    def does_the_teacher_teach_the_subject_to_the_class(self):
        return Lesson.objects.filter(
            school_class=self.school_class,
            subject=self.subject,
            teacher=self.request.user,
        ).exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "school_class": self.school_class,
                "subject": self.subject,
            }
        )

        return context


class GradeCreateView(
    LoginRequiredMixin, IsTeacherMixin, GradesViewMixin, SuccessMessageMixin, CreateView
):
    model = Grade
    form_class = GradeForm
    template_name = "grades/grade_form.html"
    success_message = "The grade has been added successfully."

    def get_initial(self):
        return {
            "student": self.request.GET.get("student"),
            "teacher": self.request.user.pk,
            "subject": self.subject.pk,
        }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                "school_class": self.school_class,
                "subject": self.subject,
            }
        )
        return kwargs

    def get_success_url(self):
        return reverse(
            "grades:class_grades",
            args=[self.kwargs["class_slug"], self.kwargs["subject_slug"]],
        )


@login_required
@teacher_view
def create_grades_in_bulk_view(request, class_slug, subject_slug):
    school_class = get_object_or_404(Class, slug=class_slug)
    subject = get_object_or_404(Subject, slug=subject_slug)
    students = User.objects.filter(school_class=school_class)
    initial = {"category": request.GET.get("category")}

    if not Lesson.objects.filter(
        school_class=school_class, subject=subject, teacher=request.user
    ).exists():
        raise Http404

    if request.method == "POST":
        common_form = BulkGradeCreationCommonInfoForm(
            request.POST,
            teacher=request.user,
            subject=subject,
            school_class=school_class,
            initial=initial,
        )

        grades_formset = BulkGradeCreationFormSet(
            request.POST,
            students=students,
        )
        if common_form.is_valid():
            grades_formset.set_common_data(common_data=common_form.cleaned_data)
            if grades_formset.is_valid():
                grades_formset.save()

                messages.success(request, "The grades have been added successfully.")
                return redirect(
                    reverse(
                        "grades:class_grades", args=[school_class.slug, subject.slug]
                    )
                )

    else:
        common_form = BulkGradeCreationCommonInfoForm(
            teacher=request.user,
            subject=subject,
            school_class=school_class,
            initial=initial,
        )
        grades_formset = BulkGradeCreationFormSet(students=students)

    return render(
        request,
        "grades/create_grades_in_bulk.html",
        {
            "common_form": common_form,
            "grades_formset": grades_formset,
            "school_class": school_class,
            "subject": subject,
        },
    )


class ClassGradesView(
    LoginRequiredMixin, IsTeacherMixin, GradesViewMixin, TemplateView
):
    template_name = "grades/class_grades.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "categories": GradeCategory.objects.filter(
                    subject=self.subject, school_class=self.school_class
                ),
                "students": User.students.with_weighted_avg(subject=self.subject)
                .with_subject_grades(subject=self.subject)
                .filter(school_class=self.school_class),
            }
        )

        return context


class SingleGradeMixin(UserPassesTestMixin):
    model = Grade
    pk_url_kwarg = "grade_pk"
    context_object_name = "grade"

    def test_func(self):
        return self.get_object().teacher == self.request.user

    def get_success_url(self):
        grade = self.get_object()
        return reverse(
            "grades:class_grades",
            args=[grade.student.school_class.slug, grade.subject.slug],
        )

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("category", "subject", "student__school_class", "teacher")
        )


class GradeUpdateView(
    LoginRequiredMixin,
    IsTeacherMixin,
    SingleGradeMixin,
    SuccessMessageMixin,
    UpdateView,
):
    fields = ["grade", "weight", "comment"]
    template_name = "grades/grade_update.html"
    success_message = "The grade has been updated successfully."


class GradeDeleteView(
    LoginRequiredMixin,
    IsTeacherMixin,
    SingleGradeMixin,
    DeleteView,
):
    template_name = "grades/grade_confirm_delete.html"
    success_message = "The grade has been deleted successfully."

    def delete(self, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(*args, **kwargs)
