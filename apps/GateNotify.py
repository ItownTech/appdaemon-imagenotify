import appdaemon.appapi as appapi
import json
import requests

#
# Notifications App
#
# Args:
#   sensor: the sensor to be monitored
#   cameraUrl: URL for an image of the area to be monitored
#   outFileName: Where to store the image from the camera
#   delaySeconds: How many seconds before sending a notification
#   sensorTriggerState: State indicating this sensor has been activated
#   sensorNormalState: State indicating this sensor is no longer activated
#   imageCamera: a local_file camera name that points to the outFileName
#   notifyTarget: Full path (including domain) to the notification device.
#   triggerMessage: Notification message when this zone has been activated
#       for the delaySeconds
#   triggerTitle: Notification title when this zone has been activated for
#       the delaySeconds
#   normalMessage: Notification message when this zone is no longer activated
#   normalTitle: Notification title when this zone is no longer activated
#   camUser: Username for the camera URL (can be !secret camusername)
#   camPassword: Password for the camera URL (can be !secret camuserpass)


class ImageNotification(appapi.AppDaemon):

    def initialize(self):
        sensor = self.args["sensor"]
        self.log(
            "Starting Image Notification monitor for " +
            self.get_state(
                sensor,
                "friendly_name"))
        sensor_trigger_state = self.args["sensorTriggerState"]
        sensor_normal_state = self.args["sensorNormalState"]
        self.listen_state(
            self.open_triggered,
            sensor,
            new=sensor_trigger_state)
        self.listen_state(
            self.send_closed_notification,
            sensor,
            new=sensor_normal_state)

    def open_triggered(self, entity, attribute, old, new, kwargs):
        if not self.get_state(entity, "alert"):
            self.log("Triggered. Getting image...")
            self.get_cam_image()
            seconds_before_sending = self.args["delaySeconds"]
            self.log("Image saved. Starting timer...")
            self.run_in(self.send_open_notification, seconds_before_sending)

    def get_cam_image(self):
        camera_url = self.args["cameraUrl"]
        out_filename = self.args["outFileName"]
        username = self.args["camUser"]
        password = self.args["camPassword"]

        r = requests.get(camera_url, auth=(username, password))
        with open(out_filename, 'wb') as out:
            for bits in r.iter_content():
                out.write(bits)

    def send_open_notification(self, kwargs):
        self.log("Delay timer has elapsed")
        sensor = self.args["sensor"]
        sensor_trigger_state = self.args["sensorTriggerState"]

        # Check to see if the gate is still open
        if self.get_state(sensor) == sensor_trigger_state:
            image_camera = self.args["imageCamera"]
            notify_target = self.args["notifyTarget"]
            message = self.args["triggerMessage"]
            title = self.args["triggerTitle"]
            ha_base_url = self.args["ha_base_url"]
            open_gate_image = ha_base_url + \
                self.get_state(image_camera,
                               "entity_picture")
            extra_data = {"tag": 'imageNotification',
                          'image': open_gate_image,
                          'url': open_gate_image}
            self.log("Sending data: " + json.dumps(extra_data))
            self.call_service(
                notify_target,
                message=message,
                title=title,
                data=extra_data)
            self.set_state(sensor, attributes={"alert": True})

    def send_closed_notification(self, entity, attribute, old, new, kwargs):
        if self.get_state(entity, "alert"):
            self.log("Sensor has been returned to normal")
            sensor = self.args["sensor"]
            notify_target = self.args["notifyTarget"]
            message = self.args["normalMessage"]
            title = self.args["normalTitle"]
            self.call_service(
                notify_target,
                message=message,
                title=title)
            self.set_state(sensor, attributes={"alert": False})
