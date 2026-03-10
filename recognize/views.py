import os
import numpy as np
import librosa
import soundfile as sf
import traceback

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from django.core.files.storage import default_storage

from .serializers import EmotionPredictSerializer

from emotion_api.middleware.server_timings import timed
from emotion_api.literals import EmotionLabels, Errors, ServiceDescriptors, OperationDescriptors

model = None
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.h5")


class EmotionPredictAPIView(APIView):

    parser_classes = [MultiPartParser, FormParser]

    emotion_labels = [
        EmotionLabels.ANGRY,
        EmotionLabels.DISGUST,
        EmotionLabels.FEAR,
        EmotionLabels.HAPPY,
        EmotionLabels.NEUTRAL,
        EmotionLabels.SURPRISE,
        EmotionLabels.SAD
    ]

    def get_model(self):
        """Load the Keras model on first request."""
        global model

        if model is None:
            from tensorflow.keras.models import load_model

            with timed(
                ServiceDescriptors.COMPUTE,
                OperationDescriptors.MODEL_LOAD
            ):
                model = load_model(MODEL_PATH)

        return model

    def extract_features(self, file_path):
        """Extract MFCC features."""

        with timed(
            ServiceDescriptors.PREPROCESS,
            OperationDescriptors.AUDIO_LOAD
        ):
            y, sr = sf.read(file_path, dtype="float32")

        if len(y.shape) > 1:
            y = y.mean(axis=1)

        with timed(
            ServiceDescriptors.PREPROCESS,
            OperationDescriptors.AUDIO_TRIM
        ):
            y = y[: int(sr * 3)]

        with timed(
            ServiceDescriptors.FEATURE,
            OperationDescriptors.MFCC_EXTRACTION
        ):
            mfcc = np.mean(
                librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40).T,
                axis=0
            )

        with timed(
            ServiceDescriptors.COMPUTE,
            OperationDescriptors.DATA_TRANSFORM
        ):
            mfcc = np.expand_dims(mfcc, axis=-1)

        return mfcc

    def post(self, request):

        with timed(
            ServiceDescriptors.API,
            OperationDescriptors.REQUEST_PARSE
        ):
            serializer = EmotionPredictSerializer(data=request.data)

            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            audio_file = serializer.validated_data["file"]

        with timed(
            ServiceDescriptors.API,
            OperationDescriptors.FILE_UPLOAD
        ):
            saved_name = default_storage.save("temp.wav", audio_file)
            file_path = default_storage.path(saved_name)

        try:

            features = self.extract_features(file_path)

            with timed(
                ServiceDescriptors.COMPUTE,
                OperationDescriptors.DATA_TRANSFORM
            ):
                features = np.expand_dims(features, axis=0)

            model_instance = self.get_model()

            with timed(
                ServiceDescriptors.PREDICTION,
                OperationDescriptors.MODEL_INFERENCE
            ):
                prediction = model_instance.predict(features, verbose=0)

            with timed(
                ServiceDescriptors.COMPUTE,
                OperationDescriptors.DATA_TRANSFORM
            ):
                predicted_emotion = self.emotion_labels[np.argmax(prediction)]

            return Response(
                {"emotion": predicted_emotion},
                status=status.HTTP_200_OK
            )

        except Exception as e:

            traceback.print_exc()

            return Response(
                {"error": str(e) or Errors.SOMETHING_WENT_WRONG},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        finally:

            with timed(
                ServiceDescriptors.API,
                OperationDescriptors.FILE_CLEANUP
            ):
                if os.path.exists(file_path):
                    os.remove(file_path)


predict_emotion = EmotionPredictAPIView.as_view()