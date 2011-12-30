###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011, Zenoss Inc.
#
###########################################################################

from Products.ZenRRD.CommandParser import CommandParser
from ZenPacks.zenoss.OpenVZ.util import VZInfoParser

class host_util(CommandParser):

    # This method is imported and run by zencommand and does not have direct
    # access to the model...

    # The processResults() method runs once for every OpenVZ host. It will be passed the full
    # set of datapoints.

    def processResults(self, cmd, result):

        # We will get the output of /proc/user_beancounters, and parse it:

        lines=cmd.result.output.split('\n')
        version=lines[0].split()[1]
        pos = 2
        veid = None
        metrics = {}
        while pos < len(lines):
            sp = lines[pos].split()
            if len(sp) == 7:
                veid = sp[0][:-1]
                if veid == "0":
                    veid = "host"
                else:
                    veid = "containers"
            elif len(sp) == 6 and sp[0] != "dummy":
                # resource held maxheld barrier limit failcnt
                r = sp[0]
                if veid not in metrics:
                    metrics[veid] = {}
                for key, val in (( r , sp[1]),( "%s.failcnt" % r , sp[5])):
                    if key not in metrics[veid]:
                        metrics[veid][key] = 0
                    metrics[veid][key] += int(val)
            pos += 1

        # We now have metrics["0"]["physpages"] and metrics["C"]["physpages"], as well as failcnts.
        # "C" = sum of values from all containers.

        for point in cmd.points:
            idsplit = point.id.split(".")
            if len(idsplit) != 2:
                continue
            # pmetric = something like "physpages"
            # pclass = "containers" or "host"
            pmetric, pclass = idsplit
            if pmetric == "failrate":
                pnt = "failcnt"
            result.values.append((point, metrics[pclass][pmetric]))
        return
