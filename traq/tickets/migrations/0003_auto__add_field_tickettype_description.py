# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'TicketType.description'
        db.add_column(u'tickets_tickettype', 'description',
                      self.gf('django.db.models.fields.CharField')(default=None, max_length=255, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'TicketType.description'
        db.delete_column(u'tickets_tickettype', 'description')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'projects.component': {
            'Meta': {'ordering': "['rank']", 'object_name': 'Component', 'db_table': "'component'"},
            'component_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'invoice_description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Project']"}),
            'rank': ('django.db.models.fields.IntegerField', [], {})
        },
        u'projects.milestone': {
            'Meta': {'ordering': "['due_on']", 'object_name': 'Milestone', 'db_table': "'milestone'"},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'due_on': ('django.db.models.fields.DateTimeField', [], {}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'milestone_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Project']"})
        },
        u'projects.project': {
            'Meta': {'ordering': "['name']", 'object_name': 'Project', 'db_table': "'project'"},
            'catch_all': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'clients': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'current_sprint_end': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'estimated_hours': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'invoice_description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_scrum': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pm': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'blank': 'True', 'to': u"orm['auth.User']"}),
            'pm_email': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'point_of_contact': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'project_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'team_dynamix_id': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'technical': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'})
        },
        u'tickets.comment': {
            'Meta': {'ordering': "['created_on']", 'object_name': 'Comment', 'db_table': "'comment'"},
            'body': ('django.db.models.fields.TextField', [], {}),
            'comment_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'edited_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tickets.Ticket']", 'null': 'True'}),
            'todo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['todos.ToDo']", 'null': 'True'})
        },
        u'tickets.ticket': {
            'Meta': {'object_name': 'Ticket', 'db_table': "'ticket'"},
            'assigned_to': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'+'", 'null': 'True', 'blank': 'True', 'to': u"orm['auth.User']"}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'branch': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'component': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Component']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'due_on': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'edited_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'estimated_time': ('django.db.models.fields.TimeField', [], {'default': 'None', 'null': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_extra': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_internal': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'milestone': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['projects.Milestone']", 'null': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tickets.TicketPriority']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Project']"}),
            'release': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'started_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 6, 19, 0, 0)'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tickets.TicketStatus']"}),
            'ticket_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tickets.TicketType']", 'null': 'True'})
        },
        u'tickets.ticketfile': {
            'Meta': {'ordering': "['file']", 'object_name': 'TicketFile', 'db_table': "'ticket_file'"},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'file_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tickets.Ticket']"}),
            'todo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['todos.ToDo']"}),
            'uploaded_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"}),
            'uploaded_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'tickets.ticketpriority': {
            'Meta': {'ordering': "['rank']", 'object_name': 'TicketPriority', 'db_table': "'ticket_priority'"},
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'rank': ('django.db.models.fields.IntegerField', [], {}),
            'ticket_priority_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'tickets.ticketstatus': {
            'Meta': {'ordering': "['rank']", 'object_name': 'TicketStatus', 'db_table': "'ticket_status'"},
            'importance': ('django.db.models.fields.IntegerField', [], {}),
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'rank': ('django.db.models.fields.IntegerField', [], {}),
            'ticket_status_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'tickets.tickettype': {
            'Meta': {'object_name': 'TicketType'},
            'description': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ticket_type_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'tickets.work': {
            'Meta': {'ordering': "['-created_on']", 'object_name': 'Work', 'db_table': "'work'"},
            'billable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'done_on': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'started_on': ('django.db.models.fields.DateTimeField', [], {}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'state_changed_on': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tickets.Ticket']"}),
            'time': ('django.db.models.fields.TimeField', [], {}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tickets.WorkType']"}),
            'work_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'tickets.worktype': {
            'Meta': {'ordering': "['rank']", 'object_name': 'WorkType', 'db_table': "'work_type'"},
            'is_default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'rank': ('django.db.models.fields.IntegerField', [], {}),
            'work_type_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'todos.todo': {
            'Meta': {'object_name': 'ToDo'},
            'ToDo_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'component': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Component']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'due_on': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'edited_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'estimate': ('django.db.models.fields.DecimalField', [], {'default': 'None', 'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'priority': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tickets.TicketPriority']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Project']"}),
            'rank': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'started_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 6, 19, 0, 0)'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tickets.TicketStatus']"}),
            'tickets': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'todos'", 'symmetrical': 'False', 'to': u"orm['tickets.Ticket']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['tickets']