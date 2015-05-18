from django.core.management.base import BaseCommand, CommandError

from traq.projects.models import Project

class Command(BaseCommand):
    help = "Generates json for data associated with a project \
            formatted for migration into jira"

    def handle(self, project=None, **options):
        try:
            project = Project.objects.get(pk=project)
        except:
            raise
        self.project_dictionary = {}
        self.generate_project_json(project)
        self.stdout.write("exported json for %s" % project)

    def generate_project_json(self, project):
        tickets = self.get_ticket_data(project.ticket_set.filter(is_deleted=False))
        todos = self.get_todos_data(project.todo_set.filter(is_deleted=False))
        self.projects = self.get_project_data(project)
        self.projects["issues"] = tickets
        self.project_dictionary["projects"] = []
        self.project_dictionary["projects"].append(self.projects)
        print(self.project_dictionary)

    def get_project_data(self, project):
        projects = {}
        projects["key"] = self.make_key(project)
        projects["name"] = project.name
        return projects

    def get_ticket_data(self, tickets):
        ticket_list = []
        for t in tickets:
            ticket = {}
            ticket["key"] = t.pk
            ticket["description"] = t.title
            ticket_list.append(ticket)
        return ticket_list

    def get_todos_data(self, todos):
        return todos

    def make_key(self, project):
        key = ''.join(map(lambda word:word[:1], project.name.split()))
        if len(key) < 3:
            print(key)
            key = ''.join([key, project.name.split()[1][1]])
            print(key)
        key = "%s-%s" % (key, project.pk)
        return key
