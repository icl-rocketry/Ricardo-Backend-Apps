import struct
import json


class JsonRnpPacketParser():
    type_format_map = {
        "char":"c",
        "int8_t":"b",
        "uint8_t":"B",
        "bool":"?",
        "int16_t":'h',
        "uint16_t":"H",
        "int":"i",
        "int32_t":"i",
        "uint32_t":"I",
        "int64_t":"q",
        "uint64_t":"Q",
        "float":"f",
        "double":"d"      
    }

    def __init__(self,json_packet_structure):
        if isinstance(json_packet_structure,dict):
            self.packet_structure = json_packet_structure
        else:
            self.packet_structure = json.loads(json_packet_structure)
        self.struct_str = self.__parse_types__()
        self.size = struct.calcsize(self.struct_str)
        self.var_dict = dict.fromkeys(self.packet_structure,0)
       


    def __parse_types__(self):
        try:
            format_character_structure = [JsonRnpPacketParser.type_format_map[key] for key in self.packet_structure.values()]
        except KeyError as e:
            print("Invalid Type Provided!")
            raise e
        return "<" + "".join(format_character_structure) 
        
