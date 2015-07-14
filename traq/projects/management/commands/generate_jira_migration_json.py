import string, re, json
import markdown

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.utils.safestring import mark_safe

from traq.projects.models import Project
from traq.tickets.models import TicketFile


class Command(BaseCommand):
    args = '<project_id>'
    help = "Generates json for data associated with a project \
            formatted for migration into jira"

    option_list = BaseCommand.option_list + (
        make_option('--agile',
        action='store_true',
        dest='agile',
        default=False,
        help='Migrates todos as Jira Story and tickets as sub-tasks'),
    )

    def handle(self, project=None, **options):
        try:
            project = Project.objects.get(pk=project)
        except ObjectDoesNotExist as e:
            raise e
        self.agile = options['agile']
        self.links = []
        self.stdout.write(self.generate_project_json(project))

    def generate_project_json(self, project):
        self.project_data = self.get_project_base_data(project)

        tickets = self.get_issue_data(project.ticket_set.filter(is_deleted=False))
        self.project_data["issues"] = tickets

        if self.agile:
            todos = self.get_issue_data(project.todo_set.filter(is_deleted=False),
                                todo=True)
            self.project_data["issues"] = tickets + todos

        # a little json massaging as jira wants it.
        top_level_dictionary = {}
        top_level_dictionary["links"] = self.links
        top_level_dictionary["projects"] = []
        top_level_dictionary["projects"].append(self.project_data)
        return json.dumps(top_level_dictionary)

    def get_project_base_data(self, project):
        project_data = {}
        project_data["key"] = self.make_key(project)
        project_data["name"] = project.name
        project_data["description"] = project.description
        project_data["components"] = list(project.component_set.all().values_list('name', flat=True))
        return project_data

    def get_issue_data(self, tickets, todo=False):
        ticket_list = []
        for t in tickets:
            ticket = {}
            ticket["summary"] = t.title
            #convert markdown to html body
            ticket["description"] = mark_safe(markdown.markdown(t.body, safe_mode='escape', extensions=['nl2br']))
            try:
                ticket["duedate"] = t.due_on.strftime("%Y-%m-%dT%H:%M:%S+00:00")
            except:
                pass
            ticket["comments"] = self.get_comments(t)
            status = t.status.name
            if status == "Completed":
               status = "Resolved"
            if status == "Stalled":
               status = "In Progess" #sorry. You'll  have to take care of these later.
            ticket["status"] = status
            ticket["components"] = []
            ticket["components"].append(t.component.name)
            ticket["created"] = t.created_on.strftime("%Y-%m-%dT%H:%M:%S+00:00") #a la SimpleDateFromat
            try:
                assignee = t.assigned_to.username
                ticket["assignee"] = assignee
            except:
                pass
            try:
                ticket["duedate"] = t.due_on.strftime("%Y-%m-%dT%H:%M:%S+00:00")
            except:
                pass

            if self.agile:
                if todo:
                    ticket["issueType"] = "Story"
                    ticket["attachments"] = self.get_attachments(t, True)
                    ticket["externalId"] = t.pk + 10000
                else:
                    ticket["externalId"] = t.pk
                    ticket["issueType"] = "sub-task"
                    ticket["attachments"] = self.get_attachments(t)
                    #and create a link between ticket and todo
                    link = self.create_sub_task_link(t)
                    if link is not None:
                        self.links.append(self.create_sub_task_link(t))
            else:
                ticket["issueType"] = "Task"

            ticket_list.append(ticket)
        return ticket_list

    def get_comments(self, ticket):
        comments = list(ticket.comment_set.all().values("body",
                    "created_by__username", "created_on")) or ""
        #clean it up for jira
        for obj in comments:
            obj["author"] = obj.pop("created_by__username")
            obj["created"] = obj.pop("created_on")
            obj["created"] = obj["created"].strftime("%Y-%m-%dT%H:%M:%S+00:00")
        if comments:
            return comments
        else:
            return []

    def create_sub_task_link(self, ticket):
        try:
            todo_id = ticket.todos.all()[0].pk
            link = {}
            link['name'] = "sub-task-link"
            link['sourceId'] = ticket.pk
            link['destinationId'] = 10000 + todo_id  #shift this so it doesn't collide with a ticket_id
            return link
        except:
            return None

    def get_attachments(self, t, todo=False):
        attachments = []
        model = 'todo' if todo else 'ticket'
        files = TicketFile.objects.filter(**{model: t.pk})
        for f in files:
            attachment = {}
            attachment['name'] = f.file.name
            attachment['uri'] = settings.BASE_URL + settings.MEDIA_URL + f.file.name
            attachments.append(attachment)
        return attachments


    def make_key(self, project):
        key=''
        regex = re.compile("[0-9%s]" % re.escape(string.punctuation))
        clean_name = regex.sub('', project.name)
        words = clean_name.split()
        if len(words) == 1:
            key = clean_name[:4]
        elif len(words) == 2:
            key = "".join([words[0][0], words[1][:2]])
        else:
            i = 0
            while len(key) < 3:
                key = key + ''.join(map(lambda word:word[i], words))
                i = i+1
            key = "%s" % (key.upper())
        return key
