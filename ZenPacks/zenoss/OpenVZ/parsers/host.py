###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011, Zenoss Inc.
#
###########################################################################

from Products.ZenRRD.CommandParser import CommandParser
from ZenPacks.zenoss.OpenVZ.util import VZInfoParser

class host(CommandParser):

    def dataForParser(self, context, datapoint):
        if datapoint.id != "container_status":
            return
        out = {}
        for c in context.openvz_containers():
           out[c.id] = c.container_status
        return out

    def processResults(self, cmd, result):

        # find a point with container_status, otherwise return
        for p in cmd.points:
            if p.id == "container_status":
                existing_veids = p.data
                break
        else:
            return
         
        lines=cmd.result.output.split('\n')
        current_veids = VZInfoParser.parse(lines)
        event_count = 0
        for veid in current_veids:
            if veid == "0":
                # do not generate any events for VEID 0
                continue
            if veid not in existing_veids:
                event_count += 1
                result.events.append(dict(
                        summary="container created",
                        severity="2",
                        eventClassKey="openvz_container_created",
                        veid = veid,
                        old_status = None,
                        new_status = current_veids[veid]
                ))
            elif existing_veids[veid] != current_veids[veid]:
                event_count += 1
                result.events.append(dict(
                        summary="container status change",
                        severity="2",
                        eventClassKey="openvz_container_status_change",
                        veid = veid,
                        old_status = existing_veids[veid],
                        new_status = current_veids[veid]
                ))
        e_set = set(existing_veids.keys())
        e_set.discard("0")
        c_set = set(current_veids.keys())
        c_set.discard("0")

        for veid in e_set - c_set:
            # in existing set, not in current - VEID disappeared
            event_count += 1
            result.events.append(dict(
                summary="container destroyed",
                severity="2",
                eventClassKey="openvz_container_destroyed",
                veid = veid,
                old_status = existing_veids[veid],
                new_status = None
            ))
