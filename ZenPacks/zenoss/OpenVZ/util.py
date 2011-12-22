# Utility code

class VZInfoParser(object):
    
    command="vzlist -a -H -o veid,status"

    # we want to auto-monitor the device if onboot is set, unless the user chooses not to....
    @classmethod
    def parse(cls,lines):
        vzinfo = {}
        for line in lines:
            ls = line.split()
            if len(ls) == 2:
                vzinfo[ls[0]] = ls[1]
        return vzinfo       
