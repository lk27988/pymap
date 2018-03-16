# Copyright (c) 2018 Kannan Subramani <Kannan.Subramani@bmw.de>
# SPDX-License-Identifier: GPL-3.0
# -*- coding: utf-8 -*-
"""Phone Book Access Profile headers"""

from PyOBEX.headers import *
from mapcommon import FILTER_ATTR_DICT


# Application Parameters Header Properties
class AppParamProperty(object):
    def __init__(self, data, encoded=False):
        if encoded:
            self.data = data
        else:
            self.data = self.encode(data)

    def encode(self, data):
        if self.__class__.__name__ == "SearchValue":
            self.length = len(data)
        return struct.pack(">BB", self.tagid, self.length) + data

    def decode(self):
        return struct.unpack(">BB", self.data[:2]), self.data[2:]


class OneByteProperty(AppParamProperty):
    length = 1  # byte
    fmt = ">B"

    def encode(self, data):
        return super(OneByteProperty, self).encode(struct.pack(self.fmt, data))

    def decode(self):
        headers, data = super(OneByteProperty, self).decode()
        return struct.unpack(self.fmt, data)[0]


class TwoByteProperty(AppParamProperty):
    length = 2  # bytes
    fmt = ">H"

    def encode(self, data):
        return super(TwoByteProperty, self).encode(struct.pack(self.fmt, data))

    def decode(self):
        headers, data = super(TwoByteProperty, self).decode()
        return struct.unpack(self.fmt, data)[0]
        
class FourByteProperty(AppParamProperty):
    length = 4  # bytes
    fmt = ">I"

    def encode(self, data):
        return super(FourByteProperty, self).encode(struct.pack(self.fmt, data))

    def decode(self):
        headers, data = super(FourByteProperty, self).decode()
        return struct.unpack(self.fmt, data)[0]


class EightByteProperty(AppParamProperty):
    length = 8  # bytes
    fmt = ">Q"

    def encode(self, data):
        return super(EightByteProperty, self).encode(struct.pack(self.fmt, data))

    def decode(self):
        headers, data = super(EightByteProperty, self).decode()
        return struct.unpack(self.fmt, data)[0]


class VariableLengthProperty(AppParamProperty):
    fmt = "{len}s"

    def encode(self, data):
        return super(VariableLengthProperty, self).encode(struct.pack(self.fmt.format(len=len(data)), data))

    def decode(self):
        headers, data = super(VariableLengthProperty, self).decode()
        tagid, length = headers
        return struct.unpack(self.fmt.format(len=length), data)[0]

class MaxListCount(TwoByteProperty):
    tagid = 0x01


class ListStartOffset(TwoByteProperty):
    tagid = 0x02

class FilterMessageType(OneByteProperty):
    tagid = 0x03
    
class FilterPeriodBegin(VariableLengthProperty):
    tagid = 0x04
    
class EndFilterPeriodEnd(VariableLengthProperty):
    tagid = 0x05
    
class FilterReadStatus(OneByteProperty):
    tagid = 0x06
    
class FilterRecipient(VariableLengthProperty):
    tagid = 0x07
    
class FilterOriginator(VariableLengthProperty):
    tagid = 0x08
    
class FilterPriority(OneByteProperty):
    tagid = 0x09
    
class Attachment(OneByteProperty):
    tagid = 0x0A
    
class Transparent(OneByteProperty):
    tagid = 0x0B
    
class Retry(OneByteProperty):
    tagid = 0x0C
    
class NewMessage(OneByteProperty):
    tagid = 0x0D
    
class NotificationStatus(OneByteProperty):
    tagid = 0x0E
    
class MASInstanceID(OneByteProperty):
    tagid = 0x0F
    
class ParameterMask(FourByteProperty):
    tagid = 0x10
    
class FolderListingSize(TwoByteProperty):
    tagid = 0x11
    
class ListingSize(TwoByteProperty):
    tagid = 0x12
    
class SubjectLength(OneByteProperty):
    tagid = 0x13
    
class Charset(OneByteProperty):
    tagid = 0x14
    
class FractionRequest(OneByteProperty):
    tagid = 0x15
    
class FractionDeliver(OneByteProperty):
    tagid = 0x16
    
class StatusIndicator(OneByteProperty):
    tagid = 0x17
    
