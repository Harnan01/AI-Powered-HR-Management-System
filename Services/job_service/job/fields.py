# fields.py
from rest_framework import serializers
from bson import ObjectId


class ObjectIdField(serializers.Field):
    def to_representation(self, value):
        return str(value)

    def to_internal_value(self, data):
        if ObjectId.is_valid(data):
            return ObjectId(data)
        raise serializers.ValidationError("Invalid ObjectId")
