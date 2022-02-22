from collections import defaultdict

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import (CreateView, DeleteView, DetailView,
                                  TemplateView, UpdateView)

from django_school.apps.classes.models import Class
from django_school.apps.common.utils import (
    AjaxRequiredMixin, GetObjectCacheMixin, RolesRequiredMixin,
    SubjectAndSchoolClassRelatedMixin,
    does_the_teacher_teach_the_subject_to_the_class, roles_required)
from django_school.apps.grades.forms import (BulkGradeCreationCommonInfoForm,
                                             BulkGradeCreationFormSet,
                                             GradeCategoryForm, GradeForm)
from django_school.apps.grades.models import Grade, GradeCategory
from django_school.apps.lessons.models import Subject
from django_school.apps.users.models import ROLES

User = get_user_model()


class GradeCreateView(
    LoginRequiredMixin,
    RolesRequiredMixin(ROLES.TEACHER),
    SubjectAndSchoolClassRelatedMixin,
    SuccessMessageMixin,
    CreateView,
):
    model = Grade
    form_class = GradeForm
    template_name = "grades/grade_form.html"
    success_message = "The grade has been added successfully."

    def get_initial(self):
        return {
            "student": self.request.GET.get("student"),
        }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                "school_class": self.school_class,
                "subject": self.subject,
                "teacher": self.request.user,
            }
        )
        return kwargs

    def get_success_url(self):
        return reverse(
            "grades:class_grades",
            args=[self.kwargs["class_slug"], self.kwargs["subject_slug"]],
        )


@login_required
@roles_required(ROLES.TEACHER)
def create_grades_in_bulk_view(request, category_pk):
    category = get_object_or_404(
        GradeCategory.objects.select_related("subject", "school_class"), pk=category_pk
    )
    school_class = category.school_class
    subject = category.subject

    students = User.students.exclude_if_has_grade_in_category(category).filter(
        school_class=school_class
    )

    if not students:
        raise Http404

    if not does_the_teacher_teach_the_subject_to_the_class(
        request.user, subject, school_class
    ):
        raise Http404

    common_form = BulkGradeCreationCommonInfoForm(
        request.POST or None,
    )
    grades_formset = BulkGradeCreationFormSet(
        request.POST or None,
        students=students,
    )

    if request.method == "POST":
        if common_form.is_valid():
            common_data = common_form.cleaned_data
            common_data.update(
                {
                    "subject": subject,
                    "teacher": request.user,
                    "category": category,
                }
            )
            grades_formset.set_common_data(common_data=common_data)
            if grades_formset.is_valid():
                grades_formset.save()

                messages.success(request, "The grades have been added successfully.")
                return redirect(
                    reverse(
                        "grades:class_grades", args=[school_class.slug, subject.slug]
                    )
                )

    return render(
        request,
        "grades/create_grades_in_bulk.html",
        {
            "common_form": common_form,
            "grades_formset": grades_formset,
            "school_class": school_class,
            "subject": subject,
            "category": category,
        },
    )


class ClassGradesView(
    LoginRequiredMixin,
    RolesRequiredMixin(ROLES.TEACHER),
    SubjectAndSchoolClassRelatedMixin,
    TemplateView,
):
    template_name = "grades/class_grades.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "categories": GradeCategory.objects.filter(
                    subject=self.subject, school_class=self.school_class
                ).prefetch_related("grades"),
                "students": User.students.with_weighted_avg_for_subject(
                    subject=self.subject
                )
                .with_subject_grades(subject=self.subject)
                .filter(school_class=self.school_class),
            }
        )

        return context


