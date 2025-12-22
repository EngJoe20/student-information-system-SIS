"""
Serializers for notifications, messages, and student requests.
"""
from rest_framework import serializers
from notifications.models import Notification, Message, StudentRequest
from accounts.serializers import UserSerializer


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""
    
    related_object = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message',
            'is_read', 'priority', 'related_object', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_related_object(self, obj):
        """Get related object information."""
        if obj.related_object_type and obj.related_object_id:
            return {
                'type': obj.related_object_type,
                'id': str(obj.related_object_id)
            }
        return None


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications."""
    
    class Meta:
        model = Notification
        fields = [
            'recipient', 'notification_type', 'title', 'message',
            'priority', 'related_object_type', 'related_object_id'
        ]


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model."""
    
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    recipient_name = serializers.CharField(source='recipient.full_name', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'sender_name', 'recipient', 'recipient_name',
            'subject', 'body', 'is_read', 'parent_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'sender', 'created_at', 'updated_at']


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating messages."""
    
    recipient_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Message
        fields = ['recipient_id', 'subject', 'body', 'parent_message']
    
    def validate_recipient_id(self, value):
        """Validate recipient exists."""
        from accounts.models import User
        if not User.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Recipient not found")
        return value
    
    def create(self, validated_data):
        """Create message with sender from context."""
        from accounts.models import User
        recipient_id = validated_data.pop('recipient_id')
        recipient = User.objects.get(id=recipient_id)
        
        message = Message.objects.create(
            sender=self.context['request'].user,
            recipient=recipient,
            **validated_data
        )
        return message


class MessageDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Message with replies."""
    
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    parent_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'recipient', 'subject', 'body',
            'is_read', 'parent_message', 'replies',
            'created_at', 'updated_at'
        ]
    
    def get_replies(self, obj):
        """Get message replies."""
        replies = obj.replies.all()
        return [{
            'id': str(reply.id),
            'sender_name': reply.sender.full_name,
            'body': reply.body,
            'created_at': reply.created_at
        } for reply in replies]
    
    def get_parent_message(self, obj):
        """Get parent message info if exists."""
        if obj.parent_message:
            return {
                'id': str(obj.parent_message.id),
                'subject': obj.parent_message.subject,
                'created_at': obj.parent_message.created_at
            }
        return None


class StudentRequestSerializer(serializers.ModelSerializer):
    """Serializer for StudentRequest model."""
    
    student_info = serializers.SerializerMethodField()
    processed_by_info = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentRequest
        fields = [
            'id', 'student_info', 'request_type', 'subject',
            'description', 'status', 'processed_by_info',
            'response', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_student_info(self, obj):
        """Get student information."""
        return {
            'id': str(obj.student.id),
            'student_id': obj.student.student_id,
            'name': obj.student.user.full_name
        }
    
    def get_processed_by_info(self, obj):
        """Get processor information."""
        if obj.processed_by:
            return {
                'id': str(obj.processed_by.id),
                'name': obj.processed_by.full_name
            }
        return None


class StudentRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating student requests."""
    
    class Meta:
        model = StudentRequest
        fields = ['request_type', 'subject', 'description']
    
    def create(self, validated_data):
        """Create request with student from context."""
        student = self.context['request'].user.student_profile
        return StudentRequest.objects.create(
            student=student,
            **validated_data
        )


class StudentRequestUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating student requests."""
    
    class Meta:
        model = StudentRequest
        fields = ['status', 'response']
    
    def update(self, instance, validated_data):
        """Update request with processor."""
        instance.processed_by = self.context['request'].user
        instance.status = validated_data.get('status', instance.status)
        instance.response = validated_data.get('response', instance.response)
        instance.save()
        return instance


class TranscriptRequestSerializer(serializers.Serializer):
    """Serializer for transcript generation request."""
    
    student_id = serializers.UUIDField()
    format = serializers.ChoiceField(choices=['pdf', 'json'], default='pdf')
    
    def validate_student_id(self, value):
        """Validate student exists."""
        from students.models import Student
        if not Student.objects.filter(id=value).exists():
            raise serializers.ValidationError("Student not found")
        return value


class ReportGenerationSerializer(serializers.Serializer):
    """Serializer for report generation requests."""
    
    report_type = serializers.ChoiceField(
        choices=['attendance', 'grades', 'enrollment']
    )
    format = serializers.ChoiceField(
        choices=['pdf', 'json', 'csv'],
        default='pdf'
    )
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    class_id = serializers.UUIDField(required=False)
    student_id = serializers.UUIDField(required=False)
    semester = serializers.CharField(required=False)
    academic_year = serializers.IntegerField(required=False)