"""Publish alert status to Particle cloud REST API."""

import logging
import os

import requests
from dotenv import load_dotenv

load_dotenv()

PARTICLE_DEVICE_ID = os.getenv("PARTICLE_DEVICE_ID", "")
PARTICLE_ACCESS_TOKEN = os.getenv("PARTICLE_ACCESS_TOKEN", "")
PARTICLE_EVENT = "alert_status"


def publish(status, session: requests.Session) -> None:
    if not PARTICLE_ACCESS_TOKEN or not PARTICLE_DEVICE_ID:
        return
    try:
        session.post(
            "https://api.particle.io/v1/devices/events",
            headers={"Authorization": f"Bearer {PARTICLE_ACCESS_TOKEN}"},
            data={
                "name": PARTICLE_EVENT,
                "data": status.value,
                "private": "true",
            },
            timeout=5,
        )
    except Exception as e:
        logging.warning(f"Particle publish failed: {e}")