class StudentGradesView(LoginRequiredMixin, GetObjectCacheMixin, DetailView):
    model = User
    slug_url_kwarg = "student_slug"
    template_name = "grades/student_grades.html"
    context_object_name = "student"

    def get(self, *args, **kwargs):
        # in template unseen grades are rendered in a different way
        result = super().get(*args, **kwargs)

        if self.request.user.is_parent:
            Grade.objects.filter(student__parent=self.request.user).update(
                seen_by_parent=True
            )
        elif self.request.user.is_student:
            Grade.objects.filter(student=self.request.user).update(seen_by_student=True)

        return result

    def get_queryset(self):
        return User.students.visible_to_user(self.request.user).prefetch_related(
            "grades_gotten__subject", "grades_gotten__category"
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data()
        student = self.get_object()
        grades = student.grades_gotten.all()
        ctx["subjects"] = self._get_list_of_subjects(grades)
        ctx["averages"] = self._get_dict_of_averages(grades)

        return ctx

    @staticmethod
    def _get_list_of_subjects(grades):
        subjects = set()
        for grade in grades:
            subjects.add(grade.subject)

        return list(subjects)

    @staticmethod
    def _get_dict_of_averages(grades):
        averages = defaultdict(int)
        sums_of_weights = defaultdict(int)

        for grade in grades:
            averages[grade.subject.name] += grade.grade * grade.weight
            sums_of_weights[grade.subject.name] += grade.weight

        for key in averages.keys():
            averages[key] /= sums_of_weights[key]

        return dict(averages)


class SingleGradeMixin:
    model = Grade
    pk_url_kwarg = "grade_pk"
    context_object_name = "grade"

    def get_success_url(self):
        return reverse(
            "grades:class_grades",
            args=[self.object.student.school_class.slug, self.object.subject.slug],
        )

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(teacher=self.request.user)
            .select_related("category", "subject", "student__school_class", "teacher")
        )


class GradeUpdateView(
    LoginRequiredMixin,
    RolesRequiredMixin(ROLES.TEACHER),
    SingleGradeMixin,
    SuccessMessageMixin,
    UpdateView,
):
    fields = ["grade", "weight", "comment"]
    template_name = "grades/grade_update.html"
    success_message = "The grade has been updated successfully."


class GradeDeleteView(
    LoginRequiredMixin,
    RolesRequiredMixin(ROLES.TEACHER),
    SingleGradeMixin,
    AjaxRequiredMixin,
    DeleteView,
):
    template_name = "grades/modals/grade_delete.html"
    success_message = "The grade has been deleted successfully."

    def delete(self, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(*args, **kwargs)


@login_required
@roles_required(ROLES.TEACHER)
def grade_categories_view(request, class_slug, subject_slug):
    school_class = get_object_or_404(Class, slug=class_slug)
    subject = get_object_or_404(Subject, slug=subject_slug)

    if not does_the_teacher_teach_the_subject_to_the_class(
        request.user, subject, school_class
    ):
        raise Http404

    if request.method == "POST":
        form = GradeCategoryForm(
            request.POST, subject=subject, school_class=school_class
        )

        if form.is_valid():
            category = form.save()
            return redirect(category.detail_url)
        else:
            return render(
                request, "grades/partials/grade_category_form.html", {"form": form}
            )

    categories = GradeCategory.objects.filter(
        subject=subject, school_class=school_class
    )
    return render(
        request,
        "grades/gradecategory_list.html",
        {
            "categories": categories,
            "school_class": school_class,
            "subject": subject,
        },
    )


class GradeCategoryAccessMixin:
    def get_object(self, queryset=None):
        category = super().get_object(queryset)

        if not does_the_teacher_teach_the_subject_to_the_class(
            self.request.user, category.subject, category.school_class
        ):
            raise Http404

        return category

    def get_queryset(self):
        return super().get_queryset().select_related("school_class", "subject")


class GradeCategoryFormTemplateView(TemplateView):
    template_name = "grades/partials/grade_category_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = GradeCategoryForm(subject=None, school_class=None)

        return context


class GradeCategoryDetailView(
    LoginRequiredMixin,
    RolesRequiredMixin(ROLES.TEACHER),
    GradeCategoryAccessMixin,
    DetailView,
):
    model = GradeCategory
    template_name = "grades/partials/grade_category_detail.html"
    context_object_name = "category"


class GradeCategoryDeleteView(
    LoginRequiredMixin,
    RolesRequiredMixin(ROLES.TEACHER),
    GradeCategoryAccessMixin,
    GetObjectCacheMixin,
    AjaxRequiredMixin,
    DeleteView,
):
    model = GradeCategory
    template_name = "grades/modals/category_delete.html"

    def get_success_url(self):
        category = self.get_object()
        redirect_url = reverse(
            "grades:categories:create",
            args=[category.school_class.slug, category.subject.slug],
        )

        return redirect_url


class GradeCategoryUpdateView(
    LoginRequiredMixin,
    RolesRequiredMixin(ROLES.TEACHER),
    GradeCategoryAccessMixin,
    UpdateView,
):
    model = GradeCategory
    form_class = GradeCategoryForm
    template_name = "grades/partials/grade_category_form.html"
    context_object_name = "category"

    def get_success_url(self):
        return self.object.detail_url

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        category = self.get_object()
        kwargs.update(
            {
                "subject": category.subject,
                "school_class": category.school_class,
            }
        )

        return kwargs
