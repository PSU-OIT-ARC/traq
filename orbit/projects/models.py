from django.db import models


class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)

# Instead of creating a whole bunch of models/tables called ProjectStatus,
# TicketStatus, TicketPriority, ComponentType, etc, I create two tables
# AttributeType, and Attribute. AttributeType is just like an enum mapping
# arbitrary ids to type names (like 1: "project_status", 2: "ticket_status", etc).
# Attribute references AttributeType, and contains all the possible values for
# each attribute type (so the attribute type "ticket_status" would contain a
# bunch of rows like "started", "working on", "completed")

# enums for the AttributeType table
class AttributeTypeName:
    TICKET_STATUS = "ticket_status"
    TICKET_PRIORITY = "ticket_priority"
    WORK_TYPE = "work_type"

# The Attribute model has a custom manager that has some helper methods
class AttributeManager(models.Manager):
    # Returns a list of tuples for the attribute of type_name
    # Useful when setting the choices parameter on model fields
    def ofType(self, type_name):
        return Attribute.objects.filter(type__name=type_name).order_by("rank")

class AttributeType(models.Model):
    attribute_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

class Attribute(models.Model):
    attribute_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    rank = models.IntegerField()

    type = models.ForeignKey(AttributeType)

    def __unicode__(self):
        return u'%s' % (self.name)

    objects = AttributeManager()

