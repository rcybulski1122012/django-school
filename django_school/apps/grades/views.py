from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import (CreateView, DeleteView, DetailView,
                                  TemplateView, UpdateView)

from django_school.apps.classes.models import Class
from django_school.apps.common.utils import (
    IsTeacherMixin, does_the_teacher_teach_the_subject_to_the_class,
    teacher_view)
from django_school.apps.grades.forms import (BulkGradeCreationCommonInfoForm,
                                             BulkGradeCreationFormSet,
                                             GradeCategoryForm, GradeForm)
from django_school.apps.grades.models import Grade, GradeCategory
from django_school.apps.lessons.models import Subject

User = get_user_model()


class SubjectAndSchoolClassRelatedMixin:
    school_class = None
    subject = None

    def dispatch(self, request, *args, **kwargs):
        self.school_class = get_object_or_404(Class, slug=self.kwargs["class_slug"])
        self.subject = get_object_or_404(Subject, slug=self.kwargs["subject_slug"])

        if not does_the_teacher_teach_the_subject_to_the_class(
            self.request.user, self.subject, self.school_class
        ):
            raise Http404

        return super().dispatch(request, *args, **kwargs)

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
    LoginRequiredMixin,
    IsTeacherMixin,
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
@teacher_view
def create_grades_in_bulk_view(request, class_slug, subject_slug):
    school_class = get_object_or_404(Class, slug=class_slug)
    subject = get_object_or_404(Subject, slug=subject_slug)
    students = User.objects.filter(school_class=school_class)
    initial = {"category": request.GET.get("category")}

    if not does_the_teacher_teach_the_subject_to_the_class(
        request.user, subject, school_class
    ):
        raise Http404

    common_form = BulkGradeCreationCommonInfoForm(
        request.POST or None,
        subject=subject,
        school_class=school_class,
        initial=initial,
    )
    grades_formset = BulkGradeCreationFormSet(
        request.POST or None,
        students=students,
    )

    if request.method == "POST":
        if common_form.is_valid():
            common_data = common_form.cleaned_data
            common_data.update({"subject": subject, "teacher": request.user})
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
        },
    )


class ClassGradesView(
    LoginRequiredMixin, IsTeacherMixin, SubjectAndSchoolClassRelatedMixin, TemplateView
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


@login_required
@teacher_view
def grade_categories_view(request, class_slug, subject_slug):
    school_class = get_object_or_404(Class, slug=class_slug)
    subject = get_object_or_404(Subject, slug=subject_slug)

    if not does_the_teacher_teach_the_subject_to_the_class(
        request.user, subject, school_class
    ):
        raise Http404

    if request.method == "POST":
        form = GradeCategoryForm(request.POST)
        form.set_subject_and_class(subject, school_class)

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
        context["form"] = GradeCategoryForm()

        return context


class GradeCategoryDetailView(
    LoginRequiredMixin, IsTeacherMixin, GradeCategoryAccessMixin, DetailView
):
    model = GradeCategory
    template_name = "grades/partials/grade_category_detail.html"
    context_object_name = "category"


@login_required
@require_http_methods(["POST"])
@teacher_view
def grade_category_delete_view(request, pk):
    category = get_object_or_404(
        GradeCategory.objects.select_related("school_class", "subject"), pk=pk
    )

    redirect_url = request.GET.get("redirect_url")  # required

    if (
        not does_the_teacher_teach_the_subject_to_the_class(
            request.user, category.subject, category.school_class
        )
        or redirect_url is None
    ):
        raise Http404

    category.delete()

    return redirect(redirect_url)


class GradeCategoryUpdateView(
    LoginRequiredMixin, IsTeacherMixin, GradeCategoryAccessMixin, UpdateView
):
    model = GradeCategory
    form_class = GradeCategoryForm
    template_name = "grades/partials/grade_category_form.html"
    context_object_name = "category"

    def get_success_url(self):
        return self.object.detail_url
