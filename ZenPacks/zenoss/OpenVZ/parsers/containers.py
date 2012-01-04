###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011, Zenoss Inc.
#
###########################################################################

from Products.ZenRRD.CommandParser import CommandParser
 
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
                # we have kmemsize on this line: we need to process it...
                sp = sp[1:]
            if len(sp) == 6 and sp[0] != "dummy":
                # resource held maxheld barrier limit failcnt
                r = sp[0]
                if veid not in metrics:
                    metrics[veid] = {}
                metrics[veid].update({ r : sp[1], "%s.maxheld" % r : sp[2], "%s.barrier" % r : sp[3], "%s.limit" % r : sp[4], "%s.failcnt" % r : sp[5] })
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
        
        # For each datapoint we need to provide data for (sent to us by Zenoss, based on the datapoint definitions in UI...)
        if len(cmd.points):
            arch, page_size = cmd.points[0].data
            if arch in [ "x86_64", "ia64" ]:
                lmax = self.long_max_64
            else:
                lmax = self.long_max_32
        for point in cmd.points:
            # point.component is the ID of the component. In our case, this is the VEID:    
            
            if point.component not in metrics:
                continue
            
            mult = 1

            # OK, VEID match, and now we match the metric too. Note that for this match to take place, the user must
            # have defined a datapoint in the UI called something like "physpages.maxheld". If they follow this pattern,
            # we will find a match in the data we grabbed from beancounters and update the RRD data. This way, we don't
            # need to pre-define tons of data points which will result in huge amounts of RRD data. Users just need to
            # add the datapoints of the data that they are actually interested in, and as long as the name matches, we
            # grab the data they want. 
            
            psplit = point.id.split(".")
            # pname = eg. "physpages"
            pname = psplit[0]
            # psuf = eg. "barrier", or None
            if len(psplit) == 2:
                psuf = psplit[1]
            else:
                psuf = None
            if pname[-5:] == "bytes":
                # source data is equivalent pages data:
                pnt = pname[:-5] + "pages"
                # add .limit, .barrier, .maxheld if we have it:
                if psuf:
                    pnt += "." + psuf
                mult = page_size
            else:
                # no tweaks necessary, use original datapoint name as source:
                pnt = point.id
            if psuf == "failrate":
                # We support a special datapoint called "failrate" which can be a DERIVED RRD, used to trigger when
                # we have an incremented failcnt. This is very useful for firing off events to alert when a failcnt
                # has been incremented, but not very useful for anything else.
                # source data is failcnt:
                psuf = "failcnt"
        
            if psuf and psuf[:4] ==  "fail":
                # don't multiply the failcnt/rate
                mult = 1

            if pnt in metrics[point.component]:
            
                # OK, append the point along with the (currently string) data to the result.values list. This will
                # hand it back to Zenoss to update the RRD data:
                
                val = int(metrics[point.component][pnt]) * mult

                if psuf in [ "limit", "barrier" ] and ( ( val == lmax ) or ( val == 0 ) ):
                    # encountered an "unlimited" value - don't record this in RRD data (so it will be NaN)
                    continue 
                result.values.append((point, val))

        # This method doesn't return anything explicitly, so just return:

        return
        
