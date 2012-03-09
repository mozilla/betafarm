import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, UpdateView, View
from django.views.generic.edit import BaseCreateView

import jingo

from tower import ugettext as _

from projects.forms import ProjectForm, LinkForm
from projects.models import Project, Link


def all(request):
    """Display a list of all projects."""
    projects = Project.objects.order_by('name')
    return jingo.render(request, 'projects/all.html', {
        'projects': projects,
        'view': 'all'
    })


def show(request, slug):
    """Display information about a single project, specified by ``slug``."""
    project = get_object_or_404(Project, slug=slug)
    is_owner = False
    if request.user.is_authenticated():
        is_owner = request.user.get_profile().owns_project(project)
    topic = request.session.get('topic', None) or project.topics.all()[0].name
    navlinks = [(project.get_absolute_url(), _(u'Info'), True)]
    if is_owner:
        navlinks.append((project.get_edit_url(), _(u'Edit'), False))
    proj_people = list(project.owners.all())
    proj_people += list(project.team_members.all())
    return jingo.render(request, 'projects/show.html', {
        'project': project,
        'topic': topic,
        'user_is_owner': is_owner,
        'navlinks': navlinks,
        'proj_people': proj_people,
    })


@login_required
@require_POST
def follow(request, slug):
    """
    Add the currently logged in user as a follower of the project specified
    by ``slug``.
    """
    project = get_object_or_404(Project, slug=slug)
    project.followers.add(request.user.get_profile())
    project.save()
    msg = _('Updates from <em>%s</em> will now appear in your dashboard.' % (
        project.name,))
    messages.success(request, msg)
    return redirect(project)


@login_required
@require_POST
def unfollow(request, slug):
    """
    Remove the currently logged in user from the list of followers for
    the project specified by ``slug``.
    """
    project = get_object_or_404(Project, slug=slug)
    project.followers.remove(request.user.get_profile())
    project.save()
    msg = _('''Updates from <em>%s</em> will no longer appear in your
               dashboard''' % (project.name,))
    messages.success(request, msg)
    return redirect(project)


def recent(request):
    """Display a list of the most recent projects."""
    projects = Project.objects.order_by('-id')
    return jingo.render(request, 'projects/all.html', {
        'projects': projects,
        'view': 'recent'
    })


class EditProjectView(UpdateView):
    template_name = 'projects/edit.html'
    model = Project
    form_class = ProjectForm
    slug_field = 'slug'
    context_object_name = 'project'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        # annoying, but have to do all this to be able to use get_object early
        self.request = request
        self.args = args
        self.kwargs = kwargs
        proj = self.get_object()
        if not request.user.get_profile().owns_project(proj):
            return redirect(proj)
        return super(EditProjectView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super(EditProjectView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super(EditProjectView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['navlinks'] = [
            (self.object.get_absolute_url(), _(u'Info'), False),
            (self.object.get_edit_url(), _(u'Edit'), True)]
        return super(EditProjectView, self).get_context_data(**kwargs)

    def get_success_url(self):
        return self.object.get_absolute_url()


class DeleteProjectLinkView(View):
    @method_decorator(login_required)
    def post(self, request, pk):
        link = get_object_or_404(Link, pk=pk)
        if not request.user.get_profile().owns_project(link.project):
            return HttpResponseForbidden()
        link.delete()
        if request.is_ajax():
            return HttpResponse(status=204)
        return redirect('projects_show', slug=link.project.slug)


class ListProjectLinksView(DetailView):
    template_name = 'projects/links.html'
    context_object_name = 'project'
    model = Project
    slug_field = 'slug'

    @method_decorator(login_required)
    def get(self, request, **kwargs):
        if not request.is_ajax():
            return HttpResponseForbidden()
        return super(ListProjectLinksView, self).get(request, **kwargs)


class AddProjectLinkView(BaseCreateView):
    model = Link
    form_class = LinkForm
    # remove 'get' to force view to return 405 for GET requests
    http_method_names = ['post', 'put', 'delete', 'head', 'options', 'trace']

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, slug=kwargs['slug'])
        # only accept ajax requests from owners
        if not (request.is_ajax() and
                request.user.get_profile().owns_project(self.project)):
            return HttpResponseForbidden()
        return super(AddProjectLinkView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        link = form.save(commit=False)
        link.project = self.project
        link.save()
        return HttpResponse(status=204)

    def form_invalid(self, form):
        return HttpResponse(json.dumps(form.errors), status=400)
