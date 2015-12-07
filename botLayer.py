import sys
import os
import logging

from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.auth import YowAuthenticationProtocolLayer
from yowsup.layers import YowLayerEvent
from yowsup.layers.network import YowNetworkLayer
from yowsup.common import YowConstants
from yowsup.layers.protocol_groups.protocolentities import *
from yowsup.layers.protocol_presence.protocolentities import *
from yowsup.layers.protocol_messages.protocolentities import *
from yowsup.layers.protocol_ib.protocolentities import *
from yowsup.layers.protocol_iq.protocolentities import *
from yowsup.layers.protocol_contacts.protocolentities import *
from yowsup.layers.protocol_chatstate.protocolentities import *
from yowsup.layers.protocol_privacy.protocolentities import *
from yowsup.layers.protocol_media.protocolentities import *
from yowsup.layers.protocol_profiles.protocolentities import *
from yowsup.common.tools import ModuleTools

from D2WBot_Utils import D2WBot_Utils

logger = logging.getLogger(__name__)


class BotLayer(D2WBot_Utils, YowInterfaceLayer):
    PROP_RECEIPT_AUTO = "org.openwhatsapp.yowsup.prop.cli.autoreceipt"
    PROP_RECEIPT_KEEPALIVE = "org.openwhatsapp.yowsup.prop.cli.keepalive"
    PROP_CONTACT_JID = "org.openwhatsapp.yowsup.prop.cli.contact.jid"
    EVENT_LOGIN = "org.openwhatsapp.yowsup.event.cli.login"
    EVENT_START = "org.openwhatsapp.yowsup.event.cli.start"
    EVENT_SHUTDOWN = "shutdown"
    EVENT_SENDANDEXIT = "org.openwhatsapp.yowsup.event.cli.sendandexit"

    MESSAGE_FORMAT = "[{FROM}({TIME})]:[{MESSAGE_ID}]\t {MESSAGE}"

    DISCONNECT_ACTION_PROMPT = 0
    DISCONNECT_ACTION_EXIT = 1

    ACCOUNT_DEL_WARNINGS = 4

    def __init__(self):
        super(BotLayer, self).__init__()
        YowInterfaceLayer.__init__(self)
        self.accountDelWarnings = 0
        self.connected = False
        self.username = None
        self.sendReceipts = True
        self.disconnectAction = self.__class__.DISCONNECT_ACTION_PROMPT
        self.credentials = None

        # add aliases to make it user to use commands. for example you can then do:
        # /message send foobar "HI"
        # and then it will get automaticlaly mapped to foobar's jid
        self.jidAliases = {
            # "NAME": "PHONE@s.whatsapp.net"
        }

    def aliasToJid(self, calias):
        for alias, ajid in self.jidAliases.items():
            if calias.lower() == alias.lower():
                return self.normalizeJid(ajid)

        return self.normalizeJid(calias)

    def jidToAlias(self, jid):
        for alias, ajid in self.jidAliases.items():
            if ajid == jid:
                return alias
        return jid

    def normalizeJid(self, number):
        if '@' in number:
            return number
        elif "-" in number:
            return "%s@g.us" % number

        return "%s@s.whatsapp.net" % number

    def setCredentials(self, username, password):
        self.getLayerInterface(YowAuthenticationProtocolLayer).setCredentials(username, password)

    def onEvent(self, layerEvent):
        if layerEvent.getName() == self.__class__.EVENT_START:
            self.startChecking()
            return True
        elif layerEvent.getName() == self.__class__.EVENT_SHUTDOWN:
            self.stopChecking()
            return True
        elif layerEvent.getName() == self.__class__.EVENT_SENDANDEXIT:
            credentials = layerEvent.getArg("credentials")
            target = layerEvent.getArg("target")
            message = layerEvent.getArg("message")
            self.sendMessageAndDisconnect(credentials, target, message)

            return True
        elif layerEvent.getName() == YowNetworkLayer.EVENT_STATE_DISCONNECTED:
            self.output("Disconnected: %s" % layerEvent.getArg("reason"))
            if self.disconnectAction == self.__class__.DISCONNECT_ACTION_PROMPT:
                self.connected = False
                # self.notifyInputThread()
            else:
                os._exit(os.EX_OK)

    def assertConnected(self):
        if self.connected:
            return True
        else:
            self.output("Not connected", tag="Error", prompt=False)
            return False

    ########### ib #######################
    # Send clean dirty
    def ib_clean(self, dirtyType):
        if self.assertConnected():
            entity = CleanIqProtocolEntity("groups", YowConstants.DOMAIN)
            self.toLower(entity)

    # Ping server
    def ping(self):
        if self.assertConnected():
            entity = PingIqProtocolEntity(to=YowConstants.DOMAIN)
            self.toLower(entity)

    ######################################
    ####### contacts/ profiles ####################
    def profile_setStatus(self, text):
        if self.assertConnected():
            def onSuccess(resultIqEntity, originalIqEntity):
                self.output("Status updated successfully")

            def onError(errorIqEntity, originalIqEntity):
                logger.error("Error updating status")

            entity = SetStatusIqProtocolEntity(text)
            self._sendIq(entity, onSuccess, onError)


    def contact_lastseen(self, jid):
        if self.assertConnected():
            def onSuccess(resultIqEntity, originalIqEntity):
                self.output("%s lastseen %s seconds ago" % (resultIqEntity.getFrom(), resultIqEntity.getSeconds()))

            def onError(errorIqEntity, originalIqEntity):
                logger.error("Error getting lastseen information for %s" % originalIqEntity.getTo())

            entity = LastseenIqProtocolEntity(self.aliasToJid(jid))
            self._sendIq(entity, onSuccess, onError)

    # Set profile picture
    def profile_setPicture(self, path):
        if self.assertConnected() and ModuleTools.INSTALLED_PIL():

            def onSuccess(resultIqEntity, originalIqEntity):
                self.output("Profile picture updated successfully")

            def onError(errorIqEntity, originalIqEntity):
                logger.error("Error updating profile picture")

            # example by @aesedepece in https://github.com/tgalal/yowsup/pull/781
            # modified to support python3
            from PIL import Image
            src = Image.open(path)
            pictureData = src.resize((640, 640)).tobytes("jpeg", "RGB")
            picturePreview = src.resize((96, 96)).tobytes("jpeg", "RGB")
            iq = SetPictureIqProtocolEntity(self.getOwnJid(), picturePreview, pictureData)
            self._sendIq(iq, onSuccess, onError)
        else:
            logger.error("Python PIL library is not installed, can't set profile picture")

    ########### groups

    # List all groups you belong to
    def groups_list(self):
        if self.assertConnected():
            entity = ListGroupsIqProtocolEntity()
            self.toLower(entity)

    # Leave a group you belong to"
    def group_leave(self, group_jid):
        if self.assertConnected():
            entity = LeaveGroupsIqProtocolEntity([self.aliasToJid(group_jid)])
            self.toLower(entity)

    # Create a new group with the specified subject and participants. Jids are a comma separated list but optional.
    def groups_create(self, subject, jids=None):
        if self.assertConnected():
            jids = [self.aliasToJid(jid) for jid in jids.split(',')] if jids else []
            entity = CreateGroupsIqProtocolEntity(subject, participants=jids)
            self.toLower(entity)

    # Invite to group. Jids are a comma separated list
    def group_invite(self, group_jid, jids):
        if self.assertConnected():
            jids = [self.aliasToJid(jid) for jid in jids.split(',')]
            entity = AddParticipantsIqProtocolEntity(self.aliasToJid(group_jid), jids)
            self.toLower(entity)

    # Promote admin of a group. Jids are a comma separated list
    def group_promote(self, group_jid, jids):
        if self.assertConnected():
            jids = [self.aliasToJid(jid) for jid in jids.split(',')]
            entity = PromoteParticipantsIqProtocolEntity(self.aliasToJid(group_jid), jids)
            self.toLower(entity)

    # Remove admin of a group. Jids are a comma separated list
    def group_demote(self, group_jid, jids):
        if self.assertConnected():
            jids = [self.aliasToJid(jid) for jid in jids.split(',')]
            entity = DemoteParticipantsIqProtocolEntity(self.aliasToJid(group_jid), jids)
            self.toLower(entity)

    # Kick from group. Jids are a comma separated list
    def group_kick(self, group_jid, jids):
        if self.assertConnected():
            jids = [self.aliasToJid(jid) for jid in jids.split(',')]
            entity = RemoveParticipantsIqProtocolEntity(self.aliasToJid(group_jid), jids)
            self.toLower(entity)

    # Change group subject
    def group_setSubject(self, group_jid, subject):
        if self.assertConnected():
            entity = SubjectGroupsIqProtocolEntity(self.aliasToJid(group_jid), subject)
            self.toLower(entity)

    # Set group picture
    def group_picture(self, group_jid, path):
        if self.assertConnected() and ModuleTools.INSTALLED_PIL():

            def onSuccess(resultIqEntity, originalIqEntity):
                self.output("Group picture updated successfully")

            def onError(errorIqEntity, originalIqEntity):
                logger.error("Error updating Group picture")

            # example by @aesedepece in https://github.com/tgalal/yowsup/pull/781
            # modified to support python3
            from PIL import Image
            src = Image.open(path)
            pictureData = src.resize((640, 640)).tobytes("jpeg", "RGB")
            picturePreview = src.resize((96, 96)).tobytes("jpeg", "RGB")
            iq = SetPictureIqProtocolEntity(self.aliasToJid(group_jid), picturePreview, pictureData)
            self._sendIq(iq, onSuccess, onError)
        else:
            logger.error("Python PIL library is not installed, can't set profile picture")

    # Get group info
    def group_info(self, group_jid):
        if self.assertConnected():
            entity = InfoGroupsIqProtocolEntity(self.aliasToJid(group_jid))
            self.toLower(entity)

    # Get shared keys
    def keys_get(self, jids):
        if ModuleTools.INSTALLED_AXOLOTL():
            from yowsup.layers.axolotl.protocolentities.iq_key_get import GetKeysIqProtocolEntity
            if self.assertConnected():
                jids = [self.aliasToJid(jid) for jid in jids.split(',')]
                entity = GetKeysIqProtocolEntity(jids)
                self.toLower(entity)
        else:
            logger.error("Axolotl is not installed")

    # Send prekeys
    def keys_set(self):
        if ModuleTools.INSTALLED_AXOLOTL():
            from yowsup.layers.axolotl import YowAxolotlLayer
            if self.assertConnected():
                self.broadcastEvent(YowLayerEvent(YowAxolotlLayer.EVENT_PREKEYS_SET))
        else:
            logger.error("Axolotl is not installed")

    # Send init seq
    def seq(self):
        priv = PrivacyListIqProtocolEntity()
        self.toLower(priv)
        push = PushIqProtocolEntity()
        self.toLower(push)
        props = PropsIqProtocolEntity()
        self.toLower(props)
        crypto = CryptoIqProtocolEntity()
        self.toLower(crypto)

    # Delete your account
    def account_delete(self):
        if self.assertConnected():
            if self.accountDelWarnings < self.__class__.ACCOUNT_DEL_WARNINGS:
                self.accountDelWarnings += 1
                remaining = self.__class__.ACCOUNT_DEL_WARNINGS - self.accountDelWarnings
                self.output("Repeat delete command another %s times to send the delete request" % remaining,
                            tag="Account delete Warning !!", prompt=False)
            else:
                entity = UnregisterIqProtocolEntity()
                self.toLower(entity)

    # Send message to a friend
    def message_send(self, number, content):
        if self.assertConnected():
            outgoingMessage = TextMessageProtocolEntity(
                content.encode("utf-8") if sys.version_info >= (3, 0) else content, to=self.aliasToJid(number))
            self.toLower(outgoingMessage)

    # Broadcast message. numbers should comma separated phone numbers
    def message_broadcast(self, numbers, content):
        if self.assertConnected():
            jids = [self.aliasToJid(number) for number in numbers.split(',')]
            outgoingMessage = BroadcastTextMessage(jids, content)
            self.toLower(outgoingMessage)

    # # Send read receipt
    def message_read(self, message_id):
        pass

    # # Send delivered receipt
    def message_delivered(self, message_id):
        pass

    # Send an image with optional caption
    def image_send(self, number, path, caption=None):
        if self.assertConnected():
            jid = self.aliasToJid(number)
            entity = RequestUploadIqProtocolEntity(RequestUploadIqProtocolEntity.MEDIA_TYPE_IMAGE, filePath=path)
            successFn = lambda successEntity, originalEntity: self.onRequestUploadResult(jid, path, successEntity,
                                                                                         originalEntity, caption)
            errorFn = lambda errorEntity, originalEntity: self.onRequestUploadError(jid, path, errorEntity,
                                                                                    originalEntity)

            self._sendIq(entity, successFn, errorFn)
    # Send audio file
    def audio_send(self, number, path):
        if self.assertConnected():
            jid = self.aliasToJid(number)
            entity = RequestUploadIqProtocolEntity(RequestUploadIqProtocolEntity.MEDIA_TYPE_AUDIO, filePath=path)
            successFn = lambda successEntity, originalEntity: self.onRequestUploadResult(jid, path, successEntity,
                                                                                         originalEntity)
            errorFn = lambda errorEntity, originalEntity: self.onRequestUploadError(jid, path, errorEntity,
                                                                                    originalEntity)

            self._sendIq(entity, successFn, errorFn)

    # Send typing state
    def state_typing(self, jid):
        if self.assertConnected():
            entity = OutgoingChatstateProtocolEntity(ChatstateProtocolEntity.STATE_TYPING, self.aliasToJid(jid))
            self.toLower(entity)

    # Send paused state
    def state_paused(self, jid):
        if self.assertConnected():
            entity = OutgoingChatstateProtocolEntity(ChatstateProtocolEntity.STATE_PAUSED, self.aliasToJid(jid))
            self.toLower(entity)

    # Sync contacts, contacts should be comma separated phone numbers, with no spaces
    def contacts_sync(self, contacts):
        if self.assertConnected():
            entity = GetSyncIqProtocolEntity(contacts.split(','))
            self.toLower(entity)

    # Disconnect
    def disconnect(self):
        if self.assertConnected():
            self.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_DISCONNECT))

    # Quick login
    def L(self):
        if self.connected:
            return self.output("Already connected, disconnect first")
        self.getLayerInterface(YowNetworkLayer).connect()
        return True

    # Login to WhatsApp
    def login(self, username, b64password):
        self.setCredentials(username, b64password)
        return self.L()

    ######## receive #########

    @ProtocolEntityCallback("chatstate")
    def onChatstate(self, entity):
        print(entity)

    @ProtocolEntityCallback("iq")
    def onIq(self, entity):
        self.sentCache.update({'groups': entity})
        print(entity)

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        self.toLower(entity.ack())

    @ProtocolEntityCallback("ack")
    def onAck(self, entity):
        if entity.getClass() == "message":
            self.output(entity.getId(), tag="Sent")

    @ProtocolEntityCallback("success")
    def onSuccess(self, entity):
        self.connected = True
        self.output("Logged in!", "Auth", prompt=False)

    @ProtocolEntityCallback("failure")
    def onFailure(self, entity):
        self.connected = False
        self.output("Login Failed, reason: %s" % entity.getReason(), prompt=False)

    @ProtocolEntityCallback("notification")
    def onNotification(self, notification):
        notificationData = notification.__str__()
        if notificationData:
            self.output(notificationData, tag="Notification")
        else:
            self.output("From :%s, Type: %s" % (self.jidToAlias(notification.getFrom()), notification.getType()),
                        tag="Notification")
        if self.sendReceipts:
            self.toLower(notification.ack())

    # @ProtocolEntityCallback("message")
    # def onMessage(self, message):
    #     messageOut = ""
    #     if message.getType() == "text":
    #         # self.output(message.getBody(), tag = "%s [%s]"%(message.getFrom(), formattedDate))
    #         messageOut = self.getTextMessageBody(message)
    #     elif message.getType() == "media":
    #         messageOut = self.getMediaMessageBody(message)
    #     else:
    #         messageOut = "Unknown message type %s " % message.getType()
    #         print(messageOut.toProtocolTreeNode())
    #
    #     formattedDate = datetime.datetime.fromtimestamp(message.getTimestamp()).strftime('%d-%m-%Y %H:%M')
    #     sender = message.getFrom() if not message.isGroupMessage() else "%s/%s" % (
    #     message.getParticipant(False), message.getFrom())
    #     output = self.__class__.MESSAGE_FORMAT.format(
    #         FROM=sender,
    #         TIME=formattedDate,
    #         MESSAGE=messageOut.encode('latin-1').decode() if sys.version_info >= (3, 0) else messageOut,
    #         MESSAGE_ID=message.getId()
    #     )
    #
    #     self.output(output, tag=None, prompt=not self.sendReceipts)
    #     if self.sendReceipts:
    #         self.toLower(message.ack())
    #         self.output("Sent delivered receipt", tag="Message %s" % message.getId())

    @ProtocolEntityCallback("message")
    def onMessage(self, message):
        if self.sendReceipts:
            self.toLower(message.ack(read=True))

    def __str__(self):
        return "Awesome Dota2 Whatsapp Results Bot"
