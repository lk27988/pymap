# Copyright (c) 2018 Kannan Subramani <Kannan.Subramani@bmw.de>
# SPDX-License-Identifier: GPL-3.0
# -*- coding: utf-8 -*-
"""Phone Book Access Profile client implemention"""


import atexit
import collections
import logging
import os
import readline
import sys
import uuid

from xml.etree import ElementTree

import bluetooth
import cmd2
import mapheaders as headers
import mapresponses as responses

from optparse import make_option
from PyOBEX import client

MAS_TARGET_UUID = uuid.UUID('{bb582b40-420c-11db-b0de-0800200c9a66}').bytes

logger = logging.getLogger(__name__)


class MAPClient(client.Client):
    """Message Access Profile Client"""

    def __init__(self, address, port):
        client.Client.__init__(self, address, port)
        self.current_dir = "/"

    def get_folder_listing(self, max_list_count=1024, list_startoffset=0):
        """Retrieves folders list from current folder"""
        logger.info("Requesting get_folder_listing with appl parameters %s", str(locals()))
        data = {"MaxListCount": headers.MaxListCount(max_list_count),
                "ListStartOffset": headers.ListStartOffset(list_startoffset)}
        application_parameters = headers.App_Parameters(data, encoded=False)
        header_list = [headers.Type("x-obex/folder-listing")]
        if application_parameters.data:
            header_list.append(application_parameters)

        response = self.get(header_list=header_list)
        if not isinstance(response, tuple) and isinstance(response, responses.FailureResponse):
            logger.error("get_folder_listing failed. reason = %s", response)
            return
        return response

    def get_messages_listing(self, name, max_list_count=1024, list_startoffset=0,
                             filter_messageType=0,filter_readStatus=0,new_message=0):
        """Retrieves messages listing object from current folder"""
        logger.info("Requesting get_messages_listing with parameters %s", str(locals()))
        data = {"MaxListCount": headers.MaxListCount(max_list_count),
                "ListStartOffset": headers.ListStartOffset(list_startoffset),
                "FilterMessageType":headers.FilterMessageType(filter_messageType),
                "FilterReadStatus":headers.FilterReadStatus(filter_readStatus),
                "NewMessage":headers.NewMessage(new_message)}

        application_parameters = headers.App_Parameters(data, encoded=False)
        header_list = [headers.Type("x-bt/MAP-msg-listing")]
        if application_parameters.data:
            header_list.append(application_parameters)

        response = self.get(name, header_list)
        if not isinstance(response, tuple) and isinstance(response, responses.FailureResponse):
            logger.error("get_messages_listing failed for bMessage '%s'. reason = %s", name, response)
            return
        return response

    def get_message(self,name,attachment=1,charset=1):
        """Retrieves a specific message from the MSE device"""
        logger.info("Requesting get_message with parameters %s", str(locals()))
        data = {"Attachment": headers.Attachment(attachment),
                "Charset": headers.Charset(charset)
                }

        application_parameters = headers.App_Parameters(data, encoded=False)
        header_list = [headers.Type("x-bt/message")]
        if application_parameters.data:
            header_list.append(application_parameters)

        response = self.get(name, header_list)
        if not isinstance(response, tuple) and isinstance(response, responses.FailureResponse):
            logger.error("get_messages_listing failed for bMessage '%s'. reason = %s", name, response)
            return
        return response
    
    def set_msg_folder(self, name="", to_parent=False, to_root=False):
        """Sets the current folder in the virtual folder architecture"""
        logger.info("Setting current folder with params '%s'", str(locals()))
        if name == "" and not to_parent and not to_root:
            logger.error("Not a valid action, "
                         "either name should be not empty or to_parent/to_root should be True")
            return
        # TODO: not exactly as per spec, limited by pyobex setpath. need to refine further
        if to_root:
            path_comp = self.current_dir.split("/")[1:]
            if not any(path_comp):
                logger.warning("Path is already in root folder, no need to change")
                return
            for _ in path_comp:
                response = self.setpath(to_parent=True)
        elif to_parent:
            if self.current_dir == "/":
                logger.warning("Path is already in root folder, can't go to parent dir")
                return
            response = self.setpath(to_parent=True)
        else:
            response = self.setpath(name)

        if not isinstance(response, tuple) and isinstance(response, responses.FailureResponse):
            logger.error("set_phonebook failed. reason = %s", name, response)
            return

        if to_root:
            self.current_dir = "/"
        elif to_parent:
            self.current_dir = os.path.dirname(self.current_dir)
        else:
            self.current_dir = os.path.join(self.current_dir, name)
        return response
    
    def set_msg_status(self,name='',status_indicator=1,status_value=''):
        '''Modify the status of a message on the MSE.'''
        logger.info("Requesting set_msg_status with parameters %s", str(locals()))
        data = {"StatusIndicator": headers.StatusIndicator(status_indicator),
                "StatusValue": headers.StatusValue(status_value)
                }
        application_parameters = headers.App_Parameters(data, encoded=False)
        header_list = [headers.Type("x-bt/messageStatus")]
        if application_parameters.data:
            header_list.append(application_parameters)
        response = self.put(name,'01',header_list=header_list)
        if not isinstance(response, tuple) and isinstance(response, responses.FailureResponse):
            logger.error("Modify the status to %s of message %s fail'. reason = %s", name,status_value, response)
            return
        return response
        
    def push_message(self,name,file_name='0123',transparent=0,retry=1,charset=1):
        """Push a message to a folder of the MSE"""
        logger.info("Requesting push_message with parameters %s", str(locals()))
        data = {"Transparent": headers.Transparent(transparent),
                "Retry": headers.Retry(retry),
                "Charset": headers.Charset(charset)
                }
        file_path=sys.path[0]+os.sep+'test'+os.sep+'data'+os.sep+file_name
        application_parameters = headers.App_Parameters(data, encoded=False)
        header_list = [headers.Type("x-bt/message")]
        if application_parameters.data:
            header_list.append(application_parameters)
        with open(file_path,'r') as f:
            file_data=f.readlines()
            response = self.put(name,''.join(file_data),header_list)
            if not isinstance(response, tuple) and isinstance(response, responses.FailureResponse):
                logger.error("push bMessage to %s fail'. reason = %s", name, response)
                return
            return response
        logger.error(" Read bMessage data fail")
        return
        
    def update_inbox(self,name=''):
        '''Initiate an update of the MSE's inbox'''
        logger.info("Requesting set_msg_status with parameters %s", str(locals()))

        header_list = [headers.Type("x-bt/MAP-messageUpdate")]
        response = self.put(name,'00',header_list=header_list)
        if not isinstance(response, tuple) and isinstance(response, responses.FailureResponse):
            logger.error("Initiate an update of the MSE's inbox fail'. reason = %s", response)
            return
        return response
        
