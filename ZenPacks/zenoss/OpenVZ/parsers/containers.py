###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011, Zenoss Inc.
#
###########################################################################

from Products.ZenRRD.CommandParser import CommandParser
 
class containers(CommandParser):

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
            elif len(sp) == 6 and sp[0] != "dummy":
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
        for point in cmd.points:
            # point.component is the ID of the component. In our case, this is the VEID:    
            if point.component in metrics:

                # OK, VEID match, and now we match the metric too. Note that for this match to take place, the user must
                # have defined a datapoint in the UI called something like "physpages.maxheld". If they follow this pattern,
                # we will find a match in the data we grabbed from beancounters and update the RRD data. This way, we don't
                # need to pre-define tons of data points which will result in huge amounts of RRD data. Users just need to
                # add the datapoints of the data that they are actually interested in, and as long as the name matches, we
                # grab the data they want. 

                if point.id in metrics[point.component]:
                
                    # We support a special datapoint called "failrate" which can be a DERIVED RRD, used to trigger when
                    # we have an incremented failcnt. This is very useful for firing off events to alert when a failcnt
                    # has been incremented, but not very useful for anything else.

                    if point.id == "failrate":
                        pnt = "failcnt"
                    else:
                        pnt = point.id
                    
                    # OK, append the point along with the (currently string) data to the result.values list. This will
                    # hand it back to Zenoss to update the RRD data:

                    result.values.append((point, metrics[point.component][pnt]))

        # This method doesn't return anything explicitly, so just return:

        return
        
