# Why PiKud exists

Living in Israel means living with the Pikud HaOref (Home Front Command) alert system.
When missiles or drones are incoming, your phone screams, the city sirens wail, and you have
somewhere between 0 and 90 seconds to get to a shelter - depending on where the threat is coming from.

The official app works. The sirens work. But I wanted something physical. Something that doesn't
rely on a phone being charged, on a notification being seen, on a sound being heard over music or sleep.
A light in the corner of the room that just *changes* - no interaction required.

I had a Raspberry Pi 1 gathering dust, a Particle Photon from a previous project, a bag of LEDs,
and a free weekend. PiKud was the result.

The Pi lives in Israel and does all the heavy lifting - polling the geo-blocked Pikud HaOref API,
tracking state, and pushing status changes to the Particle cloud. The Photon sits wherever it needs
to be and reacts: yellow when alerts are expected nearby, red when it's time to move, blue when the
all-clear comes through. No phone. No app. Just a light.

The Raspberry Pi is named **ShelteryPie**. Obviously.

---

The project got its first real-world test the same night the service was set up.
The LED turned red before the sirens did.

The family approved.

---

*Built between alerts with the amazing aid of [Claude](https://claude.ai).*
