import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, UpdateView, View
from django.views.generic.edit import BaseCreateView

import jingo
from topics.models import Topic

from tower import ugettext as _

from projects.forms import ProjectForm, LinkForm
from projects.models import Project, Link


def all(request):
    """Display a list of all projects."""
    projects = Project.objects.haz_topic().order_by('name')
    return jingo.render(request, 'projects/all.html', {
        'projects': projects,
        'view': 'all'
    })


def topic(request, slug):
    """Show a specific topic. Should be only for non-js users."""
    topic = get_object_or_404(Topic, slug=slug)
    projects = Project.objects.filter(topics=topic).order_by('name')
    return jingo.render(request, 'projects/all.html', {
        'current_topic': topic,
        'projects': projects
    })


def show(request, slug):
    """Display information about a single project, specified by ``slug``."""
    project = get_object_or_404(Project, slug=slug)
    is_owner = False
    is_follower = False
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        is_owner = profile.owns_project(project)
        is_follower = profile.follows_project(project)
    topic = request.session.get('topic', None) or project.topics.all()[0].name
    proj_people = list(project.owners.all())
    proj_people += list(project.team_members.all())
    return jingo.render(request, 'projects/show.html', {
        'project': project,
        'topic': topic,
        'user_is_owner': is_owner,
        'user_is_follower': is_follower,
        'proj_people': proj_people,
    })


@login_required
@require_POST
def follow(request, slug):
    """
    Add the currently logged in user as a follower of the project specified
    by ``slug``.
    """
    profile = request.user.get_profile()
    project = get_object_or_404(Project, slug=slug)
    project.followers.add(profile)
    cache.delete_many([project.cache_key, profile.cache_key])
    cxt = {'project_name': project.name}
    msg = _('You are now following <em>%(project_name)s</em>.') % cxt
    messages.success(request, msg)
    return redirect(project)


@login_required
@require_POST
def unfollow(request, slug):
    """
    Remove the currently logged in user from the list of followers for
    the project specified by ``slug``.
    """
    profile = request.user.get_profile()
    project = get_object_or_404(Project, slug=slug)
    project.followers.remove(profile)
    cache.delete_many([project.cache_key, profile.cache_key])
    cxt = {'project_name': project.name}
    msg = _('You are no longer following <em>%(project_name)s</em>.') % cxt
    messages.success(request, msg)
    return redirect(project)


def recent(request):
    """Display a list of the most recent projects."""
    projects = Project.objects.haz_topic().order_by('-id')
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
