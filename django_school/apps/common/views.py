import os

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from django_school.apps.common.models import AttachedFile
from django_school.apps.common.utils import ajax_required, roles_required
from django_school.apps.users.models import ROLES


@login_required
@roles_required(ROLES.TEACHER)
@ajax_required
def attached_file_delete_view(request, pk):
    attached_file = get_object_or_404(AttachedFile, pk=pk)

    if attached_file.creator_id != request.user.pk:
        raise PermissionDenied

    if request.method == "POST":
        path = attached_file.file.path
        attached_file.delete()
        os.remove(path)

    return HttpResponse()
