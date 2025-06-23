import logging
from warnings import warn

from .baseclient import ObsClient
from .error import OBSSDKError, OBSSDKRequestError
from .util import as_dataclass

"""
A class to interact with obs-websocket requests
defined in official github repo
https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md#Requests
"""

logger = logging.getLogger(__name__)


class ReqClient:
    def __init__(self, **kwargs):
        self.logger = logger.getChild(self.__class__.__name__)
        self.base_client = ObsClient(**kwargs)
        try:
            success = self.base_client.authenticate()
            self.logger.info(
                f"Successfully identified {self} with the server using RPC version:{success['negotiatedRpcVersion']}"
            )
        except OBSSDKError as e:
            self.logger.error(f"{type(e).__name__}: {e}")
            raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.disconnect()

    def __repr__(self):
        return type(
            self
        ).__name__ + "(host='{host}', port={port}, password='{password}', timeout={timeout})".format(
            **self.base_client.__dict__,
        )

    def __str__(self):
        return type(self).__name__

    def disconnect(self):
        self.base_client.ws.close()

    def send(self, param, data=None, raw=False):
        try:
            response = self.base_client.req(param, data)
            if not response["requestStatus"]["result"]:
                raise OBSSDKRequestError(
                    response["requestType"],
                    response["requestStatus"]["code"],
                    response["requestStatus"].get("comment"),
                )
        except OBSSDKRequestError as e:
            self.logger.exception(f"{type(e).__name__}: {e}")
            raise
        if "responseData" in response:
            if raw:
                return response["responseData"]
            return as_dataclass(response["requestType"], response["responseData"])

    def get_version(self):
        """
        Gets data about the current plugin and RPC version.

        :return: The version info as a dictionary
        :rtype:  dict


        """
        return self.send("GetVersion")

    def get_stats(self):
        """
        Gets statistics about OBS, obs-websocket, and the current session.

        :return: The stats info as a dictionary
        :rtype:  dict


        """
        return self.send("GetStats")

    def broadcast_custom_event(self, eventData):
        """
        Broadcasts a CustomEvent to all WebSocket clients. Receivers are clients which are identified and subscribed.

        :param eventData: Data payload to emit to all receivers
        :type eventData: object
        :return: empty response
        :rtype: str


        """
        self.send("BroadcastCustomEvent", eventData)

    def call_vendor_request(self, vendor_name, request_type, request_data=None):
        """
        Call a request registered to a vendor.

        A vendor is a unique name registered by a
        third-party plugin or script, which allows
        for custom requests and events to be added
        to obs-websocket. If a plugin or script
        implements vendor requests or events,
        documentation is expected to be provided with them.

        :param vendorName:  Name of the vendor to use
        :type vendorName: str
        :param requestType: The request type to call
        :type requestType: str
        :param requestData: Object containing appropriate request data
        :type requestData: dict, optional
        :return: responseData
        :rtype: dict


        """
        payload = {"vendorName": vendor_name, "requestType": request_type}
        if request_data:
            payload["requestData"] = request_data
        return self.send("CallVendorRequest", payload)

    def get_hot_key_list(self):
        """
        Gets an array of all hotkey names in OBS

        :return: hotkeys
        :rtype: list[str]


        """
        return self.send("GetHotkeyList")

    get_hotkey_list = get_hot_key_list

    def trigger_hot_key_by_name(self, hotkeyName, contextName=None):
        """
        Triggers a hotkey using its name. For hotkey names
        See GetHotkeyList

        :param hotkeyName: Name of the hotkey to trigger
        :type hotkeyName: str
        :param contextName: Name of context of the hotkey to trigger
        :type contextName: str, optional


        """
        payload = {"hotkeyName": hotkeyName, "contextName": contextName}
        self.send("TriggerHotkeyByName", payload)

    trigger_hotkey_by_name = trigger_hot_key_by_name

    def trigger_hot_key_by_key_sequence(
        self, keyId, pressShift=None, pressCtrl=None, pressAlt=None, pressCmd=None
    ):
        """
        Triggers a hotkey using a sequence of keys.

        :param keyId: The OBS key ID to use. See https://github.com/obsproject/obs-studio/blob/master/libobs/obs-hotkeys.h
        :type keyId: str
        :param pressShift: Press Shift
        :type pressShift: bool, optional
        :param pressCtrl: Press CTRL
        :type pressCtrl: bool, optional
        :param pressAlt: Press ALT
        :type pressAlt: bool, optional
        :param pressCmd: Press CMD (Mac)
        :type pressCmd: bool, optional


        """
        payload = {
            "keyId": keyId,
            "keyModifiers": {
                "shift": pressShift,
                "control": pressCtrl,
                "alt": pressAlt,
                "cmd": pressCmd,
            },
        }
        self.send("TriggerHotkeyByKeySequence", payload)

    trigger_hotkey_by_key_sequence = trigger_hot_key_by_key_sequence

    def sleep(self, sleepMillis=None, sleepFrames=None):
        """
        Sleeps for a time duration or number of frames.
        Only available in request batches with types SERIAL_REALTIME or SERIAL_FRAME

        :param sleepMillis: Number of milliseconds to sleep for (if SERIAL_REALTIME mode) 0 <= sleepMillis <= 50000
        :type sleepMillis: int
        :param sleepFrames: Number of frames to sleep for (if SERIAL_FRAME mode)  0 <= sleepFrames <= 10000
        :type sleepFrames: int


        """
        payload = {"sleepMillis": sleepMillis, "sleepFrames": sleepFrames}
        self.send("Sleep", payload)

    def get_persistent_data(self, realm, slotName):
        """
        Gets the value of a "slot" from the selected persistent data realm.

        :param realm: The data realm to select
                      OBS_WEBSOCKET_DATA_REALM_GLOBAL or OBS_WEBSOCKET_DATA_REALM_PROFILE
        :type realm: str
        :param slotName: The name of the slot to retrieve data from
        :type slotName: str
        :return: slotValue Value associated with the slot
        :rtype: any


        """
        payload = {"realm": realm, "slotName": slotName}
        return self.send("GetPersistentData", payload)

    def set_persistent_data(self, realm, slotName, slotValue):
        """
        Sets the value of a "slot" from the selected persistent data realm.

        :param realm: The data realm to select.
                      OBS_WEBSOCKET_DATA_REALM_GLOBAL or OBS_WEBSOCKET_DATA_REALM_PROFILE
        :type realm: str
        :param slotName: The name of the slot to retrieve data from
        :type slotName: str
        :param slotValue: The value to apply to the slot
        :type slotValue: any


        """
        payload = {"realm": realm, "slotName": slotName, "slotValue": slotValue}
        self.send("SetPersistentData", payload)

    def get_scene_collection_list(self):
        """
        Gets an array of all scene collections

        :return: sceneCollections
        :rtype: list[str]


        """
        return self.send("GetSceneCollectionList")

    def set_current_scene_collection(self, name):
        """
        Switches to a scene collection.

        :param name: Name of the scene collection to switch to
        :type name: str


        """
        payload = {"sceneCollectionName": name}
        self.send("SetCurrentSceneCollection", payload)

    def create_scene_collection(self, name):
        """
        Creates a new scene collection, switching to it in the process.
        Note: This will block until the collection has finished changing.

        :param name: Name for the new scene collection
        :type name: str


        """
        payload = {"sceneCollectionName": name}
        self.send("CreateSceneCollection", payload)

    def get_profile_list(self):
        """
        Gets a list of all profiles

        :return: profiles (List of all profiles)
        :rtype: list[str]


        """
        return self.send("GetProfileList")

    def set_current_profile(self, name):
        """
        Switches to a profile

        :param name: Name of the profile to switch to
        :type name: str


        """
        payload = {"profileName": name}
        self.send("SetCurrentProfile", payload)

    def create_profile(self, name):
        """
        Creates a new profile, switching to it in the process

        :param name: Name for the new profile
        :type name: str


        """
        payload = {"profileName": name}
        self.send("CreateProfile", payload)

    def remove_profile(self, name):
        """
        Removes a profile. If the current profile is chosen,
        it will change to a different profile first.

        :param name: Name of the profile to remove
        :type name: str


        """
        payload = {"profileName": name}
        self.send("RemoveProfile", payload)

    def get_profile_parameter(self, category, name):
        """
        Gets a parameter from the current profile's configuration.

        :param category: Category of the parameter to get
        :type category: str
        :param name: Name of the parameter to get
        :type name: str

        :return: Value and default value for the parameter
        :rtype: str


        """
        payload = {"parameterCategory": category, "parameterName": name}
        return self.send("GetProfileParameter", payload)

    def set_profile_parameter(self, category, name, value):
        """
        Sets the value of a parameter in the current profile's configuration.

        :param category: Category of the parameter to set
        :type category: str
        :param name: Name of the parameter to set
        :type name: str
        :param value: Value of the parameter to set. Use null to delete
        :type value: str

        :return: Value and default value for the parameter
        :rtype: str


        """
        payload = {
            "parameterCategory": category,
            "parameterName": name,
            "parameterValue": value,
        }
        self.send("SetProfileParameter", payload)

    def get_video_settings(self):
        """
        Gets the current video settings.
        Note: To get the true FPS value, divide the FPS numerator by the FPS denominator.
        Example: 60000/1001


        """
        return self.send("GetVideoSettings")

    def set_video_settings(
        self, numerator, denominator, base_width, base_height, out_width, out_height
    ):
        """
        Sets the current video settings.
        Note: Fields must be specified in pairs.
        For example, you cannot set only baseWidth without needing to specify baseHeight.

        :param numerator:    Numerator of the fractional FPS value  >=1
        :type  numerator:    int
        :param denominator:  Denominator of the fractional FPS value >=1
        :type  denominator:  int
        :param base_width:   Width of the base (canvas) resolution in pixels (>= 1, <= 4096)
        :type  base_width:   int
        :param base_height:  Height of the base (canvas) resolution in pixels (>= 1, <= 4096)
        :type  base_height:  int
        :param out_width:    Width of the output resolution in pixels (>= 1, <= 4096)
        :type  out_width:    int
        :param out_height:   Height of the output resolution in pixels (>= 1, <= 4096)
        :type  out_height:   int


        """
        payload = {
            "fpsNumerator": numerator,
            "fpsDenominator": denominator,
            "baseWidth": base_width,
            "baseHeight": base_height,
            "outputWidth": out_width,
            "outputHeight": out_height,
        }
        self.send("SetVideoSettings", payload)

    def get_stream_service_settings(self):
        """
        Gets the current stream service settings (stream destination).


        """
        return self.send("GetStreamServiceSettings")

    def set_stream_service_settings(self, ss_type, ss_settings):
        """
        Sets the current stream service settings (stream destination).
        Note: Simple RTMP settings can be set with type rtmp_custom
        and the settings fields server and key.

        :param ss_type:     Type of stream service to apply. Example: rtmp_common or rtmp_custom
        :type  ss_type:     string
        :param ss_setting:  Settings to apply to the service
        :type  ss_setting:  dict


        """
        payload = {
            "streamServiceType": ss_type,
            "streamServiceSettings": ss_settings,
        }
        self.send("SetStreamServiceSettings", payload)

    def get_record_directory(self):
        """
        Gets the current directory that the record output is set to.
        """
        return self.send("GetRecordDirectory")

    def set_record_directory(self, recordDirectory):
        """
        Sets the current directory that the record output writes files to.
        IMPORTANT NOTE: Requires obs websocket v5.3 or higher.

        :param recordDirectory: Output directory
        :type recordDirectory: str
        """
        payload = {
            "recordDirectory": recordDirectory,
        }
        return self.send("SetRecordDirectory", payload)

    def get_source_active(self, name):
        """
        Gets the active and show state of a source

        :param name: Name of the source to get the active state of
        :type name: str


        """
        payload = {"sourceName": name}
        return self.send("GetSourceActive", payload)

    def get_source_screenshot(self, name, img_format, width, height, quality):
        """
        Gets a Base64-encoded screenshot of a source.
        The imageWidth and imageHeight parameters are
        treated as "scale to inner", meaning the smallest ratio
        will be used and the aspect ratio of the original resolution is kept.
        If imageWidth and imageHeight are not specified, the compressed image
        will use the full resolution of the source.

        :param name:    Name of the source to take a screenshot of
        :type name:     str
        :param format:  Image compression format to use. Use GetVersion to get compatible image formats
        :type format:   str
        :param width:   Width to scale the screenshot to (>= 8, <= 4096)
        :type width:    int
        :param height:  Height to scale the screenshot to (>= 8, <= 4096)
        :type height:   int
        :param quality: Compression quality to use. 0 for high compression, 100 for uncompressed. -1 to use "default"
        :type quality:  int


        """
        payload = {
            "sourceName": name,
            "imageFormat": img_format,
            "imageWidth": width,
            "imageHeight": height,
            "imageCompressionQuality": quality,
        }
        return self.send("GetSourceScreenshot", payload)

    def save_source_screenshot(
        self, name, img_format, file_path, width, height, quality
    ):
        """
        Saves a Base64-encoded screenshot of a source.
        The imageWidth and imageHeight parameters are
        treated as "scale to inner", meaning the smallest ratio
        will be used and the aspect ratio of the original resolution is kept.
        If imageWidth and imageHeight are not specified, the compressed image
        will use the full resolution of the source.

        :param name:        Name of the source to take a screenshot of
        :type name:         str
        :param format:      Image compression format to use. Use GetVersion to get compatible image formats
        :type format:       str
        :param file_path:   Path to save the screenshot file to. Eg. C:\\Users\\user\\Desktop\\screenshot.png
        :type file_path:    str
        :param width:       Width to scale the screenshot to (>= 8, <= 4096)
        :type width:        int
        :param height:      Height to scale the screenshot to (>= 8, <= 4096)
        :type height:       int
        :param quality:     Compression quality to use. 0 for high compression, 100 for uncompressed. -1 to use "default"
        :type quality:      int


        """
        payload = {
            "sourceName": name,
            "imageFormat": img_format,
            "imageFilePath": file_path,
            "imageWidth": width,
            "imageHeight": height,
            "imageCompressionQuality": quality,
        }
        return self.send("SaveSourceScreenshot", payload)

    def get_scene_list(self):
        """
        Gets a list of all scenes in OBS.


        """
        return self.send("GetSceneList")

    def get_group_list(self):
        """
        Gets a list of all groups in OBS.
        Groups in OBS are actually scenes,
        but renamed and modified. In obs-websocket,
        we treat them as scenes where we can..


        """
        return self.send("GetGroupList")

    def get_current_program_scene(self):
        """
        Gets the current program scene.


        """
        return self.send("GetCurrentProgramScene")

    def set_current_program_scene(self, name):
        """
        Sets the current program scene

        :param name: Scene to set as the current program scene
        :type name: str


        """
        payload = {"sceneName": name}
        self.send("SetCurrentProgramScene", payload)

    def get_current_preview_scene(self):
        """
        Gets the current preview scene


        """
        return self.send("GetCurrentPreviewScene")

    def set_current_preview_scene(self, name):
        """
        Sets the current program scene

        :param name: Scene to set as the current preview scene
        :type name: str


        """
        payload = {"sceneName": name}
        self.send("SetCurrentPreviewScene", payload)

    def create_scene(self, name):
        """
        Creates a new scene in OBS.

        :param name: Name for the new scene
        :type name: str


        """
        payload = {"sceneName": name}
        self.send("CreateScene", payload)

    def remove_scene(self, name):
        """
        Removes a scene from OBS

        :param name: Name of the scene to remove
        :type name: str


        """
        payload = {"sceneName": name}
        self.send("RemoveScene", payload)

    def set_scene_name(self, old_name, new_name):
        """
        Sets the name of a scene (rename).

        :param old_name: Name of the scene to be renamed
        :type old_name: str
        :param new_name: New name for the scene
        :type new_name: str


        """
        payload = {"sceneName": old_name, "newSceneName": new_name}
        self.send("SetSceneName", payload)

    def get_scene_scene_transition_override(self, name):
        """
        Gets the scene transition overridden for a scene.

        :param name: Name of the scene
        :type name: str


        """
        payload = {"sceneName": name}
        return self.send("GetSceneSceneTransitionOverride", payload)

    def set_scene_scene_transition_override(self, scene_name, tr_name, tr_duration):
        """
        Gets the scene transition overridden for a scene.

        :param scene_name:  Name of the scene
        :type scene_name:   str
        :param tr_name:     Name of the scene transition to use as override. Specify null to remove
        :type tr_name:      str
        :param tr_duration: Duration to use for any overridden transition. Specify null to remove (>= 50, <= 20000)
        :type tr_duration:  int


        """
        payload = {
            "sceneName": scene_name,
            "transitionName": tr_name,
            "transitionDuration": tr_duration,
        }
        self.send("SetSceneSceneTransitionOverride", payload)

    def get_input_list(self, kind=None):
        """
        Gets a list of all inputs in OBS.

        :param kind: Restrict the list to only inputs of the specified kind
        :type kind: str


        """
        payload = {"inputKind": kind}
        return self.send("GetInputList", payload)

    def get_input_kind_list(self, unversioned):
        """
        Gets a list of all available input kinds in OBS.

        :param unversioned: True == Return all kinds as unversioned, False == Return with version suffixes (if available)
        :type unversioned: bool


        """
        payload = {"unversioned": unversioned}
        return self.send("GetInputKindList", payload)

    def get_special_inputs(self):
        """
        Gets the name of all special inputs.


        """
        return self.send("GetSpecialInputs")

    def create_input(
        self, sceneName, inputName, inputKind, inputSettings, sceneItemEnabled
    ):
        """
        Creates a new input, adding it as a scene item to the specified scene.

        :param sceneName:           Name of the scene to add the input to as a scene item
        :type sceneName:            str
        :param inputName            Name of the new input to created
        :type inputName:            str
        :param inputKind:           The kind of input to be created
        :type inputKind:            str
        :param inputSettings:       Settings object to initialize the input with
        :type inputSettings:        object
        :param sceneItemEnabled: 	Whether to set the created scene item to enabled or disabled
        :type sceneItemEnabled:     bool


        """
        payload = {
            "sceneName": sceneName,
            "inputName": inputName,
            "inputKind": inputKind,
            "inputSettings": inputSettings,
            "sceneItemEnabled": sceneItemEnabled,
        }
        return self.send("CreateInput", payload)

    def remove_input(self, name):
        """
        Removes an existing input

        :param name: Name of the input to remove
        :type name: str


        """
        payload = {"inputName": name}
        self.send("RemoveInput", payload)

    def set_input_name(self, old_name, new_name):
        """
        Sets the name of an input (rename).

        :param old_name: Current input name
        :type old_name: str
        :param new_name: New name for the input
        :type new_name: str


        """
        payload = {"inputName": old_name, "newInputName": new_name}
        self.send("SetInputName", payload)

    def get_input_default_settings(self, kind):
        """
        Gets the default settings for an input kind.

        :param kind: Input kind to get the default settings for
        :type kind:  str


        """
        payload = {"inputKind": kind}
        return self.send("GetInputDefaultSettings", payload)

    def get_input_settings(self, name):
        """
        Gets the settings of an input.
        Note: Does not include defaults. To create the entire settings object,
        overlay inputSettings over the defaultInputSettings provided by GetInputDefaultSettings.

        :param name: Input kind to get the default settings for
        :type name:  str


        """
        payload = {"inputName": name}
        return self.send("GetInputSettings", payload)

    def set_input_settings(self, name, settings, overlay):
        """
        Sets the settings of an input.

        :param name: Name of the input to set the settings of
        :type name:  str
        :param settings: Object of settings to apply
        :type settings:  dict
        :param overlay: True == apply the settings on top of existing ones, False == reset the input to its defaults, then apply settings.
        :type overlay:  bool


        """
        payload = {"inputName": name, "inputSettings": settings, "overlay": overlay}
        self.send("SetInputSettings", payload)

    def get_input_mute(self, name):
        """
        Gets the audio mute state of an input

        :param name:    Name of input to get the mute state of
        :type name:     str


        """
        payload = {"inputName": name}
        return self.send("GetInputMute", payload)

    def set_input_mute(self, name, muted):
        """
        Sets the audio mute state of an input.

        :param name:    Name of the input to set the mute state of
        :type name:     str
        :param muted:   Whether to mute the input or not
        :type muted:    bool


        """
        payload = {"inputName": name, "inputMuted": muted}
        self.send("SetInputMute", payload)

    def toggle_input_mute(self, name):
        """
        Toggles the audio mute state of an input.

        :param name:    Name of the input to toggle the mute state of
        :type name:     str


        """
        payload = {"inputName": name}
        return self.send("ToggleInputMute", payload)

    def get_input_volume(self, name):
        """
        Gets the current volume setting of an input.

        :param name:    Name of the input to get the volume of
        :type name:     str


        """
        payload = {"inputName": name}
        return self.send("GetInputVolume", payload)

    def set_input_volume(self, name, vol_mul=None, vol_db=None):
        """
        Sets the volume setting of an input.

        :param name:       Name of the input to set the volume of
        :type name:        str
        :param vol_mul:    Volume setting in mul (>= 0, <= 20)
        :type vol_mul:     int
        :param vol_db:     Volume setting in dB  (>= -100, <= 26)
        :type vol_db:      int


        """
        payload = {
            "inputName": name,
            "inputVolumeMul": vol_mul,
            "inputVolumeDb": vol_db,
        }
        self.send("SetInputVolume", payload)

    def get_input_audio_balance(self, name):
        """
        Gets the audio balance of an input.

        :param name: Name of the input to get the audio balance of
        :type name:  str


        """
        payload = {"inputName": name}
        return self.send("GetInputAudioBalance", payload)

    def set_input_audio_balance(self, name, balance):
        """
        Sets the audio balance of an input.

        :param name: Name of the input to get the audio balance of
        :type name:  str
        :param balance: New audio balance value (>= 0.0, <= 1.0)
        :type balance:  int


        """
        payload = {"inputName": name, "inputAudioBalance": balance}
        self.send("SetInputAudioBalance", payload)

    def get_input_audio_sync_offset(self, name):
        """
        Gets the audio sync offset of an input.

        :param name: Name of the input to get the audio sync offset of
        :type name:  str


        """
        payload = {"inputName": name}
        return self.send("GetInputAudioSyncOffset", payload)

    def set_input_audio_sync_offset(self, name, offset):
        """
        Sets the audio sync offset of an input.

        :param name: Name of the input to set the audio sync offset of
        :type name:  str
        :param offset: New audio sync offset in milliseconds (>= -950, <= 20000)
        :type offset:  int


        """
        payload = {"inputName": name, "inputAudioSyncOffset": offset}
        self.send("SetInputAudioSyncOffset", payload)

    def get_input_audio_monitor_type(self, name):
        """
        Gets the audio monitor type of an input.

        The available audio monitor types are:
            OBS_MONITORING_TYPE_NONE
            OBS_MONITORING_TYPE_MONITOR_ONLY
            OBS_MONITORING_TYPE_MONITOR_AND_OUTPUT


        :param name: Name of the input to get the audio monitor type of
        :type name:  str


        """
        payload = {"inputName": name}
        return self.send("GetInputAudioMonitorType", payload)

    def set_input_audio_monitor_type(self, name, mon_type):
        """
        Sets the audio monitor type of an input.

        :param name: Name of the input to set the audio monitor type of
        :type name:  str
        :param mon_type:  	Audio monitor type
        :type mon_type:  int


        """
        payload = {"inputName": name, "monitorType": mon_type}
        self.send("SetInputAudioMonitorType", payload)

    def get_input_audio_tracks(self, name):
        """
        Gets the enable state of all audio tracks of an input.

        :param name: Name of the input
        :type name:  str


        """
        payload = {"inputName": name}
        return self.send("GetInputAudioTracks", payload)

    def set_input_audio_tracks(self, name, track):
        """
        Sets the enable state of audio tracks of an input.

        :param name: Name of the input
        :type name:  str
        :param track: Track settings to apply
        :type track:  int


        """
        payload = {"inputName": name, "inputAudioTracks": track}
        self.send("SetInputAudioTracks", payload)

    def get_input_properties_list_property_items(self, input_name, prop_name):
        """
        Gets the items of a list property from an input's properties.
        Note: Use this in cases where an input provides a dynamic,
        selectable list of items. For example, display capture,
        where it provides a list of available displays.

        :param input_name:  Name of the input
        :type input_name:   str
        :param prop_name:   Name of the list property to get the items of
        :type prop_name:    str


        """
        payload = {"inputName": input_name, "propertyName": prop_name}
        return self.send("GetInputPropertiesListPropertyItems", payload)

    def press_input_properties_button(self, input_name, prop_name):
        """
        Presses a button in the properties of an input.
        Note: Use this in cases where there is a button
        in the properties of an input that cannot be accessed in any other way.
        For example, browser sources, where there is a refresh button.

        :param input_name:  Name of the input
        :type input_name:   str
        :param prop_name:   Name of the button property to press
        :type prop_name:    str


        """
        payload = {"inputName": input_name, "propertyName": prop_name}
        self.send("PressInputPropertiesButton", payload)

    def get_transition_kind_list(self):
        """
        Gets an array of all available transition kinds.
        Similar to GetInputKindList


        """
        return self.send("GetTransitionKindList")

    def get_scene_transition_list(self):
        """
        Gets an array of all scene transitions in OBS.


        """
        return self.send("GetSceneTransitionList")

    def get_current_scene_transition(self):
        """
        Gets an array of all scene transitions in OBS.


        """
        return self.send("GetCurrentSceneTransition")

    def set_current_scene_transition(self, name):
        """
        Sets the current scene transition.
        Small note: While the namespace of scene transitions is generally unique,
        that uniqueness is not a guarantee as it is with other resources like inputs.

        :param name: Name of the transition to make active
        :type name:  str


        """
        payload = {"transitionName": name}
        self.send("SetCurrentSceneTransition", payload)

    def set_current_scene_transition_duration(self, duration):
        """
        Sets the duration of the current scene transition, if it is not fixed.

        :param duration: Duration in milliseconds (>= 50, <= 20000)
        :type duration:  str


        """
        payload = {"transitionDuration": duration}
        self.send("SetCurrentSceneTransitionDuration", payload)

    def set_current_scene_transition_settings(self, settings, overlay=None):
        """
        Sets the settings of the current scene transition.

        :param settings: Settings object to apply to the transition. Can be {}
        :type settings:  dict
        :param overlay: Whether to overlay over the current settings or replace them
        :type overlay:  bool


        """
        payload = {"transitionSettings": settings, "overlay": overlay}
        self.send("SetCurrentSceneTransitionSettings", payload)

    def get_current_scene_transition_cursor(self):
        """
        Gets the cursor position of the current scene transition.
        Note: transitionCursor will return 1.0 when the transition is inactive.


        """
        return self.send("GetCurrentSceneTransitionCursor")

    def trigger_studio_mode_transition(self):
        """
        Triggers the current scene transition.
        Same functionality as the Transition button in studio mode.
        Note: Studio mode should be active. if not throws an
        RequestStatus::StudioModeNotActive (506) in response


        """
        self.send("TriggerStudioModeTransition")

    def set_t_bar_position(self, pos, release=None):
        """
        Sets the position of the TBar.
        Very important note: This will be deprecated
        and replaced in a future version of obs-websocket.

        :param pos: New position  (>= 0.0, <= 1.0)
        :type pos:  float
        :param release: Whether to release the TBar. Only set false if you know that you will be sending another position update
        :type release:  bool


        """
        payload = {"position": pos, "release": release}
        self.send("SetTBarPosition", payload)

    def get_source_filter_kind_list(self):
        """
        Gets an array of all available source filter kinds.


        """
        return self.send("GetSourceFilterKindList")

    def get_source_filter_list(self, name):
        """
        Gets a list of all of a source's filters.

        :param name: Name of the source
        :type name:  str


        """
        payload = {"sourceName": name}
        return self.send("GetSourceFilterList", payload)

    def get_source_filter_default_settings(self, kind):
        """
        Gets the default settings for a filter kind.

        :param kind: Filter kind to get the default settings for
        :type kind:  str


        """
        payload = {"filterKind": kind}
        return self.send("GetSourceFilterDefaultSettings", payload)

    def create_source_filter(
        self, source_name, filter_name, filter_kind, filter_settings=None
    ):
        """
        Gets the default settings for a filter kind.

        :param source_name: Name of the source to add the filter to
        :type source_name:  str
        :param filter_name: Name of the new filter to be created
        :type filter_name:  str
        :param filter_kind: The kind of filter to be created
        :type filter_kind:  str
        :param filter_settings: Settings object to initialize the filter with
        :type filter_settings:  dict


        """
        payload = {
            "sourceName": source_name,
            "filterName": filter_name,
            "filterKind": filter_kind,
            "filterSettings": filter_settings,
        }
        self.send("CreateSourceFilter", payload)

    def remove_source_filter(self, source_name, filter_name):
        """
        Gets the default settings for a filter kind.

        :param source_name: Name of the source the filter is on
        :type source_name:  str
        :param filter_name: Name of the filter to remove
        :type filter_name:  str


        """
        payload = {
            "sourceName": source_name,
            "filterName": filter_name,
        }
        self.send("RemoveSourceFilter", payload)

    def set_source_filter_name(self, source_name, old_filter_name, new_filter_name):
        """
        Sets the name of a source filter (rename).

        :param source_name: Name of the source the filter is on
        :type source_name:  str
        :param old_filter_name: Current name of the filter
        :type old_filter_name:  str
        :param new_filter_name: New name for the filter
        :type new_filter_name:  str


        """
        payload = {
            "sourceName": source_name,
            "filterName": old_filter_name,
            "newFilterName": new_filter_name,
        }
        self.send("SetSourceFilterName", payload)

    def get_source_filter(self, source_name, filter_name):
        """
        Gets the info for a specific source filter.

        :param source_name: Name of the source
        :type source_name:  str
        :param filter_name: Name of the filter
        :type filter_name:  str


        """
        payload = {"sourceName": source_name, "filterName": filter_name}
        return self.send("GetSourceFilter", payload)

    def set_source_filter_index(self, source_name, filter_name, filter_index):
        """
        Sets the index position of a filter on a source.

        :param source_name: Name of the source the filter is on
        :type source_name:  str
        :param filter_name: Name of the filter
        :type filter_name:  str
        :param filterIndex: New index position of the filter (>= 0)
        :type filterIndex:  int


        """
        payload = {
            "sourceName": source_name,
            "filterName": filter_name,
            "filterIndex": filter_index,
        }
        self.send("SetSourceFilterIndex", payload)

    def set_source_filter_settings(
        self, source_name, filter_name, settings, overlay=None
    ):
        """
        Sets the settings of a source filter.

        :param source_name: Name of the source the filter is on
        :type source_name:  str
        :param filter_name: Name of the filter to set the settings of
        :type filter_name:  str
        :param settings: Dictionary of settings to apply
        :type settings:  dict
        :param overlay: True == apply the settings on top of existing ones, False == reset the input to its defaults, then apply settings.
        :type overlay:  bool


        """
        payload = {
            "sourceName": source_name,
            "filterName": filter_name,
            "filterSettings": settings,
            "overlay": overlay,
        }
        self.send("SetSourceFilterSettings", payload)

    def set_source_filter_enabled(self, source_name, filter_name, enabled):
        """
        Sets the enable state of a source filter.

        :param source_name: Name of the source the filter is on
        :type source_name:  str
        :param filter_name: Name of the filter
        :type filter_name:  str
        :param enabled: New enable state of the filter
        :type enabled:  bool


        """
        payload = {
            "sourceName": source_name,
            "filterName": filter_name,
            "filterEnabled": enabled,
        }
        self.send("SetSourceFilterEnabled", payload)

    def get_scene_item_list(self, name):
        """
        Gets a list of all scene items in a scene.

        :param name: Name of the scene to get the items of
        :type name: str


        """
        payload = {"sceneName": name}
        return self.send("GetSceneItemList", payload)

    def get_group_scene_item_list(self, name):
        """
        Basically GetSceneItemList, but for groups.

        Using groups at all in OBS is discouraged, as they are very broken under the hood.

        :param name: Name of the group to get the items of
        :type name: str


        """
        payload = {"sceneName": name}
        return self.send("GetGroupSceneItemList", payload)

    def get_scene_item_id(self, scene_name, source_name, offset=None):
        """
        Searches a scene for a source, and returns its id.

        :param scene_name: Name of the scene or group to search in
        :type scene_name: str
        :param source_name: Name of the source to find
        :type source_name: str
        :param offset:  	Number of matches to skip during search. >= 0 means first forward. -1 means last (top) item (>= -1)
        :type offset: int


        """
        payload = {
            "sceneName": scene_name,
            "sourceName": source_name,
            "searchOffset": offset,
        }
        return self.send("GetSceneItemId", payload)

    def get_scene_item_source(self, scene_name, scene_item_id):
        """
        Gets the source associated with a scene item.

        :param scene_item_id: Numeric ID of the scene item (>= 0)
        :type scene_item_id: int
        :param scene_name: Name of the scene the item is in.
        :type scene_name: str


        """
        payload = {
            "sceneItemId": scene_item_id,
            "sceneName": scene_name,
        }
        return self.send("GetSceneItemSource", payload)

    def create_scene_item(self, scene_name, source_name, enabled=None):
        """
        Creates a new scene item using a source.
        Scenes only

        :param scene_name: Name of the scene to create the new item in
        :type scene_name: str
        :param source_name: Name of the source to add to the scene
        :type source_name: str
        :param enabled: Enable state to apply to the scene item on creation
        :type enabled: bool


        """
        payload = {
            "sceneName": scene_name,
            "sourceName": source_name,
            "sceneItemEnabled": enabled,
        }
        return self.send("CreateSceneItem", payload)

    def remove_scene_item(self, scene_name, item_id):
        """
        Removes a scene item from a scene.
        Scenes only

        :param scene_name: Name of the scene the item is in
        :type scene_name: str
        :param item_id: Numeric ID of the scene item
        :type item_id: int


        """
        payload = {
            "sceneName": scene_name,
            "sceneItemId": item_id,
        }
        self.send("RemoveSceneItem", payload)

    def duplicate_scene_item(self, scene_name, item_id, dest_scene_name=None):
        """
        Duplicates a scene item, copying all transform and crop info.
        Scenes only

        :param scene_name: Name of the scene the item is in
        :type scene_name: str
        :param item_id: Numeric ID of the scene item (>= 0)
        :type item_id: int
        :param dest_scene_name: Name of the scene to create the duplicated item in
        :type dest_scene_name: str


        """
        payload = {
            "sceneName": scene_name,
            "sceneItemId": item_id,
            "destinationSceneName": dest_scene_name,
        }
        return self.send("DuplicateSceneItem", payload)

    def get_scene_item_transform(self, scene_name, item_id):
        """
        Gets the transform and crop info of a scene item.
        Scenes and Groups

        :param scene_name: Name of the scene the item is in
        :type scene_name: str
        :param item_id: Numeric ID of the scene item (>= 0)
        :type item_id: int


        """
        payload = {
            "sceneName": scene_name,
            "sceneItemId": item_id,
        }
        return self.send("GetSceneItemTransform", payload)

    def set_scene_item_transform(self, scene_name, item_id, transform):
        """
        Sets the transform and crop info of a scene item.

        :param scene_name: Name of the scene the item is in
        :type scene_name: str
        :param item_id: Numeric ID of the scene item (>= 0)
        :type item_id: int
        :param transform: Dictionary containing scene item transform info to update
        :type transform: dict
        """
        payload = {
            "sceneName": scene_name,
            "sceneItemId": item_id,
            "sceneItemTransform": transform,
        }
        self.send("SetSceneItemTransform", payload)

    def get_scene_item_enabled(self, scene_name, item_id):
        """
        Gets the enable state of a scene item.
        Scenes and Groups

        :param scene_name: Name of the scene the item is in
        :type scene_name: str
        :param item_id: Numeric ID of the scene item (>= 0)
        :type item_id: int


        """
        payload = {
            "sceneName": scene_name,
            "sceneItemId": item_id,
        }
        return self.send("GetSceneItemEnabled", payload)

    def set_scene_item_enabled(self, scene_name, item_id, enabled):
        """
        Sets the enable state of a scene item.
        Scenes and Groups'

        :param scene_name: Name of the scene the item is in
        :type scene_name: str
        :param item_id: Numeric ID of the scene item (>= 0)
        :type item_id: int
        :param enabled: New enable state of the scene item
        :type enabled: bool


        """
        payload = {
            "sceneName": scene_name,
            "sceneItemId": item_id,
            "sceneItemEnabled": enabled,
        }
        self.send("SetSceneItemEnabled", payload)

    def get_scene_item_locked(self, scene_name, item_id):
        """
        Gets the lock state of a scene item.
        Scenes and Groups

        :param scene_name: Name of the scene the item is in
        :type scene_name: str
        :param item_id: Numeric ID of the scene item (>= 0)
        :type item_id: int


        """
        payload = {
            "sceneName": scene_name,
            "sceneItemId": item_id,
        }
        return self.send("GetSceneItemLocked", payload)

    def set_scene_item_locked(self, scene_name, item_id, locked):
        """
        Sets the lock state of a scene item.
        Scenes and Groups

        :param scene_name: Name of the scene the item is in
        :type scene_name: str
        :param item_id: Numeric ID of the scene item (>= 0)
        :type item_id: int
        :param locked: New lock state of the scene item
        :type locked: bool


        """
        payload = {
            "sceneName": scene_name,
            "sceneItemId": item_id,
            "sceneItemLocked": locked,
        }
        self.send("SetSceneItemLocked", payload)

    def get_scene_item_index(self, scene_name, item_id):
        """
        Gets the index position of a scene item in a scene.
        An index of 0 is at the bottom of the source list in the UI.
        Scenes and Groups

        :param scene_name: Name of the scene the item is in
        :type scene_name: str
        :param item_id: Numeric ID of the scene item (>= 0)
        :type item_id: int


        """
        payload = {
            "sceneName": scene_name,
            "sceneItemId": item_id,
        }
        return self.send("GetSceneItemIndex", payload)

    def set_scene_item_index(self, scene_name, item_id, item_index):
        """
        Sets the index position of a scene item in a scene.
        Scenes and Groups

        :param scene_name: Name of the scene the item is in
        :type scene_name: str
        :param item_id: Numeric ID of the scene item (>= 0)
        :type item_id: int
        :param item_index: New index position of the scene item (>= 0)
        :type item_index: int


        """
        payload = {
            "sceneName": scene_name,
            "sceneItemId": item_id,
            "sceneItemIndex": item_index,
        }
        self.send("SetSceneItemIndex", payload)

    def get_scene_item_blend_mode(self, scene_name, item_id):
        """
        Gets the blend mode of a scene item.
        Blend modes:

            OBS_BLEND_NORMAL
            OBS_BLEND_ADDITIVE
            OBS_BLEND_SUBTRACT
            OBS_BLEND_SCREEN
            OBS_BLEND_MULTIPLY
            OBS_BLEND_LIGHTEN
            OBS_BLEND_DARKEN
        Scenes and Groups

        :param scene_name: Name of the scene the item is in
        :type scene_name: str
        :param item_id: Numeric ID of the scene item (>= 0)
        :type item_id: int


        """
        payload = {
            "sceneName": scene_name,
            "sceneItemId": item_id,
        }
        return self.send("GetSceneItemBlendMode", payload)

    def set_scene_item_blend_mode(self, scene_name, item_id, blend):
        """
        Sets the blend mode of a scene item.
        Scenes and Groups

        :param scene_name: Name of the scene the item is in
        :type scene_name: str
        :param item_id: Numeric ID of the scene item (>= 0)
        :type item_id: int
        :param blend: New blend mode
        :type blend: str


        """
        payload = {
            "sceneName": scene_name,
            "sceneItemId": item_id,
            "sceneItemBlendMode": blend,
        }
        self.send("SetSceneItemBlendMode", payload)

    def get_virtual_cam_status(self):
        """
        Gets the status of the virtualcam output.


        """
        return self.send("GetVirtualCamStatus")

    def toggle_virtual_cam(self):
        """
        Toggles the state of the virtualcam output.


        """
        return self.send("ToggleVirtualCam")

    def start_virtual_cam(self):
        """
        Starts the virtualcam output.


        """
        self.send("StartVirtualCam")

    def stop_virtual_cam(self):
        """
        Stops the virtualcam output.


        """
        self.send("StopVirtualCam")

    def get_replay_buffer_status(self):
        """
        Gets the status of the replay buffer output.


        """
        return self.send("GetReplayBufferStatus")

    def toggle_replay_buffer(self):
        """
        Toggles the state of the replay buffer output.


        """
        return self.send("ToggleReplayBuffer")

    def start_replay_buffer(self):
        """
        Starts the replay buffer output.


        """
        self.send("StartReplayBuffer")

    def stop_replay_buffer(self):
        """
        Stops the replay buffer output.


        """
        self.send("StopReplayBuffer")

    def save_replay_buffer(self):
        """
        Saves the contents of the replay buffer output.


        """
        self.send("SaveReplayBuffer")

    def get_last_replay_buffer_replay(self):
        """
        Gets the filename of the last replay buffer save file.


        """
        return self.send("GetLastReplayBufferReplay")

    def get_output_list(self):
        """
        Gets the list of available outputs.
        """
        return self.send("GetOutputList")

    def get_output_status(self, name):
        """
        Gets the status of an output.

        :param name: Output name
        :type name: str
        """
        payload = {"outputName": name}
        return self.send("GetOutputStatus", payload)

    def toggle_output(self, name):
        """
        Toggles the status of an output.

        :param name: Output name
        :type name: str
        """
        payload = {"outputName": name}
        return self.send("ToggleOutput", payload)

    def start_output(self, name):
        """
        Starts an output.

        :param name: Output name
        :type name: str
        """
        payload = {"outputName": name}
        self.send("StartOutput", payload)

    def stop_output(self, name):
        """
        Stops an output.

        :param name: Output name
        :type name: str
        """
        payload = {"outputName": name}
        self.send("StopOutput", payload)

    def get_output_settings(self, name):
        """
        Gets the settings of an output.

        :param name: Output name
        :type name: str
        """
        payload = {"outputName": name}
        return self.send("GetOutputSettings", payload)

    def set_output_settings(self, name, settings):
        """
        Sets the settings of an output.

        :param name: Output name
        :type name: str
        :param settings: Output settings
        :type settings: dict
        """
        payload = {
            "outputName": name,
            "outputSettings": settings,
        }
        self.send("SetOutputSettings", payload)

    def get_stream_status(self):
        """
        Gets the status of the stream output.


        """
        return self.send("GetStreamStatus")

    def toggle_stream(self):
        """
        Toggles the status of the stream output.


        """
        return self.send("ToggleStream")

    def start_stream(self):
        """
        Starts the stream output.


        """
        self.send("StartStream")

    def stop_stream(self):
        """
        Stops the stream output.


        """
        self.send("StopStream")

    def send_stream_caption(self, caption):
        """
        Sends CEA-608 caption text over the stream output.

        :param caption: Caption text
        :type caption:  str


        """
        payload = {
            "captionText": caption,
        }
        self.send("SendStreamCaption", payload)

    def get_record_status(self):
        """
        Gets the status of the record output.


        """
        return self.send("GetRecordStatus")

    def toggle_record(self):
        """
        Toggles the status of the record output.


        """
        return self.send("ToggleRecord")

    def start_record(self):
        """
        Starts the record output.


        """
        self.send("StartRecord")

    def stop_record(self):
        """
        Stops the record output.


        """
        return self.send("StopRecord")

    def toggle_record_pause(self):
        """
        Toggles pause on the record output.


        """
        self.send("ToggleRecordPause")

    def pause_record(self):
        """
        Pauses the record output.


        """
        self.send("PauseRecord")

    def resume_record(self):
        """
        Resumes the record output.


        """
        self.send("ResumeRecord")

    def split_record_file(self):
        """
        Splits the current file being recorded into a new file.


        """
        self.send("SplitRecordFile")

    def create_record_chapter(self, chapter_name=None):
        """
        Adds a new chapter marker to the file currently being recorded.

        Note: As of OBS 30.2.0, the only file format supporting this feature is Hybrid MP4.

        :param chapter_name: Name of the new chapter
        :type chapter_name: str


        """
        payload = {"chapterName": chapter_name}
        self.send("CreateRecordChapter", payload)

    def get_media_input_status(self, name):
        """
        Gets the status of a media input.

        Media States:
            OBS_MEDIA_STATE_NONE
            OBS_MEDIA_STATE_PLAYING
            OBS_MEDIA_STATE_OPENING
            OBS_MEDIA_STATE_BUFFERING
            OBS_MEDIA_STATE_PAUSED
            OBS_MEDIA_STATE_STOPPED
            OBS_MEDIA_STATE_ENDED
            OBS_MEDIA_STATE_ERROR

        :param name: Name of the media input
        :type name:  str


        """
        payload = {"inputName": name}
        return self.send("GetMediaInputStatus", payload)

    def set_media_input_cursor(self, name, cursor):
        """
        Sets the cursor position of a media input.
        This request does not perform bounds checking of the cursor position.

        :param name: Name of the media input
        :type name:  str
        :param cursor: New cursor position to set (>= 0)
        :type cursor:  int


        """
        payload = {"inputName": name, "mediaCursor": cursor}
        self.send("SetMediaInputCursor", payload)

    def offset_media_input_cursor(self, name, offset):
        """
        Offsets the current cursor position of a media input by the specified value.
        This request does not perform bounds checking of the cursor position.

        :param name: Name of the media input
        :type name:  str
        :param offset: Value to offset the current cursor position by
        :type offset:  int


        """
        payload = {"inputName": name, "mediaCursorOffset": offset}
        self.send("OffsetMediaInputCursor", payload)

    def trigger_media_input_action(self, name, action):
        """
        Triggers an action on a media input.

        :param name: Name of the media input
        :type name:  str
        :param action: Identifier of the ObsMediaInputAction enum
        :type action:  str


        """
        payload = {"inputName": name, "mediaAction": action}
        self.send("TriggerMediaInputAction", payload)

    def get_studio_mode_enabled(self):
        """
        Gets whether studio is enabled.


        """
        return self.send("GetStudioModeEnabled")

    def set_studio_mode_enabled(self, enabled):
        """
        Enables or disables studio mode

        :param enabled:      True == Enabled, False == Disabled
        :type enabled:       bool


        """
        payload = {"studioModeEnabled": enabled}
        self.send("SetStudioModeEnabled", payload)

    def open_input_properties_dialog(self, name):
        """
        Opens the properties dialog of an input.

        :param name:      Name of the input to open the dialog of
        :type name:       str


        """
        payload = {"inputName": name}
        self.send("OpenInputPropertiesDialog", payload)

    def open_input_filters_dialog(self, name):
        """
        Opens the filters dialog of an input.

        :param name:      Name of the input to open the dialog of
        :type name:       str


        """
        payload = {"inputName": name}
        self.send("OpenInputFiltersDialog", payload)

    def open_input_interact_dialog(self, name):
        """
        Opens the filters dialog of an input.

        :param name:      Name of the input to open the dialog of
        :type name:       str


        """
        payload = {"inputName": name}
        self.send("OpenInputInteractDialog", payload)

    def get_monitor_list(self):
        """
        Gets a list of connected monitors and information about them.


        """
        return self.send("GetMonitorList")

    def open_video_mix_projector(
        self, video_mix_type, monitor_index=-1, projector_geometry=None
    ):
        """
        Opens a projector for a specific output video mix.

        The available mix types are:
            OBS_WEBSOCKET_VIDEO_MIX_TYPE_PREVIEW
            OBS_WEBSOCKET_VIDEO_MIX_TYPE_PROGRAM
            OBS_WEBSOCKET_VIDEO_MIX_TYPE_MULTIVIEW

        :param video_mix_type: Type of mix to open.
        :type video_mix_type:  str
        :param monitor_index: Monitor index, use GetMonitorList to obtain index
        :type monitor_index:  int
        :param projector_geometry:
            Size/Position data for a windowed projector, in Qt Base64 encoded format.
            Mutually exclusive with monitorIndex
        :type projector_geometry: str

        """
        warn(
            "open_video_mix_projector request serves to provide feature parity with 4.x. "
            "It is very likely to be changed/deprecated in a future release.",
            DeprecationWarning,
            stacklevel=2,
        )
        payload = {
            "videoMixType": video_mix_type,
            "monitorIndex": monitor_index,
            "projectorGeometry": projector_geometry,
        }
        self.send("OpenVideoMixProjector", payload)

    def open_source_projector(
        self, source_name, monitor_index=-1, projector_geometry=None
    ):
        """
        Opens a projector for a source.

        :param source_name: Name of the source to open a projector for
        :type source_name:  str
        :param monitor_index: Monitor index, use GetMonitorList to obtain index
        :type monitor_index:  int
        :param projector_geometry:
            Size/Position data for a windowed projector, in Qt Base64 encoded format.
            Mutually exclusive with monitorIndex
        :type projector_geometry: str

        """
        warn(
            "open_source_projector request serves to provide feature parity with 4.x. "
            "It is very likely to be changed/deprecated in a future release.",
            DeprecationWarning,
            stacklevel=2,
        )
        payload = {
            "sourceName": source_name,
            "monitorIndex": monitor_index,
            "projectorGeometry": projector_geometry,
        }
        self.send("OpenSourceProjector", payload)
