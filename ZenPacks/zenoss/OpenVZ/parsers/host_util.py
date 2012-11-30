###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011, Zenoss Inc.
#
###########################################################################

from Products.ZenRRD.CommandParser import CommandParser
from ZenPacks.zenoss.OpenVZ.util import VZInfoParser

class host_util(CommandParser):

    # dataForParser is run by zenhub and has direct access to model -- stuff in page size and arch:

    def dataForParser(self, context, datapoint):
        return ( context.hw.arch, context.hw.page_size, context.hw.totalMemory, context.os.totalSwap )

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
        metrics = { "containers" : {} }
        while pos < len(lines):
            sp = lines[pos].split()
            if len(sp) == 7:
                veid = sp[0][:-1]
                if veid == "0":
                    veid = "host"
                else:
                    veid = "containers"
                # have kmemsize on this line, still need to parse:
                sp = sp[1:]
            if len(sp) == 6 and sp[0] != "dummy":
                r = sp[0]
                if veid not in metrics:
                    metrics[veid] = {}
                for key, val in (( r , sp[1]),( "%s.failcnt" % r , sp[5])):
                    # we are doing a cumulative total (tally) for all containers, as well as the host (VEID 0)
                    if key not in metrics[veid]:
                        metrics[veid][key] = 0
                    metrics[veid][key] += int(val)
            pos += 1

        # We now have metrics["host"]["physpages"] and metrics["containers"]["physpages"], as well as failcnts:
        # metrics["containers"]["physpages.failcnt"]
        # "C" = sum of values from all containers.

        if len(cmd.points):
            arch, page_size, ram_bytes, swap_bytes = cmd.points[0].data
        
        # precalc:

        # utilization.allocated - privvmpages(cur)
        # commitmentlevel.allocated - vmguarpages(bar)
        # restrictions.allocated - privvmpages(lim) (recommended: 1 or below)
        # utilization.totalram physpages(cur) - can't be more than 1
        # utilization.totalmem - oomguarpages(cur)
        # commitmentlevel.totalmem - oomguarpages(bar) (bad if more than 1)

        ut_a = 0
        ut_rs = 0

        sockbuf = [ "tcprcvbuf", "tcpsndbuf", "dgramrcvbuf", "othersockbuf" ]
        # other stuff we need:
        otherbuf = [ "privvmpages", "oomguarpages", "kmemsize", "physpages" ]

        missing = []
        for key in sockbuf + otherbuf:
            if key not in metrics["containers"]:
                missing.append(key)

        if missing:
                result.events.append(dict(
                    summary="Unable to find metrics for OpenVZ Memory Utilization",
                    message="These metrics were unable to be read from the host device's /proc/user_beancounters file: " + " ".join(missing),
                    severity="4",
                    eventClass="/Config",
                ))
        else:
            asb = 0
            for key in sockbuf:
                asb += metrics["containers"][key] 

            ut_a = ((metrics["containers"]["privvmpages"] * page_size) + metrics["containers"]["kmemsize"] + asb)
            ut_rs = ((metrics["containers"]["oomguarpages"] * page_size) + metrics["containers"]["kmemsize"] + asb)
            ut_r = ((metrics["containers"]["physpages"] * page_size) + metrics["containers"]["kmemsize"] + asb)

            metrics["utilization"] = {}
            metrics["utilization"]["allocated"] = float(ut_a)/(ram_bytes + swap_bytes)
            metrics["utilization"]["ramswap"] = float(ut_rs)/(ram_bytes + swap_bytes)
            metrics["utilization"]["ram"] = float(ut_rs)/(ram_bytes)
    
        # we are looking for datapoints in this format now:
        # [containers|host|utilization].metric[.failcnt|failrate] (note: we are supporting failcnt/failrate only)
        #
        # For "utilization", we support "allocated" and "ramswap" as metrics.
 
        for point in cmd.points:
            mult = 1
            idsplit = point.id.split(".")
            if len(idsplit) == 2:
                pclass, pname = idsplit
                psuf = None
            elif len(idsplit) == 3:
                pname, pclass, psuf = idsplit
            else:
                continue
            if pname[-5:] == "bytes":
                pname = pname[:-5] + "pages"
                mult = page_size
            else:
                pnt = point.id

            if psuf == "failrate":
                psuf = "failcnt"
 
            pnt = pname
            if psuf:
                pnt += "." + psuf
                if psuf[:4] == "fail":
                    # don't multiply failcnt/rate
                    mult = 1
 
            if pclass in metrics and pnt in metrics[pclass]:
                # already converted to int earlier for tallying:
                val = metrics[pclass][pnt] * mult
            result.values.append((point, val))

        return
