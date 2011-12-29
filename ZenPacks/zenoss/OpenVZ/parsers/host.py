###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011, Zenoss Inc.
#
###########################################################################

from Products.ZenRRD.CommandParser import CommandParser
from ZenPacks.zenoss.OpenVZ.util import VZInfoParser

class host(CommandParser):

    # This method is imported and run by zenhub and has direct access to the model...

    def dataForParser(self, context, datapoint):

        # We are using this method to stuff data inside a 'container_status'
        # datapoint which in turn is then pased to processResults(), below. The
        # data we are stuffing in the datapoint is container status information
        # for all existing containters. This is the current status known by
        # Zenoss that is stored in each container component. We pass this along
        # so that we can later see the previous status, when reading in new
        # status. And then we can figure out if we need to send an event -- if
        # that status has changed.

        # This trick is needed because processResults() is run by zencommand
        # and does not have direct access to the model.

        # Only provide extra data if we are handling the 'container_status'
        # datapoint:

        if datapoint.id != "container_status":
            return
        out = {}
        for c in context.openvz_containers():
           out[c.id] = c.container_status

        # Return dictionary of existing container status info in "102" (VEID) :
        # "running" format:
        
        return out
    
    # This method is imported and run by zencommand and does not have direct
    # access to the model...

    def processResults(self, cmd, result):

        # We have defined an openvz datasource for our container. It has a
        # datapoint called "container_status" that really isn't used for
        # recording RRD data. But having this datapoint allows us to create a
        # data pipeline for throwing events related to container status
        # changes. We just don't write any RRD data into the point at the very
        # end.

        for p in cmd.points:
            if p.id == "container_status":
                
                # grab container status info we provided in dataForParser():

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

                # We are not explicitly setting an event class here, so it will default to
                # /Unknown. This means that the event will not be immutably locked into an
                # event class and we can then use a mapping to control everything about it.
                # This allows us to place it in the event class that we want and and attach
                # a transform to this specific type of event, based on eventClassKey. The
                # transform allows us to execute python code to perform actions based on 
                # information in the event.

                # We create event mappings in the UI, by selecting the Event and clicking on
                # the little "tree" icon, or this can be done without selecting an Event by
                # going to "Event Classes" , "Status" (for example), and at bottom of screen
                # "Event Class Mappings", you can add one here. Make sure "eventClassKey"
                # matches the "eventClassKey" set below in the code. This will place that
                # event into the /Status event class.

                # Also make sure to add the Event Mapping to the ZenPack by selecting its
                # link and going to "Add to ZenPack".

                # We can map Events based on eventClassKey. Then, there is a rule and regex
                # that can be used to make our event mapping even more specific.

                # The "rule" is a python expression. True = match; False = no match
                # The "regex" will be matched against the event's message field, which is
                # usually a copy of "summary" that hasn't been truncated. Match = match.

                # The "transform" is literal python code.
                # globals in the context of the code that executes in "transform" are:
                #
                # evt (Event Object)
                # device & dev (Device Object - may be None)
                # txnCommit (method to commit changes to the model)
                # log (logger that will output into zeneventd.log)
                # dmd (DataRoot Object)
                # component (Component Object - may be None)
                # getFacade (method to gain access to API facades)
                # IInfo (Info adapter interface - for convenience)
                #
                # Example code:
                # 
                # if component:
                #     # modify properties of the object directly...
                #     component.container_status = evt.new_status
                #     txnCommit()
                #
                # This will update the status of the component with which the event is
                # associated, and commit the new status information to the model.
                #
                # In this code, we are making direct changes to the model, which give us
                # the ability to update the model direct without using DeviceProxy().
                #
                # To test: zensendevent -d 10.0.1.2 -p 106 -s Info -k openvz_container_status_change -o "new_status=weird" "container status change" 
                #
                # An overview of event severity:
                #
                # 0 = clear (green) - can clear existing events - 
                # a clear will happen if the following match in the method: fingerprint device|component|eventClass|eventKey 
                #                                                                             (optional)           (optional)
                # 1 = debug (grey)
                # 2 = info (blue)
                # 3 = warning (yellow)
                # 4 = error (orange)
                # 5 = critical (red)                

                result.events.append(dict(
                    summary="OpenVZ container created",
                    severity="2",
                    eventClassKey="openvz_container_created",
                    component = veid,
                    old_status = None,
                    new_status = current_veids[veid]
                ))
            elif existing_veids[veid] != current_veids[veid]:
                event_count += 1
                if current_veids[veid] == "running":
                    summary = "OpenVZ container started"
                else:
                    summary = "OpenVZ container " + current_veids[veid] 
                result.events.append(dict(
                    # limited to 128 characters:
                    summary=summary,
                    severity="2",
                    eventClassKey="openvz_container_status_change",
                    component = veid,
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
                summary="OpenVZ container destroyed",
                severity="2",
                eventClassKey="openvz_container_destroyed",
                component = veid,
                old_status = existing_veids[veid],
                new_status = None
            ))
        