class REPL(cmd2.Cmd):
    """REPL to use MAP client"""

    def __init__(self):
        cmd2.Cmd.__init__(self)
        self.prompt = self.colorize("map> ", "yellow")
        self.intro = self.colorize("Welcome to the MAP Access Profile!", "green")
        self.client = None
        self._store_history()
        cmd2.set_use_arg_list(False)

    @staticmethod
    def _store_history():
        history_file = os.path.expanduser('~/.mapclient_history')
        if not os.path.exists(history_file):
            with open(history_file, "w") as fobj:
                fobj.write("")
        readline.read_history_file(history_file)
        atexit.register(readline.write_history_file, history_file)

    @cmd2.options([], arg_desc="server_address")
    def do_connect(self, line, opts):
        profile_id = "1134"  # profile id of MAP
        #service_id = "\x79\x61\x35\xf0\xf0\xc5\x11\xd8\x09\x66\x08\x00\x20\x0c\x9a\x66"
        server_address = line
        if not server_address:
            raise ValueError("server_address should not be empty")
        logger.info("Finding MAP service ...")
        services = bluetooth.find_service(address=server_address, uuid=profile_id)
        if not services:
            sys.stderr.write("No MAP service found\n")
            sys.exit(1)

        host = services[0]["host"]
        port = services[0]["port"]
        logger.info("MAP service found!")

        self.client = MAPClient(host, port)
        logger.info("Connecting to pbap server = (%s, %s)", host, port)
        result = self.client.connect(header_list=[headers.Target(MAS_TARGET_UUID)])
        if not isinstance(result, responses.ConnectSuccess):
            logger.error("Connect Failed, Terminating the MAP client..")
            sys.exit(2)
        logger.info("Connect success")
        self.prompt = self.colorize("map> ", "green")

    @cmd2.options([], arg_desc="")
    def do_disconnect(self, line, opts):
        if self.client is None:
            logger.error("MAPClient is not even connected.. Connect and then try disconnect")
            sys.exit(2)
        logger.debug("Disconnecting pbap client with pbap server")
        self.client.disconnect()
        self.client = None
        self.prompt = self.colorize("map> ", "yellow")

    @cmd2.options([make_option('-c', '--max-count', default=1024, type=int,
                               help="maximum number of contacts to be returned"),
                   make_option('-o', '--start-offset', default=0, type=int,
                               help="offset of first entry to be returned"),
                   ],
                  arg_desc="MSG_folder")
    def do_get_folder_listing(self, line,opts):
        """Returns folders as per requested options"""
        result = self.client.get_folder_listing(max_list_count=opts.max_count, 
                                        list_startoffset=opts.start_offset)
        if result is not None:
            header, data = result
            logger.info("Result of get_folder_listing:\n%s", data)

    @cmd2.options([make_option('-c', '--max-count', default=1024, type=int,
                               help="maximum number of contacts to be returned"),
                   make_option('-o', '--start-offset', default=0, type=int,
                               help="offset of first entry to be returned"),
                   #make_option('-o', '--subject-length', default=255, type=int,
                   #            help="maximum string-length of subject to be returned"),
                   #make_option('-o', '--parameter-mask', default=0, type=int,
                   #            help="parameters containe in the messages returned"),
                   make_option('-t', '--filter-messageType', default=0, type=int,
                               help="filter the messages type to be returned"),
                   #make_option('-o', '--filter-periodBegin', default=0, type=int,
                   #            help="filter begin time of the messages to be returned"),
                   #make_option('-o', '--filter-periodEnd', default=0, type=int,
                   #            help="filter end time of the messages to be returned"),
                   make_option('-u', '--filter-readStatus', default=0, type=int,
                               help="filter read status of the messages to be returned"),
                   #make_option('-o', '--filter-recipient', default=0, type=int,
                   #            help="filter recipient of the messages to be returned"),
                   #make_option('-o', '--filter-originator.', default=0, type=int,
                   #            help="ofilter originator of the messages to be returned"),
                   #make_option('-o', '--filter-priority.', default=0, type=int,
                   #            help="filter priority of the messages to be returned"),
                   make_option('-n', '--new-message', default=0, type=int,
                               help="indicate of unread messages to be returned"),
                   #make_option('-o', '--mse-time', default=0, type=int,
                   #            help="report the Local Time basis of the MSE and its UTC offset,"),
                   #make_option('-o', '--listing-size', default=0, type=int,
                   #            help="report the number of accessible messages"),
                   ],
                  arg_desc="messags_list")
    def do_get_messages_listing(self, line, opts):
        """Returns Messages_isting as per requested options"""
        result = self.client.get_messages_listing(name=line,max_list_count=opts.max_count,
                                                  list_startoffset=opts.start_offset,
                                                  #subject_length=opts.subject_length,
                                                  #parameter_mask=opts.parameter_mask,
                                                  filter_messageType=opts.filter_messageType,
                                                  #filter_periodBegin=opts.filter_periodBegin,
                                                  #filter_periodEnd=opts.filter_periodEnd,
                                                  filter_readStatus=opts.filter_readStatus,
                                                  #filter_recipient=opts.filter_recipient,
                                                  #filter_originator.=opts.filter_originator.,
                                                  #filter_priority.=opts.filter_priority.,
                                                  new_message=opts.new_message
                                                  #mse_time=opts.mse_time,
                                                  #listing_size=opts.listing_size
                                                  )
        if result is not None:
            header, data = result
            logger.info("Result of get_messages_listing:\n%s", data)

    @cmd2.options([make_option('-a', '--attachment', default=1, type=int,help="determine to shall remove any element with a MIME type different than “text/…”"),
                   make_option('-c', '--charset', default=1, type=int,help="determine the transcoding of the textual parts of the delivered bMessage-content")
                   ],
                  arg_desc="message")
    def do_get_message(self, line, opts):
        """Returns get_message as per requested options"""
        result = self.client.get_message(name=line,
                                         attachment=opts.attachment,
                                         charset=opts.charset
                                        )
        if result is not None:
            header, data = result
            logger.info("Result of get_message:\n%s", data)

    @cmd2.options([make_option('--to-parent', action="store_true", default=False,help="navigate to parent dir"),
                   make_option('--to-root', action="store_true", default=False,help="navigate to root dir")
                   ],
                  arg_desc="[folder_name]")
    def do_set_msg_folder(self, line, opts):
        """Set current folder path of pbapserver virtual folder"""
        result = self.client.set_msg_folder(name=line, to_parent=opts.to_parent, to_root=opts.to_root)
        if result is not None:
            logger.info("Result of set_msg_folder:\n%s", result)
    
    @cmd2.options([make_option('-i', '--status-indicator', default=0, type=int,help="indicate which status information is to be modified.0:readStatus,1:deletedStatus"),
                   make_option('-v', '--status-value', default=0, type=int,help="indicate the new value of the status indicator to be modified.0:no,1:yes")
                   ],
                  arg_desc="message_status")
    def do_set_msg_status(self,line,opts):
        result = self.client.set_msg_status(name=line, status_indicator=opts.status_indicator, status_value=opts.status_value)
        if result is not None:
            logger.info("Result of set_msg_folder:\n%s", result)
    
    # @cmd2.options([make_option('-f', '--file', default='0123', type=str,help="the file name of the delivered bMessage-content"),
                   # make_option('-t', '--transparent', default=0, type=int,help="determine the transcoding of the textual parts of the delivered bMessage-content"),
                   # make_option('-r', '--retry', default=1, type=int,help="determine the transcoding of the textual parts of the delivered bMessage-content"),
                   # make_option('-c', '--charset', default=1, type=int,help="determine the transcoding of the textual parts of the delivered bMessage-content"),
                   # ]
                 # ,arg_desc="push_message_to_MSE")
    # def do_push_message(self,line,opts):
        # '''Returns push_message result '''
        # result = self.client.push_message(line,
                                         # file_name=opts.file,
                                         # transparent=opts.transparent,
                                         # retry=opts.retry,
                                         # charset=opts.charset
                                        # )
        # if result is not None:
            # header, data = result
            # logger.info("Result of push_message:\n%s", data)
    @cmd2.options([],
                  arg_desc="update_inbox")
    def do_update_inbox(self,line,opts):
        result = self.client.update_inbox(name='')
        if result is not None:
            logger.info("Result of update_inbox:\n%s", result)
            
    do_q = cmd2.Cmd.do_quit


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)-8s %(message)s')
    repl = REPL()
    repl.cmdloop()
