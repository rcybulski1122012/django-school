from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import (PermissionRequiredMixin,
                                        UserPassesTestMixin)
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import (CreateView, DeleteView, TemplateView,
                                  UpdateView)

from django_school.apps.classes.models import Class
from django_school.apps.grades.forms import (BulkGradeCreationCommonInfoForm,
                                             BulkGradeCreationFormSet,
                                             GradeForm)
from django_school.apps.grades.models import Grade, GradeCategory
from django_school.apps.lessons.models import Lesson, Subject

User = get_user_model()

SUCCESS_GRADE_CREATE_MESSAGE = "Grade was added successfully."
SUCCESS_IN_BULK_GRADES_CREATE_MESSAGE = "Grades were added successfully."
SUCCESS_GRADE_UPDATE_MESSAGE = "Grade was updated successfully."
SUCCESS_GRADE_DELETE_MESSAGE = "Grade was deleted successfully."


class GradesViewMixin:
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
    PermissionRequiredMixin, SuccessMessageMixin, GradesViewMixin, CreateView
):
    model = Grade
    form_class = GradeForm
    permission_required = "grades.add_grade"
    success_message = SUCCESS_GRADE_CREATE_MESSAGE

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


class ClassGradesView(PermissionRequiredMixin, GradesViewMixin, TemplateView):
    permission_required = "grades.view_grade"
    template_name = "grades/class_grades.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "categories": GradeCategory.objects.filter(
                    subject=self.subject, school_class=self.school_class
                ),
                "students": User.objects.with_nested_student_resources().filter(
                    school_class=self.school_class
                ),
            }
        )

        return context


@login_required
@permission_required("grades.add_grade", raise_exception=True)
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

                messages.success(request, SUCCESS_IN_BULK_GRADES_CREATE_MESSAGE)
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


class GradeUpdateView(
    PermissionRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView
):
    model = Grade
    fields = ["grade", "weight", "comment"]
    template_name = "grades/grade_update.html"
    context_object_name = "grade"
    permission_required = "grades.change_grade"
    success_message = SUCCESS_GRADE_UPDATE_MESSAGE

    def test_func(self):
        return self.get_object().teacher == self.request.user

    def get_success_url(self):
        grade = self.get_object()
        return reverse(
            "grades:class_grades",
            args=[grade.student.school_class.slug, grade.subject.slug],
        )

    def get_queryset(self):
        return super().get_queryset().with_nested_resources()


class GradeDeleteView(PermissionRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Grade
    context_object_name = "grade"
    permission_required = "grades.delete_grade"
    success_message = SUCCESS_GRADE_DELETE_MESSAGE

    def test_func(self):
        return self.get_object().teacher == self.request.user

    def delete(self, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(*args, **kwargs)

    def get_success_url(self):
        grade = self.get_object()
        return reverse(
            "grades:class_grades",
            args=[grade.student.school_class.slug, grade.subject.slug],
        )

    def get_queryset(self):
        return super().get_queryset().with_nested_resources()
