# Utility code


class VZInfoParser(object):
    command = "vzlist -a -H -o veid,status"

    # we want to auto-monitor the device if onboot is set, unless the user chooses not to....
    @classmethod
    def parse(cls, lines):
        vzinfo = {}
        for line in lines:
            ls = line.split()
            if len(ls) == 2:
                vzinfo[ls[0]] = ls[1]
        return vzinfo


class VEStatParser(object):
    command = "cat /proc/vestat"

    @classmethod
    def parse(cls, lines):
        cols = lines[1].split()
        if cols[0] != "VEID":
            return [], {}
        vestat = {}
        pos = 2
        while pos < len(lines):
            lsplit = lines[pos].split()
            if len(lsplit) != len(cols):
                continue
            vestat[lsplit[0]] = lsplit[1:]
            pos += 1
        return cols[1:], vestat
