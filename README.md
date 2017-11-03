# AppDaemon-ImageNotify

## Description
Using the fantastic [appdaemon](https://home-assistant.io/docs/ecosystem/appdaemon/) integration with [Home Assistant](https://home-assistant.io/), this script monitors a sensor for a specific "triggered" and "normal" state. When the sensor is triggered, the script attempts to download an image (typically from a camera that supports an image URL) of the event. After a user configurable amount of time, the image is sent using the HTML5 notify component with the image attached.

Finally, when the sensor has returned to the normal state, another notification is sent with a user customizable message.

## My Usage
I have 2 gates to my backyard and want to be notified if they are left open for over two minutes. I also have two Hikvision IP cameras monitoring those gates. When the gate is opened, the script immediately downloads an image from the camera and then registers a callback for 120 seconds later. If the gate is still opened when the callback is triggered, a notification is sent to my phone via the [HTML5 notify plugin](https://home-assistant.io/components/notify.html5/) with the image of how the gate was opened. When the gate is finally closed, I receive another notification that that the gate has been closed.