class StatusValue(OneByteProperty):
    tagid = 0x18
    
class MSETime(VariableLengthProperty):
    tagid = 0x19
    
class DatabaseIdentifier(VariableLengthProperty):
    tagid = 0x1A
    
class ConversationListingVersionCounter(VariableLengthProperty):
    tagid = 0x1B
    
class PresenceAvailability(OneByteProperty):
    tagid = 0x1C
    
class PresenceText(VariableLengthProperty):
    tagid = 0x1D
    
class LastActivity(VariableLengthProperty):
    tagid = 0x1E
    
class FilterLastActivityBegin(VariableLengthProperty):
    tagid = 0x1F
    
class FilterLastActivityEnd(VariableLengthProperty):
    tagid = 0x20
    
class ChatState(OneByteProperty):
    tagid = 0x21
    
class ConversationID(VariableLengthProperty):
    tagid = 0x22
    
class FolderVersionCounter(VariableLengthProperty):
    tagid = 0x23
    
class FilterMessageHandle(VariableLengthProperty):
    tagid = 0x24
    
class NotificationFilterMask(FourByteProperty):
    tagid = 0x25
    
class ConvParameterMask(FourByteProperty):
    tagid = 0x26
    
class OwnerUCI(VariableLengthProperty):
    tagid = 0x27
    
class ExtendedData(VariableLengthProperty):
    tagid = 0x28
    
class MapSupportedFeatures(FourByteProperty):
    tagid = 0x29
    
class MessageHandle(VariableLengthProperty):
    tagid = 0x2A
    
class ModifyText(OneByteProperty):
    tagid = 0x2B
    

app_parameters_dict = {
    0x01: MaxListCount,
    0x02: ListStartOffset,
    0x03: FilterMessageType,
    0x04: FilterPeriodBegin,
    0x05: EndFilterPeriodEnd,
    0x06: FilterReadStatus,
    0x07: FilterRecipient,
    0x08: FilterOriginator,
    0x09: FilterPriority,
    0x0A: Attachment,
    0x0B: Transparent,
    0x0C: Retry,
    0x0D: NewMessage,
    0x0E: NotificationStatus,
    0x0F: MASInstanceID,
    0x10: ParameterMask,
    0x11: FolderListingSize,
    0x12: ListingSize,
    0x13: SubjectLength,
    0x14: Charset,
    0x15: FractionRequest,
    0x16: FractionDeliver,
    0x17: StatusIndicator,
    0x18: StatusValue,
    0x19: MSETime,
    0x1A: DatabaseIdentifier,
    0x1B: ConversationListingVersionCounter,
    0x1C: PresenceAvailability,
    0x1D: PresenceText,
    0x1E: LastActivity,
    0x1F: FilterLastActivityBegin,
    0x20: FilterLastActivityEnd,
    0x21: ChatState,
    0x22: ConversationID,
    0x23: FolderVersionCounter,
    0x24: FilterMessageHandle,
    0x25: NotificationFilterMask,
    0x26: ConvParameterMask,
    0x27: OwnerUCI,
    0x28: ExtendedData,
    0x29: MapSupportedFeatures,
    0x2A: MessageHandle,
    0x2B: ModifyText
}


# Sample App Parameters data
# code | length | data
# 4c | 00 18 | 06 08 00 00 00 3f d0 00 00 80 07 01 00 04 02 00 00 05 02 00 00

def extended_decode(self):
    # assumption:
    # size of tagid = 1 byte
    # size of length = 1 byte (This is just the data length)
    data = self.data
    res_dict = {}
    while data:
        tagid = ord(data[0])
        length = ord(data[1])
        app_param_class = app_parameters_dict[tagid]
        if tagid == 0x1B:
            res_dict['Conversation-ListingVersionCounter'] = app_param_class(data[:length + 2], encoded=True)
        else:
            res_dict[app_param_class.__name__] = app_param_class(data[:length + 2], encoded=True)
        data = data[length + 2:]
    return res_dict


def extended_encode(self, data_dict):
    data = ""
    for item in data_dict.values():
        if item is None:
            continue
        data += item.data
    return struct.pack(">BH", self.code, len(data) + 3) + data


App_Parameters.decode = extended_decode
App_Parameters.encode = extended_encode
