from pylibrnp.rnppacket import RnpPacket
from pylibrnp.json_rnp_packet_parser import JsonRnpPacketParser

class DynamicRnpPacketGenerator():
    def __init__(self,classname,json_packet_structure,packet_type = 0): 
        self.classname = classname
        self.parsed_json_packet = JsonRnpPacketParser(json_packet_structure)
        self.packet_type = packet_type
        self.new_class = self.__generate__()


    def __generate__(self):
        def packet_init(this):

            for elem in self.parsed_json_packet.var_dict.keys():
                setattr(this,elem,0)

            RnpPacket.__init__(this,
                              list(self.parsed_json_packet.var_dict.keys()),
                              self.parsed_json_packet.struct_str,
                              self.parsed_json_packet.size,
                              self.packet_type)

        new_type = type(self.classname,(RnpPacket,),{'__init__':packet_init})
        return new_type

    def getClass(self):
        return self.new_class


