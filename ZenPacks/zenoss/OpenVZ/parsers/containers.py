###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011, Zenoss Inc.
#
###########################################################################

from Products.ZenRRD.CommandParser import CommandParser
 
class containers(CommandParser):

    def processResults(self, cmd, result):
    
        # TODO: generate informational events for when a container is restarted
        
        # parse data for each VEID

        # data sources:
        # /proc/user_beancounters
        # vzlist (running/stopped, etc. and IPADDR... for each CTID)
        # /proc/vz/vestat:
        # calculate HZ
        # http://wiki.openvz.org/Vestat
        #    user, nice, system, uptime (jiffies)
        #    idle, strv, uptime, used (cycles) (strv isn't used, used is used cycles of VE's on all CPUs)
        #    maxlat, totlat, numsched - latency stats in cycles, maxlat = how long VE had to wait before it got CPU time, totlat/numsched gives average scheduling latency (Virtuozo only)
        #    user, idle, system time counters, nice time counter, strv time counter?
        #    used?
        #    maxlat
        #    totlat
        #    numsched

        # parse /proc/user_beancounters
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
        # "102" : { "foo" : 3.4 }
        # GAUGE: float
        # DERIVED: int
        c_onhost = set(metrics.keys())
        c_inmodel = set()
        for point in cmd.points:
            if point.component in metrics:
                # grab metric
                if point.id in metrics[point.component]:
                    if point.id == "failrate":
                        pnt = "failcnt"
                    else:
                        pnt = point.id
                    result.values.append((point, metrics[point.component][pnt]))
                    # record that we grabbed data for this VEID, so we can see which ones we didn't grab data for later
                    c_inmodel.add(point.component)
        # GENERATE EVENTS FOR:
        # NEW CONTAINER  ---> update model
        # CONTAINER REMOVED ---> update model
        # STATUS CHANGE OF CONTAINER (started,stopped) --> event transform to update model with this info
    # severity:
# 0 = clear (green) - can clear existing events - 
# a clear will happen if the following match in the method: fingerprint device|component|eventClass|eventKey 
#                                                                 (optional)           (optional)
# 1 = debug (grey)
# 2 = info (blue)
# 3 = warning (yellow)
# 4 = error (orange)
# 5 = critical (red)
        return

        # compare list of existing VEIDs to list of VEIDs we parsed....
        #if touched != set(metrics.keys()):
         #       # we either lost or gained VE's.... fire events, remodel
         #       result.events.append(None)

        # any change -> remodel
        # possible informational events
