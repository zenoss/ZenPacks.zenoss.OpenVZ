###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011, Zenoss Inc.
#
###########################################################################

# To debug this command parser, run the following command as the zenoss user:
# zencommand run -v10 --showfullcommand --showrawresults --device=<device_id>

# As a ZenPack developer, when specifying the command to run on the command-line,
# a "$" must be entered as "$$". If you type "$$", bash will see "$". If this is
# not done, an event will appear in Zenoss UI containing a traceback due to the
# TALES parser failing.

from Products.ZenRRD.CommandParser import CommandParser
from ZenPacks.zenoss.OpenVZ.util import VEStatParser
 
class containers(CommandParser):

    long_max_64 = 9223372036854775807
    long_max_32 = 2147483647

    # dataForParser is run by zenhub and has direct access to model -- stuff in page size and arch:

    def dataForParser(self, context, datapoint):

        h = context.host().hw
        return ( h.arch, h.page_size )

    def processResults(self, cmd, result):
    
        # This code is run once for each container. Zenoss detects we are running the exact same command on all containers,
        # so it will only execute the command on the host once, and the cmd results will be cached and passed to this 
        # function multiple times.

        lines=cmd.result.output.split('\n')
        pos = 0
        bclines = []
        stlines = []
        iolines = []

        # /proc/user_beancounters lines
        while pos < len(lines) and lines[pos] != "#beancounters-end":
            bclines.append(lines[pos])
            pos += 1
        pos += 1
        # /proc/vz/vestat lines
        while pos < len(lines) and lines[pos] != "#vestat-end":
            stlines.append(lines[pos])
            pos += 1
        pos += 1
        while pos < len(lines) and lines[pos] != "#iostat end":
            iolines.append(lines[pos])
            pos += 1

        # process beancounters lines:

        lines = bclines
        pos = 2
        veid = None
        metrics = {}
        while pos < len(lines):
            sp = lines[pos].split()
            if len(sp) == 7:
                veid = sp[0][:-1]
                # we have kmemsize on this line: we need to process it...
                sp = sp[1:]
            if len(sp) == 6 and sp[0] != "dummy":
                # resource held maxheld barrier limit failcnt
                r = sp[0]
                if veid not in metrics:
                    metrics[veid] = {}
                metrics[veid].update({ r : sp[1], "%s.maxheld" % r : sp[2], "%s.barrier" % r : sp[3], "%s.limit" % r : sp[4], "%s.failcnt" % r : sp[5] })
            pos += 1

        # augment with ioacct lines:

        lines = iolines
        veid = None
        pos = 0
        while pos < len(lines):
            sp = lines[pos].split()
            # expecting a line like this: "#ioacct /proc/bc/102/ioacct". The "102" is the VEID of the metrics that follow:
            if len(sp) == 2:
                if sp[0] == "#ioacct" and sp[1][:9] == "/proc/bc/":
                    veid = sp[1][9:].split("/")[0]
                else:
                    # this should not happen, but we check anyway. We can't record metrics if we haven't found the VEID yet.
                    if veid == None:
                        pos += 1
                        continue
                    if veid not in metrics:
                        metrics[veid] = {}
                    metric = sp[0]
                    if metric in ( "read", "write", "dirty", "cancel", "missed"):
                        metric += "bytes"
                    metric = "ioacct." + metric
                    metrics[veid][metric] = sp[1]
            pos += 1

        # OK, now we have a data structure that looks like this:
        #
        # { veid : { metric : value } }
        #
        # ie.
        #
        # "102" : { "foo" : "3.4" }
        # 
        # It's OK for everything to be strings. Zenoss will automatically handle the conversion to float (for DERIVED RRD
        # data) or int (for GAUGE data) for us.

        vestatcols, vestatdata = VEStatParser.parse(stlines)
 
        # For each datapoint we need to provide data for (sent to us by Zenoss, based on the datapoint definitions in UI...)
        if len(cmd.points):
            arch, page_size = cmd.points[0].data
            if arch in [ "x86_64", "ia64" ]:
                lmax = self.long_max_64
            else:
                lmax = self.long_max_32

        # main loop to process through all the datapoints we need to populate with data:

        for point in cmd.points:

            mult = 1

            # OK, VEID match, and now we match the metric too. Note that for this match to take place, the user must
            # have defined a datapoint in the UI called something like "physpages.maxheld". If they follow this pattern,
            # we will find a match in the data we grabbed from beancounters and update the RRD data. This way, we don't
            # need to pre-define tons of data points which will result in huge amounts of RRD data. Users just need to
            # add the datapoints of the data that they are actually interested in, and as long as the name matches, we
            # grab the data they want. 
            psplit = point.id.split(".")
            pname = psplit[0]
            # pname = eg. "physpages"
            # psuf = eg. "barrier", or None
            vestat = False
            if len(psplit) == 2:
                if pname == "ioacct":
                    pname = point.id
                    psuf = None
                else:
                    pname = psplit[0]
                    psuf = psplit[1]
            elif len(psplit) == 3 and psplit[0] == "vestat":
                pname = psplit[1]
                psuf = psplit[2]
                vestat = True
            else:
                pname = psplit[0]
                psuf = None
            if not vestat:
                if pname[-5:] == "bytes":
                    if pname[:-5] + "pages" in metrics:
                        # source data is equivalent pages data:
                        pname = pname[:-5] + "pages"
                        mult = page_size
            
                if psuf == "failrate":
                    # We support a special datapoint called "failrate" which can be a DERIVED RRD, used to trigger when
                    # we have an incremented failcnt. This is very useful for firing off events to alert when a failcnt
                    # has been incremented, but not very useful for anything else.
                    # source data is failcnt:
                    psuf = "failcnt"
                
                # pnt defines where in the dict to get the source data. It is based on pname, set earlier.
                pnt = pname
                if psuf:
                    pnt += "." + psuf
                    if psuf[:4] == "fail":
                        # don't multiply the failcnt/rate
                        mult = 1
                # write out our beancounters RRD data:
                if point.component in metrics and pnt in metrics[point.component]:
                    val = int(metrics[point.component][pnt]) * mult
                    if psuf in [ "limit", "barrier" ] and ( ( val == lmax ) or ( val == 0 ) ):
                        # encountered an "unlimited" value - don't record this in RRD data (so it will be NaN)
                        continue 
                    result.values.append((point, val))
            else:
                # VESTAT
                try:
                    if psuf == "jiffies":
                        # the jiffy values appear first in the list (there is a duplicate "uptime" column, first is jiffies)
                        veindex = vestatcols.index(pname) 
                    elif psuf == "seconds":
                        # synthetic (but easy to compute) metric -- seconds are jiffies * .01 on linux systems (SC_CLK_TCK)
                        veindex = vestatcols.index(pname) 
                        mult = .01
                    elif psuf == "cycles":
                        # cycles are the later columns, and we have two "uptime" cols - this avoids seeing the first one:
                        veindex = vestatcols.index(pname[5:]) + 5
                except ValueError:
                    # couldn't find something in vestatcols
                    # TODO - log error, fire event to alert user...
                    continue
  
                # write out our vestat RRD data: 
                if point.component in vestatdata and pname in vestatcols:
                    val = int(vestatdata[point.component][veindex]) * mult
                    result.values.append((point, val))
# vim: set ts=4 sw=4 expandtab: 
