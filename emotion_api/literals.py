
class EmotionLabels:
    ANGRY = "angry"
    SAD = "sad"
    HAPPY = "happy"
    DISGUST = "disgust"
    FEAR = "fear"
    NEUTRAL = "neutral"
    SURPRISE = "surprise"

class Errors:
    MISSING_FILE = 'Upload a .wav file using "file" field'
    INVALID_FILE_TYPE = 'Please ensure to upload only .wav files'
    FILE_TOO_LARGE = 'File size exceeds limit (10MB)'
    SOMETHING_WENT_WRONG = "Something went wrong"

class ServiceDescriptors:
    API = "api"
    PREPROCESS = "preprocess"
    FEATURE = "feature"
    PREDICTION = "prediction"
    COMPUTE = "compute"

    DB = "db"
    CACHE = "cache"

    EXTERNAL_API = "external_api"

class OperationDescriptors:

    REQUEST_PARSE = "request parsing"
    FILE_UPLOAD = "file upload handling"
    RESPONSE_SERIALIZE = "response serialization"

    AUDIO_LOAD = "audio loading"
    AUDIO_RESAMPLE = "audio resampling"
    AUDIO_TRIM = "silence trimming"
    AUDIO_NORMALIZE = "rms normalization"

    MFCC_EXTRACTION = "mfcc extraction"
    FEATURE_SCALING = "feature scaling"

    MODEL_LOAD = "model loading"
    MODEL_INFERENCE = "model inference"

    DATA_TRANSFORM = "data transformation"
    NUMPY_COMPUTE = "numerical compute"

    DB_QUERY = "database query"
    DB_INSERT = "database insert"

    CACHE_LOOKUP = "cache lookup"
    CACHE_WRITE = "cache write"

    EXTERNAL_REQUEST = "external api request"

    FILE_CLEANUP = "cleanup temp files"