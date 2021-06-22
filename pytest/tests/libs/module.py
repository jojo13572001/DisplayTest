
class Module:

    @staticmethod
    def check_h264_codec_type(codec):
    	if codec == "RTCCodec_0_Inbound_96" or \
           codec == "RTCCodec_0_Inbound_108":
           return True