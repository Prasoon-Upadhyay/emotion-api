from rest_framework import serializers
from emotion_api.literals import Errors


class EmotionPredictSerializer(serializers.Serializer):

    file = serializers.FileField()

    def validate_file(self, value):

        if not value.name.endswith(".wav"):
            raise serializers.ValidationError(
                Errors.INVALID_FILE_TYPE
            )

        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError(
                Errors.FILE_TOO_LARGE
            )

        return value